# -*- coding: utf-8 -*-
__author__ = "legendzdy@dingtalk.com"
"""
Author: legendzdy@dingtalk.com
Data: 20250114
Description:
function map.
"""
from .cmdtools import run_command

def minimap2(input, reference, output, tool="minimap2", params="--secondary=no --cs -a", threads=8):
    """
    map with minimap2.
    Args:
        input: input fasta file.
        reference: reference fasta file.
        output: output sam/bam file.
        threads: number of threads.
        tool: minimap2 tool path.
        params: minimap2 params.
    """
    params_list = params.split()
    suffix = output.split(".")[-1]
    if suffix == "sam":
        bam = output.replace(".sam", ".bam")
        sorted_bam = output.replace(".sam", ".sorted.bam")
        command = [
            tool, *params_list, "-t", str(threads),
            "-o", output, reference, input
        ]
        run_command(command)
        run_command(["samtools", "view", "-bS", "-@", str(threads), output, "-o", bam])
        run_command(["samtools", "sort", "-@", str(threads), "-o", sorted_bam, bam])
        run_command(["samtools", "index", sorted_bam])
        run_command(["rm", bam])
    elif suffix == "bam":
        sam = output.replace(".bam", ".sam")
        bam = output.replace(".bam", ".unsorted.bam")
        command = [
            tool, *params_list, "-t", str(threads),
            "-o", sam, reference, input
        ]
        run_command(command)
        run_command(["samtools", "view", "-bS", "-@", str(threads), sam, "-o", bam])
        run_command(["samtools", "sort", "-@", str(threads), "-o", output, bam])
        run_command(["samtools", "index", output])
        run_command(["rm", sam, bam])
    else:
        raise ValueError("output file suffix must be sam or bam.")