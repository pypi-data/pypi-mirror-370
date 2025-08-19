


def safe_import(module_name, log=False, ret=True, verifyOnly=False):
	import subprocess as sub
	import importlib
	import sys
	from inspect import stack

	def pip_installed():
		try:
			sub.check_call(
				[sys.executable, '-m', 'pip', '--version'],
				stdout=sub.DEVNULL,
				stderr=sub.DEVNULL
			)
			return True
		except (sub.CalledProcessError, FileNotFoundError):
			return False

	def install_pip():
		if log: print('PIP NOT FOUND. INSTALLING...')
		try:
			sub.check_call(
				[sys.executable, '-m', 'ensurepip', '--upgrade'],
				stdout=sub.DEVNULL,
				stderr=sub.DEVNULL
			)
			return pip_installed()
		except Exception as e:
			return False

	if not pip_installed():
		if not install_pip():
			if log: print('[safe_import] Failed to install PIP!')
			return None

	try:
		imported = importlib.import_module(module_name)
		if __name__ == '__main__':
			if verifyOnly:
				pass
			else:
				globals()[module_name] = imported
		else:
			if verifyOnly:
				pass
			else:
				stack()[1].frame.f_globals[module_name] = imported
		if ret: return imported
	except ImportError:
		if log: print(f'MODULE {module_name} NOT FOUND. INSTALLING...')
		try:
			sub.check_call(
				[sys.executable, '-m', 'pip', 'install', module_name],
				stdout=sub.DEVNULL,
				stderr=sub.DEVNULL
			)
			imported = importlib.import_module(module_name)
			if __name__ == '__main__':
				if verifyOnly:
					pass
				else:
					globals()[module_name] = imported
			else:
				if verifyOnly:
					pass
				else:
					stack()[1].frame.f_globals[module_name] = imported
			if log: print(f'MODULE {module_name} IMPORTED SUCCESSFULLY!')
			if ret: return imported
		except Exception as e:
			if log: print(f'[safe_import] Failed to import {module_name}: {e}')
			if ret: return None
