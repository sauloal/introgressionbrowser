#https://github.com/travist/jsencrypt
KEY_SIZE=2048

rm rsa_${KEY_SIZE}_priv.pem rsa_${KEY_SIZE}_pub.pem

openssl genrsa -out rsa_${KEY_SIZE}_priv.pem $KEY_SIZE

openssl rsa -pubout -in rsa_${KEY_SIZE}_priv.pem -out rsa_${KEY_SIZE}_pub.pem

