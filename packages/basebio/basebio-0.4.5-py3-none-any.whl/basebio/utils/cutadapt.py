# -*- coding: utf-8 -*-
__author__ = "legendzdy@dingtalk.com"
"""
Author: legendzdy@dingtalk.com
Data: 20250725
Description:
This script is used to cut adapter with cutadapt.
"""
from .cmdtools import run_command

def cutadapt(read1, read2, read1_out, read2_out, tool, parms):
    """
    Cut adapter with cutadapt.

    Args:
        read1: read1 file path.
        read2: read2 file path.
        read1_out: output read1 file path.
        read2_out: output read2 file path.
        tool: cutadapt tool path.
        parms: cutadapt params.
    
    Examples:
        cutadapt_run(
            read1="read1.fq",
            read2="read2.fq",
            read1_out="read1_cut.fq",
            read2_out="read2_cut.fq",
            tool="cutadapt",
            parms="-a AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT"
        )
    """
    params_list = parms.split()
    command = [
        tool, *params_list, 
        "-o", read1_out, "-p", read2_out,
        read1, read2
        ]
    run_command(command)