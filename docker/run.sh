touch access.log error.log

#--security-opt="apparmor:unconfine" \

docker run -it --rm \
-v $PWD/..:/var/www/ibrowser \
-v $PWD/../data:/var/www/ibrowser/data \
-v $PWD/access.log:/var/log/apache2/access.log \
-v $PWD/error.log:/var/log/apache2/error.log \
-p 0.0.0.0:9000:10000 \
--hostname="assembly.ab.wurnet.nl" \
--name ibrowser \
sauloal/ibrowser

