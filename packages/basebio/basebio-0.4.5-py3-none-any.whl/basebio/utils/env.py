# -*- coding: utf-8 -*-
__author__ = "legendzdy@dingtalk.com"
"""
Author: legendzdy@dingtalk.com
Data: 20250114
Description:
function map.
"""
from .cmdtools import run_command

def create_env(env_file: str, tools: str = "conda") -> None:
    """
    Run any shell command with a common function.
    
    Args:
        env_file: The path of the environment yaml file.
        tools: The name of the package manager, default is conda.
    
    Examples:
        create_env("env.yaml", "mamba")
    """
    
    command = [tools, "env", "create", "-f", env_file]
    run_command(command)