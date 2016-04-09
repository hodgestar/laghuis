#!/bin/bash

echo "Sources"
echo "======="
echo
pactl list sources | grep -B 3 "Description: CM108 Audio"
echo

echo "Sinks"
echo "====="
echo
pactl list sinks | grep -B 3 "Description: CM108 Audio"
echo
