Introgression Viewer
Saulo Aflitos - 2013-2015
sauloalves.aflitos@wur.nl
Cluster Bioinformatics
Plant Research International - PRI
Wageningen University and Research Centre - WageningenUR

![Travis Continuous Integration Build Status](https://travis-ci.org/sauloal/introgressionbrowser.svg?branch=master "Travis Continuous Integration Build Status")


Manual and Wiki: https://github.com/sauloal/introgressionbrowser/wiki

1. Introduction
2. Methodology
3. Installation
3.1. Clone Introgression browser
3.1.1. Processing
3.1.2. Server
3.2. Install dependencies
3.2.2. Server
3.2.3. Server add-ons
3.2.4. System
4. Run
4.1. Processing
4.2. Server
5. Run
5.1. Processing
5.2. Server
6. Acknowledgements



1. Introduction

2. Methodology
This set of scripts takes as input a series of Variant Call Files (VCF) of species mapped against a single reference.

After a series of conversions, all homozigous Single Nucleotide Polymorphisms (SNP) are extracted while ignoring heterozigous SNPS (hetSNP), Multiple Nucleotide Polymorphisms (MNP) and Insertion/Deletion events (InDel).

For each individual, the reference's nucleotide will be assigned unless a SNP is presented. If any individual has a MNP, hetSNP or InDel at a given position, this position is skipped entirely.

A General Feature Format (GFF) describing coordinates is used to split the genome into segments. Those segments can be genes, even sized fragments (10kb, 50kb, etc) or particular segments of interest as long as the coordinates are the same as the VCF files. A auxiliary script is provided to generate evenly sized segments.

For each selected segment a fasta file will be generated and FastTree will create a distance matrix and a Newick Tree. After all data has been processed, the three files (fasta, matrix and newick) will be read and converted to a database.

The webserver scripts will read and serve the data to a web browser. There are three scripts, a main script serves the data and two auxiliary servers to perform on-the-fly clustering and image conversion (from SVG to PNG).




3. Installation
3.1. Clone Introgression browser
    Clone or download Introgression Browser.


3.1.1. Processing
    Add your files under data subfolder.
    Add vcfmerger subfolder to your path or create symbolic links inside the data folder.


3.1.2. Server
    Get a database and modify config.py accordingly.
    The databases are are multiplatform.


3.2. Install dependencies
3.2.1. Processing
    Check if FastTree runs in your machine (Linux only)
    Install python dependencies:
        sqlalchemy
    Install pypy (Optional but speeds up analysis)


3.2.2. Server
    Install python
    Install python dependencies:
        sqlalchemy - already in virtualenv
        flask - already in virtualenv
	#py-editdist - already in vcfmerger/aux/ - wget 'https://py-editdist.googlecode.com/files/py-editdist-0.3.tar.gz'
	#fastcluster
	pymix

3.2.3. Server add-ons
    Install python dependencies:
        on-the-fly clustering:
            numpy
            scipy
        PNG download:
            wand

3.2.4. System
	apt-get update
	apt-get install build-essential checkinstall
	apt-get install python-setuptools python-dev
	apt-get install python-numpy python-scipy python-matplotlib python-pandas python-sympy
	apt-get install libmagickwand-dev
	apt-get install sqlite3 libsqlite3-dev

	easy_install pip
	easy_install flask
	easy_install sqlalchemy
	easy_install wand

3.2.5. Vistualization
3.2.5.1. VirtualBox
	share your data folder as "data" shared folder
	wget http://download.virtualbox.org/virtualbox/4.3.6/VBoxGuestAdditions_4.3.6.iso
	mkdir vbox
	mount VBoxGuestAdditions_4.3.6.iso vbox
	cd vbox
	./VBoxLinuxAdditions.run
	cd ..
	umount vbox
	edit /etc/fstab adding
		data /media/data vboxsf re 0 0
	mount -a
	ls /media/data

3.2.5.1. VMware
	share your data folder as "data" shared folder
	attach the VMware tools
	mkdir /mnt/cdrom
	mount /dev/cdrom /mnt/cdrom
	mkdir ~/vm
	cd ~/vm
	tar xvf /dev/cdrom/VMwareTools-9.6.1-1378637.tar.gz
	cd vmware-tools-distrib
	./vmware-install.pl -d
	cd ../..
	rm -rf vm
	ls /mnt/hgfs/data
	

4. Configuration
4.1. Processing
    Inside the "data" folder create a tab delimited file containing path to the VCF files and the "pretty" name for them. The first column is ignored.
        1	input/RF_001_SZAXPI008746-45.vcf.gz	Moneymaker (001)
        0	input/RF_002_SZAXPI009284-57.vcf.gz	Alisa Craig (002)
        0	input/RF_003_SZAXPI009285-62.vcf.gz	Gardeners Delight (003)


4.2. Server
    Edit config.py to create users, configure the server's port, the encryption key, describe available databases and decide whether to use SQL ot RAM database.




5. Run
5.1. Processing
    Merge VCF files:
        vcfmerger/vcfmerger.py short.lst
            OUTPUT: short.lst.vcf.gz
                #CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  FILENAMES
                SL2.40ch00      280     .       A       C       .       PASS    NV=1;NW=1;NS=1;NT=1;NU=1        FI      S cheesemaniae (055)
                SL2.40ch00      284     .       A       G       .       PASS    NV=1;NW=1;NS=1;NT=1;NU=1        FI      S cheesemaniae (054)
                SL2.40ch00      316     .       C       T       .       PASS    NV=1;NW=1;NS=1;NT=1;NU=1        FI      S arcanum (059)
                SL2.40ch00      323     .       C       T       .       PASS    NV=1;NW=1;NS=1;NT=1;NU=1        FI      S arcanum (059)
                SL2.40ch00      332     .       A       T       .       PASS    NV=1;NW=1;NS=1;NT=1;NU=1        FI      S pimpinellifolium (047)
                SL2.40ch00      362     .       G       T       .       PASS    NV=1;NW=1;NS=1;NT=1;NU=1        FI      S galapagense (104)
                SL2.40ch00      385     .       A       C       .       PASS    NV=1;NW=1;NS=1;NT=1;NU=1        FI      S neorickii (056)
                SL2.40ch00      391     .       C       T       .       PASS    NV=1;NW=1;NS=6;NT=6;NU=6        FI      S chiemliewskii (052),S neorickii (056),S arcanum (059),S habrochaites glabratum (066),S habrochaites glabratum (067),S habrochaites (072)


    Simplify merged VCF deleting hetSNP, MNP and InDels:
        vcfmerger/vcfsimplify.py short.lst.vcf.gz
            OUTPUT: short.lst.vcf.gz.filtered.vcf.gz
                SL2.40ch00      391     .       C       T       .       PASS    NV=1;NW=1;NS=6;NT=6;NU=6        FI      S arcanum (059),S chiemliewskii (052),S habrochaites (072),S habrochaites glabratum (066),S habrochaites glabratum (067),S neorickii (056)
                SL2.40ch00      416     .       T       A       .       PASS    NV=1;NW=1;NS=6;NT=6;NU=6        FI      S arcanum (059),S chiemliewskii (052),S habrochaites (072),S habrochaites glabratum (066),S habrochaites glabratum (067),S neorickii (056)
                SL2.40ch00      424     .       C       T       .       PASS    NV=1;NW=1;NS=5;NT=5;NU=5        FI      LA0113 (039),S cheesemaniae (054),S pimpinellifolium (044),S pimpinellifolium unc (045),S pimpinellifolium (047)


    Generate even sized fragments (if needed):
        vcfmerger/aux/fasta_spacer.py GENOME.fa 50000
            OUTPUT: GENOME.fa.50000.gff
                SL2.40ch00      .       fragment_10000  1       10000   .       .       .       Alias=Frag_SL2.40ch00g10000_1;ID=fragment:Frag_SL2.40ch00g10000_1;Name=Frag_SL2.40ch00g10000_1;length=10000;csize=21805821
                SL2.40ch00      .       fragment_10000  10001   20000   .       .       .       Alias=Frag_SL2.40ch00g10000_2;ID=fragment:Frag_SL2.40ch00g10000_2;Name=Frag_SL2.40ch00g10000_2;length=10000;csize=21805821


    Filter with gff:
        vcfmerger/vcffiltergff.py -k -f PROJNAME -g GENOME.fa_50000.gff -i short2.lst.vcf.gz.simplified.vcf.gz 2>&1 | tee short2.lst.vcf.gz.simplified.vcf.gz.log
            OUTPUT:
                #CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  FILENAMES
                SL2.40ch00      391     .       C       T       .       PASS    NV=1;NW=1;NS=6;NT=6;NU=6        FI      S arcanum (059),S chiemliewskii (052),S habrochaites (072),S habrochaites glabratum (066),S habrochaites glabratum (067),S neorickii (056)


    Concatenate the SNPs of each fragment into FASTA:
        find PROJNAME -name '*.vcf.gz' | xargs -I{} -P50 bash -c 'vcfmerger/vcfconcat.py -f -i {} 2>&1 | tee {}.concat.log'
            OUTPUT: PROJNAME/CHROMOSOME/short2.lst.vcf.gz.simplified.vcf.gz.filtered.vcf.gz.SL2.40ch01.000090300001-000090310000.Frag_SL2.40ch01g10000_9031.vcf.gz.SL2.40ch01.fasta
                >Moneymaker_001
                ATAATCTAGCTGGAACCCTTGTTTTTCTCGCGATTGGGGTTCAAGTGCACACCACATGTC
                AGGGA
                >Alisa_Craig_002
                ATAATCTAGCTGGAACCCTTGTTTTTCTTGCGATTGGGGTTCAAGTGCGCGCTGCGTGAC
                AGGAA


    Run FastTree in each of the FASTA files:
        export OMP_NUM_THREADS=3
        find PROJNAME -name '*.fasta' | sort | xargs -I{} -P30 bash -c 'vcfmerger/aux/FastTreeMP -fastest -gamma -nt -bionj -boot 100 -log {}.tree.log -out {}.tree {}'
            OUTPUT: PROJNAME/CHROMOSOME/short2.lst.vcf.gz.simplified.vcf.gz.filtered.vcf.gz.SL2.40ch01.000090300001-000090310000.Frag_SL2.40ch01g10000_9031.vcf.gz.SL2.40ch01.fasta.tree
                ((((Dana_018:0.0,Belmonte_033:0.0):0.00054,((TR00026_102:0.01587,(PI272654_023:0.03426,(((S_huaylasense_063:0.00054,((Lycopersicon_sp_025:0.0,S_chilense_065:0.0):0.00054,S_chilense_064:0.01555)0.780:0.01548)0.860:0.01547,((S_peruvianum_new_049:0.0,S_chiemliewskii_051:0.0,S_chiemliewskii_052:0.0,S_cheesemaniae_053:0.0,S_cheesemaniae_054:0.0,S_neorickii_056:0.0,S_neorickii_057:0.0,S_peruvianum_060:0.0,S_habrochaites_glabratum_066:0.0,S_habrochaites_glabratum_068:0.0,S_habrochaites_070:0.0,S_habrochaites_071:0.0,S_habrochaites_072:0.0,S_pennellii_073:0.0,S_pennellii_074:0.0,TR00028_LA1479_105:0.0,ref:0.0):0.00054,((S_arcanum_058:0.01482,(S_huaylasense_062:0.08258,S._arcanum_new_075:0.00054)0.880:0.03260)0.960:0.04917,(((Gardeners_Delight_003:0.00054,(Katinka_Cherry_007:0.0,Trote_Beere_016:0.0,Winter_Tipe_031:0.0):0.01559)0.900:0.03206,(PI129097_022:0.00054,(S_galapagense_104:0.04782,(LA0113_039:0.01223,((S_pimpinellifolium_047:0.01628,(S_arcanum_059:0.00055,(S_habrochaites_glabratum_067:0.01562,S_habrochaites_glabratum_069:0.01562)1.000:0.08287)0.920:0.04857)0.670:0.01186,S_habrochaites_042:0.03551)0.990:0.12956)0.960:0.06961)0.710:0.00054)0.800:0.01578)0.760:0.01558,(T1039_017:0.08246,S_pimpinellifolium_044:0.00054)0.980:0.08153)0.230:0.00053)0.910:0.00055)0.910:0.00054)0.830:0.01549,S_pimpinellifolium_046:0.00054)0.980:0.08610)0.660:0.01369)0.530:0.04644,(TR00027_103:0.00054,(PI365925_037:0.04936,S_cheesemaniae_055:0.03179)0.650:0.08462)1.000:0.41706)0.650:0.00296)0.940:0.01555,(The_Dutchman_028:0.00053,(((Polish_Joe_026:0.0,Brandywine_089:0.0):0.00054,((((Porter_078:0.01608,Kentucky_Beefsteak_093:0.01542)0.880:0.03271,(Thessaloniki_096:0.08543,Bloodt_Butcher_088:0.03267)0.700:0.01564)0.800:0.01585,(Giant_Belgium_091:0.01562,(Moneymaker_001:0.00054,(Dixy_Golden_Giant_090:0.01579,(Large_Red_Cherry_077:0.03276,Momatero_015:0.04969)0.720:0.01528)0.870:0.01570)0.850:0.01556)0.480:0.00055)0.930:0.03157,Marmande_VFA_094:0.03158)0.970:0.00053)0.880:0.00053,Watermelon_Beefsteak_097:0.01555)0.890:0.01559)0.970:0.03159)0.950:0.00054,PI169588_041:0.00054,((Sonato_012:0.11798,(((All_Round_011:0.01555,Chih-Mu-Tao-Se_038:0.00054)0.180:0.00054,(((Jersey_Devil_024:0.0,Chag_Li_Lycopersicon_esculentum_032:0.0,S_pimpinellifolium_unc_043:0.0):0.00054,(((PI311117_036:0.04839,((Taxi_006:0.0,Tiffen_Mennonite_034:0.0):0.00054,(Cal_J_TM_VF_027:0.00053,(Lycopersicon_esculentum_828_021:0.00054,(Black_Cherry_029:0.03245,(Galina_005:0.00054,S_pimpinellifolium_unc_045:0.01559)0.880:0.03248)0.770:0.01547)0.950:0.03179)0.160:0.01560)0.840:0.01563)0.420:0.00054,Lycopersicon_esculentum_825_020:0.00054)0.860:0.01556,((Cross_Country_013:0.0,ES_58_Heinz_040:0.0):0.00054,(Rutgers_004:0.01554,Lidi_014:0.04758)0.900:0.00054)0.880:0.00054)0.860:0.01558)0.080:0.01560,(Alisa_Craig_002:0.01560,John_s_big_orange_008:0.00054)1.000:0.00054)0.840:0.01558)0.800:0.01566,(Large_Pink_019:0.01555,Anto_030:0.00054)0.140:0.00054)0.920:0.01555)0.680:0.00054,Wheatley_s_Frost_Resistant_035:0.03155)0.950:0.00054);

        find PROJNAME -name '*.fasta' | sort | xargs -I{} -P30 bash -c 'vcfmerger/aux/FastTreeMP -nt -makematrix {} > {}.matrix'
            OUTPUT: PROJNAME/CHROMOSOME/short2.lst.vcf.gz.simplified.vcf.gz.filtered.vcf.gz.SL2.40ch01.000090300001-000090310000.Frag_SL2.40ch01g10000_9031.vcf.gz.SL2.40ch01.fasta.matrix
                Moneymaker_001 0.000000 0.134437 0.345611 0.134437  0.321609
                Alisa_Craig_002 0.134437 0.000000 0.211925 0.064210
                Gardeners_Delight_003 0.345611 0.211925 0.000000 0.211925



    Process the data into memory dump database (pyckle):
        vcf_walk_ram.py --pickle PROJNAME
            OUTPUT:
                walk_out_10k.db
                walk_out_10k_SL2.40ch00.db
                walk_out_10k_SL2.40ch01.db
                walk_out_10k_SL2.40ch02.db
                walk_out_10k_SL2.40ch03.db
                walk_out_10k_SL2.40ch04.db
                walk_out_10k_SL2.40ch05.db
                walk_out_10k_SL2.40ch06.db
                walk_out_10k_SL2.40ch07.db
                walk_out_10k_SL2.40ch08.db
                walk_out_10k_SL2.40ch09.db
                walk_out_10k_SL2.40ch10.db
                walk_out_10k_SL2.40ch11.db
                walk_out_10k_SL2.40ch12.db


    Convert (pickle) database to SQLite (if dependencies installed):
        vcf_walk_sql.py PROJNAME
            OUTPUT:
                walk_out_10k.sql.db


5.2. Server
    Run vcf_walk_server.py

    Run svg_server.py (if dependencis are installed)

    Run cluster_server.py (if dependencis are installed)




6. Acknowledgements
The co-authors:
	Dick de Ridder
	Eric M. Schranz
	Gabino Perez
	Hans de Jong
	Sander Peters
	Paul Franz
The beta testers:
	Remco Stam
	Ruud de Maagd
	Yongfeng Zhou


Manual: http://sauloal.github.io/introgressionbrowser
