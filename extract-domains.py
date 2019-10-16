#!/usr/bin/python2.7

# I don't believe in license.
# You can do whatever you want with this program.

import os
import sys
import argparse
import tldextract
from urlparse import urlparse


parser = argparse.ArgumentParser()
parser.add_argument( "-u","--urls",help="set urls list (required)" )
parser.add_argument( "-s","--sub",help="subdomains wanted", action="store_true" )
parser.parse_args()
args = parser.parse_args()

if not args.urls:
    parser.error( 'urls list is missing' )

if os.path.isfile(args.urls):
    fp = open( args.urls, 'r' )
    t_urls = fp.read().split("\n")
    fp.close()
else:
    t_urls = [args.urls]
# print(t_urls)

t_found = []

for url in t_urls:
    if not url.startswith( 'http' ):
        url = 'https://'+url
    
    t_url_parse = urlparse( url )
    # print( t_url_parse )
    
    if args.sub:
        found = t_url_parse.netloc
    else:
        t_host_parse = tldextract.extract( t_url_parse.netloc )
        # print( t_host_parse )
        found = t_host_parse.domain + '.' + t_host_parse.suffix
    
    if not found in t_found:
        t_found.append( found )

print( "\n".join(t_found) )
exit()
