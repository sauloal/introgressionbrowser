FOLDER=$1
CHROMOSOME=$2
START=$3
END=$4

for f in $FOLDER/*.vcf.gz; do echo "parsing $f"; bash filterpos.sh $f $CHROMOSOME $START $END; done
