#!/usr/bin/python3.5

import os
import sys
import json
import argparse
import urllib.parse
from goop import goop
from functools import partial
from multiprocessing.dummy import Pool
from colored import fg, bg, attr

parser = argparse.ArgumentParser()
parser.add_argument( "-f","--file",help="source file that contains the dorks" )
parser.add_argument( "-t","--term",help="search term", action="append" )
parser.add_argument( "-d","--decode",help="urldecode the results", action="store_true" )
parser.add_argument( "-e","--endpage",help="search end page, default 50" )
parser.add_argument( "-s","--startpage",help="search start page, default 0" )
parser.add_argument( "-c","--fbcookie",help="your facebook cookie" )
parser.add_argument( "-o","--output",help="output file" )
parser.add_argument( "-n","--numbers-only",help="don't display the results but how many results where found", action="store_true" )

parser.parse_args()
args = parser.parse_args()

if args.startpage:
    start_page = int(args.startpage)
else:
    start_page = 0

if args.endpage:
    end_page = int(args.endpage)
else:
    end_page = 50

if args.fbcookie:
    fb_cookie = args.fbcookie
else:
    fb_cookie = os.getenv('FACEBOOK_COOKIE')
if not fb_cookie:
    parser.error( 'facebook cookie is missing' )

if args.file:
    if os.path.isfile(args.file):
        fp = open( args.file, 'r' )
        t_terms = fp.read().split('\n')
        fp.close()
    else:
        parser.error( '%s file not found' % args.file )
elif args.term:
    t_terms = args.term
else:
    parser.error( 'term is missing' )

if args.output:
    numbers_only = True
else:
    numbers_only = False

if args.numbers_only:
    numbers_only = True
else:
    numbers_only = False

if args.decode:
    urldecode = True
else:
    urldecode = False


def doMultiSearch( term, numbers_only, urldecode, page ):
    zero_result = 0
    for i in range(page-5,page-1):
        if i != page and i in page_history and page_history[i] == 0:
            zero_result = zero_result + 1

    if zero_result < 3:
        s_results = goop.search( term, fb_cookie, page, True )
        # print(s_results)
        # print(s_results)
        page_history[page] = len(s_results)
        if not numbers_only:
            for i in s_results:
                if urldecode:
                    print( urllib.parse.unquote(s_results[i]['url']) )
                else:
                    print( s_results[i]['url'] )
    else:
        for i in range(page,end_page):
            page_history[i] = 0 

for term in t_terms:
    page_history = {}

    pool = Pool( 5 )
    pool.map( partial(doMultiSearch,term,numbers_only,urldecode), range(start_page,end_page) )
    pool.close()
    pool.join()

    if numbers_only:
        n_results = sum( page_history.values() )
        if n_results:
            color = 'white'
        else:
            color = 'dark_gray'

        full_url = 'https://www.google.com/search?q=' + urllib.parse.quote(term)
        sys.stdout.write( '%s%s (%d)%s\n' % (fg(color),full_url,n_results,attr(0)) )
