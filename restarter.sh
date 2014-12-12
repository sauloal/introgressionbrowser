RUNNING=`ps aux | grep ibrowser.py | grep -v grep | wc -l`

if [[ "$RUNNING" == "0" ]]; then
	echo "NOT RUNNING. STARTING AGAIN"
	
else
	echo "ALREADY RUNNING"
fi
