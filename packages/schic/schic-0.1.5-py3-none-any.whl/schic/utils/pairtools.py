# -*- coding: utf-8 -*-
__author__ = "legendzdy@dingtalk.com"
"""
Author: legendzdy@dingtalk.com
Data: 20250725
Description:
pairtools.
"""
import os, gzip
from basebio import run_command

def mkpairs(input_pairs, output_pairs):
    """
    unzip pairs file and extract only the first 8 columns

    Args:
        input_pairs: input pairs file.
        output_pairs: output pairs file.
    
    Example:
        mkpairs('input.pairs.gz', 'output.pairs')
    """
    
    if not os.path.exists(input_pairs):
        raise FileNotFoundError(f"Pairs file not found: {input_pairs}")
    
    with gzip.open(input_pairs, 'rt') as f_in, open(output_pairs, 'w') as f_out:
        for line in f_in:
            if not line.startswith('#'):
                cols = line.strip().split('\t')
                if len(cols) >= 8:
                    f_out.write('\t'.join(cols[:8]) + '\n')

def mkstats(input_stats, output_stats):
    """
    Parse stats file and extract only the required columns and rename them.

    Args:
        input_stats: input stats file.
        output_stats: output stats file.
    
    Example:
        mkstats('input.stats', 'output.stats')
    """
    stats_dict = {}
    with open(input_stats, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                stats_dict[parts[0]] = parts[1]
    
    total = int(stats_dict.get("total", 0))
    unmapped = int(stats_dict.get("total_unmapped", 0))
    mapped = int(stats_dict.get("total_mapped", 0))
    dups = int(stats_dict.get("total_dups", 0))
    nodups = int(stats_dict.get("total_nodups", 0))
    cis = int(stats_dict.get("cis", 0))
    trans = int(stats_dict.get("trans", 0))
    cis_gt1kb = int(stats_dict.get("cis_1kb+", 0))
    cis_lt1kb = cis - cis_gt1kb
    cis_gt10kb = int(stats_dict.get("cis_10kb+", 0))
    valid_pairs = trans + cis_gt1kb
    
    with open(output_stats, 'w') as f_out:
        f_out.write(f"""
            Total_Read_Pairs\t{total}\n
            Unmapped_Read_Pairs\t{unmapped}\n
            Mapped_Read_Pairs\t{mapped}\n
            PCR_Dup_Read_Pairs\t{dups}\n
            No-Dup_Read_Pairs\t{nodups}\n
            Cis_Read_Pairs\t{cis}\n
            Trans_Read_Pairs\t{trans}\n
            Valid_Read_Pairs\t{valid_pairs}\n
            Cis1kb\t{cis_lt1kb}\n
            Cis1kb+\t{cis_gt1kb}\n
            Cis10kb+\t{cis_gt10kb}\n
            """)

def pairtools(input_R1, input_R2, reference, genome_size, prefix, threads=8):
    """
    Align and deduplicate paired-end reads using bwa mem and pairtools.

    Args:
        input_R1: input R1 fastq file.
        input_R2: input R2 fastq file.
        reference: reference fasta file.
        genome_size: size of the reference genome.
        prefix: output prefix.
        threads: number of threads.
    
    Example:
        pairtools(input_R1="R1.fastq.gz", input_R2="R2.fastq.gz", reference="reference.fasta", genome_size="3.0e9", prefix="output", threads=8)
    """
    out_sam = prefix + ".aligned.sam"
    cmd = ["bwa", "mem", "-5SP", "-T0", "-t", str(threads), reference, input_R1, input_R2, ">", out_sam]
    run_command(" ".join(cmd), use_shell=True)

    out_pairs = prefix + ".pairs.gz"
    run_command(["pairtools", "parse", "-c", genome_size, "-o", out_pairs, out_sam])

    out_sorted = prefix + ".sorted.pairs.gz"
    run_command(["pairtools", "sort", "--nproc", str(threads), "-o", out_sorted, out_pairs])

    out_nodups = prefix + ".nodups.pairs.gz"
    out_dups = prefix + ".dups.pairs.gz"
    out_unmapped = prefix + ".unmapped.pairs.gz"
    out_stats = prefix + ".dedup.stats"
    run_command(["pairtools", "dedup", "--mark-dups", "--output", out_nodups, "--output-dups", out_dups, "--output-unmapped", out_unmapped, "--output-stats", out_stats, out_sorted])

    mapped_pairs = prefix + "_mapped.pairs"
    mkpairs(out_nodups, mapped_pairs)

    qc_file = prefix + ".qc.txt"
    mkstats(out_stats, qc_file)