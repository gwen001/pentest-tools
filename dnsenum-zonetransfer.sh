#!/bin/bash

function usage() {
    echo "Usage: "$0" <domain>" 
    if [ -n "$1" ] ; then
	echo "Error: "$1"!"
    fi
    exit
}

if ! [ $# -eq 1 ] ; then
    usage
fi

domain=$1
n=0

for server in $(host -t ns $domain |cut -d ' ' -f 4) ; do
    tmp=`host -l $1 $server |grep 'has address' | tr "\n" "|"`
    if [ -n "$tmp" ] ; then
	echo $tmp | tr "|" "\n"
	n=1
    fi
done

if [ $n -eq 0 ] ; then
    echo "Zone transfer not possible!"
fi

exit
