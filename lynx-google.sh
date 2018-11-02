#!/bin/bash


function usage() {
    echo "Usage: "$0" <file>"
    if [ -n "$1" ] ; then
		echo "Error: "$1"!"
    fi
    exit
}


if [ $# -lt 1 ] || [ $# -gt 2 ] ; then
    usage
fi

file=$1

if ! [ -f $file ] ; then
	usage "File not found"
fi

if [ $# -eq 2 ] ; then 
    remove_args=1
else
    remove_args=0
fi

tmp='/tmp/'$(date +%s)
echo $tmp

cat /home/gwen/Bureau/p | egrep "\s[0-9]+\. https?://" > $tmp

if [ $remove_args -eq 1 ] ; then 
    cat $tmp | awk -F 'http' '{s="";for(i=3;i<=NF;i++) s = s $i " "; print "http"s}' | awk -F '?' '{print $1}' | awk -F '&' '{print $1}' | awk -F '+' '{print $1}' | sort -fu | grep -v 'https://www.google'
else
    cat $tmp | awk -F 'http' '{s="";for(i=3;i<=NF;i++) s = s $i " "; print "http"s}' | sort -fu | grep -v 'https://www.google'
fi
