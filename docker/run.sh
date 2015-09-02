touch access.log error.log

#--security-opt="apparmor:unconfine" \

docker run -it --rm \
-v $PWD/..:/var/www/ibrowser \
-v $PWD/../data:/var/www/ibrowser/data \
-p 0.0.0.0:10000:10000 \
--name ibrowser \
sauloal/introgressionbrowser

