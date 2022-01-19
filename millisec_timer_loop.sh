# WESmith 01/19/22 print out streaming milliseconds to
# the terminal. This is a potential way to measure latency
# in time-stamped video streaming from a different source.

#!/bin/bash

read -p "Enter the number of times to stream the time (H:M:S.ms): " n

for i in $(seq 1 $n); do

  date +"%T.%3N"; 

done