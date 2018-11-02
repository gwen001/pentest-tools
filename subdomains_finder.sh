#!/bin/bash


function usage() {
    echo "Usage: "$0" <domain> [<method (bzhs)>]"
    if [ -n "$1" ] ; then
        echo "Error: "$1"!"
    fi
    exit
}


if [ $# -lt 1 ] || [ $# -gt 3 ] ; then
    usage
fi

if [ $# -eq 2 ] ; then
    method=$2
else
    method="bzhs"
fi

domain=$1
output="/tmp/"$domain".txt"
#echo "" > $output
tmpfile="/tmp/"$domain".tmp"
#echo "" > $tmpfile
echo "Processing "$domain
echo

if $( echo $method | grep --quiet 'h' ) ; then
    echo "TheHarvester..."
    th_limit=1000
    th_se="all"
    harvest=$(theharvester -l $th_limit -b $th_se -d $domain)
    harv=$(echo $harvest | grep -E '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | grep $domain)
    echo $harv | tr " " "\n" | tr ":" "\n" | grep $domain | grep -v "@" >> $tmpfile
fi

if $( echo $method | grep --quiet 'z' ) ; then
    echo "dnsrecon (axfr)..."
    axfr=$(dnsrecon -d $domain -t axfr | grep $domain | egrep "A|CNAME" | awk '{print $3}')
    echo $axfr | tr " " "\n" >> $tmpfile
fi

if $( echo $method | grep --quiet 'b' ) ; then
    echo "dnsrecon (brt)..."
    brt_src="/opt/SecLists/Discovery/DNS/subdomains-top1mil-20000.txt"
    #brt_src="/opt/SecLists/Discovery/DNS/namelist.txt"
    brt=$(dnsrecon -d $domain -t brt -D $brt_src | grep $domain | egrep "A|CNAME" | awk '{print $3}')
    echo $brt | tr " " "\n" >> $tmpfile
fi

if $( echo $method | grep --quiet 's' ) ; then
    echo "subthreat..."
    cmd_sub=$(subthreat $domain | grep -iv "error")
    echo $cmd_sub | tr " " "\n" >> $tmpfile
fi

cat $tmpfile | sort -fu > $output
rm $tmpfile
n=$(wc -l $output)
#n=$[$n-1]
echo
echo $n" subdomains found!"

exit
