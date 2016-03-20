#!/bin/bash

function usage() {
    echo "Usage: "$0" <arpa_file> [domain]"
    if [ -n "$1" ] ; then
	echo "Error: "$1"!"
    fi
    exit
}

if [ $# -lt 1 ] || [ $# -gt 2 ] ; then
    usage
fi

file=$1

if [ ! -f $file ] ; then
    usage "file not found"
fi

arpa=`cat $file | grep arpa`

if [ $# -eq 2 ] ; then
    domain=$2
    arpa=`cat $file | grep $domain`
fi

#echo $arpa
arpa=$(echo $arpa | sed "s/ /YYY/g")
#echo $arpa
arpa=$(echo $arpa | sed "s/\.YYY/\.WWW/g")
#echo $arpa
arpa=$(echo $arpa | sed "s/WWW/ /g")
#echo $arpa

for a in $arpa ; do
    str=$(echo "$a" | awk -F "YYY" '{print $1}')
    ip=$(echo "$str" | awk -F "." '{print $4"."$3"."$2"."$1}')
    #echo $ip
    dom=$(echo "$a" | awk -F "YYY" '{print $2}')
    dom=${dom:0:-1}
    #echo $dom
    echo $ip" "$dom
done

exit
