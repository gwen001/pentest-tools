#!/usr/bin/python3.5

# I don't believe in license.
# You can do whatever you want with this program.

import os
import sys
import argparse
import xml.etree.ElementTree as ET
from colored import fg, bg, attr


def printTitle( title ):
    sys.stdout.write( '%s### %s ###%s\n\n' % (fg('cyan'),title,attr(0)) )

def readInfos( grep_term ):
    printTitle( 'INFOS' )

    sys.stdout.write( 'Package: %s\n' % root.attrib['package'] )

    if 'platformBuildVersionCode' in root.attrib:
        version = root.attrib['platformBuildVersionCode']
    elif '{http://schemas.android.com/apk/res/android}compileSdkVersion' in root.attrib:
        version = root.attrib['{http://schemas.android.com/apk/res/android}compileSdkVersion']
    else:
        version = '?'
    sys.stdout.write( 'Build: %s\n' % version )

    if not grep_term:
        grep_term = root.attrib['package'].split('.')[1]
    sys.stdout.write( 'Grep Term: %s\n' % grep_term )
    sys.stdout.write( '\n\n' )

    return grep_term


def listPermissions():
    grep_term = 'android.permission'
    t_all = root.findall('uses-permission')
    t_term = []
    t_noterm = []
    for obj in t_all:
        if grep_term in obj.attrib['{http://schemas.android.com/apk/res/android}name']:
            t_term.append( obj )
        else:
            t_noterm.append( obj )
    printTitle( 'PERMISSIONS (%d/%d)' % (len(t_term),len(t_all)) )
    printPermissions( t_term, 'white', 'light_red' )
    if len(t_term):
        sys.stdout.write( '\n' )
    printPermissions( t_noterm, 'dark_gray', 'dark_red' )
    sys.stdout.write( '\n\n' )

def printPermissions( tab, c_good, c_bad ):
    t_warning = ['EXTERNAL_STORAGE','INTERNET']
    for obj in tab:
        extra = ''
        color = c_good
        for w in t_warning:
            if w in obj.attrib['{http://schemas.android.com/apk/res/android}name']:
                extra = '(warning)'
                color = c_bad
        sys.stdout.write( '%s%s %s%s\n' % (fg(color),obj.attrib['{http://schemas.android.com/apk/res/android}name'],extra,attr(0)) )



def listActivities():
    app = root.find( 'application' )
    t_all = app.findall('activity')
    t_term = []
    t_noterm = []
    for obj in t_all:
        if grep_term in obj.attrib['{http://schemas.android.com/apk/res/android}name']:
            t_term.append( obj )
        else:
            t_noterm.append( obj )
    printTitle( 'ACTIVITIES (%d/%d)' % (len(t_term),len(t_all)) )
    printActivities( t_term, 'white', 'light_red' )
    if len(t_term):
        sys.stdout.write( '\n' )
    printActivities( t_noterm, 'dark_gray', 'red' )
    sys.stdout.write( '\n\n' )

def printActivities( tab, c_good, c_bad ):
    for obj in tab:
        if '{http://schemas.android.com/apk/res/android}exported' in obj.attrib:
            exported = obj.attrib['{http://schemas.android.com/apk/res/android}exported']
        else:
            exported = 'false'
        if obj.findall('intent-filter'):
            exported = 'true'
        if exported.lower() == 'false':
            extra = ''
            color = c_good
        else:
            extra = '(warning)'
            color = c_bad
        sys.stdout.write( '%s%s %s%s\n' % (fg(color),obj.attrib['{http://schemas.android.com/apk/res/android}name'],extra,attr(0)) )


def listServices():
    app = root.find( 'application' )
    t_all = app.findall('service')
    t_term = []
    t_noterm = []
    for obj in t_all:
        if grep_term in obj.attrib['{http://schemas.android.com/apk/res/android}name']:
            t_term.append( obj )
        else:
            t_noterm.append( obj )
    printTitle( 'SERVICES (%d/%d)' % (len(t_term),len(t_all)) )
    printServices( t_term, 'white', 'light_red' )
    if len(t_term):
        sys.stdout.write( '\n' )
    printServices( t_noterm, 'dark_gray', 'red' )
    sys.stdout.write( '\n\n' )

def printServices( tab, c_good, c_bad ):
    for obj in tab:
        if '{http://schemas.android.com/apk/res/android}exported' in obj.attrib:
            exported = obj.attrib['{http://schemas.android.com/apk/res/android}exported']
        else:
            exported = 'false'
        if obj.findall('intent-filter'):
            exported = 'true'
        if exported.lower() == 'false':
            extra = ''
            color = c_good
        else:
            extra = '(warning)'
            color = c_bad
        sys.stdout.write( '%s%s %s%s\n' % (fg(color),obj.attrib['{http://schemas.android.com/apk/res/android}name'],extra,attr(0)) )


def listReceivers():
    app = root.find( 'application' )
    t_all = app.findall('receiver')
    t_term = []
    t_noterm = []
    for obj in t_all:
        if grep_term in obj.attrib['{http://schemas.android.com/apk/res/android}name']:
            t_term.append( obj )
        else:
            t_noterm.append( obj )
    printTitle( 'RECEIVERS (%d/%d)' % (len(t_term),len(t_all)) )
    printReceivers( t_term, 'white', 'light_red' )
    if len(t_term):
        sys.stdout.write( '\n' )
    printReceivers( t_noterm, 'dark_gray', 'red' )
    sys.stdout.write( '\n\n' )

