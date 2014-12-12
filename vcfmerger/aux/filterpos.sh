#set -xeu

INFILE=$1
CHROMOSOME=$2
START=$3
END=$4

gunzip -c $INFILE | gawk '{ if ($1=="'$CHROMOSOME'") { if ( $2 >= '$START' && $2 <= '$END' ) { print }}}'
