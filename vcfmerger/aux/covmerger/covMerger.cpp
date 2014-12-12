#include <iostream>
#include <stdio.h>
#include <string>
#include <string.h>
#include <vector>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <cstdlib>
#include <cctype>
#include <map>
#include <math.h>
#include <ctime>
#include <gzstream.h>

//./covMerger <out.mcov.gz> infolder/*.cov.gz

//#define DEBUG

using namespace std;


const int CRJUSTCLOSED = 0;
const int CRCLOSED     = 1;
const int CRVALID      = 2;


typedef unsigned long long int         uint64l_t;
typedef                    double      udou64_t;
typedef vector<string                > vecString;
typedef map<   string, int           > mapString;
//typedef vector<vector<vector<int>  > > dataStruct;
//typedef vector<bool                  > vecBool;


struct covRegister {
    string    chr;
    uint64l_t pos;
    string    cov;
    int       state;
};


typedef vector<covRegister           > vecCovRegister;


template <typename T> // convert from string to number
T ston(const string str)
{
        T dSub;
        istringstream iss(str);
        iss >> dSub;
        return dSub;
};


inline int getMax(int argc, char **argv)
{
    if ( argc > 1 )
    {
        //cerr << "ARGC GT 1" << endl;
        //cerr << "  ARGC EQ 2" << endl;
        string inp = argv[1];
        int    val = ston<int>(inp);
        return val;
    } else {
        //cerr << "ARGC LT 1" << endl;
        return 0;
    }
}


inline bool getGap(int argc, char **argv)
{
    if ( argc > 1 )
    {
        //cerr << "ARGC GT 1" << endl;
        if ( argc == 3 )
        {
            //cerr << "  ARGC EQ 3" << endl;
            if ( strcmp(argv[2], "g") == 0 )
            {
                //cerr << "    THIRD IS G" << endl;
                return true;
            } else {
                //cerr << "    THIRD IS NOT G [" << argv[2] << "]" << endl;
                return false;
            }
        } else {
            //cerr << "  ARGC NE 2 [" << argc << "]" << endl;
            return false;
        }
    } else {
        //cerr << "ARGC LT 1" << endl;
        return false;
    }
}


//http://stackoverflow.com/questions/236129/how-to-split-a-string-in-c
inline void tokenize(const std::string& str, vecString& tokens,
              const std::string& delimiters = " ", bool trimEmpty = false)
{
    int pos, lastPos = 0;
    while(true)
    {
        pos = str.find_first_of(delimiters, lastPos);
        //cerr << "pos " << pos << endl;

        if(pos == std::string::npos)
        {
            pos = str.length();
        }

        if (pos != lastPos || !trimEmpty)
        {
            vecString::value_type r = vecString::value_type(
                        str.data() + lastPos,
                        pos        - lastPos
                );
            //cerr << "  re '" << r << "'" << endl;
            tokens.push_back( r );
        }

        if(pos == str.length())
        {
            break;
        }

        lastPos = pos + 1;
   }
};


class FileHolder {
    public:
        bool status;
        virtual ~FileHolder() {};
        virtual string  getFileName() {};
        virtual void open( const string fn ) {};
        virtual bool good() {};
        virtual void write( const string line ) { cerr << "wrong write" << endl; };
        virtual bool eof() {};
        virtual void close() {};

        virtual void getLine(vecString &tokens) {};
};


typedef vector<FileHolder*           > vecFileHolder;
struct  heapResult {
    vecCovRegister result;
    string         chr;
    int            pos;
    int            chrCount;
    int            posCount;
    int            sumCov;
    bool           valid;
};


template<typename streamtype>
class oFileHolder: public FileHolder {
    private:
        string       fileName;
        int          pos;
        streamtype   stream;

    public:
        //bool status;

        string  getFileName() {
            return fileName;
        };

