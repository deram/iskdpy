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
	console.setLevel(logging.DEBUG)

	formatter = logging.Formatter('%(name)s: %(levelname)-8s %(message)s')
	console.setFormatter(formatter)

	root.addHandler(console)

def adjust_logger_levels(conf=None):
	logger.info('Adjusting logger levels')
	levels={ "DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR, "CRITICAL": logging.CRITICAL }
	if conf:
		for log, level in conf.items():
			logging.debug(' - %s -> %s', log, level)
			logging.getLogger(log).setLevel(levels[level])

def log_break(text, width=80):
	filled_text=" %s " % text
	barlen = (width-(len(filled_text)))/2
	full=("="*barlen + filled_text + "="*barlen)
	if len(full) < width:
		full+="="*(width-len(full))
	return full

def main(): #pragma: no cover
	setup_logger()

	logger.info(log_break("INIT"))
	logger.info('Importing components...')
	logger.debug(' - config...')
	from . import config
	logger.debug(' - presenter...')
	from . import presenter
	logger.debug(' - source plugins...')
	from . import source_plugins
	logger.debug(' - output plugins...')
	from . import output_plugins
	logger.info('DONE')

	adjust_logger_levels(config.logger_levels)

	from .output import OutputPlugin#, thread

	import gc
	gc.disable()

	logger.info(log_break("STARTED"))
	ret=output.run()
	presenter.goto_next_slide()
	ret.get()
	logger.info(log_break("STOPPED"))
