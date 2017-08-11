#!/bin/bash

function usage() {
    echo "Usage: "$0" <ip> <port> <wordlist> [<prefix>] [<suffix>]"
    if [ -n "$1" ] ; then
		echo "Error: "$1"!"
    fi
    exit
}

if [ $# -lt 3 ] || [ $# -gt 5 ] ; then
    usage
fi

ip=$1
port=$2
wordlist=$3

if ! [ -f $wordlist ] ; then
    usage "wordlist file not found"
fi

if [ $# -ge 4 ] ; then
    prefix=$4
else
    prefix=""
fi

if [ $# -eq 5 ] ; then
    suffix=$5
else
    suffix=""
fi

for w in $(cat $wordlist) ; do
	input=$prefix$w$suffix
	input=`echo $input | tr '[:lower:]' '[:upper:]'`
	echo $input
    echo $input | nc -nv $ip $port
done

exit;