        void open( const string fn ) {
            fileName = fn;

            stream.open( fileName.c_str(), ios::out );

            if ( stream ) {
                if ( !stream.good() ) {
                    cerr << "error reading out file" << fn << endl;
                    exit( 1 );
                }
                cerr << "successfully opened out file" << fn  << endl;

            } else {
                cerr << "error opening out file" << fn  << fn << endl;
                exit( 1 );
            }

            status = true;
        };

        bool good() {
#ifdef DEBUG
            cerr << fileName << " getting good" << " status " << status << endl;
#endif
            return stream.good();
        };

        void write( const string line ) {
#ifdef DEBUG
            //cerr << fileName << " wrinting " << line << endl;
#endif
            if ( good() && !eof()) {
                stream << line;
            }
        }

        bool eof() {
#ifdef DEBUG
            cerr << fileName << " getting eof" << " status " << status << endl;
#endif
            return stream.eof();
        };

        void close() {
            cerr << fileName << " closing" << endl;
            status = false;
            return stream.close();
        };
};


template<typename streamtype>
class iFileHolder: public FileHolder  {
    private:
        string     fileName;
        string     line;
        int        pos;
        streamtype stream;
        string     token;

    public:
        //bool status;

        string  getFileName() {
            return fileName;
        };

        void open( const string fn ) {
            fileName = fn;

            cerr << "opening in file " << fileName << endl;

            stream.open( fileName.c_str(), ios::in );

            if ( stream ) {
                if ( !stream.good() ) {
                    cerr << "error reading in file " << fileName << endl;
                    exit( 1 );
                }
                cerr << "successfully opened in file " << fileName << endl;

            } else {
                cerr << "error opening in file " << fileName << endl;
                exit( 1 );
            }
            status = true;
        };

        bool good() {
#ifdef DEBUG
            cerr << fileName << " getting good " << stream.good() << " status " << status << endl;
#endif
            return stream.good();
        };

        bool eof() {
#ifdef DEBUG
            cerr << fileName << " getting eof " << stream.eof() << " status " << status  << endl;
#endif
            return stream.eof();
        };

        void getLine(vecString &tokens) {
            tokens.clear();
            //tokens.resize(3);

            if ( status && good() && !eof() ) {

                getline( stream, line );

#ifdef DEBUG
                cerr << fileName << " getting line   "  << line << endl;
                cerr << fileName << " getting tolkens"  << endl;
#endif


                tokenize(line, tokens, "\t");

//            int currTokenPos = 0;
//            istringstream iss(line);
//            while( getline(iss, token, '\t') ) {
//                tokens[currTokenPos] = token;
//                currTokenPos++;
//#ifdef DEBUG
//                //cerr << "  token " << token << endl;
//#endif
//            }
//
                if ( tokens.size() != 3 ) {
                    tokens.clear();
                } else {

#ifdef DEBUG
                cerr << fileName << " tolken size " << tokens.size() << endl;
                cerr << fileName << " tolken size " << tokens.size() << " tolkens 0 '" << tokens[0] << "' 1 '" << tokens[1] << "' 2 '" << tokens[2] << "'" << endl;
#endif
                }
            }
        };

        void close() {
            cerr << fileName << "closing in" << endl;
            status = false;
            return stream.close();
        };
};


class fileHolderCreator {
    public:
        FileHolder* createOut( string fileName ) {
            if ( fileName.substr( fileName.length() - 2 ) == "gz" ) {
                oFileHolder<ogzstream>* fh = new oFileHolder<ogzstream>();
                fh->open(fileName);
                return fh;
            } else {
                oFileHolder<ofstream>* fh = new oFileHolder<ofstream>();
                fh->open(fileName);
                return fh;
            }
        }

        FileHolder* createIn( string fileName ) {
            if ( fileName.substr( fileName.length() - 2 ) == "gz" ) {
                iFileHolder<igzstream>* fh = new iFileHolder<igzstream>;
                fh->open(fileName);
                return fh;
            } else {
                iFileHolder<ifstream>* fh = new iFileHolder<ifstream>;
                fh->open(fileName);
                return fh;
            }
        }
};


