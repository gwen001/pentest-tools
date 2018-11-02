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
    tmp=`nmap -sP $ip"."$i | grep -B 1 'Host is up' |grep 'scan report' |cut -d ' ' -f 5`
    if [ -n "$tmp" ] ; then
	echo $tmp
	n=$[$n+1]
    fi
done

echo
echo $n" hosts are up."
exit
