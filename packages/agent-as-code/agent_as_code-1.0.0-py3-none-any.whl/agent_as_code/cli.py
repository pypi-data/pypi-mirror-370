"""
Agent as Code CLI Wrapper
=========================

Python wrapper around the Go-based Agent as Code CLI binary.
This module provides seamless integration between Python and the high-performance
Go implementation while maintaining familiar Python development patterns.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional, Union


class AgentCLI:
    """
    Python wrapper for the Agent as Code CLI.
    
    This class provides a Python interface to the Go-based CLI binary,
    automatically detecting the correct binary for the current platform
    and providing both direct execution and Python API methods.
    """
    
    def __init__(self, binary_path: Optional[str] = None):
        """
        Initialize the Agent CLI wrapper.
        
        Args:
            binary_path: Optional path to the agent binary. If not provided,
                        will auto-detect based on the current platform.
        """
        self.binary_path = binary_path or self._detect_binary()
        self._validate_binary()
    
    def _detect_binary(self) -> Path:
        """
        Auto-detect the correct binary for the current platform.
        
        Returns:
            Path to the appropriate binary for the current platform.
            
        Raises:
            RuntimeError: If the platform is unsupported or binary not found.
        """
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Normalize architecture names
        arch_map = {
            'x86_64': 'amd64',
            'amd64': 'amd64',
            'arm64': 'arm64',
            'aarch64': 'arm64',
        }
        
        arch = arch_map.get(machine)
        if not arch:
            raise RuntimeError(f"Unsupported architecture: {machine}")
        
        # Map platform to binary name
        platform_map = {
            'linux': f'agent-linux-{arch}',
            'darwin': f'agent-darwin-{arch}',
            'windows': f'agent-windows-{arch}.exe',
        }
        
        binary_name = platform_map.get(system)
        if not binary_name:
            raise RuntimeError(f"Unsupported platform: {system}")
        
        # Find binary in package
        package_dir = Path(__file__).parent
        binary_path = package_dir / "bin" / binary_name
        
        if not binary_path.exists():
            raise RuntimeError(
                f"Binary not found: {binary_path}\n"
                f"Platform: {system}-{arch}\n"
                f"Expected binary: {binary_name}\n"
                f"This may indicate a corrupted installation. "
                f"Try reinstalling: pip install --force-reinstall agent-as-code"
            )
        
        return binary_path
    
    def _validate_binary(self):
        """
        Validate that the binary exists and is executable.
        
        Raises:
            RuntimeError: If the binary is not found or not executable.
        """
        if not self.binary_path.exists():
            raise RuntimeError(f"Agent binary not found: {self.binary_path}")
        
        # Make executable on Unix systems
        if platform.system() != 'Windows':
            self.binary_path.chmod(0o755)
        
        # Test binary execution
        try:
            result = subprocess.run(
                [str(self.binary_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise RuntimeError(f"Binary test failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Binary test timed out")
        except Exception as e:
            raise RuntimeError(f"Binary validation failed: {e}")
    
    def execute(self, args: Optional[List[str]] = None) -> int:
        """
        Execute the agent CLI with the given arguments.
        
        Args:
            args: List of command line arguments. If None, uses sys.argv[1:].
            
        Returns:
            Exit code from the CLI execution.
        """
        if args is None:
            args = sys.argv[1:]
        
        try:
            # Execute the binary
            result = subprocess.run(
                [str(self.binary_path)] + args,
                check=False
            )
            return result.returncode
            
        except KeyboardInterrupt:
            return 130  # Standard exit code for Ctrl+C
        except Exception as e:
            print(f"Error executing agent: {e}", file=sys.stderr)
            return 1
    
    def run_command(self, args: List[str], capture_output: bool = False, 
                   timeout: Optional[float] = None) -> subprocess.CompletedProcess:
        """
        Run a command and return the result.
        
        Args:
            args: Command arguments to pass to the CLI.
            capture_output: Whether to capture stdout/stderr.
            timeout: Timeout in seconds for the command.
            
        Returns:
            CompletedProcess instance with the result.
        """
        try:
            return subprocess.run(
                [str(self.binary_path)] + args,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                check=False
            )
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"Command timed out after {timeout}s: {' '.join(args)}") from e
    
    def get_version(self) -> Optional[str]:
        """
        Get the version of the agent CLI binary.
        
        Returns:
            Version string or None if unable to determine.
        """
        try:
            result = self.run_command(["--version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def init(self, name: str, template: Optional[str] = None, 
             runtime: Optional[str] = None, model: Optional[str] = None) -> bool:
        """
        Initialize a new agent project.
        
        Args:
            name: Name of the agent project.
            template: Template to use (chatbot, sentiment, etc.).
            runtime: Runtime environment (python, nodejs, go).
            model: Model to use (openai/gpt-4, local/llama2, etc.).
            
        Returns:
            True if successful, False otherwise.
        """
        args = ["init", name]
        
        if template:
            args.extend(["--template", template])
        if runtime:
            args.extend(["--runtime", runtime])
        if model:
            args.extend(["--model", model])
        
        result = self.run_command(args)
        return result.returncode == 0
    
    def build(self, path: str = ".", tag: Optional[str] = None, 
              no_cache: bool = False, push: bool = False) -> bool:
        """
        Build an agent from agent.yaml.
        
        Args:
            path: Path to the agent project directory.
            tag: Tag for the built image.
            no_cache: Whether to disable build cache.
            push: Whether to push after building.
            
        Returns:
            True if successful, False otherwise.
        """
        args = ["build"]
        
        if tag:
            args.extend(["-t", tag])
        if no_cache:
            args.append("--no-cache")
        if push:
            args.append("--push")
        
        args.append(path)
        
        result = self.run_command(args)
        return result.returncode == 0
    
    def run(self, image: str, port: Optional[str] = None, 
            env: Optional[List[str]] = None, detach: bool = False,
            name: Optional[str] = None) -> bool:
        """
        Run an agent container.
        
        Args:
            image: Image name to run.
            port: Port mapping (e.g., "8080:8080").
            env: List of environment variables.
            detach: Whether to run in background.
            name: Container name.
            
        Returns:
            True if successful, False otherwise.
        """
        args = ["run"]
        
        if port:
            args.extend(["-p", port])
        if env:
            for e in env:
                args.extend(["-e", e])
        if detach:
            args.append("-d")
        if name:
            args.extend(["--name", name])
        
        args.append(image)
        
        result = self.run_command(args)
        return result.returncode == 0
    
    def push(self, image: str, registry: Optional[str] = None) -> bool:
        """
        Push an agent to a registry.
        
        Args:
            image: Image name to push.
            registry: Registry to push to.
            
        Returns:
            True if successful, False otherwise.
        """
        args = ["push"]
        
        if registry:
            args.extend(["--registry", registry])
        
        args.append(image)
        
        result = self.run_command(args)
        return result.returncode == 0
    
    def pull(self, image: str, registry: Optional[str] = None, 
             quiet: bool = False) -> bool:
        """
        Pull an agent from a registry.
        
        Args:
            image: Image name to pull.
            registry: Registry to pull from.
            quiet: Whether to suppress verbose output.
            
        Returns:
            True if successful, False otherwise.
        """
        args = ["pull"]
        
        if registry:
            args.extend(["--registry", registry])
        if quiet:
            args.append("-q")
        
        args.append(image)
        
        result = self.run_command(args)
        return result.returncode == 0
    
    def images(self, quiet: bool = False, all_images: bool = False) -> Union[bool, List[str]]:
        """
        List agent images.
        
        Args:
            quiet: Whether to only show image IDs.
            all_images: Whether to show all images.
            
        Returns:
            True if successful (when not quiet), or list of image IDs (when quiet).
        """
        args = ["images"]
        
        if quiet:
            args.append("-q")
        if all_images:
            args.append("-a")
        
        result = self.run_command(args, capture_output=quiet)
        
        if quiet and result.returncode == 0:
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        return result.returncode == 0


def main():
    """
    Main entry point for the agent CLI command.
    
    This function is called when the 'agent' command is executed from the
    command line after installing the package via pip.
    """
    try:
        cli = AgentCLI()
        exit_code = cli.execute()
        sys.exit(exit_code)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()