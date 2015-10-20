echo "KILLING"
pgrep -f ibrowser.py | xargs kill
echo "CALLING"
RFOLDER=/home/ibrowser/introgressionbrowser
$RFOLDER/reloader.py $RFOLDER/ibrowser.py $RFOLDER/data &
echo "CALLED"
