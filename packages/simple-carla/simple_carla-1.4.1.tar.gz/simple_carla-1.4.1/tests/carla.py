#  simple_carla/tests/carla.py
#
#  Copyright 2024 liyang <liyang@veronica>
#
import logging
from time import sleep
from PyQt5.QtCore import QCoreApplication
from simple_carla import Carla, Plugin

APPLICATION_NAME = 'simple_carla'


class TestApp:

	def __init__(self, meter_class='EBUMeter'):
		super().__init__()
		self.ready = False
		carla = Carla(APPLICATION_NAME)
		carla.on_engine_started(self.carla_started)
		carla.on_engine_stopped(self.carla_stopped)
		if not carla.engine_init():
			audioError = carla.get_last_error()
			if audioError:
				raise Exception("Could not connect to JACK; possible reasons:\n%s" % audioError)
			else:
				raise Exception('Could not connect to JACK')

	def carla_started(self, plugin_count, process_mode, transport_mode, buffer_size, sample_rate, driver_name):
		logging.debug('======= Engine started ======== ')
		self.meter = EBUMeter()
		self.meter.on_ready(self.meter_ready)
		self.meter.add_to_carla()

	def carla_stopped(self):
		logging.debug('======= Engine stopped ========')

	def meter_ready(self):
		logging.debug('TestApp meter_ready ')
		self.ready = True
		assert(Carla.instance is Carla(APPLICATION_NAME))

	def wait_ready(self):
		"""
		Blocks until sig_ready received from MeteringWorker.
		"""
		watchdog = 0
		while not self.ready:
			watchdog += 1
			if watchdog > 3:
				logging.debug('Tired of waiting')
				break
			else:
				logging.debug('TestApp waiting for meter_ready_event ...')
				sleep(0.4)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.shutdown()

	def shutdown(self):
		logging.debug('TestApp.shutdown');
		Carla.instance.delete()



class EBUMeter(Plugin):

	plugin_def = {
		'name': 'EBU Meter (Mono)',
		'build': 2,
		'type': 4,
		'filename': 'meters.lv2',
		'label': 'http://gareus.org/oss/lv2/meters#EBUmono',
		'uniqueId': 0
	}

	def finalize_init(self):
		self.parameters[0].value = -6.0

	def value(self):
		return self.parameters[1].get_internal_value()



if __name__ == "__main__":
	logging.basicConfig(
		level = logging.DEBUG,
		format = "[%(filename)24s:%(lineno)-4d] %(message)s"
	)
	with TestApp() as tester:
		tester.wait_ready()
	logging.debug('Done')



#  end simple_carla/tests/carla.py
