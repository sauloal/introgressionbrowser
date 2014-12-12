GFF=ITAG2.3_gene_models.gff3.gene.gff3
IVCF=short2.lst.vcf.gz.simplified.vcf.gz
PROJNAME=walk_genes

OVCF=$IVCF.filtered.vcf.gz
FA=$OVCF.fa

rm $IVCF.*

set -xeu



python vcfmerger/vcffiltergff.py -k -f $PROJNAME -g $GFF -i $IVCF 2>&1 | tee $OVCF.log

##./pypy vcfconcat.py -f -i $OVCF 2>&1 | tee $OVCF.concat.log
find $PROJNAME -name '*.vcf.gz' | xargs -I{} -P50 bash -c 'python vcfmerger/vcfconcat.py -f -i {} 2>&1 | tee {}.concat.log'



#python alnmerger.py $FA *.fasta 2>&1| tee $FA.log

#bash runFastTree.sh $FA 2>&1 | tee $FA.tree.log

export OMP_NUM_THREADS=3

find $PROJNAME -name '*.fasta' | sort | xargs -I{} -P30 bash -c 'vcfmerger/aux/FastTreeMP -fastest -gamma -nt -bionj -boot 100 -log {}.tree.log -out {}.tree {}'

find $PROJNAME -name '*.fasta' | sort | xargs -I{} -P30 bash -c 'vcfmerger/aux/FastTreeMP -nt -makematrix {} > {}.matrix'


python vcf_walk_ram.py --pickle $PROJNAME
python vcf_walk_sql.py $PROJNAME

exit 0
python vcf_walk.py --graph                                    --spp ref $PROJNAME

exit 0
python vcf_walk.py --graph          --tree                    --spp ref $PROJNAME
python vcf_walk.py --graph          --treex                   --spp ref $PROJNAME
python vcf_walk.py --graph          --treey                   --spp ref $PROJNAME

python vcf_walk.py --graph --evenly                           --spp ref $PROJNAME
python vcf_walk.py --graph --evenly --tree                    --spp ref $PROJNAME
python vcf_walk.py --graph --evenly --treex                   --spp ref $PROJNAME
python vcf_walk.py --graph --evenly --treey                   --spp ref $PROJNAME

python vcf_walk.py --graph                  --cluster 10000   --spp ref $PROJNAME
python vcf_walk.py --graph          --tree  --cluster 10000   --spp ref $PROJNAME
python vcf_walk.py --graph          --treex --cluster 10000   --spp ref $PROJNAME
python vcf_walk.py --graph          --treey --cluster 10000   --spp ref $PROJNAME

python vcf_walk.py --graph                  --cluster 100000  --spp ref $PROJNAME
python vcf_walk.py --graph          --tree  --cluster 100000  --spp ref $PROJNAME
python vcf_walk.py --graph          --treex --cluster 100000  --spp ref $PROJNAME
python vcf_walk.py --graph          --treey --cluster 100000  --spp ref $PROJNAME

python vcf_walk.py --graph                  --cluster 1000000 --spp ref $PROJNAME
python vcf_walk.py --graph          --tree  --cluster 1000000 --spp ref $PROJNAME
python vcf_walk.py --graph          --treex --cluster 1000000 --spp ref $PROJNAME
python vcf_walk.py --graph          --treey --cluster 1000000 --spp ref $PROJNAME
