touch access.log error.log
docker run -it --security-opt="apparmor:unconfine" \
-v $PWD/data:/var/www/ibrowser/data \
-v $PWD/access.log:/var/log/apache2/access.log \
-v $PWD/error.log:/var/log/apache2/error.log \
--hostname="assembly.ab.wurnet.nl" \
ibrowser

