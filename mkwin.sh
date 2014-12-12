OUTFILE=introgression_viewer.tgz
INFOLDER=win

rm $OUTFILE
rm $INFOLDER/*.*
rm -rf $INFOLDER/static

cp -l   *.py            $INFOLDER
cp -l   walk_out.sql.db $INFOLDER
cp -l   run.bat         $INFOLDER
cp -lar static          $INFOLDER

tar --exclude '*.pyc' --totals --level 9 -cvSzf $OUTFILE $INFOLDER

rm $INFOLDER/*.*
rm -rf $INFOLDER/static
