#https://github.com/travist/jsencrypt
KEY_FILE="../config.keylen"

if [[ ! -f "$KEY_FILE" ]]; then
	echo "key file $KEY_FILE does not exists. create it first"
	exit 1
fi

KEY_SIZE=`cat ../config.keylen`
echo "KEY SIZE $KEY_SIZE"

PRIV=rsa_${KEY_SIZE}_priv.pem
PUB=rsa_${KEY_SIZE}_pub.pem

echo "PRIVATE KEY $PRIV"
echo "PUBLIC  KEY $PUB"

if [[ ! -f "$PRIV" ]]; then
	echo "PRIVATE KEY $PRIV DOES NOT EXISTS. CREATING"
	rm $PRIV $PUB || true
	openssl genrsa -out $PRIV $KEY_SIZE
	openssl rsa -pubout -in $PRIV -out $PUB
else
	echo "PRIVATE KEY $PRIV EXISTS. SKIPPING"
fi
