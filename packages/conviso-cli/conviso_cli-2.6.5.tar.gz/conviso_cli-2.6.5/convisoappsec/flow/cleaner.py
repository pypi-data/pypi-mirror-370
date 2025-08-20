import subprocess
import shutil
import os
from pathlib import Path
from typing import List, Optional


class RunnerCleanup:
    """Class to handle CI/CD runner cleanup operations"""

    def __init__(self, temp_dirs: Optional[List[str]] = None):
        """
        Initialize cleanup class

        Args:
            temp_dirs: Optional list of temporary directories to clean
        """
        self.temp_dirs = temp_dirs or [
            "/tmp",
            "/var/tmp",
            str(Path.home() / ".cache")
        ]
        self.is_runner = self._is_running_in_ci()
        self._check_requirements()

    def _is_running_in_ci(self) -> bool:
        """Check if running in a CI/CD environment"""
        ci_indicators = {
            'CI': None,
            'GITLAB_CI': None,
            'GITHUB_ACTIONS': None,
            'JENKINS_URL': None,
            'TRAVIS': None,
            'CIRCLECI': None,
            'BUILD_ID': None,
            'CI_JOB_ID': None,
            'GITHUB_RUN_ID': None,
        }

        # Check if any CI-specific environment variable is set
        for var in ci_indicators:
            if os.environ.get(var):
                print(f"Detected CI environment: {var}")
                return True

        # Additional check for runner-specific variables
        if os.environ.get('RUNNER_TEMP') or os.environ.get('RUNNER_WORKSPACE'):
            print("Detected GitHub Actions runner environment")
            return True

        print("No CI environment detected")
        return False

    def _run_command(self, command: str) -> Optional[str]:
        """Execute shell command and return output"""

        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error executing '{command}': {e.stderr}")
            return None

    def _check_requirements(self) -> None:
        """Check system requirements"""
        if not self._run_command("docker --version"):
            raise RuntimeError("Docker is not installed or not accessible")

    def get_disk_space(self) -> tuple[float, float, float]:
        """Get disk space information in GB"""
        stat = shutil.disk_usage("/")
        total = stat.total / (1024 ** 3)
        used = stat.used / (1024 ** 3)
        free = stat.free / (1024 ** 3)
        return total, used, free

    def cleanup_docker(self) -> None:
        """Clean up Docker resources"""
        commands = [
            "docker container prune -f",
            "docker image prune -f",
            "docker volume prune -f",
            "docker network prune -f"
        ]

        for cmd in commands:
            self._run_command(cmd)

    def cleanup_temp(self) -> None:
        """Clean up temporary directories"""

        for dir_path in self.temp_dirs:
            dir_path = Path(dir_path)
            if not dir_path.exists():
                continue

            for item in dir_path.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                except Exception as e:
                    print(f"Failed to remove {item}: {e}")

    def cleanup_all(self):
        """Perform full cleanup and return before/after disk space stats"""
        print("Cleaning up ...")

        self.cleanup_docker()
        self.cleanup_temp()
