#!/bin/bash


source myutils.sh


function usage() {
    echo "Usage: "$0" <url> <wordlist>"
    if [ -n "$1" ] ; then
	echo "Error: "$1"!"
    fi
    exit
}


function test() {
  local url=$1
  local wordlist=$2
  
  for w in $(cat $2) ; do
    read -t 0.1 -s -r -n 1

    if [ "$REPLY" = "n" ] ; then
	echo
	echo "Skipping directory..."
	return
    fi
    
    ww=`echo $w | tr "/" "-"`
    current=$url"/"$ww
     echo
    _print "Testing: "$current
    res=`davtest -url $current 2>/dev/null`
    found=`echo $res | grep SUCCEED | wc -w`
     
    if [ ! $found -eq 0 ] ; then
      _print " FOUND!" RED
      test $current $wordlist
    fi

  done
}


if [ ! $# -eq 2 ] ; then
    usage
fi

url=$1

wordlist=$2
if ! [ -f $wordlist ] ; then
    usage "wordlist not found"
fi


url="${url%"${url##*[![:space:]]}"}"
url="${url%"${url##*[!/]}"}"
test $url $wordlist
echo
echo

exit
