INGFF=ITAG2.3_gene_models.gff3.gene.gff3
INVCF=
OUTDIR=randomgenelist
OUTNAME=randomgenelist
NUMLINES=10
NUMSAMPLES=999

mkdir $OUTDIR

set -xeu

OUTLIST=$OUTDIR/$INGFF.genelist

cat $INGFF | cut -f 9 | cut -d\; -f1 | cut -d\= -f2 | uniq > $OUTLIST

for i in $(seq 0 ${NUMSAMPLES}); do
	n=`printf "%04d" $i`
	echo $n
	OUTLST=$OUTDIR/${OUTNAME}_${n}.lst
	OUTGFF=$OUTLST.gff3
	shuf $OUTLIST | shuf | head -$NUMLINES > $OUTLST
	grep -f $OUTLST $INGFF > $OUTGFF

	#./pypy vcffiltergff.py -g $OUTGFF -i $INVCF 2>&1 | tee $OVCF.log
done

