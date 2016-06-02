#!/bin/bash


source myutils.sh


t_command="VRFY RCPT EXPN";

function usage() {
    echo "Usage: "$0" <ip file>"
    if [ -n "$1" ] ; then
	echo "Error: "$1"!"
    fi
    exit
}

if [ ! $# -eq 1 ] ; then
    usage
fi

src=$1
if [ ! -f $src ] ; then
  usage "ip file not found!"
fi

for ip in $(cat $src) ; do
  for c in $t_command ; do
    output=`smtp-user-enum -M $c -u root -t $ip`
    res=`echo $output | egrep -o "[0-9]+ results" | cut -d ' ' -f 1`
    #echo $res
    _print "$ip -> $c ($res)"
    
    if [ ! $res -eq 0 ] ; then
       _print " VULNERABLE!" RED
    fi
    
    echo
  done
done

exit
