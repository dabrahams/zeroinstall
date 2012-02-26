"""Adding icons and menu items using the freedesktop.org system.
(xdg = X Desktop Group)
"""
# Copyright (C) 2009, Thomas Leonard
# See the README file for details, or visit http://0install.net.

from zeroinstall import _
import shutil, os, tempfile, subprocess
from logging import info, warn

from zeroinstall import SafeException
from zeroinstall.support import basedir
from zeroinstall.injector import namespaces

_template = """[Desktop Entry]
# This file was generated by 0install.
# See the Zero Install project for details: http://0install.net
Type=Application
Version=1.0
Name=%(name)s
Comment=%(comment)s
Exec=%(0launch)s -- %(iface)s %%f
Categories=Application;%(category)s
"""

_icon_template = """Icon=%s
"""

def add_to_menu(iface, icon_path, category, zlaunch=None):
	"""Write a .desktop file for this application.
	@param iface: the program being added
	@param icon_path: the path of the icon, or None
	@param category: the freedesktop.org menu category"""
	tmpdir = tempfile.mkdtemp(prefix = 'zero2desktop-')
	try:
		desktop_name = os.path.join(tmpdir, 'zeroinstall-%s.desktop' % iface.get_name().lower().replace(os.sep, '-').replace(' ', ''))
		desktop = open(desktop_name, 'w')
		desktop.write(_template % {'name': iface.get_name(),
                                   'comment': iface.summary,
                                   '0launch': zlaunch or '0launch',
                                   'iface': iface.uri,
                                   'category': category})
		if icon_path:
			desktop.write(_icon_template % icon_path)
		if len(iface.get_metadata(namespaces.XMLNS_IFACE, 'needs-terminal')):
			desktop.write('Terminal=true\n')
		desktop.close()
		status = subprocess.call(['xdg-desktop-menu', 'install', desktop_name])
	finally:
		shutil.rmtree(tmpdir)

	if status:
		raise SafeException(_('Failed to run xdg-desktop-menu (error code %d)') % status)

def discover_existing_apps():
	"""Search through the configured XDG datadirs looking for .desktop files created by L{add_to_menu}.
	@return: a map from application URIs to .desktop filenames"""
	already_installed = {}
	for d in basedir.load_data_paths('applications'):
		for desktop_file in os.listdir(d):
			if desktop_file.startswith('zeroinstall-') and desktop_file.endswith('.desktop'):
				full = os.path.join(d, desktop_file)
				try:
					for line in open(full):
						line = line.strip()
						if line.startswith('Exec=0launch '):
							bits = line.split(' -- ', 1)
							if ' ' in bits[0]:
								uri = bits[0].split(' ', 1)[1]		# 0launch URI -- %u
							else:
								uri = bits[1].split(' ', 1)[0].strip()	# 0launch -- URI %u
							already_installed[uri] = full
							break
					else:
						info(_("Failed to find Exec line in %s"), full)
				except Exception as ex:
					warn(_("Failed to load .desktop file %(filename)s: %(exceptions"), {'filename': full, 'exception': ex})
	return already_installed
