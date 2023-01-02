#!/usr/bin/python3

import os
import sys
import re
import argparse
import urllib.parse
from colored import fg, bg, attr


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

# based on HUNT from BugCrowd
# https://github.com/bugcrowd/HUNT/blob/master/Burp/conf/issues.json
t_vulns = {
    'debug': {
        'color': 'purple_1b',
        'params': [
            "access",
            "admin",
            "dbg",
            "debug",
            "edit",
            "grant",
            "test",
            "alter",
            "clone",
            "create",
            "delete",
            "disable",
            "enable",
            "exec",
            "execute",
            "load",
            "make",
            "modify",
            "rename",
            "reset",
            "shell",
            "toggle",
            "adm",
            "root",
            "cfg",
            "config",
        ]
    },
    'idor': {
        'color': 'magenta_1',
        'params': [
            "id",
            "user",
            "account",
            "number",
            "order",
            "no",
            "doc",
            "key",
            "email",
            "group",
            "profile",
            "edit",
            "report"
        ]
    },
    'lfi': {
        'color': 'yellow',
        'params': [
            "dir",
            "directory",
            "display",
            "dl",
            "doc",
            "docs",
            "document",
            "documents",
            "download",
            "file",
            "filename",
            "files",
            "folder",
            "folders",
            "image",
            "images",
            "img",
            "include",
            "includes",
            "list",
            "load",
            "locale",
            "locales",
            "location",
            "path",
            "pdf",
            "pdffilename",
            "pg",
            "php_path",
            "read",
            "retrieve",
            "root",
            "style",
            "styles",
            "template",
            "view",
            "views",
        ]
    },
    'sqli': {
        'color': 'light_green',
        'params': [
            "code",
            "column",
            "columns",
            "count",
            "delete",
            "fetch",
            "field",
            "filter",
            "filters",
            "from",
            "id",
            "ids",
            "input",
            "key",
            "keys",
            "keyword",
            "keywords",
            "name",
            "names",
            "number",
            "order",
            "param",
            "params",
            "process",
            "query",
            "report",
            "result",
            "results",
            "role",
            "roles",
            "row",
            "rows",
            "search",
            "sel",
            "select",
            "set",
            "sleep",
            "sort",
            "string",
            "table",
            "tables",
            "update",
            "user",
            "view",
            "where",
        ]
    },
    'ssrf': {
        'color': 'salmon_1',
        'params': [
            "access",
            "adm",
            "admin",
            "alter",
            "callback",
            "cfg",
            "clone",
            "continue",
            "create",
            "data",
            "datas",
            "dbg",
            "debug",
            "delete",
            "dest",
            "dir",
            "disable",
            "domain",
            "domains",
            "edit",
            "enable",
            "exec",
            "execute",
            "feed",
            "feeds",
            "grant",
            "host",
            "html",
            "load",
            "make",
            "modify",
            "navigation",
            "next",
            "open",
            "out",
            "page",
            "pages",
            "path",
            "port",
            "ports",
            "redirect",
            "reference",
            "rename",
            "reset",
            "return",
            "root",
            "shell",
            "show",
            "site",
            "test",
            "to",
            "toggle",
            "uri",
            "url",
            "val",
            "validate",
            "value",
            "values",
            "view",
            "window",
        ]
    },
    'ssti': {
        'color': 'cyan',
        'params': [
            "template",
            "preview",
            "id",
            "view",
            "activity",
            "name",
            "content",
            "redirect"
        ]
    },
    'rce': {
        'color': 'light_red',
        'params': [
            "daemon",
            "upload",
            "dir",
            "execute",
            "download",
            "log",
            "ip",
            "cli",
            "cgi",
            "cmd",
            "eval",
            "exec",
            "system",
            "proc",
            "process",
        ]
    },
    'openredirect': {
        'color': 'light_red',
        'params': [
            "url",
            "uri",
            "callback",
            "next",
            "return",
            "rurl",
            "returnurl",
            "returnuri",
            "return_url",
            "return_uri",
            "page",
            "r",
            "redirect",
            "redirect_url",
            "redirect_uri",
            "redirecturl",
            "redirecturi",
            "redir",
            "redir_url",
            "redir_uri",
            "redirurl",
            "rediruri",
            "forward",
            "dest",
            "path",
            "continue",
            "window",
            "to",
            "out",
            "view",
            "dir",
            "show",
            "navigation",
            "open",
            "file",
            "val",
            "validate",
            "domain",
            "feed",
            "host",
            "port",
            "data",
            "reference",
            "site",
            "html",
            "location",
        ]
    },
}

