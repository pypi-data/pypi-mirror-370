"""Tests for container module coverage gaps."""

import pytest
from unittest.mock import Mock, patch
import subprocess

from ctenv.container import (
    get_platform_specific_gosu_name,
    is_installed_package,
    expand_tilde_in_path,
    ContainerRunner,
)
from ctenv.config import VolumeSpec


@pytest.mark.unit
class TestPlatformDetection:
    """Tests for platform-specific functionality."""

    def test_get_platform_specific_gosu_name_arm64_target(self):
        """Test ARM64 platform detection from target platform."""
        result = get_platform_specific_gosu_name("linux/arm64")
        assert result == "gosu-arm64"

    def test_get_platform_specific_gosu_name_amd64_target(self):
        """Test AMD64 platform detection from target platform."""
        result = get_platform_specific_gosu_name("linux/amd64")
        assert result == "gosu-amd64"

    def test_get_platform_specific_gosu_name_unknown_target(self):
        """Test unknown platform defaults to amd64."""
        result = get_platform_specific_gosu_name("linux/unknown")
        assert result == "gosu-amd64"

    @patch("platform.machine")
    def test_get_platform_specific_gosu_name_host_arm64(self, mock_machine):
        """Test ARM64 host platform detection."""
        mock_machine.return_value = "aarch64"
        result = get_platform_specific_gosu_name(None)
        assert result == "gosu-arm64"

    @patch("platform.machine")
    def test_get_platform_specific_gosu_name_host_arm64_variant(self, mock_machine):
        """Test ARM64 variant host platform detection."""
        mock_machine.return_value = "arm64"
        result = get_platform_specific_gosu_name(None)
        assert result == "gosu-arm64"

    @patch("platform.machine")
    def test_get_platform_specific_gosu_name_host_x86_64(self, mock_machine):
        """Test x86_64 host platform detection."""
        mock_machine.return_value = "x86_64"
        result = get_platform_specific_gosu_name(None)
        assert result == "gosu-amd64"

    @patch("platform.machine")
    def test_get_platform_specific_gosu_name_host_unknown(self, mock_machine):
        """Test unknown host platform defaults to amd64."""
        mock_machine.return_value = "unknown_arch"
        result = get_platform_specific_gosu_name(None)
        assert result == "gosu-amd64"


@pytest.mark.unit
class TestPackageDetection:
    """Tests for package detection functionality."""

    @patch("importlib.util.find_spec")
    def test_is_installed_package_true(self, mock_find_spec):
        """Test detection when running as installed package."""
        mock_spec = Mock()
        mock_find_spec.return_value = mock_spec
        assert is_installed_package() is True

    @patch("importlib.util.find_spec")
    def test_is_installed_package_false(self, mock_find_spec):
        """Test detection when not running as installed package."""
        mock_find_spec.return_value = None
        assert is_installed_package() is False

    @patch("importlib.util.find_spec")
    def test_is_installed_package_import_error(self, mock_find_spec):
        """Test import error handling in package detection."""
        mock_find_spec.side_effect = ImportError("Module not found")
        assert is_installed_package() is False


@pytest.mark.unit
class TestHomeDirectoryExpansion:
    """Tests for home directory expansion functionality."""

    def test_expand_tilde_in_path_bare_tilde(self):
        """Test expansion of bare tilde."""
        runtime = Mock()
        runtime.user_home = "/home/testuser"

        result = expand_tilde_in_path("~", runtime)
        assert result == "/home/testuser"

    def test_expand_tilde_in_path_tilde_with_path(self):
        """Test expansion of tilde with path."""
        runtime = Mock()
        runtime.user_home = "/home/testuser"

        result = expand_tilde_in_path("~/documents", runtime)
        assert result == "/home/testuser/documents"

    def test_expand_tilde_in_path_no_tilde(self):
        """Test no expansion when no tilde present."""
        runtime = Mock()
        runtime.user_home = "/home/testuser"

        result = expand_tilde_in_path("/absolute/path", runtime)
        assert result == "/absolute/path"


