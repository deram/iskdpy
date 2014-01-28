import logging
logger = logging.getLogger(__name__)

import gc

from . import presenter
from . import source_plugins
from . import output_plugins
from . import config

from .output import OutputPlugin

def setup_logger():
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

def main():
	setup_logger()

	gc.disable()

	logger.info('Started')
	presenter.goto_next_slide()
	output=OutputPlugin.factory(config.output)
	output.run()

	logger.info('Stopped')
