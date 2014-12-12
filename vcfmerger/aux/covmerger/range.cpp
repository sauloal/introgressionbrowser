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

using namespace std;

template <typename T> // convert from string to number
T ston(const string str)
{
        T dSub;
        istringstream iss(str);
        iss >> dSub;
        return dSub;
};

int getMax(int argc, char **argv)
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


bool getGap(int argc, char **argv)
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


int main (int argc, char **argv)
{
    //vector<int> * svLines = new vector<int>;
    vector<unsigned short> * svLines = new vector<unsigned short>;

    int  iMax = getMax(argc, argv);
    bool gap  = getGap(argc, argv);

    if ( iMax > 0 )
    {
        //cerr  << "GOT MAX [" << iMax << "]" << endl;
        svLines->resize(iMax, 0);
    }


    int lastEnd = 0;
    while(!cin.eof() && cin.good()) {
        string cinStr;
        getline(cin, cinStr);
        istringstream iss(cinStr);
        //cout << "CINSTR " << cinStr << endl;

        string sSub;
        int j       =  0;
        int begin   = -1;
        int end     = -1;

        while(getline(iss, sSub, '\t'))
        { // split each tab
            //cout << "  SUB " << sSub << endl;
            if ( j == 0 )
            { // begin
                begin = ston<int>(sSub);
            }
            else if ( j == 1 )
            { // end
                end = ston<int>(sSub);
            //} else {
                //cerr << "SHOULD BE ONLY TWO COLUMNS. MORE FOUND";
                //cerr << cLine;
                //exit(1);
            }
            //double dSub = ston<double>(sSub);
            j++;
        }

        if (( begin > -1 ) && ( end > -1  ))
        {
            if ( end <= begin )
            {
                cerr  << "BEGIN [" << begin << "] IS BIGGER THAN END [" << end
                      << "]" << endl << ". ALTHOUGH I COULD DEAL WITH THAT, I'VE "
                      << "CHOOSEN TO DIE AND LET YOU KNOW THAT YOUR DATA IS "
                      << "WRONG" << endl;
                exit(1);
            }


            if ( begin < 0 )
            {
                cerr  << "BEGIN [" << begin << "] IS SMALLER THAN 0." << endl
                      << "ALTHOUGH I COULD DEAL WITH THAT, I'VE "
                      << "CHOOSEN TO DIE AND LET YOU KNOW THAT YOUR DATA IS "
                      << "WRONG" << endl;
                exit(2);
            }


            if ( iMax == 0 )
            {
                int iArrSize = (int) svLines->size();
                if ( iArrSize < end   )
                {
                    svLines->resize(end + 1, 0);
                }
            } else {
                if ( end > iMax )
                {
                    cerr    << "END [" << end << "] IS GREATER THAN MAXIMUM ["
                            << iMax << "] PASSED IN THE COMMAND LINE." << endl;
                    exit(3);
                }
            }


            if ( end > lastEnd ) {
                lastEnd = end;
            }

            for ( int i = begin; i <= end; ++i )
            {
                ++(*svLines)[i];
            }

            //cout << cLine << " BEGIN " << begin << " END " << end << endl;
        } else {
            //cerr << "empty line : " << cLine << endl;
            //pass
        }
    };

    int iArrSize = (int) svLines->size();

    if ( gap )
    {
        //cerr << "CLOSING GAP BETWEEN " << lastEnd << " AND " << iArrSize << "\n";
        for ( int i = lastEnd; i < iArrSize; ++i )
        {
            //closes with 1 when needed a reverse (1-n) probability
            (*svLines)[i] = 1;
        }
    }

    for ( int i = 0; i < iArrSize; ++i )
    {
        unsigned short val = (*svLines)[i];
        //int val = (*svLines)[i];
        //cout << i << "\t" << val << endl;
        cout << i << "\t" << val << "\n";
        //cout << i << "\t" << val << terminal;
    }

    return 0;

}
