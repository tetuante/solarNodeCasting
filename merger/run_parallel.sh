#!/bin/bash

stations = (dh3, dh4, dh5, dh10, dh11, dh9, dh2, dh1, ap6, ap1, ap3, ap5, ap4, ap7, dh6, dh7, dh8)

for station in "$(stations[@])";
do
    python3 merger.py $station &
done
