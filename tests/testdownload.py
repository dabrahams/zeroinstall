#!/usr/bin/env python2.3
import sys, tempfile, os, shutil
from StringIO import StringIO
import unittest
from logging import getLogger, DEBUG, INFO
#getLogger().setLevel(DEBUG)

sys.path.insert(0, '..')

from zeroinstall.injector import model, basedir, autopolicy, gpg, iface_cache, download
import data

import server

class Reply:
	def __init__(self, reply):
		self.reply = reply

	def readline(self):
		return self.reply

class TestDownload(unittest.TestCase):
	def setUp(self):
		self.config_home = tempfile.mktemp()
		self.cache_home = tempfile.mktemp()
		os.environ['XDG_CONFIG_HOME'] = self.config_home
		os.environ['XDG_CACHE_HOME'] = self.cache_home
		reload(basedir)

		os.mkdir(self.config_home, 0700)
		os.mkdir(self.cache_home, 0700)
		if os.environ.has_key('DISPLAY'):
			del os.environ['DISPLAY']
		self.gnupg_home = tempfile.mktemp()
		os.environ['GNUPGHOME'] = self.gnupg_home
		os.mkdir(self.gnupg_home, 0700)
		stream = tempfile.TemporaryFile()
		stream.write(data.thomas_key)
		stream.seek(0)
		gpg.import_key(stream)
		iface_cache.iface_cache.__init__()
		download._downloads = {}
	
	def tearDown(self):
		shutil.rmtree(self.config_home)
		shutil.rmtree(self.cache_home)
		shutil.rmtree(self.gnupg_home)
	
	def testRejectKey(self):
		old_out = sys.stdout
		try:
			sys.stdout = StringIO()
			child = server.handle_requests('Hello', '6FCF121BE2390E0B.gpg')
			policy = autopolicy.AutoPolicy('http://localhost:8000/Hello', download_only = False)
			assert policy.need_download()
			sys.stdin = Reply("N\n")
			try:
				policy.download_and_execute(['Hello'])
				assert 0
			except model.SafeException, ex:
				if "Not signed with a trusted key" not in str(ex):
					raise ex
			os.waitpid(child, 0)
		finally:
			sys.stdout = old_out
	
	def testAcceptKey(self):
		old_out = sys.stdout
		try:
			sys.stdout = StringIO()
			child = server.handle_requests('Hello', '6FCF121BE2390E0B.gpg', 'HelloWorld.tgz')
			policy = autopolicy.AutoPolicy('http://localhost:8000/Hello', download_only = False)
			assert policy.need_download()
			sys.stdin = Reply("Y\n")
			try:
				policy.download_and_execute(['Hello'], main = 'Missing')
				assert 0
			except model.SafeException, ex:
				if "HelloWorld/Missing" not in str(ex):
					raise ex
			os.waitpid(child, 0)
		finally:
			sys.stdout = old_out

suite = unittest.makeSuite(TestDownload)
if __name__ == '__main__':
	sys.argv.append('-v')
	unittest.main()