#!/bin/bash


NC='\033[0m'
BLACK='0;30'
RED='0;31'
GREEN='0;32'
ORANGE='0;33'
BLUE='0;34'
PURPLE='0;35'
CYAN='0;36'
LIGHT_GRAY='0;37'
DARK_GRAY='1;30'
LIGHT_RED='1;31'
LIGHT_GREEN='1;32'
YELLOW='1;33'
LIGHT_BLUE='1;34'
LIGHT_PURPLE='1;35'
LIGHT_CYAN='1;36'
WHITE='1;37'


function _print() {
    if [ -n "$2" ] ; then
		c=$2
    else
		c='WHITE'
    fi

	color="\033[${!c}m"
    printf ${color}"$1"
    printf ${NC}
}


function usage() {
    echo "Usage: "$0" <domain file>"
    if [ -n "$1" ] ; then
		echo "Error: "$1"!"
    fi
    exit
}


if ! [ $# -eq 1 ] ; then
    usage
fi

file=$1

if ! [ -f $file ] ; then
	usage "File not found"
fi

method="GET"
user_agent="User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.7.1"
url="https://www.google.fr/search?sourceid=chrome-psyapi2&ion=1&espv=2&ie=UTF-8&q=intitle%3A%22index%20of%22%20site%3A"
str="aucun document"
str="environ"

for d in $(cat $file) ; do
	u=${url}${d}
	#echo $u
	cmd="curl -i -s -k -L -X $method -H \"$user_agent\" $u | grep -i \"$str\""
	echo $cmd
	#exit
	go=$($cmd)
	echo $go
	if [ -n "$go" ] ; then
		color="GREEN"
	else
		color="DARK_GRAY"
	fi
	_print $d $color
	echo ""
	#wait 1
done

exit
