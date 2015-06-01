if [[ -f covMerger ]]; then
	rm covMerger
fi

#-I./gzstream -L./gzstream -lgzstream
g++ -g -o covMerger gzstream/gzstream.C covMerger.cpp -O3 -std=c++11 -fexpensive-optimizations -ffast-math -floop-parallelize-all -fwhole-program -m64 -mmmx -msse -msse2 -msse3 -mssse3 -msse4.1 -msse4.2 -msse4 -I./gzstream -L./gzstream -lgzstream -lz
#ulimit -c unlimited;

chmod +x covMerger

#./covMerger <out.mcov.gz> infolder/*.cov.gz