class stats {
    private:
        uint64l_t sum; // TODO: CONVERT TO LONG INT
        uint64l_t count;
        udou64_t var;
    public:
        stats(): sum(0), count(0), var(0) {};

        double avg() {
            return float(sum) / float(count);
        };

        void add(int val) {
            sum += val;
            ++count;
            var +=  val - avg();
        };

        double getVar()    { return var;       };
        double gatStdDev() { return sqrt(var); };
        int    getSum()    { return sum;       };
        int    getCount()  { return count;     };
};


class covheap {
    private:
        int               numOpenFiles;
        int               chromCount;
        int               posCount;
        int               lastPos;

        vecString         fileNames;
        mapString         filePos;
        vecFileHolder     fileHandlers;
        fileHolderCreator creator;
        string            lastChr;
        vecCovRegister    heapHead;
        vecString         tokens;

    public:
        covheap(): numOpenFiles(0), chromCount(0), posCount(0), lastPos(0), lastChr("") {
        };

        void addFile( const string fileName ) {
            filePos[ fileName ] = fileNames.size();

            fileNames.push_back( fileName );

            FileHolder* inFileHandle = creator.createIn( fileName );

            fileHandlers.push_back( inFileHandle );

            ++numOpenFiles;

            covRegister firstRegister;
            getRegister( filePos[ fileName ], firstRegister );
            heapHead.push_back( firstRegister );
        };

        string getCurrChr() {
            return lastChr;
        };

        int getCurrpos(){
            return lastPos;
        };

        int getNumFiles() {
            return fileNames.size();
        };

        bool isempty() {
            //cerr << "is empty? " << numOpenFiles << "\n";
            return numOpenFiles == 0;
        };

        void getRegister( const int fileNum, covRegister &currRegister ) {
            FileHolder* holder   = fileHandlers[ fileNum ];

            if ( holder->good() && holder->status ) {
                if ( !holder->eof() ) {

                    holder->getLine(tokens);

                    if ( tokens.size() == 3 ) {

#ifdef DEBUG
                        string fileName = fileNames[ fileNum ];
                        cerr << fileName  << " got ";
                        cerr << tokens[0] << " ";
                        cerr << tokens[1] << " ";
                        cerr << tokens[2];
                        cerr << endl;
#endif

                        currRegister.chr    =            tokens[0];
                        currRegister.pos    = ston<int>( tokens[1] );
                        currRegister.cov    =            tokens[2];
                        currRegister.state  = CRVALID;

#ifdef DEBUG
                        cerr << " chr " << currRegister.chr << endl;
                        cerr << " pos " << currRegister.pos << endl;
                        cerr << " cov " << currRegister.cov << endl;
#endif

                    } else {
#ifdef DEBUG
                        string fileName = fileNames[ fileNum ];
                        cerr << fileName << " requesting again" << endl;
#endif
                        getRegister( fileNum, currRegister ); // empty line. request next
                    }
                } else {
                    string fileName = fileNames[ fileNum ];
                    cerr << "\n" << fileName << " closing file" << endl;
                    holder->close();
                    holder->status = false;
                    currRegister.state  = CRJUSTCLOSED; // file is empty. close it and return empty

                }
            } else {
                string fileName = fileNames[ fileNum ];
                cerr << "\n" << fileName << " file closed. GOOD " << holder->good() << " !EOF " << (!holder->eof()) << " STATUS " << holder->status << " STATE " << (currRegister.state == CRVALID) << endl;
                holder->status = false;
                currRegister.state  = CRCLOSED; // file is closed. shouldn't have been requested
                --numOpenFiles;
            }
        };

