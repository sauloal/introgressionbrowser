print "importing sqlalchemy"

from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm             import sessionmaker, relationship, backref
from sqlalchemy.orm             import sessionmaker
#from sqlalchemy                 import select, create_engine, Column, Integer, String, Float, ForeignKey, PickleType, LargeBinary, Sequence, and_
from sqlalchemy                 import create_engine, Column, Integer, String, LargeBinary, and_

from HTMLParser import HTMLParser
htmlparser      = HTMLParser()

Base            = declarative_base()
chromNameLength = 1024

import sys
sys.path.insert(0, '.')
import vcf_walk
from filemanager import loads_data

def getsession(db_file, echo=False):
    print "CREATING SESSSION"
    engine    = create_engine('sqlite:///'+db_file, echo=echo )
    Session   = sessionmaker(bind=engine)
    session   = Session()
    session._model_changes = {}

    """
    Create database strucuture
    """
    Base.metadata.create_all(engine)

    session.commit()


    return ( engine, Session, session )

#register[DB_START  ] = start
#register[DB_END    ] = end
#register[DB_LEN_OBJ] = 1
#register[DB_LEN_SNP] = len_aln_snp
#register[DB_NAME   ] = name
#register[DB_TREE   ] = tree_str
#register[DB_FASTA  ] = snpSeq
#register[DB_LINE   ] = data
class info_db(Base):
    """
    Database containing database info
    """
    __tablename__ = 'info'
    chrom  = Column(String(chromNameLength), nullable=False, primary_key=True)
    size   = Column(Integer                , nullable=False                  )

    def __init__(self, chrom, size):
        self.chrom = chrom
        self.size  = size
        #print "chromNameLength:", chromNameLength

    def __repr__(self):
        return "<CHROMS('*%s', '%d')>"

    def raw(self):
        return { self.chrom: self.size }


class chroms_db(Base):
    """
    Database containing chromosome names
    """
    __tablename__ = 'chrom'
    chrom  = Column(String(chromNameLength), nullable=False, primary_key=True)
    size   = Column(Integer                , nullable=False                  )

    def __init__(self, chrom, size):
        self.chrom = chrom
        self.size  = size
        #print "chromNameLength:", chromNameLength

    def __repr__(self):
        return "<CHROMS('*%s', '%d')>"

    def raw(self):
        return { self.chrom: self.size }


class spp_db(Base):
    """
    Database containing species names
    """
    __tablename__ = 'spps'
    spp     = Column(String                 , nullable=False, primary_key=True)
    pos     = Column(Integer                , nullable=False )

    def __init__(self, spp, pos):
        self.spp     = spp
        self.pos     = pos

    def __repr__(self):
        return "<SPP('*%s', '%d')>" % ( self.spp, self.pos )

    def raw(self):
        return { htmlparser.unescape(self.spp): self.pos }


class fasta_db(Base):
    """
    Database containing alignments
    """
    __tablename__ = 'fastas'
    chrom  = Column(String(chromNameLength), nullable=False, primary_key=True)
    regnum = Column(Integer                , nullable=False, primary_key=True)
    name   = Column(String                 , nullable=False, primary_key=True)
    fasta  = Column(LargeBinary            , nullable=False)

    def __init__(self, chrom, regnum, name, fasta):
        self.chrom  = chrom
        self.regnum = regnum
        self.name   = name
        self.fasta  = fasta

    def __repr__(self):
        return "<FASTA('*%s', '*%d', '*%s', '%d')>" % (self.chrom, self.regnum, self.name, len(self.fasta))

    def raw(self):
        return (self.regnum, loads_data(self.fasta))


class tree_db(Base):
    """
    Database containing trees
    """
    __tablename__ = 'trees'
    chrom  = Column(String(chromNameLength), nullable=False, primary_key=True)
    regnum = Column(Integer                , nullable=False, primary_key=True)
    name   = Column(String                 , nullable=False, primary_key=True)
    tree   = Column(LargeBinary            , nullable=False)

    def __init__(self, chrom, regnum, name, tree):
        self.chrom  = chrom
        self.regnum = regnum
        self.name   = name
        self.tree   = tree

    def __repr__(self):
        return "<TREE('*%s', '*%d', '*%s', '%d')>" % (self.chrom, self.regnum, self.name, len(self.tree))

    def raw(self):
        return (self.regnum, loads_data(self.tree))


