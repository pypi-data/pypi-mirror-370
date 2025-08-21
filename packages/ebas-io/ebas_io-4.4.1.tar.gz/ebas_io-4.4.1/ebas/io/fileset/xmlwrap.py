"""
ebas/io/xmlwrap.py
$Id: xmlwrap.py 1527 2017-02-15 18:36:36Z pe $

EBAS I/O module, xmlwrap
"""

import sys

def xmlwrap_header():
    """
    Writes the xmlwrap-header.
    """
    sys.stdout.write('<?xml version="1.0" encoding="UTF-8" '
                    'standalone="yes"?>\n')
    sys.stdout.write('<Fileset>\n')

def xmlwrap_trailer():
    """
    Writes the xmlwrap-trailer.
    """
    sys.stdout.write('</Fileset>\n')

def xmlwrap_fileheader(filename):
    """
    Writes the xmlwrap-fileheader.
    """
    sys.stdout.write(' <File filename="{}">\n'.format(filename))
    sys.stdout.write('  <![CDATA[')
    # no newline

def xmlwrap_filetrailer():
    """
    Writes the xmlwrap-filetrailer.
    """
    sys.stdout.write(']]>\n')
    sys.stdout.write(' </File>\n')
