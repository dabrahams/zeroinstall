#!/usr/bin/env python

from __future__ import print_function

import sys, os
from zeroinstall import zerostore, SafeException
from zeroinstall.zerostore import cli, manifest

def main():
        # Make all system files world-readable, even if the default
        # system umask is more strict.
        os.umask(0o022)

        # import logging; logging.getLogger().setLevel(logging.DEBUG)

        try:
                if 'ENV_NOT_CLEARED' in os.environ:
                        raise SafeException("Environment not cleared. Check your sudoers file.")
                if os.environ['HOME'] == 'Unclean':
                        raise SafeException("$HOME not set. Check your sudoers file has 'always_set_home' turned on for zeroinst.")

                if len(sys.argv) != 2:
                        raise cli.UsageError('Usage: %s DIGEST' % sys.argv[0])
                required_digest = sys.argv[1]

                manifest_data = open('.manifest', 'rb').read()

                stores = zerostore.Stores()

                manifest.copy_tree_with_verify('.', '/var/cache/0install.net/implementations',
                                                manifest_data, required_digest)
        except (IOError, SafeException) as ex:
                print(ex, file=sys.stderr)
                sys.exit(1)
