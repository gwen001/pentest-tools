#!/bin/bash


bash_source=$(ls -ld ${BASH_SOURCE[0]})
source_dir=$(echo $bash_source | awk -F "-> " '{print $2}')
if [ ${#source_dir} -gt 0 ] ; then
  source_dir=$(dirname $source_dir)"/"
else
  source_dir=$(dirname $(echo $bash_source | awk -F " " '{print $(NF)}'))"/"
fi

source $source_dir"myutils.sh"
source $source_dir"s3-buckets-func.sh"


function usage() {
    echo "Usage: "$0" <bucket>"
    if [ -n "$1" ] ; then
	echo "Error: "$1"!"
    fi
    exit
}


if [ ! $# -eq 1 ] ; then
    usage
fi

bucket=$1

f="/tmp/s3bf-"$(date +%s)
`echo $(date) > $f`

test $bucket

rm $f
exit