def printReceivers( tab, c_good, c_bad ):
    for obj in tab:
        if '{http://schemas.android.com/apk/res/android}exported' in obj.attrib:
            exported = obj.attrib['{http://schemas.android.com/apk/res/android}exported']
        else:
            exported = 'false'
        if obj.findall('intent-filter'):
            exported = 'true'
        if exported.lower() == 'false':
            extra = ''
            color = c_good
        else:
            extra = '(warning)'
            color = c_bad
        sys.stdout.write( '%s%s %s%s\n' % (fg(color),obj.attrib['{http://schemas.android.com/apk/res/android}name'],extra,attr(0)) )


def listProviders():
    app = root.find( 'application' )
    t_all = app.findall('provider')
    t_term = []
    t_noterm = []
    for obj in t_all:
        if grep_term in obj.attrib['{http://schemas.android.com/apk/res/android}name']:
            t_term.append( obj )
        else:
            t_noterm.append( obj )
    printTitle( 'PROVIDERS (%d/%d)' % (len(t_term),len(t_all)) )
    printProviders( t_term, 'white', 'light_red' )
    if len(t_term):
        sys.stdout.write( '\n' )
    printProviders( t_noterm, 'dark_gray', 'red' )
    sys.stdout.write( '\n\n' )

def printProviders( tab, c_good, c_bad ):
    for obj in tab:
        if '{http://schemas.android.com/apk/res/android}exported' in obj.attrib:
            exported = obj.attrib['{http://schemas.android.com/apk/res/android}exported']
        else:
            exported = 'false'
        if obj.findall('intent-filter'):
            exported = 'true'
        if exported.lower() == 'false':
            extra = ''
            color = c_good
        else:
            extra = '(warning)'
            color = c_bad
        sys.stdout.write( '%s%s%s %s\n' % (fg(color),obj.attrib['{http://schemas.android.com/apk/res/android}name'],extra,attr(0)) )


def listAssets():
    assets_directory = src_directory + '/assets/'
    t_all = []
    t_files = []
    t_warning = ['secret','pass','key','auth','cer']
    t_ignore = ['.ico','.gif','.jpg','.jpeg','.png','.bmp','.svg','.avi','.mpg','.mpeg','.mp3','.woff','.woff2','.ttf','.eot','.mp3','.mp4','.wav','.mpg','.mpeg','.avi','.mov','.wmv' ]
    
    # r=root, d=directories, f=files
    for r, d, f in os.walk(assets_directory):
        for file in f:
            filename = os.path.join(r,file).replace(src_directory+'/','')
            t_all.append( filename )
            ignore = False
            for i in t_ignore:
                if i in filename.lower():
                    ignore = True
            if not ignore:
                t_files.append( filename )

    printTitle( 'ASSETS (%d/%d)' % (len(t_files),len(t_all)) )

    for filename in sorted(t_files):
        extra = ''
        color = 'white'
        for w in t_warning:
            if w in filename.lower():
                extra = '(warning)'
                color = 'light_red'
        sys.stdout.write( '%s%s %s%s\n' % (fg(color),filename,extra,attr(0)) )

    sys.stdout.write( '\n\n' )


def listRaw():
    assets_directory = src_directory + '/res/raw/'
    t_all = []
    t_files = []
    t_warning = ['secret','pass','key','auth','cer']
    t_ignore = ['.ico','.gif','.jpg','.jpeg','.png','.bmp','.svg','.avi','.kml','.matc','.sfb','.mpg','.mpeg','.mp3','.woff','.woff2','.ttf','.eot','.mp3','.mp4','.wav','.mpg','.mpeg','.avi','.mov','.wmv' ]
    
    # r=root, d=directories, f=files
    for r, d, f in os.walk(assets_directory):
        for file in f:
            filename = os.path.join(r,file).replace(src_directory+'/','')
            t_all.append( filename )
            ignore = False
            for i in t_ignore:
                if i in filename.lower():
                    ignore = True
            if not ignore:
                t_files.append( filename )

    printTitle( 'RES/RAW (%d/%d)' % (len(t_files),len(t_all)) )

    for filename in sorted(t_files):
        extra = ''
        color = 'white'
        for w in t_warning:
            if w in filename.lower():
                extra = '(warning)'
                color = 'light_red'
        sys.stdout.write( '%s%s %s%s\n' % (fg(color),filename,extra,attr(0)) )

    sys.stdout.write( '\n\n' )


parser = argparse.ArgumentParser()
parser.add_argument( "-d","--directory",help="source directory" )
parser.add_argument( "-t","--term",help="term referencing the editor" )
parser.parse_args()
args = parser.parse_args()

if args.term:
    grep_term = args.term
else:
    grep_term = ''

if not args.directory:
    parser.error( 'source directory is missing' )

src_directory = args.directory
if not os.path.isdir(src_directory):
    parser.error( 'source directory not found' )

src_manifest = src_directory + '/' + 'AndroidManifest.xml'
if not os.path.isfile(src_manifest):
    parser.error( 'Manifest file not found' )

try:
    etparse = ET.parse( src_manifest )
except:
    parser.error( 'Cannot read Manifest' )

root = etparse.getroot()
if not root:
    parser.error( 'Cannot read Manifest' )

sys.stdout.write('\n')

grep_term = readInfos( grep_term )
listPermissions()
listAssets()
listRaw()
listActivities()
listServices()
listReceivers()
listProviders()

