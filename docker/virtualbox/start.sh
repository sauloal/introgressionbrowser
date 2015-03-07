HPATH=/home/ibrowser
XPATH=$HPATH/introgressionbrowser
MPATH=$XPATH/data
LOG=$HPATH/start.log
SNAME=DATA
NID=1000


echo "SLEEPING"
sleep 20
echo "AWAKEN"


date >> $LOG
echo "NID $NID HPATH $HPATH XPATH $XPATH MPATH $MPATH" >> $LOG
sudo umount $MPATH >> $LOG

set -xeu
sudo mount -t vboxsf $SNAME $MPATH >> $LOG
#sudo mount -t vboxsf -o uid=$NID,gid=$NID $SNAME $MPATH >> $LOG

if [[ ! -f "$MPATH/config.py" ]]; then
	echo "CONFIG FILE NOT FOUND. CHECK IF SHARED FOLDER HAS BEEN MOUNTED"
	exit 1
fi


echo "RUNNING"
$HPATH/restart.sh
echo "RUN"