        void next(heapResult &currResult) {
            vecCovRegister response;

            int numFiles = fileNames.size();

            response.resize( numFiles );

            chromCount       = 0;
            posCount         = 0;
            int trueStatuses = 0;
            //int sumCov = 0;

            for ( int fileNum = 0; fileNum < numFiles; ++fileNum ) {
                if ( fileHandlers[ fileNum ]->good() && (!fileHandlers[ fileNum ]->eof()) && fileHandlers[ fileNum ]->status ) { // if file not closed
                    covRegister &currRegister = heapHead[ fileNum ];

                    if ( currRegister.state == CRVALID ) { // is valid
                        if ( lastChr == "" ) {
                            lastChr = currRegister.chr;
                            cerr  << endl << "STARTING CHROMOSOME " << lastChr << endl;
                            //TODO: FIGURE OUT WHAT IS THE NEXT CHROMOSOME AMONG ALL THE OPTIONS
                            //      IN CASE A FILE SKIPS ONE CHROMOSOME
                        }

                        ++trueStatuses;

                        if ( currRegister.chr == lastChr ) { // if chrom is correct
                            ++chromCount; // chrom still exists

                            if ( currRegister.pos == lastPos ) { // if pos is correct
                                ++posCount;

                                response[ fileNum ]  = currRegister; // get info add to response

                                covRegister nextRegister;
                                getRegister( fileNum, nextRegister );
                                heapHead[ fileNum ] = nextRegister; // get next line add to response

#ifdef DEBUG
                            } else {// end if file is open
                                cerr << "WRONG POS " << currRegister.pos << " != " << lastPos << endl;
#endif
                            } // end if pos is correct
#ifdef DEBUG
                        } else {// end if file is open
                            cerr << "CHROMOSOME IS DIFFERENT " << currRegister.chr << " != " << lastChr << endl;
#endif
                        } // if chrom is correct
#ifdef DEBUG
                    } else {// end if file is open
                        cerr << "STATE IS NOT VALID " << currRegister.state << endl;
#endif
                    }
#ifdef DEBUG
                } else {// end if file is open
                    cerr << "STATUS IS FALSE. GOOD " << fileHandlers[ fileNum ]->good() << " EOF " << (!fileHandlers[ fileNum ]->eof()) << " STATUS " << fileHandlers[ fileNum ]->status << endl;
#endif
                }
            } // end for sppnum


            currResult.result   = response;
            currResult.chr      = lastChr;
            currResult.pos      = lastPos;
            currResult.chrCount = chromCount;
            currResult.posCount = posCount;
            currResult.valid    = trueStatuses > 0;
            //currResult.sumCov   = sumCov;

            ++lastPos;

            if ( chromCount == 0 && trueStatuses > 0 ) { // no more positions to current chromosome
#ifdef DEBUG
                cerr << "CHROM COUNT == 0: REQUESTING AGAIN" << endl;
#endif

                lastPos = 0;
                lastChr = "";
                next( currResult );
            }
        };
};




