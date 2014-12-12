LST=introgress_moneymaker.lst
#ls trees/*.tree | xargs -I{} -P 20 bash -c 'echo {};  ./newick_to_png.py {} pimp_problems.lst; ./newick_to_png.py {} cherry.lst;'
ls trees/*.tree | xargs -I{} -P 20 bash -c 'echo {};  ./newick_to_png.py {} '$LST';'

#./pngfolder_to_html.py trees/*_pimp_problems.lst.png
#convert -page A4 -resample 1200 -quality 100 -density 1200 -compress Zip *_pimp_problems.lst.png*.png index_trees_short2.lst.vcf.gz.simplified.vcf.gz.filtered.vcf.gz.SL2.40ch06.0000_.vcf.gz.SL2.40ch06.fasta.tree_pimp_problems.lst.png.pdf

#./pngfolder_to_html.py trees/*_cherry.lst.png
#convert -page A4 -resample 1200 -quality 100 -density 1200 -compress Zip *_cherry.lst.png*.png        index_trees_short2.lst.vcf.gz.simplified.vcf.gz.filtered.vcf.gz.SL2.40ch06.0000_.vcf.gz.SL2.40ch06.fasta.cherry.lst.png.pdf

./pngfolder_to_html.py trees/*_${LST}.png
convert -page A4 -resample 1200 -quality 100 -density 1200 -compress Zip *_${LST}.png*.png        index_trees_short2.lst.vcf.gz.simplified.vcf.gz.filtered.vcf.gz.SL2.40ch06.0000_.vcf.gz.SL2.40ch06.fasta.${LST}.png.pdf

