#!/bin/bash -e

DEVICES=`printenv LAG_DEVICES  || echo ""`
DEVICES="${DEVICES:-0 1 2}"

LAGHOME="$HOME/laghuis"
LOGFILE="$HOME/lag-jack.log"

echo "This is LAG JACK."
echo "================="

echo "Using devices $DEVICES."

echo "Running in $LAGHOME."

echo "Logging to $LOGFILE ..."

echo "Cleaning up rampant processes ..."

pkill -9 "python" && true
pkill -9 "alsa_in" && true
pkill -9 "alsa_out" && true
pkill -9 "jackdbus" && true

echo "Setting up dbus environment variables ..."

DBUS_ENV=`dbus-launch`
for VAR in $DBUS_ENV
do
  export $VAR
done

echo "Start JACK with dummy device ..."

jack_control ds dummy
jack_control start

echo "Setting up ALSA devices ..."

for i in $DEVICES
do
   alsa_in -j "alsa-in-$i" -d "hw:$i" -c 1 >> "$LOGFILE" &
   alsa_out -j "alsa-out-$i" -d "hw:$i" -c 2 >> "$LOGFILE" &
done

echo "Launching GStreamer pipeline ..."

PYTHONPATH="$LAGHOME" python -m laghuis.lagjack &

echo "Waiting for pipeline to launch ..."

sleep 1

echo "Jack ports are:"

jack_lsp

echo "Connecting Jack ports ..."

for i in $DEVICES
do
   MIC_CHANNEL=`expr $i % 2 + 1`
   jack_connect \
       "alsa-in-$i:capture_1" \
       "gst-launch-1.0-01:in_jackaudiosrc0_$MIC_CHANNEL"
   jack_connect \
       "gst-launch-1.0:out_jackaudiosink0_1" \
       "alsa-out-$i:playback_1"
   jack_connect \
       "gst-launch-1.0:out_jackaudiosink0_2" \
       "alsa-out-$i:playback_2"
done

echo "Running ..."

echo "Press enter when done ..."
read user_input

echo "Cleaning up ..."

JOBS=`jobs -p`

for job in $JOBS
do
    kill "$job"
done

for job in $JOBS
do
    wait "$job"
done

echo "Stopping JACK ..."

jack_control stop
jack_control exit