parser = argparse.ArgumentParser()
# parser.add_argument( 'url', metavar='url', help='an integer for the accumulator')
parser.add_argument( "-a","--add",help="extensions to add the default ignore list" )
parser.add_argument( "-c","--nocolor",help="disable colored output", action="store_true" )
parser.add_argument( "-r","--remove",help="extensions to remove from the default ignore list" )
parser.add_argument( "-i","--ignore",help="set extensions to ignore" )
parser.add_argument( "-k","--keep",help="set extensions to keep" )
parser.add_argument( "-p","--params",help="keep only urls with parameters", action="store_true" )
parser.add_argument( "-u","--urls",help="set url list" )
parser.add_argument( "-t","--type",help="type of issue you ant to display, default: all" )
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

show_issue = []
if args.type:
    tmp = args.type.split(',')
    for issue in tmp:
        if not issue in t_vulns.keys():
            parser.error( "error: %s vuln type not found" % issue )
        show_issue.append( issue )
else:
    show_issue = ['all']

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


def check_params( t_urlparse ):
    if args.params and not len(t_urlparse.query):
        return False
    return True


def check_noextension( t_urlparse ):
    if not len(t_urlparse.path):
        if not 'none' in t_extension_keep:
            # t_filtered.append( url )
            return False
            # continue
    if not '.' in t_urlparse.path:
        if not 'none' in t_extension_keep:
            # t_filtered.append( url )
            return False
            # continue
    ext = t_urlparse.path.split('.')[-1]
    if not len(ext):
        if not 'none' in t_extension_keep:
            # t_filtered.append( url )
            return False
            # continue

    return True

def check_extension( t_urlparse ):
    ext = t_urlparse.path.split('.')[-1].lower()
    if not ext in t_extension_ignore or ext in t_extension_keep:
        return True
    return False

def check_issue( url, show_issue):

    new_url = url

    if show_issue[0] == 'all':
        new_url = re.sub( '[\?&]([a-z0-9_\-\.\[\]]+)=', lambda m: '\x1b[1;32m{}\x1b[0m'.format(m.group()), new_url, flags=re.I )
        # new_url = re.sub( '&([a-z0-9_\-\.\[\]]+)=', lambda m: '\x1b[1;32m{}\x1b[0m'.format(m.group()), new_url, flags=re.I )
        if args.nocolor:
            return url
        else:
            return new_url

    for issue in show_issue:
        for param in t_vulns[issue]['params']:
            new_url = re.sub( '[\?&]'+param+'=', lambda m: '\x1b[1;32m{}\x1b[0m'.format(m.group()), new_url, flags=re.I )
            # new_url = re.sub( '&'+param+'=', lambda m: '\x1b[1;32m{}\x1b[0m'.format(m.group()), new_url, flags=re.I )

    if new_url == url:
        return ''
    else:
        if args.nocolor:
            return url
        else:
            return new_url


for url in t_urls:

    url = url.strip()
    if not len(url):
        continue
    # print(url)

    t_urlparse = urllib.parse.urlparse( url )
    # print( t_urlparse )

    if not check_params(t_urlparse):
        # print('no params failed')
        continue

    if not check_noextension(t_urlparse):
        # print('no extension failed')
        continue

    if not check_extension(t_urlparse):
        # print('extension failed')
        continue

    url = check_issue(url,show_issue)
    if not len(url):
        # print('issue failed')
        continue

    print( url )
