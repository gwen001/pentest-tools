#!/bin/bash


function usage() {
    echo "Usage: "$0" <ip>"
    if [ -n "$1" ] ; then
	echo "Error: "$1"!"
    fi
    exit
}

if [ ! $# -eq 1 ] ; then
    usage
fi

ip=$1

echo ">>>>>>>> finger <<<<<<<<"
finger -l root@$ip
echo

echo ">>>>>>>> rusers <<<<<<<<"
rusers -l $ip
echo

echo ">>>>>>>> showmount <<<<<<<<"
showmount -e $ip
echo
