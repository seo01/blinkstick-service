 #!/bin/sh

#Script needs to be run with super user priverlages
#Optionally takes one argument - the url to monitor

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

if [ "$1" != "" ]; then
    URL=$1
else
    URL="$DIR/../example.json"
fi

CMD="python $DIR/../src/light.py -f $URL"

echo "1. sed \"s,<COMMAND>,${CMD},g\" $DIR/blinkstick-service-init.sh > /etc/init.d/blinkstick-service"
sed "s,<COMMAND>,${CMD},g" $DIR/blinkstick-service-init.sh > /etc/init.d/blinkstick-service
echo "2. chmod 755 /etc/init.d/blinkstick-service"
chmod 755 /etc/init.d/blinkstick-service
echo "3. touch /var/log/blinkstick-service.log && chown pi /var/log/blinkstick-service.log"
touch /var/log/blinkstick-service.log && chown pi /var/log/blinkstick-service.log
echo "4. touch /var/run/blinkstick-service.pid && chown pi /var/run/blinkstick-service.pid"
touch /var/run/blinkstick-service.pid && chown pi /var/run/blinkstick-service.pid
echo "5. update-rc.d blinkstick-service defaults"
update-rc.d blinkstick-service defaults
echo "6. service blinkstick-service start"
service blinkstick-service start