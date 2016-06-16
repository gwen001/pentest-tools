#!/bin/bash


source myutils.sh


function usage() {
    echo "Usage: "$0" <ip start> <ip end> <wordlist> [<port>] [<force ssl>]"
    if [ -n "$1" ] ; then
        echo "Error: "$1"!"
    fi
    exit
}

function testip() {
    i=$1
    ip=$2

    # 0.0.0.0/0.255.255.255 , 10.0.0.0/10.255.255.255 , 172.16.0.0/172.31.255.255 , 192.168.0.0/192.168.255.255
    if ( [ $i -ge 0 ] && [ $i -le 16777215 ] ) || ( [ $i -ge 167772160 ] && [ $i -le 184549375 ] ) || ( [ $i -ge 2886729728 ] && [ $i -le 2887778303 ] ) || ( [ $i -ge 3232235520 ] && [ $i -le 3232301055 ] ) ; then
	echo 0
	return
    fi
    
    ip2=$(echo $ip | tr '.' ' ')
    for n in $ip2 ; do
	if [ $n -eq 0 ] || [ $n -eq 254 ] || [ $n -eq 255 ] ; then
	    echo 0
	    return
	fi
    done
    
    echo 1
    return
}


if [ $# -lt 3 ] || [ $# -gt 5 ] ; then
    usage
fi

wordlist=$3

if [ ! -f $wordlist ] ; then
        usage "File not found!"
fi

if [ $# -ge 4 ] ; then
    port=$4
else
    port=80,443
fi

tport=$(echo $port|tr ',' " ")

if [ $# -eq 5 ] ; then
    ssl=1
else
    ssl=0
fi

start=$1
start_n=`ip2dec $start`
end=$2
end_n=`ip2dec $end`

if [ $end_n -lt $start_n ] ; then
    tmp=$start
    start=$end
    end=$tmp
    tmp=$start_n
    start_n=$end_n
    end_n=$tmp
fi

i=$(( $start_n - 1 ))
coption="-s --connect-timeout 2"

while [ $i -lt $end_n ] ; do
    i=$(( $i + 1 ))
    ip=`dec2ip $i`
    isvalid=$(testip $i $ip)
    #isvalid=1
    
    if [ $isvalid -eq 0 ] ; then
	continue
    fi
        
    for p in $tport ; do
	if [ $ssl -eq 0 ] && [ ! $p -eq 443 ] ; then
	    proto="http"
	    co=$coption
	else
	    proto="https"
	    co="$coption --insecure"
	fi
	
	url="$proto://$ip:$p"
	output=`curl $co $url`
	res=`echo $output | grep 'html'`
	echo "Connecting: $url"
	
	if [ ! -n "$res" ] ; then
	    _print "Skipping..."
	    echo
	else
            for w in $(cat $wordlist) ; do	    
		url="http://$ip:$p/$w"
		output=`curl $co -I $url`
		res=`echo $output | grep 'HTTP/1.1 200 OK'`
		_print "Testing: $url"
		
		if [ -n "$res" ] ; then
		    _print " FOUND!" GREEN
		fi
		
		echo
	    done
	fi
    done
    
    echo
done
  

exit

