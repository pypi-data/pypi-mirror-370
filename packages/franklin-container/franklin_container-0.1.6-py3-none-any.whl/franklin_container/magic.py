"""Jupyter magic commands for Franklin container environment.

This module provides IPython magic commands for managing packages
within Franklin exercise containers using Pixi package manager.
"""

from IPython.core.magic import register_line_magic
import subprocess
import shutil
import pyperclip
import webbrowser
from functools import wraps
from typing import Callable, Any, Optional
import sys
import os
import tempfile

def crash_report(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to handle exceptions and create crash reports.
    
    Parameters
    ----------
    func : Callable[..., Any]
        Function to wrap with crash reporting.
        
    Returns
    -------
    Callable[..., Any]
        Wrapped function with crash reporting.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Wrapper function that handles exceptions.
        
        Parameters
        ----------
        *args : Any
            Positional arguments passed to wrapped function.
        **kwargs : Any
            Keyword arguments passed to wrapped function.
            
        Returns
        -------
        Any
            Return value from wrapped function.
        """
        try:
            ret = func(*args, **kwargs)
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            url = 'https://github.com/munch-group/franklin-container/issues'
            print(f"Error while running magic: {e}", file=sys.stderr)
            print("Please report this by creating an issue at:")
            print(url)
            print("The error description has been copied to your clipboard "
                   "for you to paste into the issue description.")
            pyperclip.copy(f"Exception occurred while running magic: {e}")
            webbrowser.open(url, new=1)
        return ret
    return wrapper

install_pixi_script: str = f'''
WORKSPACE_FOLDER="{os.getcwd()}"
ENVIRONMENT="prod"
export PIXI_HOME=/home/vscode
export PIXI_PROJECT_MANIFEST="$WORKSPACE_FOLDER/pixi.toml"
curl -fsSL https://pixi.sh/install.sh | bash
'''

@crash_report
def load_ipython_extension(ipython: Any) -> None:
    """Load the Franklin container magic extension into IPython.
    
    This function is called when `%load_ext franklin_container.magic` is run in IPython.
    It registers the %franklin line magic command for package management.
    
    Parameters
    ----------
    ipython : Any
        IPython instance to register magic commands with.
    """
    @register_line_magic
    def franklin(line: str) -> None:
        """Franklin line magic for installing packages in containers.
        
        Parameters
        ----------
        line : str
            Space-separated list of package names to install.
            
        Examples
        --------
        >>> %franklin numpy pandas matplotlib
        Installing: numpy, pandas, matplotlib
        
        Notes
        -----
        This magic command only works within Franklin exercise repositories
        (directories containing a Dockerfile). It uses Pixi package manager
        to install packages for the exercise environment.
        """

        if not os.path.exists('Dockerfile'):
            # do nothing if unless in a cloned exercise repo
            return

        packages: list[str] = line.strip().split()
        if not packages:
            print("Usage: %franklin <package-name> <package-name> ...")
            return
        
        pixi_exe: str = os.environ['PIXI_EXE']
        if not os.path.exists(pixi_exe):
            print("Installing pixi")
            script_file = tempfile.NamedTemporaryFile(mode='w')
            script_file.write(install_pixi_script)
            cmd: list[str] = ["bash", script_file.name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode:
                print(f"Error installing {', '.join(packages)}':\n{result.stderr}")

        print(f"Installing: {', '.join(packages)}")
        cmd: list[str] = [pixi_exe, "add", "--feature", "exercise", "--platform", "linux-64"] + packages
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
#        print(f"Packages {', '.join(packages)} installed successfully.")
        # else:
        #     print(f"Error installing {', '.join(packages)}:\n{result.stderr}")

