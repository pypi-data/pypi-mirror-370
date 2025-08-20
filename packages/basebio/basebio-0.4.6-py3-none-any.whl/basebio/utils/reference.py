# -*- coding: utf-8 -*-
__author__ = "legendzdy@dingtalk.com"
"""
Author: legendzdy@dingtalk.com
Data: 20250114
Description:
function map.
"""
import subprocess

def init_reference(command: str|list, use_shell: bool=False) -> None:
    """
    Run any shell command with a common function.
    
    Args:
        command (str/list): The command to be executed, can be in string or list format.
        use_shell (bool): Whether to use shell mode to execute (True if need to handle pipes/redirects).
    
    Examples:
        #### List
        run_command(['ls', '-l', '/tmp'])
        
        #### string
        run_command('ls -l /tmp | grep log', use_shell=True)
    """
    try:
        if isinstance(command, list):
            printable_command = ' '.join(command)
        else:
            printable_command = command
            
        print(f"Running command: {printable_command}")
        subprocess.run(
            command,
            check=True,
            shell=use_shell,
            # stderr=subprocess.PIPE,
            # stdout=subprocess.PIPE,
            # universal_newlines=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
        raise SystemExit(1) 
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise SystemExit(1) 