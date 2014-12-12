grep -v "#" short2.lst.vcf.gz.gt1.vcf | gawk '{print $1$2}' | uniq | wc -l
pigz -d -p4 -c short2.lst.vcf.gz | grep -v "#" | gawk '{print $1$2}' | uniq | wc -l
