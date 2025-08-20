#!/bin/bash
:<<author
Author: legendzdy@dingtalk.com
Data: 20250416
Description:
This a pipeline of single-cell HiC data from Legendzdy. 
CMD: nohup contacts.sh -i /inputs -o /outputs &
author

usage() {
    echo "Usage:"
    echo "  contacts.sh [-i/--inputs /inputs] [-o/--outputs /outputs]"
    echo "Description:"
    echo "    -i | --inputs, input dir, default: /inputs"
    echo "    -o | --outputs, output dir, default: /outputs"
    echo "    -h | --help, help info."
    exit 1
}
# set defult

PARSED_ARGUMENTS=$(getopt -a -o i:o:h --long inputs:,outputs:,help -- "$@")
if [ $? -ne 0 ]; then usage; exit 1;fi
eval set -- ${PARSED_ARGUMENTS}
while true; do
    case $1 in
        -i|--inputs)     INPUT=$2; shift 2;;
        -o|--outputs)    OUTPUT=$2; shift 2;;
        --)              shift; break;;
        -h|--help)       usage; exit 1;;
        ?)               usage; exit 1;;
    esac
done


bwa mem -5SP -T0 -t ${CORES} ${WKD}/reference/index/bwa/genome ${WKD}/${FORWORD}/{}_R1.filtered.fastq.gz ${WKD}/${FORWORD}/{}_R2.filtered.fastq.gz > {}.aligned.sam

pairtools parse -c ${WKD}/reference/index/bwa/genome.size -o {}.pairs.gz {}.aligned.sam

pairtools sort --nproc 8 -o {}.sorted.pairs.gz {}.pairs.gz

pairtools dedup \
    --mark-dups \
    --output {}.nodups.pairs.gz \
    --output-dups {}.dups.pairs.gz \
    --output-unmapped {}.unmapped.pairs.gz \
    --output-stats {}.dedup.stats \
    {}.sorted.pairs.gz

zcat {}.nodups.pairs.gz|grep -v "^#"|awk -F \"\t\" '{print \$1,\$2,\$3,\$4,\$5,\$6,\$7,\$8}' OFS=\"\t\" > {}_mapped.pairs

python ${SOFT}/get_qc.py -p ./{}.dedup.stats > ./{}.qc.txt
cat ${WKD}/${FORWORD}/{}_GRIDv1.flagstat.txt|awk 'NR==1{print \"total_reads_raw\t\"\$1}' > {}.total_reads.txt
cat {}.total_reads.txt {}.qc.txt > {}.temp.txt
cat {}.temp.txt| sed -e 's/,//g' \
    -e 's/Total Read Pairs/Reads_with_linker/g' \
    -e 's/Unmapped Read Pairs/Unmapped_Read_Pairs/g' \
    -e 's/Mapped Read Pairs/Mapped_Read_Pairs/g' \
    -e 's/PCR Dup Read Pairs/PCR_Dup_Read_Pairs/g' \
    -e 's/No-Dup Read Pairs/No-Dup_Read_Pairs/g' \
    -e 's/No-Dup Cis Read Pairs/Cis_Read_Pairs/g' \
    -e 's/No-Dup Trans Read Pairs/Trans_Read_Pairs/g' \
    -e 's/No-Dup Valid Read Pairs (cis >= 1kb + trans)/Valid_Read_Pairs/g' \
    -e 's/Cis_Read_Pairs < 1kb/Cis1kb/g' \
    -e 's/Cis_Read_Pairs >= 1kb/Cis1kb+/g' \
    -e 's/Cis_Read_Pairs >= 10kb/Cis10kb+/g' |awk '{print \$1,\$2}' OFS=\"\t\" > {}.sample.txt