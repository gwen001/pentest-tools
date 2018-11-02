#!/bin/bash


function usage() {
    echo "Usage: "$0" <ip> <port start> <port end> [<udp>]"
    if [ -n "$1" ] ; then
	echo "Error: "$1"!"
    fi
    exit
}

if [ $# -lt 3 ] || [ $# -gt 4 ] ; then
    usage
fi

ip=$1
start=$2
end=$3
options="-n -v -z -w 1"

if [ $# -eq 4 ] ; then
    options=$options" -u"
fi

if [ $end -lt $start ] ; then
    tmp=$start
    start=$end
    end=$tmp
fi

i=0
test_found=0
test_limit=20
test_rate=10

for port in $(seq $start $end); do
	if [ $i -lt $test_limit ] ; then
    	tmp=$(nc $options $ip $port 2>&1 | egrep "\) open|\] succeeded" &)
    	if [ -n "$tmp" ] ; then
	    	echo $tmp
			test_found=$[$test_found+1]
    	fi
	    if [ $test_found -ge $test_rate ] ; then
	    	echo "Too much success, exiting!"
	    	exit
	    fi 
    else
    	nc $options $ip $port 2>&1 | egrep "\) open|\] succeeded" &
    fi
	i=$[$i+1]
done

exit
