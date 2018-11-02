#!/bin/bash


source myutils.sh


function usage() {
    echo "Usage: "$0" <domain_file>"
    if [ -n "$1" ] ; then
		echo "Error: "$1"!"
    fi
    exit
}

if [ ! $# -eq 1 ] ; then
    usage
fi

file=$1

if [ ! -f $file ] ; then
    usage "file not found"
fi

n=0
domains=$(cat $file)
#domains=$(cat $file | sort -fu)
echo "Running "$(cat $file | wc -l)" zone transfer..."
echo

for d in $domains ; do
	echo -ne $d"\r"
    axfr=`fierce -tcptimeout 3 -dns $d -wordlist /tmp/null | grep 'Whoah, it worked' &`
    #axfr=`dnsrecon -t axfr -d $d | grep 'Zone Transfer was successful' &`
    if [ -n "$axfr" ] ; then
		_print "$d successful!" GREEN
		echo
		n=$[$n+1]
    fi
done

echo
echo
echo $n" zone transfer performed."
echo

exit
