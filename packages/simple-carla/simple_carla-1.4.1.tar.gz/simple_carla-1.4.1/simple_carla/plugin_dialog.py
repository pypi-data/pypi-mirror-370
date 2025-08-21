#  simple_carla/plugin_dialog.py
#
#  Copyright 2024 liyang <liyang@veronica>
#
"""
Provides a means to use Carla's plugin dialog to compile a plugin's
"plugin_def"; a dict containing the values essential for identifying and
loading the plugin.
"""
import sys, os
from simple_carla import carla_binaries_path
from carla_frontend import CarlaFrontendLib
from carla_shared import DLL_EXTENSION


class CarlaPluginDialog():
	"""
	Wrapper for Carla's native plugin selection dialog.
	This is a singleton class. You may call the constructor repatedly, and it will
	usethe same instance for the life of the program.
	"""
	_instance = None
	_carla_felib = None

	def __new__(cls, parent):
		if cls._instance is None:
			cls._instance = super().__new__(cls)
		return cls._instance

	def __init__(self, parent):
		if self._carla_felib is None:
			felib_path = os.path.join(carla_binaries_path, 'libcarla_frontend.so')
			self._carla_felib = CarlaFrontendLib(felib_path)
			self._plugin_list_dialog = self._carla_felib.createPluginListDialog(parent, {
				'showPluginBridges': False,
				'showWineBridges': False,
				'useSystemIcons': False,
				'wineAutoPrefix': '',
				'wineExecutable': '',
				'wineFallbackPrefix': ''
			})

	def exec_dialog(self):
		"""
		Displays the plugin dialog.
		Returns a dict which may be used as a "plugin_def".
		"""
		return self._carla_felib.execPluginListDialog(self._plugin_list_dialog)



#  end simple_carla/plugin_dialog.py
