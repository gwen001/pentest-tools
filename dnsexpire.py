#!/usr/bin/python3.5

# I don't believe in license.
# You can do whatever you want with this program.

import os
import sys
import re
import socket
# import whois
import pythonwhois
import subprocess
import argparse
import tldextract
from colored import fg, bg, attr
from datetime import datetime
from threading import Thread
from queue import Queue
from multiprocessing.dummy import Pool


def banner():
	print("""
              _                           _                            
           __| |_ __  ___  _____  ___ __ (_)_ __ ___       _ __  _   _ 
          / _` | '_ \/ __|/ _ \ \/ / '_ \| | '__/ _ \     | '_ \| | | |
         | (_| | | | \__ \  __/>  <| |_) | | | |  __/  _  | |_) | |_| |
          \__,_|_| |_|___/\___/_/\_\ .__/|_|_|  \___| (_) | .__/ \__, |
                                   |_|                    |_|    |___/ 

                                by @gwendallecoguic

""")
	pass

banner()


ALERT_LIMIT = 30

parser = argparse.ArgumentParser()
parser.add_argument( "-a","--all",help="also test dead hosts and non alias", action="store_true" )
parser.add_argument( "-o","--host",help="set host, can be a file or single host" )
parser.add_argument( "-t","--threads",help="threads, default 10" )
parser.add_argument( "-v","--verbose",help="display output, can be: 0=everything, 1=only alias, 2=only possible vulnerable, default 1" )
parser.parse_args()
args = parser.parse_args()

if args.threads:
    _threads = int(args.threads)
else:
    _threads = 10

if args.verbose:
    _verbose = int(args.verbose)
else:
    _verbose = 1

if args.all:
    _testall = True
else:
    _testall = False

t_hosts = []
if args.host:
    if os.path.isfile(args.host):
        fp = open( args.host, 'r' )
        t_hosts = fp.read().strip().split("\n")
        fp.close()
    else:
        t_hosts = [args.host]

n_host = len(t_hosts)

if not n_host:
    parser.error( 'hosts list missing' )

sys.stdout.write( '%s[+] %d hosts loaded: %s%s\n' % (fg('green'),n_host,args.host,attr(0)) )
sys.stdout.write( '[+] resolving...\n\n' )


def resolve( host ):
    try:
        cmd = 'host ' + host
        # print(cmd)
        output = subprocess.check_output( cmd, stderr=subprocess.STDOUT, shell=True ).decode('utf-8')
        # print( output )
    except Exception as e:
        # sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
        output = ''

    return output


def getDomain( host ):
    t_host_parse = tldextract.extract( host )
    return t_host_parse.domain + '.' + t_host_parse.suffix


def getWhois( domain ):
    if not domain in t_whois_history:
        try:
            w = pythonwhois.get_whois( domain )
            # w = whois.whois( domain )
            t_whois_history[ domain ] = w
        except Exception as e:
            sys.stdout.write( "%s[-] error occurred: %s (%s)%s\n" % (fg('red'),e,domain,attr(0)) )
            return False

    return t_whois_history[domain]


def getExpirationDate( domain ):
    whois = getWhois( domain )
    # print(type(whois))
    
    if not type(whois) is bool and 'expiration_date' in whois:
        # if type(whois.expiration_date) is list:
            # return whois.expiration_date[0]
        # else:
            # return whois.expiration_date
        if type(whois['expiration_date']) is list:
            return whois['expiration_date'][0]
        else:
            return whois['expiration_date']
        return False
    else:
        return False


def getColor( expiration_date ):
    # expiration_date = datetime(2019, 12, 29, 6, 56, 55)
    timedelta = expiration_date - datetime.now()
    # print(timedelta)

    if timedelta.days < -1: # to avoid false positive from smart whois who always return the current date
        return 'light_red'
    elif timedelta.days < ALERT_LIMIT:
        return 'light_yellow'
    else:
        return 'light_green'


def printExpirationDate( domain ):
    expiration_date = getExpirationDate( domain )
    # print(type(expiration_date))

    if type(expiration_date) is datetime:
        color = getColor( expiration_date )
        if color == 'light_red':
            alert = 'TRY TAKEOVER!!'
        elif color == 'light_yellow':
            alert = 'WARNING!'
        else:
            alert = ''
        return '%s%s %s%s\n' % (fg(color),expiration_date,alert,attr(0))
    else:
        return '%serror%s\n' % (fg('red'),attr(0))


def dnsexpire( host ):
    sys.stdout.write( 'progress: %d/%d\r' %  (t_multiproc['n_current'],t_multiproc['n_total']) )
    t_multiproc['n_current'] = t_multiproc['n_current'] + 1
    output = ''

    resolution = resolve( host )
    if resolution == '':
        is_alias = False
        if not _testall:
            if not _verbose:
                sys.stdout.write( '%s%s doesn\'t resolve%s\n' % (fg('dark_gray'),host,attr(0)) )
            return
    else:
        is_alias = re.findall( r'(.*) is an alias for (.*)\.', resolution );
        # print(is_alias)
    
    if not _testall and not is_alias:
        if not _verbose:
            sys.stdout.write( '%s%s is not an alias%s\n' % (fg('dark_gray'),host,attr(0)) )
        return

    if _testall:
        domain = getDomain( host )
        output = output + "%s -> %s -> " % (host,domain)
        output = output + printExpirationDate( domain )

    if is_alias:
        for alias in is_alias:
            domain = getDomain( alias[1] )
            output = output + ("%s is an alias for %s -> %s -> " % (alias[0],alias[1],domain))
            output = output + printExpirationDate( domain )

    if _verbose < 2 or ('WARNING' in output or 'TAKEOVER' in output): # remove the "progress:" text
        sys.stdout.write( '%s\n%s' % (' '.rjust(100,' '),output) )
    
    if not _testall:
        sys.stdout.write( '\n' )


def doWork():
    while True:
        host = q.get()
        dnsexpire( host )
        q.task_done()



t_whois_history = {}
t_multiproc = {
    'n_current': 0,
    'n_total': n_host
}

q = Queue( _threads*2 )

for i in range(_threads):
    t = Thread( target=doWork )
    t.daemon = True
    t.start()

try:
    for host in t_hosts:
        q.put( host )
    q.join()
except KeyboardInterrupt:
    sys.exit(1)


sys.stdout.write( '\n%s[+] finished%s\n' % (fg('green'),attr(0)) )

exit()

