#!/usr/bin/python3.5

# I don't believe in license.
# You can do whatever you want with this program.

import os
import sys
import argparse
import urllib.parse


t_urls = []
t_filtered = []
t_extension_keep = ['none']
t_extension_ignore = [
    'js','css',
    'ico','gif','jpg','jpeg','png','bmp','svg',
    'woff','woff2','ttf','eot',
    'mp3','mp4','wav','mpg','mpeg','avi','mov','wmv',
    'doc','docx','xls','xlsx','pdf',
    'zip','tar','7z','rar','tgz','gz',
    'exe','rtp'
]

parser = argparse.ArgumentParser()
# parser.add_argument( 'url', metavar='url', help='an integer for the accumulator')
parser.add_argument( "-a","--add",help="extensions to add the default ignore list" )
parser.add_argument( "-r","--remove",help="extensions to remove from the default ignore list" )
parser.add_argument( "-i","--ignore",help="set extensions to ignore" )
parser.add_argument( "-p","--params",help="keep only urls with parameters", action="store_true" )
parser.add_argument( "-k","--keep",help="set extensions to keep" )
parser.add_argument( "-u","--urls",help="set url list" )
parser.parse_args()
args = parser.parse_args()

if args.add:
    t_extension_ignore = t_extension_ignore + args.add.split(',')

if args.remove:
    for ext in args.remove.split(','):
        if ext in t_extension_keep:
            t_extension_ignore.remove( ext )

if args.ignore:
    t_extension_ignore = args.ignore.split(',')

if args.keep:
    t_extension_keep = t_extension_keep + args.keep.split(',')

if args.urls:
    try:
        fp = open( args.urls )
    except Exception as e:
        sys.stdout.write( 'Error: %s\n' % e )
        exit()
    else:
        t_urls = fp.read().split("\n")
        fp.close()
else:
    while True:
        try:
            url = input()
        except EOFError:
            break
        else:
            t_urls.append( url )

# print(t_extension_ignore)
# print(t_extension_keep)

for url in t_urls:
    t_urlparse = urllib.parse.urlparse( url )
    # print( t_urlparse )

    if args.params and not len(t_urlparse.query):
        continue

    if not len(t_urlparse.path):
        if 'none' in t_extension_keep:
            t_filtered.append( url )
        continue
    
    if not '.' in t_urlparse.path:
        if 'none' in t_extension_keep:
            t_filtered.append( url )
        continue
    
    ext = t_urlparse.path.split('.')[-1]
    # print(ext)
    if not len(ext):
        if 'none' in t_extension_keep:
            t_filtered.append( url )
        continue

    if not ext in t_extension_ignore or ext in t_extension_keep:
        t_filtered.append( url )

print( "\n".join(t_filtered) )
