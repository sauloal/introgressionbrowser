--------------------------------------------
SUMMARY
--------------------------------------------
generates a GFF file containingn the gaps in coverage in the coverage files defined in a list file.

covMergerMake.sh - used to compile covMerger

rangeMake.sh - used to compile range

covMerger - merge coverage files

range - calculate ranges of gaps

filter.py - filters a range file taking in account only the sequences requested in the input.lst



--------------------------------------------
RUN
--------------------------------------------
find . -name '*.bam' | xargs -I{} -P10 bash -c 'if [[ ! -f "{}.cov" ]]; then samtools depth {} | gzip -c1 > {}.cov.gz; fi'
OR
for <bam file> in infolder/*.bam
	samtools depth <bam file> | gzip -c1 > <bam file>.cov.gz

./covMerger <out.mcov.gz> infolder/*.cov.gz

./filter.py <out.mcov.gz> <input list> [<min coverage>]

./range [<max gap size> <g:report gaps instead of covered frags>]


--------------------------------------------
FILES
--------------------------------------------
-------------------
INPUT.LST
-------------------
[-1,0,1],[COV FILE],[NAME]
[-1,0,1]
-1 = show only coordinates where this particular individual is not present
 0 = ignore individual
 1 = show only coordinates where this particular individual is present

[COV FILE]
Path to coverage file

[NAME]
Pretty name of individual

-------------------
.COV
-------------------
[CHROMOSOME]    [POSITION] [READ DEPTH]
SL2.40ch00      101        1





--------------------------------------------
FILES EXAMPLES
--------------------------------------------
-------------------
INPUT.LST
-------------------
1   samcov/RF_001_SZAXPI008746-45.bam.cov	Moneymaker
1	samcov/RF_002_SZAXPI009284-57.bam.cov	Alisa Craig
0	samcov/RF_003_SZAXPI009285-62.bam.cov	Gardeners Delight
1	samcov/RF_004_SZAXPI009286-74.bam.cov	Rutgers
0	samcov/RF_005_SZAXPI009287-75.bam.cov	Galina
1	samcov/RF_006_SZAXPI009288-79.bam.cov	Taxi
0	samcov/RF_007_SZAXPI009289-84.bam.cov	Katinka Cherry


-------------------
INPUT.LST.FILTERED.COV
-------------------
SL2.40ch00      622     38      28      33      31      25      43      32      26      23      36      37      27      31      34      38      28      39      38
      33      0       34      42      0       30      20      29      22      43      19      41      30      32      35      27      15      47      33      36      34      0       27      37      38      0       13      0       0       2       35      21      33      3       0       0       0       0       0       0       0
       0       0       2       1       5       0       2       2       0       2       0       28      20      28      46      45      29      41      27      40
      26      31      19      33      0


-------------------
INPUT.LST.FILTERED.GFF3
-------------------
##gff-version 3
#Required:
#       samcov/RF_001_SZAXPI008746-45.bam.cov   Moneymaker
#       samcov/RF_011_SZAXPI009291-88.bam.cov   All Round
#Ignored:
#       samcov/RF_002_SZAXPI009284-57.bam.cov   Alisa Craig
#       samcov/RF_003_SZAXPI009285-62.bam.cov   Gardeners Delight
#       samcov/RF_004_SZAXPI009286-74.bam.cov   Rutgers
#Forbidden:
#       samcov/RF_058_SZAXPI009359-46.bam.cov   S arcanum
#       samcov/RF_059_SZAXPI009335-169.bam.cov  S arcanum
#seqId  source  type    start   end     score   strand  phase   attributes
SL2.40ch00      heinz2.40       gap     125204  125292  .       +       .       ID=1;chr_id=1;count=176;chr_count=176;NAME=SL2.40ch00_1
SL2.40ch00      heinz2.40       gap     125568  125617  .       +       .       ID=2;chr_id=2;count=226;chr_count=226;NAME=SL2.40ch00_2
SL2.40ch00      heinz2.40       gap     125907  126053  .       +       .       ID=3;chr_id=3;count=373;chr_count=373;NAME=SL2.40ch00_3
SL2.40ch00      heinz2.40       gap     129108  129163  .       +       .       ID=4;chr_id=4;count=473;chr_count=473;NAME=SL2.40ch00_4
