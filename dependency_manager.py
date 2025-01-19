from typing import Dict, List, Optional
import subprocess
import sys
import pkg_resources
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DependencyManager:
    def __init__(self, requirements_file: str = "requirements.txt"):
        self.requirements_file = requirements_file
        self.installed_packages = self._get_installed_packages()
    
    def _get_installed_packages(self) -> Dict[str, str]:
        """Get dictionary of installed packages and their versions."""
        return {
            pkg.key: pkg.version
            for pkg in pkg_resources.working_set
        }
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if all required dependencies are installed."""
        missing = {}
        with open(self.requirements_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    package = line.strip().split('==')[0]
                    missing[package] = package.lower() in self.installed_packages
        return missing
    
    def install_dependencies(
        self,
        upgrade: bool = False
    ) -> Dict[str, str]:
        """Install all required dependencies."""
        cmd = [sys.executable, "-m", "pip", "install", "-r", self.requirements_file]
        if upgrade:
            cmd.append("--upgrade")
        
        try:
            subprocess.check_call(cmd)
            self.installed_packages = self._get_installed_packages()
            return {"status": "success", "message": "Dependencies installed successfully"}
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to install dependencies: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def add_dependency(
        self,
        package: str,
        version: Optional[str] = None
    ) -> Dict[str, str]:
        """Add a new dependency to requirements.txt."""
        if version:
            package_spec = f"{package}=={version}"
        else:
            package_spec = package
        
        try:
            # Install the package
            subprocess.check_call([
                sys.executable,
                "-m",
                "pip",
                "install",
                package_spec
            ])
            
            # Add to requirements.txt
            with open(self.requirements_file, 'a') as f:
                f.write(f"\n{package_spec}")
            
            return {
                "status": "success",
                "message": f"Added {package_spec} to requirements"
            }
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to add dependency {package}: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def remove_dependency(self, package: str) -> Dict[str, str]:
        """Remove a dependency from requirements.txt."""
        try:
            # Read current requirements
            with open(self.requirements_file, 'r') as f:
                lines = f.readlines()
            
            # Filter out the package
            new_lines = [
                line for line in lines
                if not line.strip().startswith(package)
            ]
            
            # Write back filtered requirements
            with open(self.requirements_file, 'w') as f:
                f.writelines(new_lines)
            
            # Uninstall the package
            subprocess.check_call([
                sys.executable,
                "-m",
                "pip",
                "uninstall",
                "-y",
                package
            ])
            
            return {
                "status": "success",
                "message": f"Removed {package} from requirements"
            }
        except Exception as e:
            error_msg = f"Failed to remove dependency {package}: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def export_dependencies(
        self,
        output_file: str = "requirements.txt"
    ) -> Dict[str, str]:
        """Export current environment dependencies."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True,
                text=True
            )
            
            with open(output_file, 'w') as f:
                f.write(result.stdout)
            
            return {
                "status": "success",
                "message": f"Dependencies exported to {output_file}"
            }
        except Exception as e:
            error_msg = f"Failed to export dependencies: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def check_updates(self) -> Dict[str, Dict[str, str]]:
        """Check for available updates to dependencies."""
        updates = {}
        
        for package, current_version in self.installed_packages.items():
            try:
                # Get latest version from PyPI
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "index",
                        "versions",
                        package
                    ],
                    capture_output=True,
                    text=True
                )
                
                if "Available versions:" in result.stdout:
                    latest_version = result.stdout.split(
                        "Available versions:"
                    )[1].split()[0]
                    
                    if latest_version != current_version:
                        updates[package] = {
                            "current": current_version,
                            "latest": latest_version
                        }
            except Exception as e:
                logger.warning(
                    f"Failed to check updates for {package}: {str(e)}"
                )
        
        return updates
