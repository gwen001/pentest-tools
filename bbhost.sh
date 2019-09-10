#!/bin/bash

if [ $# -lt 1 ] ; then
    input="hosts.txt"
else
    input=$1
fi
#echo $input

if [ $# -gt 1 ] ; then
    output=$2
else
    output="tmp_hosts.txt"
fi
#echo $output

parallel -j 10 "host " :::: $input | tee $output
exit;

for h in $(cat $input) ; do
    host $h | tee -a $output
    echo "" | tee -a $output
done
