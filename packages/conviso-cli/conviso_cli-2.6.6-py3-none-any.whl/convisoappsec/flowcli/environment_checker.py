import os
import platform
import subprocess

class EnvironmentChecker:
    """
    A class to check the system environment for required software and services.
    """

    def __init__(self):
        self.checks = {}

    def _run_command(self, command, check_running=False):
        """Helper function to run shell commands and capture output/errors."""
        try:
            process = subprocess.run(command, capture_output=True, text=True, check=not check_running)
            if check_running:
                return process.returncode == 0, "", ""
            return process.returncode == 0, process.stdout.strip(), process.stderr.strip()
        except FileNotFoundError:
            return False, "", "Command not found"
        except subprocess.CalledProcessError as e:
            return False, "", e.stderr.strip()

    def check_docker(self):
        """Checks if Docker is installed and the daemon is running."""
        installed, _, _ = self._run_command(["docker", "--version"])
        running, _, _ = self._run_command(["docker", "info"], check_running=True)
        self.checks["docker_installed"] = installed
        self.checks["docker_running"] = running
        return installed and running

    def run_all_checks(self):
        """Runs all checks and prints a summary."""
        self.check_docker()

        print("Environment Check Summary:")
        for check, result in self.checks.items():
            if "version" in check:
                print(f"- {check.replace('_',' ').title()}: {result}")
            else:
                status = "OK" if result else "FAILED"
                print(f"- {check.replace('_',' ').title()}: {status}")

        return all(self.checks.values())
