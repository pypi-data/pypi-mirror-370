#  simple_carla/tests/qt_carla.py
#
#  Copyright 2024 liyang <liyang@veronica>
#
import logging
from time import sleep
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from simple_carla import Plugin, PatchbayPort
from simple_carla.qt import CarlaQt, QtPlugin


APPLICATION_NAME = 'qt_carla'


class TestApp(QMainWindow):

	def __init__(self):
		super().__init__()
		self.ready = False
		carla = CarlaQt(APPLICATION_NAME)
		carla.sig_engine_started.connect(self.carla_started)
		carla.sig_engine_stopped.connect(self.carla_stopped)
		if not carla.engine_init():
			audioError = carla.get_last_error()
			if audioError:
				raise Exception("Could not connect to JACK; possible reasons:\n%s" % audioError)
			raise Exception('Could not connect to JACK')

	@pyqtSlot(int, int, int, int, float, str)
	def carla_started(self, plugin_count, process_mode, transport_mode, buffer_size, sample_rate, driver_name):
		logging.debug('======= Engine started ======== ')
		self.meter = EBUMeter()
		self.meter.sig_ready.connect(self.meter_ready)
		self.meter.sig_connection_change.connect(self.meter_connect)
		self.meter.add_to_carla()

	@pyqtSlot()
	def carla_stopped(self):
		logging.debug('======= Engine stopped ========')

	@pyqtSlot(Plugin)
	def meter_ready(self, plugin):
		logging.debug('Received sig_ready from %s', plugin)
		for out_port, in_port in zip(plugin.audio_outs(), CarlaQt.instance.system_audio_in_ports()):
			out_port.connect_to(in_port)

	@pyqtSlot(PatchbayPort, PatchbayPort, bool)
	def meter_connect(self, self_port, other_port, state):
		logging.debug('Received sig_connection_change: %s to %s: %s', self_port, other_port, state)
		self.close()

	def closeEvent(self, event):
		logging.debug('Closing');
		CarlaQt.instance.delete()
		event.accept()



class EBUMeter(QtPlugin):

	plugin_def = {
		'name': 'EBU Meter (Mono)',
		'build': 2,
		'type': 4,
		'filename': 'meters.lv2',
		'label': 'http://gareus.org/oss/lv2/meters#EBUmono',
		'uniqueId': 0
	}

	def ready(self):
		"""
		Called after post_embed_init() and all ports ready
		"""
		self.parameters[0].value = -6.0
		super().ready()

	def value(self):
		return self.parameters[1].get_internal_value()



if __name__ == "__main__":
	logging.basicConfig(
		level = logging.DEBUG,
		format = "[%(filename)24s:%(lineno)-4d] %(message)s"
	)
	app = QApplication([])
	main_window = TestApp()
	main_window.show()
	logging.debug('Done')
	app.exec()



#  end simple_carla/tests/qt_carla.py
