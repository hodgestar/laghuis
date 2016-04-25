#!/bin/bash -e

SERVICE="$1"

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

jack_control stop && true
jack_control start
jack_control ds dummy

echo "Setting up ALSA devices ..."

for i in $DEVICES
do
   alsa_in -j "alsa-in-$i" -d "hw:$i" -c 1 >> "$LOGFILE" &
   alsa_out -j "alsa-out-$i" -d "hw:$i" -c 2 >> "$LOGFILE" &
done

echo "Launching GStreamer pipeline ..."

PYTHONPATH="$LAGHOME" python -m laghuis.lagjack &
PIPEPROC="python"
LAG_AUDIO_SRC="laghuis_jackaudiosrc"
LAG_AUDIO_SINK="laghuis_jackaudiosink"

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
       "$PIPEPROC-01:in_${LAG_AUDIO_SRC}_${MIC_CHANNEL}"
   jack_connect \
       "$PIPEPROC:out_${LAG_AUDIO_SINK}_1" \
       "alsa-out-$i:playback_1"
   jack_connect \
       "$PIPEPROC:out_${LAG_AUDIO_SINK}_2" \
       "alsa-out-$i:playback_2"
done

echo "Running ..."

if [ -z "$SERVICE" ] ;
then
    echo "Press enter when done ..."
    read user_input
else
    wait
fi

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
