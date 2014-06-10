import logging
logger = logging.getLogger(__name__)

def setup_logger(): #pragma: no cover
	logging.basicConfig(filename='iskdpy.log', 
						level=logging.DEBUG,
						format='%(asctime)s %(name)-32s %(levelname)-8s %(message)s',
						datefmt='%H:%M:%S'
						)
	root=logging.getLogger()

	console = logging.StreamHandler()
	console.setLevel(logging.INFO)

	formatter = logging.Formatter('%(name)s: %(levelname)-8s %(message)s')
	console.setFormatter(formatter)

	root.addHandler(console)

def main(): #pragma: no cover
	setup_logger()

	logger.info('Importing components...')
	logger.debug(' - config...')
	from . import config
	logger.debug(' - presenter...')
	from . import presenter
	logger.debug(' - source plugins...')
	from . import source_plugins
	logger.debug(' - output plugins...')
	from . import output_plugins
	logger.info('Importing components DONE')

	from .output import OutputPlugin, thread

	import gc
	gc.disable()

	logger.info('Started')
	presenter.goto_next_slide()
	output=OutputPlugin.factory(config.output)
	output.run()
	thread.thread.join()
	logger.info('Stopped')
