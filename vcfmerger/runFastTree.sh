INFASTA=$1
echo "FastTree $1"
export OMP_NUM_THREADS=20

#./FastTreeMP -fastest -gtr -gamma -nt -bionj -boot 100 -log $INFASTA.tree.log $INFASTA | tee ${INFASTA}.tree
./FastTreeMP -fastest -gamma -nt -bionj -boot 100 -log $INFASTA.tree.log -out ${INFASTA}.tree $INFASTA &

#tail -f $INFASTA.tree.log

