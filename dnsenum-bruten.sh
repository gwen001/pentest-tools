#!/bin/bash

function usage() {
    echo "Usage: "$0" <prefix> <suffix> [<dns_server>]"
    if [ -n "$1" ] ; then
	    echo "Error: "$1"!"
    fi
    exit
}

if [ $# -lt 2 ] || [ $# -gt 3 ] ; then
    usage
fi

prefix=$1
suffix=$2
dnsserver=""
n=0

if [ $# -eq 3 ] ; then
    dnsserver=$3
fi

for i in $(seq 0 9) ; do
    echo $prefix"0"$i$suffix
    tmp=`host $prefix"0"$i$suffix $dnsserver |grep "has address" |cut -d ' ' -f 1,4`
    if [ -n "$tmp" ] ; then
		echo $tmp
		n=$[$n+1]
    fi
done

for i in $(seq 1 100) ; do
    echo $prefix$i$suffix
    tmp=`host $prefix$i$suffix $dnsserver |grep "has address" |cut -d ' ' -f 1,4`
    if [ -n "$tmp" ] ; then
		echo $tmp
		n=$[$n+1]
    fi
done

echo
echo $n" sub domains found."
exit
