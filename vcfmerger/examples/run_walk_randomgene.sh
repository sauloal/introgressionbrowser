GFF=input.gff3
IVCF=short2.lst.vcf.gz.simplified.vcf.gz

OVCF=$IVCF.filtered.vcf.gz
FA=$OVCF.fa

rm $IVCF.*

set -xeu


./pypy vcffiltergff.py -g $GFF -i $IVCF 2>&1 | tee $OVCF.log

./pypy vcfconcat.py -f -i $OVCF 2>&1 | tee $OVCF.concat.log

rm *ch00.fasta

./pypy alnmerger.py $FA *.fasta 2>&1| tee $FA.log

bash runFastTree.sh $FA 2>&1 | tee $FA.tree.log