class matrix_db(Base):
    """
    Database containing matrices
    """
    __tablename__ = 'matrices'
    #matrix_db(   chromosome, regnum, NAME, sppi, dumps_data(line) )
    chrom  = Column(String(chromNameLength), nullable=False, primary_key=True)
    regnum = Column(Integer                , nullable=False, primary_key=True)
    name   = Column(String                 , nullable=False, primary_key=True)
    sppi   = Column(Integer                , nullable=False, primary_key=True)
    matrix = Column(LargeBinary            , nullable=False)

    def __init__(self, chrom, regnum, name, sppi, matrix):
        self.chrom  = chrom
        self.regnum = regnum
        self.name   = name
        self.sppi   = sppi
        self.matrix = matrix

    def __repr__(self):
        return "<MATRIX('*%s', '*%d', '*%s', '*%d', '%d')>" % (self.chrom, self.regnum, self.name, self.sppi, len(self.matrix))

    def raw(self):
        return (self.regnum, self.sppi, loads_data(self.matrix))


class register_db(Base):
    """
    Database containing all information such as:
    chromosome, start position, end position, number of (sub)objects, number of SNPs, fragment name and distance matrix
    """
    __tablename__ = 'registers'
    chrom  = Column(String(chromNameLength), nullable=False, primary_key=True)
    regnum = Column(Integer                , nullable=False, primary_key=True)
    start  = Column(Integer                , nullable=False)
    end    = Column(Integer                , nullable=False)
    objLen = Column(Integer                , nullable=False)
    snpLen = Column(Integer                , nullable=False)
    name   = Column(String                 , nullable=False, primary_key=True)
    #tree   = Column(String                 , nullable=False)
    #fasta  = Column(LargeBinary            , nullable=False)
    #data   = Column(LargeBinary            , nullable=False)

    def __init__(self, chrom, regnum, start, end, objLen, snpLen, name):#, data):#, tree, fasta):
        self.chrom  = chrom
        self.regnum = regnum

        self.start  = start
        self.end    = end
        self.objLen = objLen
        self.snpLen = snpLen
        self.name   = name
        #self.tree   = tree
        #self.fasta  = fasta
        #self.data   = data

    def __repr__(self):
        return "<REGISTER('*%s', '*%d', '%d', '%d', '%d', '%d', '*%s')>" % \
                (self.chrom, self.regnum, self.start, self.end, self.objLen, self.snpLen, self.name)

    def raw(self):
        reg  = [None]*vcf_walk.NUM_REGISTER_VARS
        reg[ vcf_walk.DB_START   ] = self.start
        reg[ vcf_walk.DB_END     ] = self.end
        reg[ vcf_walk.DB_LEN_OBJ ] = self.objLen
        reg[ vcf_walk.DB_LEN_SNP ] = self.snpLen
        reg[ vcf_walk.DB_NAME    ] = self.name
        #reg[ vcf_walk.DB_TREE    ] = self.tree
        #reg[ vcf_walk.DB_FASTA   ] = self.get_fasta()
        #reg[ vcf_walk.DB_LINE    ] = self.get_data()

        return (self.regnum, reg)

    #def get_fasta(self):
    #    return loads(self.fasta )

    #def get_data(self):
    #    return loads_data( self.data  )


class cluster_db(Base):
    """
    Database containing alignments
    """
    __tablename__ = 'clusters'
    chrom   = Column(String(chromNameLength), nullable=False, primary_key=True)
    spp     = Column(String                 , nullable=False, primary_key=True)
    cluster = Column(LargeBinary            , nullable=False)

    def __init__(self, chrom, spp, cluster):
        self.chrom   = chrom
        self.spp     = spp
        self.cluster = cluster

    def __repr__(self):
        return "<CLUSTER('*%s', '*%s', '%d')>" % (self.chrom, self.spp, len(self.cluster))

    def raw(self):
        return loads_data(self.cluster)
