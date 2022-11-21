#!/bin/bash

function usage() {
    echo "Usage: "$0" <ip> <start> <end>"
    if [ -n "$1" ] ; then
	echo "Error: "$1"!"
    fi
    exit
}

if ! [ $# -eq 3 ] ; then
    usage
fi

ip=$1
start=$2
end=$3
n=0

for i in $(seq $start $end); do
    tmp=`ping -t 3 -c 1 $ip"."$i | grep 'bytes from' | cut -d ' ' -f 4 | cut -d ':' -f1 &`
    if [ -n "$tmp" ] ; then
		echo $tmp
		n=$[$n+1]
    fi
done

echo
echo $n" hosts are up."
