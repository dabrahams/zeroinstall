import tempfile as _tempfile, os as _os

"""
Most of this code shamelessly lifted from Python's standard tempfile library
"""
class _TemporaryFileWrapper:
	"""Temporary file wrapper

	This class provides a wrapper around files opened for
	temporary use.  In particular, it seeks to automatically
	remove the file when it is no longer needed.
	"""

	def __init__(self, file, name, delete=True):
		self.file = file
		self.name = name
		self.close_called = False
		self.unlinked = False
		self.delete = delete
	
	def __getattr__(self, name):
		# Attribute lookups are delegated to the underlying file
		# and cached for non-numeric results
		# (i.e. methods are cached, closed and friends are not)
		file = self.__dict__['file']
		a = getattr(file, name)
		if not issubclass(type(a), type(0)):
			setattr(self, name, a)
		return a
	
	# The underlying __enter__ method returns the wrong object
	# (self.file) so override it to return the wrapper
	def __enter__(self):
		self.file.__enter__()
		return self
		
	# Cache the unlinker so we don't get spurious errors at
	# shutdown when the module-level "os" is None'd out.  Note
	# that this must be referenced as self.unlink, because the
	# name TemporaryFileWrapper may also get None'd out before
	# __del__ is called.
	unlink = _os.unlink
	
	def close(self, preserve = False):
		if not self.close_called:
			self.close_called = True
			self.file.close()
		if not preserve and self.delete and not self.unlinked:
			self.unlinked = True
			self.unlink(self.name)

	def __del__(self):
		self.close()

	# Need to trap __exit__ as well to ensure the file gets
	# deleted when used in a with statement
	def __exit__(self, exc, value, tb):
		result = self.file.__exit__(exc, value, tb)
		self.close()
		return result
	
template = "tmp"

def NamedTemporaryFile(mode='w+b', bufsize=-1, suffix="",
			   prefix=template, dir=None, delete=True):
	"""Create and return a temporary file.
	Arguments:
	'prefix', 'suffix', 'dir' -- as for mkstemp.
	'mode' -- the mode argument to os.fdopen (default "w+b").
	'bufsize' -- the buffer size argument to os.fdopen (default -1).
	'delete' -- whether the file is deleted on close (default True).
	The file is created as mkstemp() would do it.

	Returns an object with a file-like interface; the name of the file
	is accessible as file.name.	 The file will be automatically deleted
	when it is closed unless the 'delete' argument is set to False.
	"""

	if dir is None:
                dir = _tempfile.gettempdir()

	(fd, name) = _tempfile.mkstemp(dir=dir, prefix=prefix, suffix=suffix, text=not 'b' in mode)
	file = _os.fdopen(fd, mode, bufsize)
	return _TemporaryFileWrapper(file, name, delete)
