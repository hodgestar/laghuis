#!/bin/bash -e

echo "Setting up dbus environment variables ..."

DBUS_ENV=`dbus-launch`
for VAR in $DBUS_ENV
do
  export $VAR
done

export HOME="/home/pi"

exec /home/pi/laghuis/utils/lag-jack.sh service 2>&1 >/home/pi/rc-lag.log
