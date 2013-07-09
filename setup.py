from cx_Freeze import setup, Executable
 
setup(
	name = "iskdpy",
	version = "0.0",
	description = "ISK Display",
	#package_dir = {'': 'iskdpy'},
	packages=['iskdpy', 'iskdpy.scene', 'iskdpy.source_plugins', 'iskdpy.utils'],
        scripts=['iskdpy.py'],
	executables = [Executable("iskdpy.py")],
	#options = {"build_exe": {"excludes": ['local_config']}}
	)