int main (int argc, char **argv) {
    if ( argc < 4 ) {
        cerr << " needs at least 1 output file and 2 input files" << endl;
        return 1;
    }

    string      outFile = argv[1];

    cout << "saving to " << outFile << "\n";

    //dataStruct  data;

    vecString   chromNames;
    mapString   chromPos;

    covheap     heap;

    for ( int argnum = 2; argnum < argc; ++argnum ) {
        string infile = argv[argnum];
        cerr << "opening " << infile << endl;
        heap.addFile( infile );
    }

    stats     statistics; //TODO: PER CHROMOSOME

    int numFiles = heap.getNumFiles();




    fileHolderCreator creator;

    FileHolder *outFileHandle = creator.createOut( outFile );

    string lastChr  = "";
    string cov      = "";
    int    lastPos  = 0;
    int    enterPos = 0;
    time_t t1       = time(0);
    time_t t2       = time(0);
    time_t t3       = time(0);
    time_t tc       = time(0);
    time_t td       = time(0);

    while ( !heap.isempty() ) {
        heapResult val;
        heap.next( val );

        //cerr << "CHR " << val.chr << " POS " << val.pos << " CHR COUNT " << val.chrCount << " POS COUNT " << val.posCount << " SUM COV " << val.sumCov << "\n";
        //for ( int fileNum = 0; fileNum < numFiles; ++fileNum ) {
        //    cerr << "  chr " << val.result[fileNum].chr << " pos " << val.result[fileNum].pos << " cov " << val.result[fileNum].cov << " state " << val.result[fileNum].state << "\n";
        //    if ( val.result[fileNum].cov > 0 ) {
        //        statistics.add( val.result[fileNum].cov );
        //    }
        //}

        if ( val.valid ) {
            int posPer = (int)(val.pos/10000);
            if (( lastChr != val.chr ) || ( lastPos != posPer )) {
                if ( lastChr != val.chr ) {
                    lastChr  = val.chr;
                    lastPos  = 0;
                    enterPos = 0;
                    tc       = time(0);
                    td       = tc - t2;
                    t2       = time(0);
                    cerr << " previous " << td;
                    td       = tc - t1;
                    cerr << "s total " << td << "s" << endl << val.chr << " ";
                    outFileHandle->write( val.chr + "\n" );
                    //if ( td != 0 ) {
                    //    break;
                    //}
                }

                if ( lastPos != posPer ) {
                    lastPos = posPer;
                    cout << " " << val.pos;
                    ++enterPos;
                    if ( ( enterPos % 10 ) == 0 ) {
                        tc = time(0);
                        td = tc - t3;
                        t3 = time(0);
                        cout << " " << td << "s" << endl << val.chr << " ";
                    }
                }
            }

            outFileHandle->write( to_string( val.pos ) );

            for ( int fileNum = 0; fileNum < numFiles; ++fileNum ) {
#ifdef DEBUG
                cerr << "main loop cov " << val.result[fileNum].cov << " chr " << val.result[fileNum].chr << " pos " << val.result[fileNum].pos << endl;
#endif
                cov = val.result[fileNum].cov;

                if ( cov == "" ) {
                    cov = "0";
                }

                outFileHandle->write(  "\t" + cov );

                //if ( val.result[fileNum].cov > 0 ) {
                //    statistics.add( val.result[fileNum].cov );
                //}
            }

            outFileHandle->write( "\n" );
        }
    }

    outFileHandle->close();


    cerr << "STATISTICS" << endl;
    cerr << "SUM   : "   << statistics.getSum()    << "\n";
    cerr << "AVG   : "   << statistics.avg()       << "\n";
    cerr << "COUNT : "   << statistics.getCount()  << "\n";
    cerr << "VAR   : "   << statistics.getVar()    << "\n";
    cerr << "STDDEV: "   << statistics.gatStdDev() << "\n";

    int sq1min = statistics.avg() - statistics.gatStdDev();

    if ( sq1min < 0 ) { sq1min = 1; };

    cerr << "1SQMIN: "   << sq1min << "\n";

    //for ( int chromPos = 0; chromPos < data.size(); ++chromPos ) {
    //    //data[ lastChromPos ][ pos ] += 1;
    //    string chromName = chromNames[ chromPos ];
    //    for ( int pos = 0; pos < data[ chromPos ].size(); ++pos ) {
    //        cout << chromName << "\t" << pos;
    //        int sum = 0;
    //        int num = 0;
    //        for ( int fileNum = 0; fileNum < data[ chromPos ][ pos ].size(); ++fileNum ) {
    //            int val = data[ chromPos ][ pos ][ fileNum ];
    //            cout << "\t" << val;
    //            sum += val;
    //            if ( val > 0 ) {
    //                ++num;
    //            }
    //        }
    //        cout << "\t" << sum << "\t" << num << "\n";
    //    }
    //}
}


