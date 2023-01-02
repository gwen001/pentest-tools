#!/bin/bash


function usage() {
    echo "Usage: "$0" <(sub)domain>"
    if [ -n "$1" ] ; then
		echo "Error: "$1"!"
    fi
    exit
}

if [ ! $# -eq 1 ] ; then
    usage
fi


t_types=("*" "A" "A6" "AAAA" "AFSDB" "AMTRELAY" "APL" "ATMA" "AVC" "AXFR" "CAA" "CDNSKEY" "CDS" "CERT" "CNAME" "CSYNC" "DHCID" "DLV" "DNAME" "DNSKEY" "DOA" "DS" "EID" "EUI48" "EUI64" "GID" "GPOS" "HINFO" "HIP" "IPSECKEY" "ISDN" "IXFR" "KEY" "KX" "L32" "L64" "LOC" "LP" "MAILA" "MAILB" "MB" "MD" "MF" "MG" "MINFO" "MR" "MX" "NAPTR" "NID" "NIMLOC" "NINFO" "NS" "NSAP" "NSAP-PTR" "NSEC" "NSEC3" "NSEC3PARAM" "NULL" "NXT" "OPENPGPKEY" "OPT" "PTR" "PX" "RKEY" "RP" "RRSIG" "RT" "SIG" "SINK" "SMIMEA" "SOA" "SPF" "SRV" "SSHFP" "TA" "TALINK" "TKEY" "TLSA" "TSIG" "TXT" "UID" "UINFO" "UNSPEC" "URI" "WKS" "X25" "ZONEMD")

n=0
i=0
total=${#t_types[@]}
domain=$1
echo "Trying $total types... $domain"
echo

host=$(host -t NS $domain)
# echo "$host"
has_ns=$(echo "$host" | grep " name server ")

if [ -n "$has_ns" ] ; then
    ns=$(echo "$host" | awk '{print $NF}' | sed "s/\.$//")
    # echo "$ns"

    for nnss in $(echo "$ns") ; do
        for type in ${t_types[@]} ; do
            rq=`timeout 3 host -4 -W 1 -t "$type" $domain $nnss 2>&1`
            # echo "$rq"

            fail=$(echo "$rq" | egrep "connection timed out|$domain has no|host: invalid type:|FORMERR|REFUSED|SERVFAIL|NOTAUTH|NXDOMAIN")
            if [ ! -n "$fail" ] ; then
                echo "-----------------------------"
                echo "$domain -> $nnss -> $type"
                echo "-----------------------------"
                echo "$rq"
                echo
                echo
            fi

        done
    done
fi