@pytest.mark.unit
class TestContainerExecutionErrors:
    """Tests for container execution error handling."""

    @patch("ctenv.container.subprocess.run")
    def test_container_execution_failure_non_dry_run(self, mock_run):
        """Test container execution failure handling in non-dry-run mode."""
        # Setup the mock to raise CalledProcessError
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["docker", "run"], stderr="Container failed"
        )

        runner = ContainerRunner()

        # Create a minimal container spec
        spec = Mock()
        spec.image = "test:latest"
        spec.command = ["echo", "hello"]
        spec.env_vars = []
        spec.volumes = []
        spec.run_args = []
        spec.workdir = "/workspace"
        spec.user_name = "testuser"
        spec.user_id = 1000
        spec.group_name = "testgroup"
        spec.group_id = 1000
        spec.user_home = "/home/testuser"
        spec.container_name = "test-container"
        spec.network = None
        spec.platform = None
        spec.ulimits = {}
        spec.sudo = False
        spec.post_start_commands = []
        spec.env = []  # Environment variables (iterable)
        spec.tty = False
        # Required VolumeSpec attributes
        spec.workspace = VolumeSpec(host_path="/project", container_path="/workspace", options=[])
        spec.gosu = VolumeSpec(
            host_path="/usr/local/bin/gosu", container_path="/ctenv/gosu", options=[]
        )
        spec.chown_paths = []  # No chown paths for this test

        # Mock the entrypoint script creation and path checks
        with (
            patch("ctenv.container.build_entrypoint_script") as mock_build_script,
            patch("pathlib.Path.exists") as mock_exists,
            patch("pathlib.Path.is_file") as mock_is_file,
            patch("pathlib.Path.is_dir") as mock_is_dir,
            patch("shutil.which") as mock_which,
        ):
            mock_build_script.return_value = "#!/bin/bash\necho test"
            mock_exists.return_value = True  # gosu and workspace exist
            mock_is_file.return_value = True  # gosu is a file
            mock_is_dir.return_value = True  # workspace is a directory
            mock_which.return_value = "/usr/bin/docker"  # docker exists

            with pytest.raises(RuntimeError, match="Container execution failed"):
                runner.run_container(spec, dry_run=False)

    @patch("ctenv.container.subprocess.run")
    def test_container_execution_success_dry_run(self, mock_run):
        """Test container execution success in dry-run mode."""
        # Mock won't be called in dry-run mode, but set it up anyway
        mock_run.return_value = Mock(returncode=0)

        runner = ContainerRunner()

        # Create a minimal container spec
        spec = Mock()
        spec.image = "test:latest"
        spec.command = ["echo", "hello"]
        spec.env_vars = []
        spec.volumes = []
        spec.run_args = []
        spec.workdir = "/workspace"
        spec.user_name = "testuser"
        spec.user_id = 1000
        spec.group_name = "testgroup"
        spec.group_id = 1000
        spec.user_home = "/home/testuser"
        spec.container_name = "test-container"
        spec.network = None
        spec.platform = None
        spec.ulimits = {}
        spec.sudo = False
        spec.post_start_commands = []
        spec.env = []  # Environment variables (iterable)
        spec.tty = False
        # Required VolumeSpec attributes
        spec.workspace = VolumeSpec(host_path="/project", container_path="/workspace", options=[])
        spec.gosu = VolumeSpec(
            host_path="/usr/local/bin/gosu", container_path="/ctenv/gosu", options=[]
        )
        spec.chown_paths = []  # No chown paths for this test

        # Mock the entrypoint script creation and path checks
        with (
            patch("ctenv.container.build_entrypoint_script") as mock_build_script,
            patch("pathlib.Path.exists") as mock_exists,
            patch("pathlib.Path.is_file") as mock_is_file,
            patch("pathlib.Path.is_dir") as mock_is_dir,
            patch("shutil.which") as mock_which,
        ):
            mock_build_script.return_value = "#!/bin/bash\necho test"
            mock_exists.return_value = True  # gosu and workspace exist
            mock_is_file.return_value = True  # gosu is a file
            mock_is_dir.return_value = True  # workspace is a directory
            mock_which.return_value = "/usr/bin/docker"  # docker exists

            # In dry-run mode, should return successful result without calling subprocess
            result = runner.run_container(spec, dry_run=True)
            assert result.returncode == 0
            # Verify subprocess.run was not called in dry-run mode
            mock_run.assert_not_called()

    @patch("ctenv.container.subprocess.run")
    def test_container_with_custom_run_args_logging(self, mock_run):
        """Test debug logging of custom run arguments."""
        mock_run.return_value = Mock(returncode=0)

        runner = ContainerRunner()

        # Create a container spec with custom run args
        spec = Mock()
        spec.image = "test:latest"
        spec.command = ["echo", "hello"]
        spec.env_vars = []
        spec.volumes = []
        spec.run_args = ["--privileged", "--cap-add=SYS_ADMIN"]  # Custom run args
        spec.workdir = "/workspace"
        spec.user_name = "testuser"
        spec.user_id = 1000
        spec.group_name = "testgroup"
        spec.group_id = 1000
        spec.user_home = "/home/testuser"
        spec.container_name = "test-container"
        spec.network = None
        spec.platform = None
        spec.ulimits = {}
        spec.sudo = False
        spec.post_start_commands = []
        spec.env = []  # Environment variables (iterable)
        spec.tty = False
        # Required VolumeSpec attributes
        spec.workspace = VolumeSpec(host_path="/project", container_path="/workspace", options=[])
        spec.gosu = VolumeSpec(
            host_path="/usr/local/bin/gosu", container_path="/ctenv/gosu", options=[]
        )
        spec.chown_paths = []  # No chown paths for this test

        # Mock the entrypoint script creation and path checks
        with (
            patch("ctenv.container.build_entrypoint_script") as mock_build_script,
            patch("pathlib.Path.exists") as mock_exists,
            patch("pathlib.Path.is_file") as mock_is_file,
            patch("pathlib.Path.is_dir") as mock_is_dir,
            patch("shutil.which") as mock_which,
        ):
            mock_build_script.return_value = "#!/bin/bash\necho test"
            mock_exists.return_value = True  # gosu and workspace exist
            mock_is_file.return_value = True  # gosu is a file
            mock_is_dir.return_value = True  # workspace is a directory
            mock_which.return_value = "/usr/bin/docker"  # docker exists

            # Enable debug logging to test the logging code path
            with patch("logging.debug") as mock_debug:
                runner.run_container(spec, dry_run=True)

                # Verify debug logging was called for custom run args
                debug_calls = [call[0][0] for call in mock_debug.call_args_list]
                assert any("Custom run arguments:" in call for call in debug_calls)
                assert any("--privileged" in call for call in debug_calls)
                assert any("--cap-add=SYS_ADMIN" in call for call in debug_calls)
