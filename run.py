import os, sys

from policy import policy
from model import *

def do_env_binding(binding, iface):
	impl = policy.implementation[iface]
	extra = os.path.join(impl.path, binding.insert)
	if binding.name in os.environ:
		os.environ[binding.name] = extra + ':' + os.environ[binding.name]
	else:
		os.environ[binding.name] = extra

def execute(iface, prog, prog_args):
	def setup_bindings(i):
		impl = policy.implementation[i]
		for dep in impl.dependencies.values():
			dep_iface = dep.get_interface()
			for b in dep.bindings:
				if isinstance(b, EnvironmentBinding):
					do_env_binding(b, dep_iface)
			setup_bindings(dep_iface)
	setup_bindings(iface)
	
	prog_path = os.path.join(policy.implementation[iface].path, prog)
	if not os.path.exists(prog_path):
		print "'%s' does not exist." % prog_path
		print "(implementation '%s' + program '%s')" % (policy.implementation[iface].path, prog)
		sys.exit(1)
	os.execl(prog_path, prog_path, *prog_args)