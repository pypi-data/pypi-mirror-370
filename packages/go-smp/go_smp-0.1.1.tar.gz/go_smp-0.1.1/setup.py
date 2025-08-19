import os
import subprocess
import sys
from pathlib import Path
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from setuptools.errors import SetupError


class GoExtension(Extension):
    """Extension that builds Go shared library."""
    
    def __init__(self, name):
        # Don't pass sources to Extension as we'll handle Go compilation
        super().__init__(name, sources=[])


class BuildGoExt(build_ext):
    """Custom build_ext to handle Go compilation."""
    
    def build_extension(self, ext):
        if isinstance(ext, GoExtension):
            self._build_go_extension(ext)
        else:
            super().build_extension(ext)
    
    def _build_go_extension(self, ext):
        """Build the Go shared library."""       
        # Hard-code the output filename to match what bindings.py expects
        ext_path = self.get_ext_fullpath(ext.name)
        
        # Build the shared library directly to the target location
        cmd = [
            "go", "build", "-buildmode=c-shared",
            "-o", ext_path, "."
        ]
        
        # Check if verbose flag is passed to pip install
        verbose = any('--verbose' in arg or '-v' in arg for arg in sys.argv)
        
        try:
            env = os.environ.copy()
            env['CGO_ENABLED'] = '1'
            if verbose:
                # Show stdout and stderr in real-time when verbose
                result = subprocess.run(cmd, check=False, env=env)
            else:
                # Run quietly, suppress output when not verbose
                result = subprocess.run(cmd, check=False, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            raise SetupError(f"Failed to execute Go build command: {e}")
        
        if result.returncode != 0:
            error_msg = f"Go build failed with exit code {result.returncode}"
            if not verbose:
                if result.stderr:
                    error_msg += f"\nSTDERR:\n{result.stderr.decode()}"
                if result.stdout:
                    error_msg += f"\nSTDOUT:\n{result.stdout.decode()}"
            raise SetupError(error_msg)
        
        # Clean up the generated header file (adjust extension for Windows)
        if sys.platform == "win32":
            h_file = ext_path.replace(".pyd", ".h")
        else:
            h_file = ext_path.replace(".so", ".h")
        if os.path.exists(h_file):
            os.unlink(h_file)


# Create the Go extension
go_ext = GoExtension(
    name="go_smp._gosmp"
)

setup(
    ext_modules=[go_ext],
    cmdclass={
        "build_ext": BuildGoExt,
    }
)