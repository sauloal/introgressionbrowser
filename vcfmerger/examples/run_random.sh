GFF=$1
IVCF=../short2.lst.vcf.gz.simplified.vcf.gz

OVCF=$GFF.filtered.vcf.gz
FA=$OVCF.fa

#rm $IVCF.*

#randomgenelist_0000.lst.gff3.filtered.vcf.gz.SL2.40ch01.fasta

set -xeu


if [[ ! -f "$OVCF"  ]]; then
	./pypy vcffiltergff.py -g $GFF -i $IVCF -o $OVCF 2>&1 | tee $OVCF.log
fi


if [[ ! -f "$OVCF.ch00.fasta"  ]]; then
	./pypy vcfconcat.py -f -i $OVCF 2>&1 | tee $OVCF.concat.log
    if [[ -f "${OVCF}.filtered.vcf.gz.SL2.40ch00.fasta" ]]; then
        rm ${OVCF}.filtered.vcf.gz.SL2.40ch00.fasta
    fi
fi

if [[ ! -f "$FA"  ]]; then
	./pypy alnmerger.py $FA ${OVCF}*.fasta 2>&1| tee $FA.log
fi


if [[ ! -f "$FA.tree" ]]; then
    set +xeu
	bash runFastTree.sh $FA 2>&1 | tee $FA.tree.log
fi

exit 0
