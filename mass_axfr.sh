#!/bin/bash


function usage() {
    echo "Usage: "$0" <domain_file>"
    if [ -n "$1" ] ; then
		echo "Error: "$1"!"
    fi
    exit
}

if [ ! $# -eq 1 ] ; then
    usage
fi

file=$1

if [ ! -f $file ] ; then
    usage "file not found"
fi

n=0
i=0
total=$(cat $file | wc -l | tr -d [:space:])
domains=$(cat $file)
echo "Trying $total zone transfer..."
echo

for d in $domains ; do
    i=$[$i+1]
	echo -ne " [$i/$total] $d\r"

    host=$(host -t NS $d)
    has_ns=$(echo $host | grep " name server ")

    if [ -n "$has_ns" ] ; then
        ns=$(echo $host | awk '{print $NF}' | sed "s/\.$//")

        for nnss in $(echo $ns) ; do
            axfr=`timeout 3 host -4 -W 1 -t axfr $d $nnss | grep ";; ANSWER SECTION:"`
            # axfr=`timeout 3 host -4 -W 1 -t ixfr $d $nnss | grep ";; ANSWER SECTION:"`
            if [ -n "$axfr" ] ; then
                printf "\033[0;32m [$i/$total] $d successful\033[0m"
                echo
                n=$[$n+1]
            fi
            # axfr=`host -4 -W 1 -t axfr $d $nnss`
            # failed=`echo "$axfr" | grep 'Transfer failed'`
            # timeout=`echo "$axfr" | grep 'timed out'`
            # error=`echo "$axfr" | grep 'communications error'`

            # if [ ! -n "$timeout" ] ; then
            #     if [ ! -n "$error" ] ; then
            #         if [ ! -n "$failed" ] ; then
            #             _print "$d successful!" GREEN
            #             echo
            #             n=$[$n+1]
            #         fi
            #     fi
            # fi
        done
    fi

	echo -ne "                                                                                                                                          \r"
done

echo
echo $n" zone transfer successful."
echo

exit




# #!/bin/bash



# NC='\033[0m'
# BLACK='0;30'
# RED='0;31'
# GREEN='0;32'
# ORANGE='0;33'
# BLUE='0;34'
# PURPLE='0;35'
# CYAN='0;36'
# LIGHT_GRAY='0;37'
# DARK_GRAY='1;30'
# LIGHT_RED='1;31'
# LIGHT_GREEN='1;32'
# YELLOW='1;33'
# LIGHT_BLUE='1;34'
# LIGHT_PURPLE='1;35'
# LIGHT_CYAN='1;36'
# WHITE='1;37'


# function _print() {
#     if [ -n "$2" ] ; then
# 		c=$2
#     else
# 		c='WHITE'
#     fi

# 	color="\033[${!c}m"
#     printf ${color}"$1"
#     printf ${NC}
# }

# dec2ip() {
#     local ip dec=$@
#     for e in {3..0}
#     do
#         ((octet = dec / (256 ** e) ))
#         ((dec -= octet * 256 ** e))
#         ip+=$delim$octet
#         delim=.
#     done
#     printf '%s\n' "$ip"
# }

# ip2dec() {
#     local a b c d ip=$@
#     IFS=. read -r a b c d <<< "$ip"
#     printf '%d\n' "$((a * 256 ** 3 + b * 256 ** 2 + c * 256 + d))"
# }



# function usage() {
#     echo "Usage: "$0" <domain_file>"
#     if [ -n "$1" ] ; then
# 		echo "Error: "$1"!"
#     fi
#     exit
# }

# if [ ! $# -eq 1 ] ; then
#     usage
# fi

# file=$1

# if [ ! -f $file ] ; then
#     usage "file not found"
# fi

# n=0
# domains=$(cat $file)
# #domains=$(cat $file | sort -fu)
# echo "Running "$(cat $file | wc -l)" zone transfer..."
# echo

# for d in $domains ; do
# 	echo -ne "                                                                                                                                          \r"
# 	echo -ne $d"\r"
#     axfr=`host -t axfr $d | grep 'Transfer failed' &`
#     if [ ! -n "$axfr" ] ; then
# 		_print "$d successful!" GREEN
# 		echo
# 		n=$[$n+1]
#     fi
#     # axfr=`fierce -tcptimeout 3 -dns $d -wordlist /tmp/null | grep 'Whoah, it worked' &`
#     # if [ -n "$axfr" ] ; then
# 	# 	_print "$d successful!" GREEN
# 	# 	echo
# 	# 	n=$[$n+1]
#     # fi
# done

# echo
# echo
# echo $n" zone transfer performed."
# echo

# exit
