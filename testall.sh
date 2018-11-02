#!/bin/bash


function usage() {
    echo "Usage: "$0" <url> [<rce:0|1>] [<lfi:0|1>] [<ti:0|1>] [<xss:0|1>] [<sqli:0|1>] [<cookies>]"
    if [ -n "$1" ] ; then
	echo "Error: "$1"!"
    fi
    exit
}

if [ $# -lt 1 ] || [ $# -gt 7 ] ; then
    usage
fi


url=$1
color=1
verbose=2
sqlmap_smart=0


if [ $# -gt 1 ] ; then
	rce=$2
else
	rce=1
fi

if [ $# -gt 2 ] ; then
	lfi=$3
else
	lfi=1
fi

if [ $# -gt 3 ] ; then
	ti=$4
else
	ti=1
fi

if [ $# -gt 4 ] ; then
	xss=$5
else
	xss=1
fi

if [ $# -gt 5 ] ; then
	sqli=$6
else
	sqli=1
fi

if [ $# -gt 6 ] ; then
	cookies=$7
else
	cookies=''
fi


# RCE
if [ $rce -eq 1 ] ; then
	echo
	echo "####################### TEST Remote Command Execution #######################"
	echo
	cmd='testrce /home/gwen/SecLists/mine/payload-rce-ping.txt "'$1'" 2 "'$cookies'"'
	echo $cmd
	eval $cmd
fi

# LFI
if [ $lfi -eq 1 ] ; then
	echo
	echo "####################### TEST Local File Inclusion #######################"
	echo
	cmd='testxss --cookies "'$cookies'" --verbose '$verbose' --inject GP --replace GP --gpg --threads 5 --payload /home/gwen/SecLists/mine/payload-lfi-short.txt --prefix --suffix --single "'$1'" --wish "root:[0x]:|\[boot loader"'
	if [ $color -eq 0 ] ; then
		cmd=$cmd" --no-color"
	fi
	echo $cmd
	eval $cmd
fi

# Template Injection
if [ $ti -eq 1 ] ; then
	echo
	echo "####################### TEST Template Injection #######################"
	echo
	cmd='testxss --cookies "'$cookies'" --verbose '$verbose' --inject GP --gpg --threads 5 --payload /home/gwen/SecLists/mine/payload-ti-short-25536.txt --prefix --suffix --single "'$1'" --wish "25536"'
	if [ $color -eq 0 ] ; then
		cmd=$cmd" --no-color"
	fi
	echo $cmd
	eval $cmd
fi

# XSS
if [ $xss -eq 1 ] ; then
	echo
	echo "####################### TEST Cross Site Scripting #######################"
	echo
	cmd='testxss --encode --cookies "'$cookies'" --verbose '$verbose' --gpg --threads 5 --phantom /usr/local/bin/phantomjs --payload /home/gwen/SecLists/mine/xss-mytop50.txt --prefix --suffix --sos --single "'$1'"'
	if [ $color -eq 0 ] ; then
		cmd=$cmd" --no-color"
	fi
	echo $cmd
	eval $cmd
fi

# SQL Injection
if [ $sqli -eq 1 ] ; then
	echo
	echo "####################### TEST SQL Injection #######################"
	echo
	cmd='sqlmap --cookie="'$cookies'" --threads=5 --random-agent --dbms=mysql --batch -u "'$1'"'
	if [ $sqlmap_smart -eq 1 ] ; then
		cmd=$cmd" --smart"
	fi
	echo $cmd
	eval $cmd
fi

echo
echo "####################### THE END #######################"
echo
