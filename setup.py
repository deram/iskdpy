from cx_Freeze import setup, Executable
 
setup(
	name = "iskdpy",
	version = "0.0",
	description = "ISK Display",
	package_dir = {'isk': '.'},
	packages=['isk', 'isk.source_plugins'],
	executables = [Executable("main.py")],
	options = {"build_exe": {"excludes": ['local_config']}}
	)

