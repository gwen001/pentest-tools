#!/bin/bash

f_payload=$1
f_url=$2
rand1=$(tr -dc 'A-HJ-NP-Za-km-z2-9' < /dev/urandom | dd bs=12 count=1 status=none)
rand2=$(tr -dc 'A-HJ-NP-Za-km-z2-9' < /dev/urandom | dd bs=12 count=1 status=none)
tmpfile="/tmp/$rand1"
echo "tmpfile: $tmpfile"
subdomain=$rand2
echo "subdomain: $subdomain"

if [ $# -gt 2 ] ; then
	verbose=$3
else
	verbose=0
fi

if [ $# -gt 3 ] ; then
	cookies=$4
else
	cookies=''
fi


cp $f_payload $tmpfile
sed -i "s/__RANDOM_STR__/$subdomain/g" $tmpfile
cmd='testxss --cookies "'$cookies'"  --no-color --threads 5 --payload $tmpfile --prefix --suffix --single "'$f_url'" --inject GP --gpg --encode --wish "QSDFGHJKLMNBVCXWAZERTYPOIU" --verbose '$verbose
echo $cmd
eval $cmd


sleep 5s
#rm $tmpfile
