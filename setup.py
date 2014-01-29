from cx_Freeze import setup, Executable


exe= Executable(
	script='iskdpy.py',
	copyDependentFiles = True
)

 
setup(
	name = "iskdpy",
	version = "0.0",
	description = "ISK Display",
	#package_dir = {'': 'iskdpy'},
	packages=['iskdpy', 'iskdpy.source_plugins', 'iskdpy.utils', 'iskdpy.output_plugins', 'iskdpy.output_plugins.cocos_scene'],
        scripts=['iskdpy.py'],
	executables = [exe],
	options = {"build_exe": {
		'include_files': [
				['base.png', 'base.png'],
				['run.bat', 'run.bat'],
				['C:/Windows/System32/Python27.dll', 'Python27.dll'],
				['C:/Windows/System32/avbin.dll', 'avbin.dll']],
	}}
	)

