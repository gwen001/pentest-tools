#!/bin/bash

target_dir=$1
script_dir=$(dirname "$(readlink -f "$0")")

cat $script_dir"/apk-regexp.txt" | while read -r r; do
	title=`echo "$r" | awk -F ";;" '{print $1}'`
	echo "[+] $title"
	reg=`echo "$r" | awk -F ";;" '{print $2}'`
	escape_reg=$reg
	escape_reg=$(echo $escape_reg | sed "s/\"/\\\\\"/g")
	echo "-> $escape_reg"
	egrep --color -ri "$escape_reg" $target_dir
	echo
	echo
done
