export GZIP=-1

tar acvf iBrowser.code.tar.gz static/ vcfmerger/ *.sh *.bat *.py *.md

cd data
tar acvf ../iBrowser.data.tar.gz *.sqlite *.nfo *.customorder




