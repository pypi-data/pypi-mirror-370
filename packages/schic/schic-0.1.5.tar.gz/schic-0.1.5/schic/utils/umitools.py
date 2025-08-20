# -*- coding: utf-8 -*-
__author__ = "legendzdy@dingtalk.com"
"""
Author: legendzdy@dingtalk.com
Data: 20250114
Description:
function map.
"""
import subprocess

def extract_run(bc_pattern, stdin, stdout,read2_in, read2_out, whitelist, tool, tool_command, parms):
    """
    extract UMI with umitools.
    Args:
        bc-pattern: Barcode pattern for paired reads.
        stdin: input read1 file.
        stdout: output read1 file.
        read2-in: input read2 file.
        read2-out: output read2 file.
        whitelist: whitelist file.
        tool: umitools tool path.
        tool_command: umitools command.
        params: umitools params.
    """
    params_list = parms.split()
    command = [
        tool, tool_command, *params_list, f"--bc-pattern={bc_pattern}", f"--stdin={stdin}", f"--stdout={stdout}", f"--read2-in={read2_in}", f"--read2-out={read2_out}", f"--whitelist={whitelist}"
        ]
    try:
        print(f"Running command: {' '.join(command)}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        exit(1)

def whitelist_run(bc_pattern, stdin, set_cell_number, plot_prefix, stdout, tool, tool_command, parms):
    """
    extract UMI with umitools.
    Args:
        bc-pattern: Barcode pattern for paired reads.
        stdin: input read1 file.
        set_cell_number: setting cell number.
        plot_prefix: plot prefix.
        stdout: output whitelist file.
        tool: umitools tool path.
        tool: umitools tool path.
        tool_command: umitools command.
        params: umitools params.
    """
    params_list = parms.split()
    command = [
        tool, tool_command, f"--stdin={stdin}", f"--bc-pattern={bc_pattern}", *params_list, f"--set-cell-number={set_cell_number}", f"--plot-prefix={plot_prefix}", f"--stdout={stdout}"
        ]
    try:
        print(f"Running command: {' '.join(command)}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        exit(1)