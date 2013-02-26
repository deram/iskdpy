
if __name__ == "__main__":
	import main
	import cProfile
	cProfile.run('main.main()', 'profile')
