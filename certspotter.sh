#!/bin/bash

curl -s https://certspotter.com/api/v0/certs?domain=$1 | jq -c '.[].dns_names' | grep -o '"[^"]\+"' | tr -d '"' | sort -fu;