//
//int main2 (int argc, char **argv)
//{
//    //vector<int> * svLines = new vector<int>;
//    vector<unsigned short> * svLines = new vector<unsigned short>;
//
//    int  iMax = getMax(argc, argv);
//    bool gap  = getGap(argc, argv);
//
//    if ( iMax > 0 )
//    {
//        //cerr  << "GOT MAX [" << iMax << "]" << endl;
//        svLines->resize(iMax, 0);
//    }
//
//
//    int lastEnd = 0;
//    while(!cin.eof() && cin.good()) {
//        string cinStr;
//        getline(cin, cinStr);
//        istringstream iss(cinStr);
//        //cout << "CINSTR " << cinStr << endl;
//
//        string sSub;
//        int j       =  0;
//        int begin   = -1;
//        int end     = -1;
//
//        while(getline(iss, sSub, '\t'))
//        { // split each tab
//            //cout << "  SUB " << sSub << endl;
//            if ( j == 0 )
//            { // begin
//                begin = ston<int>(sSub);
//            }
//            else if ( j == 1 )
//            { // end
//                end = ston<int>(sSub);
//            //} else {
//                //cerr << "SHOULD BE ONLY TWO COLUMNS. MORE FOUND";
//                //cerr << cLine;
//                //exit(1);
//            }
//            //double dSub = ston<double>(sSub);
//            j++;
//        }
//
//        if (( begin > -1 ) && ( end > -1  ))
//        {
//            if ( end <= begin )
//            {
//                cerr  << "BEGIN [" << begin << "] IS BIGGER THAN END [" << end
//                      << "]" << endl << ". ALTHOUGH I COULD DEAL WITH THAT, I'VE "
//                      << "CHOOSEN TO DIE AND LET YOU KNOW THAT YOUR DATA IS "
//                      << "WRONG" << endl;
//                exit(1);
//            }
//
//
//            if ( begin < 0 )
//            {
//                cerr  << "BEGIN [" << begin << "] IS SMALLER THAN 0." << endl
//                      << "ALTHOUGH I COULD DEAL WITH THAT, I'VE "
//                      << "CHOOSEN TO DIE AND LET YOU KNOW THAT YOUR DATA IS "
//                      << "WRONG" << endl;
//                exit(2);
//            }
//
//
//            if ( iMax == 0 )
//            {
//                int iArrSize = (int) svLines->size();
//                if ( iArrSize < end   )
//                {
//                    svLines->resize(end + 1, 0);
//                }
//            } else {
//                if ( end > iMax )
//                {
//                    cerr    << "END [" << end << "] IS GREATER THAN MAXIMUM ["
//                            << iMax << "] PASSED IN THE COMMAND LINE." << endl;
//                    exit(3);
//                }
//            }
//
//
//            if ( end > lastEnd ) {
//                lastEnd = end;
//            }
//
//            for ( int i = begin; i <= end; ++i )
//            {
//                ++(*svLines)[i];
//            }
//
//            //cout << cLine << " BEGIN " << begin << " END " << end << endl;
//        } else {
//            //cerr << "empty line : " << cLine << endl;
//            //pass
//        }
//    };
//
//    int iArrSize = (int) svLines->size();
//
//    if ( gap )
//    {
//        //cerr << "CLOSING GAP BETWEEN " << lastEnd << " AND " << iArrSize << "\n";
//        for ( int i = lastEnd; i < iArrSize; ++i )
//        {
//            //closes with 1 when needed a reverse (1-n) probability
//            (*svLines)[i] = 1;
//        }
//    }
//
//    for ( int i = 0; i < iArrSize; ++i )
//    {
//        unsigned short val = (*svLines)[i];
//        //int val = (*svLines)[i];
//        //cout << i << "\t" << val << endl;
//        cout << i << "\t" << val << "\n";
//        //cout << i << "\t" << val << terminal;
//    }
//
//    return 0;
//
//}
