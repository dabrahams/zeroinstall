#!/usr/bin/env python

import locale
from logging import warn
try:
	locale.setlocale(locale.LC_ALL, '')
except locale.Error:
	warn('Error setting locale (eg. Invalid locale)')

## PATH ##

def main():
        from zeroinstall.gtkui import desktop
        import sys
        desktop.main(sys.argv[1:])

if __name__ == '__main__':
        main()
