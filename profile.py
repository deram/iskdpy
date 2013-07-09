
if __name__ == "__main__":
	from iskdpy.main import main
	import cProfile
	cProfile.run('main()', 'profile')
