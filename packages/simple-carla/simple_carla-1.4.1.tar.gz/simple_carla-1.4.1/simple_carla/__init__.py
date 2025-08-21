#  simple_carla/__init__.py
#
#  Copyright 2024 liyang <liyang@veronica>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
An easy-to-use, object-oriented interface to the carla plugin host.
"""
import os, sys, threading, time, logging, traceback
from ctypes import byref, cast, c_char_p, c_void_p, POINTER
from functools import wraps
from struct import pack
from numpy import zeros as np_zeros
from log_soso import StreamToLogger

# --- discover carla paths before importing carla resources ---
if os.path.exists('/usr/local/lib/carla'):
	carla_binaries_path = '/usr/local/lib/carla'
elif os.path.exists('/usr/lib/carla'):
	carla_binaries_path = '/usr/lib/carla'
else:
	raise FileNotFoundError(f"Carla binaries not found")
if os.path.exists('/usr/local/share/carla'):
	carla_resources_path = '/usr/local/share/carla'
elif os.path.exists('/usr/share/carla'):
	carla_resources_path = '/usr/share/carla'
else:
	raise FileNotFoundError(f"Carla resources not found")
sys.path.append(carla_resources_path)			# Ugh. I know.
# -------------------------------------------------------------

from carla_utils import getPluginTypeAsString

from carla_shared import (

	splitter,

	CARLA_KEY_PATHS_LADSPA,
	CARLA_KEY_PATHS_DSSI,
	CARLA_KEY_PATHS_LV2,
	CARLA_KEY_PATHS_VST2,
	CARLA_KEY_PATHS_VST3,
	CARLA_KEY_PATHS_SF2,
	CARLA_KEY_PATHS_SFZ,
	CARLA_DEFAULT_DSSI_PATH,
	CARLA_DEFAULT_LADSPA_PATH,
	CARLA_DEFAULT_LV2_PATH,
	CARLA_DEFAULT_SF2_PATH,
	CARLA_DEFAULT_SFZ_PATH,
	CARLA_DEFAULT_VST2_PATH,
	CARLA_DEFAULT_VST3_PATH
)

from carla_backend import (

	CarlaHostDLL,
	charPtrToString,
	c_uintptr,
	charPtrPtrToStringList,
	structToDict,
	EngineCallbackFunc,
	FileCallbackFunc,

	# Callback action codes:
	ENGINE_CALLBACK_DEBUG,
	ENGINE_CALLBACK_PLUGIN_ADDED,
	ENGINE_CALLBACK_PLUGIN_REMOVED,
	ENGINE_CALLBACK_PLUGIN_RENAMED,
	ENGINE_CALLBACK_PLUGIN_UNAVAILABLE,
	ENGINE_CALLBACK_PARAMETER_VALUE_CHANGED,
	ENGINE_CALLBACK_PARAMETER_DEFAULT_CHANGED,
	ENGINE_CALLBACK_PARAMETER_MAPPED_CONTROL_INDEX_CHANGED,
	ENGINE_CALLBACK_PARAMETER_MIDI_CHANNEL_CHANGED,
	ENGINE_CALLBACK_OPTION_CHANGED,
	ENGINE_CALLBACK_PROGRAM_CHANGED,
	ENGINE_CALLBACK_MIDI_PROGRAM_CHANGED,
	ENGINE_CALLBACK_UI_STATE_CHANGED,
	ENGINE_CALLBACK_NOTE_ON,
	ENGINE_CALLBACK_NOTE_OFF,
	ENGINE_CALLBACK_UPDATE,
	ENGINE_CALLBACK_RELOAD_INFO,
	ENGINE_CALLBACK_RELOAD_PARAMETERS,
	ENGINE_CALLBACK_RELOAD_PROGRAMS,
	ENGINE_CALLBACK_RELOAD_ALL,
	ENGINE_CALLBACK_PATCHBAY_CLIENT_ADDED,
	ENGINE_CALLBACK_PATCHBAY_CLIENT_REMOVED,
	ENGINE_CALLBACK_PATCHBAY_CLIENT_RENAMED,
	ENGINE_CALLBACK_PATCHBAY_CLIENT_DATA_CHANGED,
	ENGINE_CALLBACK_PATCHBAY_PORT_ADDED,
	ENGINE_CALLBACK_PATCHBAY_PORT_REMOVED,
	ENGINE_CALLBACK_PATCHBAY_PORT_CHANGED,
	ENGINE_CALLBACK_PATCHBAY_CONNECTION_ADDED,
	ENGINE_CALLBACK_PATCHBAY_CONNECTION_REMOVED,
	ENGINE_CALLBACK_ENGINE_STARTED,
	ENGINE_CALLBACK_ENGINE_STOPPED,
	ENGINE_CALLBACK_PROCESS_MODE_CHANGED,
	ENGINE_CALLBACK_TRANSPORT_MODE_CHANGED,
	ENGINE_CALLBACK_BUFFER_SIZE_CHANGED,
	ENGINE_CALLBACK_SAMPLE_RATE_CHANGED,
	ENGINE_CALLBACK_CANCELABLE_ACTION,
	ENGINE_CALLBACK_PROJECT_LOAD_FINISHED,
	ENGINE_CALLBACK_NSM,
	ENGINE_CALLBACK_IDLE,
	ENGINE_CALLBACK_INFO,
	ENGINE_CALLBACK_ERROR,
	ENGINE_CALLBACK_QUIT,
	ENGINE_CALLBACK_INLINE_DISPLAY_REDRAW,
	ENGINE_CALLBACK_PATCHBAY_PORT_GROUP_ADDED,
	ENGINE_CALLBACK_PATCHBAY_PORT_GROUP_REMOVED,
	ENGINE_CALLBACK_PATCHBAY_PORT_GROUP_CHANGED,
	ENGINE_CALLBACK_PARAMETER_MAPPED_RANGE_CHANGED,
	ENGINE_CALLBACK_PATCHBAY_CLIENT_POSITION_CHANGED,

	# Engine options
	ENGINE_OPTION_PATH_BINARIES,
	ENGINE_OPTION_PATH_RESOURCES,
	ENGINE_OPTION_PLUGIN_PATH,
	ENGINE_OPTION_AUDIO_DRIVER,
	ENGINE_OPTION_CLIENT_NAME_PREFIX,
	ENGINE_OPTION_DEBUG_CONSOLE_OUTPUT,
	ENGINE_OPTION_FORCE_STEREO,
	ENGINE_OPTION_MAX_PARAMETERS,
	ENGINE_OPTION_PREFER_PLUGIN_BRIDGES,
	ENGINE_OPTION_PREFER_UI_BRIDGES,
	ENGINE_OPTION_PREVENT_BAD_BEHAVIOUR,
	ENGINE_OPTION_PROCESS_MODE,
	ENGINE_OPTION_RESET_XRUNS,
	ENGINE_OPTION_TRANSPORT_MODE,
	ENGINE_OPTION_UI_BRIDGES_TIMEOUT,
	ENGINE_OPTION_UIS_ALWAYS_ON_TOP,

	# Transport modes
	ENGINE_TRANSPORT_MODE_JACK,
	ENGINE_TRANSPORT_MODE_INTERNAL,
	ENGINE_TRANSPORT_MODE_DISABLED,

	# Process modes
	ENGINE_PROCESS_MODE_MULTIPLE_CLIENTS,
	ENGINE_PROCESS_MODE_SINGLE_CLIENT,
	ENGINE_PROCESS_MODE_PATCHBAY,

	# Plugin types:
	PLUGIN_DSSI,
	PLUGIN_JACK,
	PLUGIN_LADSPA,
	PLUGIN_LV2,
	PLUGIN_NONE,
	PLUGIN_SF2,
	PLUGIN_SFZ,
	PLUGIN_VST2,
	PLUGIN_VST3,

	# Plugin options:
	PLUGIN_OPTION_FIXED_BUFFERS,
	PLUGIN_OPTION_FORCE_STEREO,
	PLUGIN_OPTION_MAP_PROGRAM_CHANGES,
	PLUGIN_OPTION_USE_CHUNKS,
	PLUGIN_OPTION_SEND_CONTROL_CHANGES,
	PLUGIN_OPTION_SEND_CHANNEL_PRESSURE,
	PLUGIN_OPTION_SEND_NOTE_AFTERTOUCH,
	PLUGIN_OPTION_SEND_PITCHBEND,
	PLUGIN_OPTION_SEND_ALL_SOUND_OFF,
	PLUGIN_OPTION_SEND_PROGRAM_CHANGES,
	PLUGIN_OPTION_SKIP_SENDING_NOTES,
	PLUGIN_OPTIONS_NULL,

	# Plugin hints:
	PLUGIN_IS_BRIDGE,
	PLUGIN_IS_RTSAFE,
	PLUGIN_IS_SYNTH,
	PLUGIN_HAS_CUSTOM_UI,
	PLUGIN_CAN_DRYWET,
	PLUGIN_CAN_VOLUME,
	PLUGIN_CAN_BALANCE,
	PLUGIN_CAN_PANNING,
	PLUGIN_NEEDS_FIXED_BUFFERS,
	PLUGIN_NEEDS_UI_MAIN_THREAD,
	PLUGIN_USES_MULTI_PROGS,
	PLUGIN_HAS_INLINE_DISPLAY,

	#Parameter types
	PARAMETER_UNKNOWN,
	PARAMETER_INPUT,
	PARAMETER_OUTPUT,

	# Parameter hints
	PARAMETER_IS_BOOLEAN,
	PARAMETER_IS_INTEGER,
	PARAMETER_IS_LOGARITHMIC,
	PARAMETER_IS_ENABLED,
	PARAMETER_IS_AUTOMATABLE,
	PARAMETER_IS_READ_ONLY,
	PARAMETER_USES_SAMPLERATE,
	PARAMETER_USES_SCALEPOINTS,
	PARAMETER_USES_CUSTOM_TEXT,
	PARAMETER_CAN_BE_CV_CONTROLLED,
	PARAMETER_IS_NOT_SAVED,

	# Carla -specific parameter indexes:
	PARAMETER_NULL,
	PARAMETER_ACTIVE,
	PARAMETER_DRYWET,
	PARAMETER_VOLUME,
	PARAMETER_BALANCE_LEFT,
	PARAMETER_BALANCE_RIGHT,
	PARAMETER_PANNING,
	PARAMETER_CTRL_CHANNEL,
	PARAMETER_MAX,

	# Port identity
	PATCHBAY_PORT_IS_INPUT,
	PATCHBAY_PORT_TYPE_AUDIO,
	PATCHBAY_PORT_TYPE_CV,
	PATCHBAY_PORT_TYPE_MIDI,
	PATCHBAY_PORT_TYPE_OSC,

	# File open dialog flags
	FILE_CALLBACK_OPEN,
	FILE_CALLBACK_SAVE
)

from resources_rc import qCleanupResources


__version__ = "1.4.1"


# -------------------------------------------------------------------
# Decorator which forces a function call to wait for engine idle

_engine_exclusive = threading.BoundedSemaphore()

def polite_function(func):
	"""
	Decorator to synchronize function calls and engine idle
	"""
	@wraps(func)
	def wrapper(*args, **kwargs):
		with _engine_exclusive:
			retval = func(*args, **kwargs)
		return retval
	return wrapper

# -------------------------------------------------------------------
# Utility function used when saving plugin state

def encode_properties(thing, keys = None):
	"""
	Returns a dictionary which may be used for encoding an object's state, used by
	Plugin.encode_saved_state() function.
	"""
	pe = {}
	for key in dir(thing):
		if key[0] != '_' and (keys is None or key in keys):
			val = getattr(thing, key)
			if hasattr(val, "encode_saved_state"):
				val = val.encode_saved_state()
			pe[key] = val
	return pe


# -------------------------------------------------------------------
# Carla host wrapper

class _SimpleCarla(CarlaHostDLL):
	"""
	Abstract class which provides an object-oriented interface to CarlaHostDLL.
	Inherited by: Carla, CarlaQt
	"""

	idle_interval		= 1 / 50
	instance			= None
	client_name			= None
	__autoload_plugin	= None
	__autoload_filename	= None

	# -------------------------------------------------------------------
	# Singleton instantiation

	def __new__(cls, client_name):
		if cls.instance is None:
			cls.instance = Carla.instance = super().__new__(cls)
		return cls.instance

	@classmethod
	def delete(cls):
		"""
		Close the engine and delete the current instance to avoid hanging when exiting.
		"""
		cls.instance.engine_close()
		cls.instance = Carla.instance = None

	def __init__(self, client_name):
		"""
		client_name is the name which appears in JACK audio connection kit.
		"""
		if self.client_name is None:
			self.client_name = client_name
			self._plugins			= {}	# Plugin, indexed on Carla -generated "plugin_id"
			self._clients			= {}	# PatchbayClient, indexed on Carla -generated "client_id"
			self._sys_clients		= {}	# SystemPatchbayClient, indexed on "client_name"
			self._connections		= {}	# PatchbayConnection, indexed on Carla -generated "connection_id"
			self._plugin_by_uuid	= {}	# Plugin, indexed on "uuid", used for identifying plugin during instantiation
			self._uuid				= 0		# Current "uuid", incremented sequentially
			libname = "libcarla_standalone2.so"
			CarlaHostDLL.__init__(self, os.path.join(carla_binaries_path, libname), False)

			self._run_idle_loop = False
			self._engine_callback = EngineCallbackFunc(self.engine_callback)
			self.lib.carla_set_engine_callback(self.handle, self._engine_callback, None)
			self._file_callback = FileCallbackFunc(self.file_callback)
			self.lib.carla_set_file_callback(self.handle, self._file_callback, None)

			self.audioDriverForced = "JACK"
			self.forceStereo = False
			self.resetXruns = True
			self.transportMode = ENGINE_TRANSPORT_MODE_JACK
			self.maxParameters = 200
			self.preferPluginBridges = False
			self.preferUIBridges = True
			self.preventBadBehaviour = False
			self.uiBridgesTimeout = 4000
			self.uisAlwaysOnTop = True
			self.processMode = ENGINE_PROCESS_MODE_MULTIPLE_CLIENTS
			self.nextProcessMode = self.processMode
			self.processModeForced = True
			self.showLogs = False

			self.set_engine_option(ENGINE_OPTION_PATH_BINARIES, 0, carla_binaries_path)
			self.set_engine_option(ENGINE_OPTION_PATH_RESOURCES, 0, carla_resources_path)
			self.set_engine_option(ENGINE_OPTION_AUDIO_DRIVER, 0, self.audioDriverForced)
			self.set_engine_option(ENGINE_OPTION_FORCE_STEREO, self.forceStereo, "")
			self.set_engine_option(ENGINE_OPTION_RESET_XRUNS, self.resetXruns, "")
			self.set_engine_option(ENGINE_OPTION_TRANSPORT_MODE, self.transportMode, "")
			self.set_engine_option(ENGINE_OPTION_MAX_PARAMETERS, self.maxParameters, "")
			self.set_engine_option(ENGINE_OPTION_PREFER_PLUGIN_BRIDGES, self.preferPluginBridges, "")
			self.set_engine_option(ENGINE_OPTION_PREFER_UI_BRIDGES, self.preferUIBridges, "")
			self.set_engine_option(ENGINE_OPTION_PREVENT_BAD_BEHAVIOUR, self.preventBadBehaviour, "")
			self.set_engine_option(ENGINE_OPTION_UI_BRIDGES_TIMEOUT, self.uiBridgesTimeout, "")
			self.set_engine_option(ENGINE_OPTION_UIS_ALWAYS_ON_TOP, self.uisAlwaysOnTop, "")
			self.set_engine_option(ENGINE_OPTION_PROCESS_MODE, self.processMode, "")
			self.set_engine_option(ENGINE_OPTION_DEBUG_CONSOLE_OUTPUT, self.showLogs, "")
			self.set_engine_option(ENGINE_OPTION_CLIENT_NAME_PREFIX, 0, self.client_name)

	# -------------------------------------------------------------------
	# Engine control / idle loop

	def engine_init(self, driver_name = 'JACK'):
		"""
		Initialize the engine.
		Make sure to call carla_engine_idle() at regular intervals afterwards.
		driver_name:		Driver to use
		"""
		self.__engine_idle_thread = threading.Thread(target=self.__engine_idle)
		if super().engine_init(driver_name, self.client_name):
			self._run_idle_loop = True
			self.__engine_idle_thread.start()
			return True
		return False

	def set_ui_parent(self, window):
		"""
		Set the parent window of dialogs opened by the Carla engine.
		Not needed if the file open dialog will not be needed.
		"""
		self._file_callback_parent = window

	def engine_idle(self):
		"""
		Overrides CarlaHostDLL engine_idle() function, as this is handled internally.
		"""
		raise NotImplementedError()

	def __engine_idle(self):
		next_run_time = time.time()
		while self._run_idle_loop:
			with _engine_exclusive:
				CarlaHostDLL.engine_idle(self)
			next_run_time += self.idle_interval
			sleep_time = next_run_time - time.time()
			if sleep_time > 0:
				time.sleep(sleep_time)

	def engine_close(self):
		"""
		Close the engine.
		This function always closes the engine even if it returns false.
		In other words, even when something goes wrong when closing the engine it still be closed nonetheless.
		"""
		if self._run_idle_loop:
			self._run_idle_loop = False
			self.__engine_idle_thread.join()
		self.set_engine_about_to_close()
		return super().engine_close()

	# -------------------------------------------------------------------
	# Engine functions

	def is_engine_running(self):
		"""
		Check if the engine is running.
		"""
		return bool(self.lib.carla_is_engine_running(self.handle))

	def get_last_error(self):
		"""
		Get the last error.
		"""
		return charPtrToString(self.lib.carla_get_last_error(self.handle))

	@polite_function
	def clear_engine_xruns(self):
		"""
		Clear the xrun count on the engine, so that the next time carla_get_runtime_engine_info() is called, it returns 0.
		"""

		self.lib.carla_clear_engine_xruns(self.handle)

	@polite_function
	def cancel_engine_action(self):
		"""
		Tell the engine to stop the current cancelable action.
		"""
		self.lib.carla_cancel_engine_action(self.handle)

	def get_engine_driver_count(self):
		"""
		Get how many engine drivers are available.
		"""
		return int(self.lib.carla_get_engine_driver_count())

	def get_engine_driver_name(self, index):
		"""
		Get an engine driver name.
		index:		Driver index
		"""
		return charPtrToString(self.lib.carla_get_engine_driver_name(index))

	def get_engine_driver_device_names(self, index):
		"""
		Get the device names of an engine driver.
		index:		Driver index
		"""
		return charPtrPtrToStringList(self.lib.carla_get_engine_driver_device_names(index))

	def get_engine_driver_device_info(self, index, name):
		"""
		Get information about a device driver.
		index:		Driver index
		name:		Device name
		"""
		return structToDict(self.lib.carla_get_engine_driver_device_info(index, name.encode("utf-8")).contents)

	def get_runtime_engine_info(self):
		"""
		Get information about the currently running engine.
		"""
		return structToDict(self.lib.carla_get_runtime_engine_info(self.handle).contents)

	def get_runtime_engine_driver_device_info(self):
		"""
		Get information about the currently running engine driver device.
		"""
		return structToDict(self.lib.carla_get_runtime_engine_driver_device_info(self.handle).contents)

	def show_engine_device_control_panel(self):
		"""
		Show the custom control panel for the current engine device.
		@see ENGINE_DRIVER_DEVICE_HAS_CONTROL_PANEL
		"""
		return bool(self.lib.carla_show_engine_device_control_panel(self.handle))

	def show_engine_driver_device_control_panel(self, index, name):
		"""
		Show a device custom control panel.
		@see ENGINE_DRIVER_DEVICE_HAS_CONTROL_PANEL
		index:		Driver index
		name:		Device name
		"""
		return bool(self.lib.carla_show_engine_driver_device_control_panel(index, name.encode("utf-8")))

	def set_engine_about_to_close(self):
		"""
		Tell the engine it's about to close.
		This is used to prevent the engine thread(s) from reactivating.
		"""
		return bool(self.lib.carla_set_engine_about_to_close(self.handle))

	def set_engine_option(self, option, value, string_value):
		"""
		Set an engine option.
		option:			Option
		value:			Value as number
		string_value:	Value as string
		"""
		self.lib.carla_set_engine_option(self.handle, option, value, string_value.encode("utf-8"))

	def set_engine_buffer_size_and_sample_rate(self, buffer_size, sample_rate):
		"""
		Dynamically change buffer size and/or sample rate while engine is running.
		@see ENGINE_DRIVER_DEVICE_VARIABLE_BUFFER_SIZE
		@see ENGINE_DRIVER_DEVICE_VARIABLE_SAMPLE_RATE
		"""
		return bool(self.lib.carla_set_engine_buffer_size_and_sample_rate(self.handle, buffer_size, sample_rate))

	def get_buffer_size(self):
		"""
		Get the current engine buffer size.
		"""
		return int(self.lib.carla_get_buffer_size(self.handle))

	def get_sample_rate(self):
		"""
		Get the current engine sample rate.
		"""
		return float(self.lib.carla_get_sample_rate(self.handle))

	# -------------------------------------------------------------------
	# Load / save file functions

	@polite_function
	def load_file(self, filename):
		"""
		Load a file of any type.
		This will try to load a generic file as a plugin,
		either by direct handling (SF2 and SFZ) or by using an internal plugin (like Audio and MIDI).
		@see carla_get_supported_file_extensions()
		"""
		return bool(self.lib.carla_load_file(self.handle, filename.encode("utf-8")))

	@polite_function
	def load_project(self, filename):
		"""
		Load a Carla project file.
		@note Currently loaded plugins are not removed; call carla_remove_all_plugins() first if needed.
		"""
		return bool(self.lib.carla_load_project(self.handle, filename.encode("utf-8")))

	@polite_function
	def save_project(self, filename):
		"""
		Save current project to a file.
		"""
		return bool(self.lib.carla_save_project(self.handle, filename.encode("utf-8")))

	@polite_function
	def clear_project_filename(self):
		"""
		Clear the currently set project filename.
		"""
		self.lib.carla_clear_project_filename(self.handle)

	# -------------------------------------------------------------------
	# Patchbay connection functions

	@polite_function
	def patchbay_connect(self, external, group_id_a, port_id_a, group_id_b, port_id_b):
		"""
		Connect two patchbay ports.
		group_id_a:		Output group
		port_id_a:		Output port
		group_id_b:		Input group
		port_id_b:		Input port
		@see ENGINE_CALLBACK_PATCHBAY_CONNECTION_ADDED
		"""
		return bool(self.lib.carla_patchbay_connect(self.handle, external, group_id_a, port_id_a, group_id_b, port_id_b))

	@polite_function
	def patchbay_disconnect(self, external, connection_id):
		"""
		Disconnect two patchbay ports.
		connection_id:		Connection Id
		@see ENGINE_CALLBACK_PATCHBAY_CONNECTION_REMOVED
		"""
		return bool(self.lib.carla_patchbay_disconnect(self.handle, external, connection_id))

	def patchbay_set_group_pos(self, external, group_id, x1, y1, x2, y2):
		"""
		Set the position of a group.
		This is purely cached and saved in the project file, Carla backend does nothing with the value.
		When loading a project, callbacks are used to inform of the previously saved positions.
		@see ENGINE_CALLBACK_PATCHBAY_CLIENT_POSITION_CHANGED
		"""
		return bool(self.lib.carla_patchbay_set_group_pos(self.handle, external, group_id, x1, y1, x2, y2))

	def patchbay_refresh(self, external):
		"""
		Force the engine to resend all patchbay clients, ports and connections again.
		external:		Wherever to show external/hardware ports instead of internal ones.
						Only valid in patchbay engine mode, other modes will ignore this.
		"""
		return bool(self.lib.carla_patchbay_refresh(self.handle, external))

	# -------------------------------------------------------------------
	# Transport functions

	@polite_function
	def transport_play(self):
		"""
		Start playback of the engine transport.
		"""
		self.lib.carla_transport_play(self.handle)

	@polite_function
	def transport_pause(self):
		"""
		Pause the engine transport.
		"""
		self.lib.carla_transport_pause(self.handle)

	@polite_function
	def transport_bpm(self, bpm):
		"""
		Set the bpm of the engine transport.
		"""
		self.lib.carla_transport_bpm(self.handle, bpm)

	@polite_function
	def transport_relocate(self, frame):
		"""
		Relocate the engine transport to a specific frame.
		"""
		self.lib.carla_transport_relocate(self.handle, frame)

	def get_current_transport_frame(self):
		"""
		Get the current transport frame.
		"""
		return int(self.lib.carla_get_current_transport_frame(self.handle))

	def get_transport_info(self):
		"""
		Get the engine transport information, i.e.:
		{'playing': False, 'frame': 53248, 'bar': 1, 'beat': 3, 'tick': 7, 'bpm': 109.0002}
		"""
		return structToDict(self.lib.carla_get_transport_info(self.handle).contents)

	# -------------------------------------------------------------------
	# Plugin add / remove / save / restore

	def get_max_plugin_number(self):
		"""
		Maximum number of loadable plugins allowed.
		Returns 0 if engine is not started.
		"""
		return int(self.lib.carla_get_max_plugin_number(self.handle))

	def get_current_plugin_count(self):
		"""
		Current number of plugins loaded.
		"""
		return int(self.lib.carla_get_current_plugin_count(self.handle))

	def _add_plugin(self, btype, ptype, filename, name, label, unique_id, extra_pointer, options):
		"""
		Add a new plugin.
		If you don't know the binary type use the BINARY_NATIVE macro.
		btype:			Binary type
		ptype:			Plugin type
		filename:		Filename, if applicable
		name:			Name of the plugin, can be NULL
		label:			Plugin label, if applicable
		unique_id:		Plugin unique Id, if applicable
		extra_pointer:	Extra pointer, defined per plugin type
		options:		Initial plugin options
		"""
		cfilename = filename.encode("utf-8") if filename else None
		cname = name.encode("utf-8") if name else None
		if ptype == PLUGIN_JACK:
			clabel = bytes(ord(b) for b in label)
		else:
			clabel = label.encode("utf-8") if label else None
		return bool(self.lib.carla_add_plugin(self.handle, btype, ptype, cfilename, cname, clabel, unique_id, cast(extra_pointer, c_void_p), options))

	@polite_function
	def remove_plugin(self, plugin_id):
		"""
		Remove a plugin.
		plugin_id:		Plugin to remove.
		"""
		if not self.lib.carla_remove_plugin(self.handle, plugin_id):
			raise RuntimeError('Carla will not remove plugin')

	@polite_function
	def remove_all_plugins(self):
		"""
		Remove all plugins.
		"""
		for plugin in self._plugin_by_uuid.values():
			plugin.removing_from_carla = True
		return bool(self.lib.carla_remove_all_plugins(self.handle))

	@polite_function
	def rename_plugin(self, plugin_id, new_name):
		"""
		Rename a plugin.
		Returns the new name, or NULL if the operation failed.
		plugin_id:		Plugin to rename
		new_name:		New plugin name
		"""
		return bool(self.lib.carla_rename_plugin(self.handle, plugin_id, new_name.encode("utf-8")))

	@polite_function
	def clone_plugin(self, plugin_id):
		"""
		Clone a plugin.
		plugin_id:		Plugin to clone
		"""
		return bool(self.lib.carla_clone_plugin(self.handle, plugin_id))

	@polite_function
	def replace_plugin(self, plugin_id):
		"""
		Prepare replace of a plugin.
		The next call to carla_add_plugin() will use this id, replacing the current plugin.
		plugin_id:		Plugin to replace
		@note This function requires carla_add_plugin() to be called afterwards *as soon as possible*.
		"""
		return bool(self.lib.carla_replace_plugin(self.handle, plugin_id))

	@polite_function
	def switch_plugins(self, plugin_id_a, plugin_id_b):
		"""
		Switch two plugins positions.
		plugin_id_a:	Plugin A
		plugin_id_b:	Plugin B
		"""
		return bool(self.lib.carla_switch_plugins(self.handle, plugin_id_a, plugin_id_b))

	@polite_function
	def load_plugin_state(self, plugin_id, filename):
		"""
		Load a plugin state.
		plugin_id:		Plugin
		filename:		Path to plugin state
		@see carla_save_plugin_state()
		"""
		return bool(self.lib.carla_load_plugin_state(self.handle, plugin_id, filename.encode("utf-8")))

	@polite_function
	def save_plugin_state(self, plugin_id, filename):
		"""
		Save a plugin state.
		plugin_id:		Plugin
		filename:		Path to plugin state
		@see carla_load_plugin_state()
		"""
		return bool(self.lib.carla_save_plugin_state(self.handle, plugin_id, filename.encode("utf-8")))

	@polite_function
	def export_plugin_lv2(self, plugin_id, lv2_path):
		"""
		Export plugin as LV2.
		plugin_id:		Plugin
		lv2_path:		Path to lv2 plugin folder
		"""
		return bool(self.lib.carla_export_plugin_lv2(self.handle, plugin_id, lv2_path.encode("utf-8")))

	# -------------------------------------------------------------------
	# Plugin information

	def get_plugin_info(self, plugin_id):
		"""
		Get information from a plugin.
		plugin_id:		Plugin
		"""
		return structToDict(self.lib.carla_get_plugin_info(self.handle, plugin_id).contents)

	def get_real_plugin_name(self, plugin_id):
		"""
		Get a plugin's real name.
		This is the name the plugin uses to identify itself; may not be unique.
		plugin_id:		Plugin
		"""
		return charPtrToString(self.lib.carla_get_real_plugin_name(self.handle, plugin_id))

	def get_audio_port_count_info(self, plugin_id):
		"""
		Get audio port count information from a plugin.
		plugin_id:		Plugin
		"""
		return structToDict(self.lib.carla_get_audio_port_count_info(self.handle, plugin_id).contents)

	def get_midi_port_count_info(self, plugin_id):
		"""
		Get MIDI port count information from a plugin.
		plugin_id:		Plugin
		"""
		return structToDict(self.lib.carla_get_midi_port_count_info(self.handle, plugin_id).contents)

	def get_parameter_count(self, plugin_id):
		"""
		Get how many parameters a plugin has.
		plugin_id:		Plugin
		"""
		return int(self.lib.carla_get_parameter_count(self.handle, plugin_id))

	def get_parameter_count_info(self, plugin_id):
		"""
		Get parameter count information from a plugin.
		plugin_id:		Plugin
		"""
		return structToDict(self.lib.carla_get_parameter_count_info(self.handle, plugin_id).contents)

	# -------------------------------------------------------------------
	# Plugin options

	@polite_function
	def set_ctrl_channel(self, plugin_id, channel):
		"""
		Change a plugin's internal control channel.
		plugin_id:		Plugin
		channel:		New channel
		"""
		self.lib.carla_set_ctrl_channel(self.handle, plugin_id, channel)

	@polite_function
	def set_program(self, plugin_id, program_id):
		"""
		Change a plugin's current program.
		plugin_id:		Plugin
		program_id:		New program
		"""
		self.lib.carla_set_program(self.handle, plugin_id, program_id)

	@polite_function
	def set_option(self, plugin_id, option, state):
		"""
		Enable a plugin's option.
		plugin_id:		Plugin
		option:			An option from PluginOptions
		state:			New enabled state
		"""
		self.lib.carla_set_option(self.handle, plugin_id, option, state)

	# -------------------------------------------------------------------
	# Plugin values

	@polite_function
	def set_active(self, plugin_id, state):
		"""
		Enable or disable a plugin.
		plugin_id:		Plugin
		state:			New active state
		"""
		self.lib.carla_set_active(self.handle, plugin_id, state)

	def set_drywet(self, plugin_id, value):
		"""
		Change a plugin's internal dry/wet.
		plugin_id:		Plugin
		value:			New dry/wet value
		"""
		self.lib.carla_set_drywet(self.handle, plugin_id, value)

	def set_volume(self, plugin_id, value):
		"""
		Change a plugin's internal volume.
		plugin_id:		Plugin
		value:			New volume
		"""
		self.lib.carla_set_volume(self.handle, plugin_id, value)

	def set_balance_left(self, plugin_id, value):
		"""
		Change a plugin's internal stereo balance, left channel.
		plugin_id:		Plugin
		value:			New value
		"""
		self.lib.carla_set_balance_left(self.handle, plugin_id, value)

	def set_balance_right(self, plugin_id, value):
		"""
		Change a plugin's internal stereo balance, right channel.
		plugin_id:		Plugin
		value:			New value
		"""
		self.lib.carla_set_balance_right(self.handle, plugin_id, value)

	def set_panning(self, plugin_id, value):
		"""
		Change a plugin's internal mono panning value.
		plugin_id:		Plugin
		value:			New value
		"""
		self.lib.carla_set_panning(self.handle, plugin_id, value)

	def get_input_peak_value(self, plugin_id, left_value):
		"""
		Get a plugin's input peak value.
		plugin_id:		Plugin
		left_value:		Wherever to get the left/mono value, otherwise right.
		"""
		return float(self.lib.carla_get_input_peak_value(self.handle, plugin_id, left_value))

	def get_output_peak_value(self, plugin_id, left_value):
		"""
		Get a plugin's output peak value.
		plugin_id:		Plugin
		left_value:		Wherever to get the left/mono value, otherwise right.
		"""
		return float(self.lib.carla_get_output_peak_value(self.handle, plugin_id, left_value))

	# -------------------------------------------------------------------
	# Plugin parameter information / values

	def get_parameter_info(self, plugin_id, parameter_id):
		"""
		Get parameter information from a plugin.
		plugin_id:		Plugin
		parameter_id:	Parameter index
		@see carla_get_parameter_count()
		"""
		return structToDict(self.lib.carla_get_parameter_info(self.handle, plugin_id, parameter_id).contents)

	def get_parameter_ranges(self, plugin_id, parameter_id):
		"""
		Get a plugin's parameter ranges.
		plugin_id:		Plugin
		parameter_id:	Parameter index
		@see carla_get_parameter_count()
		"""
		return structToDict(self.lib.carla_get_parameter_ranges(self.handle, plugin_id, parameter_id).contents)

	def get_parameter_scalepoint_info(self, plugin_id, parameter_id, scale_point_id):
		"""
		Get parameter scale point information from a plugin.
		plugin_id:		Plugin
		parameter_id:	Parameter index
		scale_point_id:	Parameter scale-point index
		@see CarlaParameterInfo::scalePointCount
		"""
		return structToDict(self.lib.carla_get_parameter_scalepoint_info(self.handle, plugin_id, parameter_id, scale_point_id).contents)

	def get_parameter_data(self, plugin_id, parameter_id):
		"""
		Get a plugin's parameter data.
		plugin_id:		Plugin
		parameter_id:	Parameter index
		@see carla_get_parameter_count()
		"""
		return structToDict(self.lib.carla_get_parameter_data(self.handle, plugin_id, parameter_id).contents)

	def get_parameter_text(self, plugin_id, parameter_id):
		"""
		Get a plugin's parameter text (custom display of internal values).
		plugin_id:		Plugin
		parameter_id:	Parameter index
		@see PARAMETER_USES_CUSTOM_TEXT
		"""
		return charPtrToString(self.lib.carla_get_parameter_text(self.handle, plugin_id, parameter_id))

	def get_default_parameter_value(self, plugin_id, parameter_id):
		"""
		Get a plugin's default parameter value.
		plugin_id:		Plugin
		parameter_id:	Parameter index
		"""
		return float(self.lib.carla_get_default_parameter_value(self.handle, plugin_id, parameter_id))

	def get_current_parameter_value(self, plugin_id, parameter_id):
		"""
		Get a plugin's current parameter value.
		plugin_id:		Plugin
		parameter_id:	Parameter index
		"""
		return float(self.lib.carla_get_current_parameter_value(self.handle, plugin_id, parameter_id))

	def get_internal_parameter_value(self, plugin_id, parameter_id):
		"""
		Get a plugin's internal parameter value.
		plugin_id:		Plugin
		parameter_id:	Parameter index, maybe be negative
		@see InternalParameterIndex
		"""
		return float(self.lib.carla_get_internal_parameter_value(self.handle, plugin_id, parameter_id))

	def set_parameter_value(self, plugin_id, parameter_id, value):
		"""
		Change a plugin's parameter value.
		plugin_id:		Plugin
		parameter_id:	Parameter index
		value:			New value
		"""
		self.lib.carla_set_parameter_value(self.handle, plugin_id, parameter_id, value)

	def reset_parameters(self, plugin_id):
		"""
		Reset all plugin's parameters.
		plugin_id:		Plugin
		"""
		self.lib.carla_reset_parameters(self.handle, plugin_id)

	def randomize_parameters(self, plugin_id):
		"""
		Randomize all plugin's parameters.
		plugin_id:		Plugin
		"""
		self.lib.carla_randomize_parameters(self.handle, plugin_id)

	# -------------------------------------------------------------------
	# Plugin custom / chunk data

	def get_custom_data_count(self, plugin_id):
		"""
		Get how many custom data sets a plugin has.
		plugin_id:		Plugin
		@see carla_get_custom_data()
		"""
		return int(self.lib.carla_get_custom_data_count(self.handle, plugin_id))

	def get_custom_data(self, plugin_id, custom_data_id):
		"""
		Get a plugin's custom data, using index.
		plugin_id:		Plugin
		custom_data_id:	Custom data index
		@see carla_get_custom_data_count()
		"""
		return structToDict(self.lib.carla_get_custom_data(self.handle, plugin_id, custom_data_id).contents)

	def get_custom_data_value(self, plugin_id, type_, key):
		"""
		Get a plugin's custom data value, using type and key.
		plugin_id:		Plugin
		type:			Custom data type
		key:			Custom data key
		@see carla_get_custom_data_count()
		"""
		return charPtrToString(self.lib.carla_get_custom_data_value(self.handle, plugin_id, type_.encode("utf-8"), key.encode("utf-8")))

	def set_custom_data(self, plugin_id, type_, key, value):
		"""
		Set a plugin's custom data set.
		plugin_id:		Plugin
		type:			Type
		key:			Key
		value:			New value
		@see CustomDataTypes and CustomDataKeys
		"""
		self.lib.carla_set_custom_data(self.handle, plugin_id, type_.encode("utf-8"), key.encode("utf-8"), value.encode("utf-8"))

	def get_chunk_data(self, plugin_id):
		"""
		Get a plugin's chunk data.
		plugin_id:		Plugin
		@see PLUGIN_OPTION_USE_CHUNKS
		"""
		return charPtrToString(self.lib.carla_get_chunk_data(self.handle, plugin_id))

	def set_chunk_data(self, plugin_id, chunk_data):
		"""
		Set a plugin's chunk data.
		plugin_id:		Plugin
		chunk_data:		New chunk data
		@see PLUGIN_OPTION_USE_CHUNKS and carla_get_chunk_data()
		"""
		self.lib.carla_set_chunk_data(self.handle, plugin_id, chunk_data.encode("utf-8"))

	def prepare_for_save(self, plugin_id):
		"""
		Tell a plugin to prepare for save.
		This should be called before saving custom data sets.
		plugin_id:		Plugin
		"""
		self.lib.carla_prepare_for_save(self.handle, plugin_id)

	# -------------------------------------------------------------------
	# Program functions

	def get_program_count(self, plugin_id):
		"""
		Get how many programs a plugin has.
		plugin_id:		Plugin
		@see carla_get_program_name()
		"""
		return int(self.lib.carla_get_program_count(self.handle, plugin_id))

	def get_current_program_index(self, plugin_id):
		"""
		Get a plugin's program index.
		plugin_id:		Plugin
		"""
		return int(self.lib.carla_get_current_program_index(self.handle, plugin_id))

	def get_program_name(self, plugin_id, program_id):
		"""
		Get a plugin's program name.
		plugin_id:		Plugin
		program_id:		Program index
		@see carla_get_program_count()
		"""
		return charPtrToString(self.lib.carla_get_program_name(self.handle, plugin_id, program_id))

	# -------------------------------------------------------------------
	# MIDI program functions

	def get_midi_program_count(self, plugin_id):
		"""
		Get how many MIDI programs a plugin has.
		plugin_id:			Plugin
		@see carla_get_midi_program_name() and carla_get_midi_program_data()
		"""
		return int(self.lib.carla_get_midi_program_count(self.handle, plugin_id))

	def get_midi_program_name(self, plugin_id, midi_program_id):
		"""
		Get a plugin's MIDI program name.
		plugin_id:			Plugin
		midi_program_id:	MIDI Program index
		@see carla_get_midi_program_count()
		"""
		return charPtrToString(self.lib.carla_get_midi_program_name(self.handle, plugin_id, midi_program_id))

	def get_midi_program_data(self, plugin_id, midi_program_id):
		"""
		Get a plugin's MIDI program data.
		plugin_id:			Plugin
		midi_program_id:	MIDI Program index
		@see carla_get_midi_program_count()
		"""
		return structToDict(self.lib.carla_get_midi_program_data(self.handle, plugin_id, midi_program_id).contents)

	def get_current_midi_program_index(self, plugin_id):
		"""
		Get a plugin's midi program index.
		plugin_id:			Plugin
		"""
		return int(self.lib.carla_get_current_midi_program_index(self.handle, plugin_id))

	def set_midi_program(self, plugin_id, midi_program_id):
		"""
		Change a plugin's current MIDI program.
		plugin_id:			Plugin
		midi_program_id:	New value
		"""
		self.lib.carla_set_midi_program(self.handle, plugin_id, midi_program_id)

	# -------------------------------------------------------------------
	# Mapped controls

	@polite_function
	def set_parameter_midi_channel(self, plugin_id, parameter_id, channel):
		"""
		Change a plugin's parameter MIDI channel.
		plugin_id:		Plugin
		parameter_id:	Parameter index
		channel:		New control index
		"""
		self.lib.carla_set_parameter_midi_channel(self.handle, plugin_id, parameter_id, channel)

	@polite_function
	def set_parameter_mapped_control_index(self, plugin_id, parameter_id, index):
		"""
		Change a plugin's parameter MIDI channel.
		plugin_id:		Plugin
		parameter_id:	Parameter index
		channel:		New control index
		"""
		self.lib.carla_set_parameter_mapped_control_index(self.handle, plugin_id, parameter_id, index)

	@polite_function
	def set_parameter_mapped_range(self, plugin_id, parameter_id, minimum, maximum):
		"""
		Change a plugin's parameter mapped range.
		plugin_id:		Plugin
		parameter_id:	Parameter index
		minimum:		New mapped minimum
		maximum:		New mapped maximum
		"""
		self.lib.carla_set_parameter_mapped_range(self.handle, plugin_id, parameter_id, minimum, maximum)

	@polite_function
	def set_parameter_touch(self, plugin_id, parameter_id, touch):
		"""
		Change a plugin's parameter in drag/touch mode state.
		Usually happens from a UI when the user is moving a parameter with a mouse or similar input.
		plugin_id:		Plugin
		parameter_id:	Parameter index
		touch:			New state
		"""
		self.lib.carla_set_parameter_touch(self.handle, plugin_id, parameter_id, touch)

	# -------------------------------------------------------------------
	# MIDI

	@polite_function
	def send_midi_note(self, plugin_id, channel, note, velocity):
		"""
		Send a single note of a plugin.
		If velocity is 0, note-off is sent; note-on otherwise.
		plugin_id:		Plugin
		channel:		Note channel
		note:			Note pitch
		velocity:		Note velocity
		"""
		self.lib.carla_send_midi_note(self.handle, plugin_id, channel, note, velocity)

	# -------------------------------------------------------------------
	# UI / inline display

	@polite_function
	def show_custom_ui(self, plugin_id, state):
		"""
		Tell a plugin to show its own custom UI.
		plugin_id:		Plugin
		state:			New UI state, visible or not
		@see PLUGIN_HAS_CUSTOM_UI
		"""
		self.lib.carla_show_custom_ui(self.handle, plugin_id, state)

	@polite_function
	def render_inline_display(self, plugin_id, width, height):
		"""
		Render a plugin's inline display.
		plugin_id:		Plugin
		"""
		ptr = self.lib.carla_render_inline_display(self.handle, plugin_id, width, height)
		if not ptr or not ptr.contents:
			return None
		contents = ptr.contents
		datalen = contents.height * contents.stride
		databuf = pack("%iB" % datalen, *contents.data[:datalen])
		return {
			'data': databuf,
			'width': contents.width,
			'height': contents.height,
			'stride': contents.stride,
		}

	# ---
	# OSC

	def get_host_osc_url_tcp(self):
		"""
		Get the current engine OSC URL (TCP).
		"""
		return charPtrToString(self.lib.carla_get_host_osc_url_tcp(self.handle))

	def get_host_osc_url_udp(self):
		"""
		Get the current engine OSC URL (UDP).
		"""
		return charPtrToString(self.lib.carla_get_host_osc_url_udp(self.handle))

	# ---
	# NSM

	@polite_function
	def nsm_init(self, pid, executable_name):
		"""
		Initialize NSM (that is, announce ourselves to it).
		Must be called as early as possible in the program's lifecycle.
		Returns true if NSM is available and initialized correctly.
		"""
		return bool(self.lib.carla_nsm_init(self.handle, pid, executable_name.encode("utf-8")))

	@polite_function
	def nsm_ready(self, opcode):
		"""
		Respond to an NSM callback.
		"""
		self.lib.carla_nsm_ready(self.handle, opcode)

	# -------------------------------------------------------------------
	# Plugin-related engine callback functions

	def cb_plugin_added(self, plugin_id, plugin_type, carla_plugin_name):
		"""
		After Carla adds a plugin, it signals this with an assigned plugin_id. This
		function uses the uuid given to the Plugin by this class to retrieve the
		plugin from the "_plugin_by_uuid" dict, and add the association with the plugin_id in
		the "_plugins" dict.
		"""
		if plugin_id in self._plugins:
			logging.warning('cb_plugin_added: Cannot add plugin %s', plugin_id)
			logging.warning('"%s" - plugin %s already in _plugins"', carla_plugin_name, self._plugins[plugin_id])
			return
		if carla_plugin_name in self._plugin_by_uuid:
			self._plugins[plugin_id] = self._plugin_by_uuid[carla_plugin_name]
			self._plugins[plugin_id].post_embed_init(plugin_id) 		# Set up parameters, etc.
		else:
			logging.warning('cb_plugin_added: Plugin "%s" not found in _plugin_by_uuid when added', carla_plugin_name)

	def cb_plugin_removed(self, plugin_id):
		if plugin_id in self._plugins:
			plugin = self._plugins[plugin_id]
			if plugin.uuid in self._plugin_by_uuid:
				del self._plugin_by_uuid[plugin.uuid]
			else:
				logging.warning('cb_plugin_removed: "%s" uuid %s not in self._plugin_by_uuid', plugin, plugin.uuid)
			self._alert_plugin_removed(plugin)
			# Renumber plugins per Carla plugin_id conventions:
			for i in range(plugin_id, len(self._plugins) - 1):
				self._plugins[i] = self._plugins[i + 1]
				self._plugins[i].plugin_id_changed(i)
			self._plugins.pop(len(self._plugins) - 1)
			plugin.got_removed()
			if self.is_clear():
				self._alert_last_plugin_removed()
		else:
			logging.warning('cb_plugin_removed: Plugin removed (%d) not in _plugins', plugin_id)

	def cb_plugin_renamed(self, plugin_id, new_name):
		self._plugins[plugin_id].plugin_renamed(new_name)

	def cb_plugin_unavailable(self, plugin_id, errorMsg):
		self._plugins[plugin_id].plugin_unavailable(error_msg)

	def cb_parameter_value_changed(self, plugin_id, index, value):
		if plugin_id in self._plugins:
			plugin = self._plugins[plugin_id]
			if index == PARAMETER_NULL:
				return
			elif index == PARAMETER_ACTIVE:
				plugin.active = value != 0
			elif index == PARAMETER_DRYWET:
				plugin.dry_wet = value
			elif index == PARAMETER_VOLUME:
				plugin.volume = value
			elif index == PARAMETER_BALANCE_LEFT:
				plugin.balance_left = value
			elif index == PARAMETER_BALANCE_RIGHT:
				plugin.balance_right = value
			elif index == PARAMETER_PANNING:
				plugin.panning = value
			elif index == PARAMETER_CTRL_CHANNEL:
				plugin.ctrl_channel = value
			elif index == PARAMETER_MAX:
				return
			else:
				if index in plugin.parameters:
					parameter = plugin.parameters[index]
					parameter.internal_value_changed(value)
					plugin.parameter_internal_value_changed(parameter, value)
				else:
					logging.error('Parameter index not in plugin.parameters')
		else:
			logging.debug('cb_parameter_value_changed: plugin_id %s not in self._plugins', plugin_id)

	def cb_parameter_default_changed(self, plugin_id, index, value):
		self._plugins[plugin_id].parameter_default_changed(index, value)

	def cb_parameter_mapped_control_index_changed(self, plugin_id, index, ctrl):
		self._plugins[plugin_id].parameter_mapped_control_index_changed(index, ctrl)

	def cb_parameter_mapped_range_changed(self, plugin_id, index, minimum, maximum):
		self._plugins[plugin_id].parameter_mapped_range_changed(index, minimum, maximum)

	def cb_parameter_midi_channel_changed(self, plugin_id, index, channel):
		self._plugins[plugin_id].parameter_midi_channel_changed(index, channel)

	def cb_program_changed(self, plugin_id, index):
		self._plugins[plugin_id].program_changed(index)

	def cb_midi_program_changed(self, plugin_id, index):
		self._plugins[plugin_id].midi_program_changed(index)

	def cb_option_changed(self, plugin_id, option, state):
		self._plugins[plugin_id].option_changed(option, state)

	def cb_ui_state_changed(self, plugin_id, state):
		self._plugins[plugin_id].ui_state_changed(state)

	def cb_note_on(self, plugin_id, channel, note, velocity):
		self._plugins[plugin_id].note_on(channel, note, velocity)

	def cb_note_off(self, plugin_id, channel, note):
		self._plugins[plugin_id].note_off(channel, note)

	def cb_update(self, plugin_id):
		self._plugins[plugin_id].update()

	def cb_reload_info(self, plugin_id):
		self._plugins[plugin_id].reload_info()

	def cb_reload_parameters(self, plugin_id):
		self._plugins[plugin_id].reload_parameters()

	def cb_reload_programs(self, plugin_id):
		self._plugins[plugin_id].reload_programs()

	def cb_reload_all(self, plugin_id):
		self._plugins[plugin_id].reload_all(self)

	def cb_inline_display_redraw(self, plugin_id):
		self._plugins[plugin_id].inline_display_redraw()

	def cb_debug(self, plugin_id, value1, value2, value3, valuef, valueStr):
		self._plugins[plugin_id].debug(value1, value2, value3, valuef, value_str)

	# -------------------------------------------------------------------
	# Patchbay-related engine callback functions

	def cb_patchbay_client_added(self, client_id, client_icon, plugin_id, client_name):
		"""
		After Carla adds a plugin, it creates patchbay clients and patchbay ports for
		each plugin. This function uses the "client_name" to identity the plugin, and
		assign it a "client_id". Then it is added to the "_clients" dict, which is
		used to reference patchbay clients henceforth.

		Clients which are not plugins added via this class become "System Clients".
		Notification of their existence is made using the method appropriate to the
		class/enviroment used. If Qt, sig_patchbay_client_added is emitted. If non-Qt,
		use "on_client_added".
		"""
		if client_id in self._clients:
			return logging.warning('cb_patchbay_client_added: "%s" already in _clients as "%s"',
				self._clients[client_id], client_name)
		plugin_uuid = client_name.rsplit("/")[-1]
		if plugin_uuid in self._plugin_by_uuid:
			plugin = self._plugin_by_uuid[plugin_uuid]
			plugin.client_id = client_id
			plugin.client_name = client_name
			self._clients[client_id] = plugin
		else:
			self._clients[client_id] = SystemPatchbayClient(client_id, client_name)
			self._sys_clients[client_name] = self._clients[client_id]
		self._alert_client_added(self._clients[client_id])
		return None

	def cb_patchbay_client_removed(self, client_id):
		"""
		Called when a client, either a managed plugin or a "SystemClient", is removed.

		Clients which are not plugins added via this class become "System Clients".
		Notification of their existence is made using the method appropriate to the
		class/enviroment used. If Qt, sig_patchbay_client_removed is emitted. If non-Qt,
		use "on_client_removed".
		"""
		if client_id in self._clients:
			client = self._clients[client_id]
			self._alert_client_removed(client)
			client.client_removed()
			if client.client_name in self._sys_clients:
				del self._sys_clients[client.client_name]
			del self._clients[client_id]
		else:
			logging.warning('cb_patchbay_client_removed: Client removed (%s) not in _clients', client_id)

	def cb_patchbay_client_renamed(self, client_id, new_client_name):
		logging.debug('cb_patchbay_client_renamed: "%s" new name: "%s"',
			self._clients[client_id], new_client_name)
		client = self._clients[client_id]
		if client.client_name in self._sys_clients:
			del self._sys_clients[client.client_name]
			self._sys_clients[new_client_name] = client
		self._clients[client_id].client_renamed(new_client_name)

	def cb_patchbay_client_data_changed(self, client_id, client_icon, plugin_id):
		logging.debug('cb_patchbay_client_data_changed: %s', self._clients[client_id])

	def cb_patchbay_client_position_changed(self, client_id, x1, y1, x2, y2):
		logging.debug('cb_patchbay_client_position_changed: %s', self._clients[client_id])

	def cb_patchbay_port_added(self, client_id, port_id, port_flags, group_id, port_name):
		if client_id in self._clients:
			self._clients[client_id].port_added(port_id, port_flags, group_id, port_name)
			self._alert_port_added(self._clients[client_id].ports[port_id])
		else:
			logging.warning('cb_patchbay_port_added: client %s not in _clients', client_id)

	def cb_patchbay_port_removed(self, client_id, port_id):
		if client_id in self._clients:
			self._alert_port_removed(self._clients[client_id].ports[port_id])
			self._clients[client_id].port_removed(port_id)
		else:
			logging.warning('cb_patchbay_port_removed: client %s not in _clients', client_id)

	def cb_patchbay_port_changed(self, client_id, port_id, port_flags, group_id, new_port_name):
		logging.debug('cb_patchbay_port_changed: client_id %s port_id %s group_id %s new_port_name %s',
			client_id, port_id, group_id, new_port_name)

	def cb_patchbay_port_group_added(self, client_id, port_id, group_id, new_port_name):
		logging.debug('cb_patchbay_port_group_added: groupId %s port_id %s group_id %s new_port_name %s',
			groupId, port_id, group_id, new_port_name)

	def cb_patchbay_port_group_removed(self, groupId, port_id):
		logging.debug('cb_patchbay_port_group_removed: groupId %s port_id %s',
			groupId, port_id)

	def cb_patchbay_port_group_changed(self, groupId, port_id, group_id, new_port_name):
		logging.debug('cb_patchbay_port_group_changed: groupId %s port_id %s group_id %s new_port_name %s',
			groupId, port_id, group_id, new_port_name)

	def cb_patchbay_connection_added(self, connection_id, client_out_id, port_out_id, client_in_id, port_in_id):
		"""
		Handles patchbay changes. Passes notification of change to the clients.
		"""
		out_client = self._clients[client_out_id]
		in_client = self._clients[client_in_id]
		out_port = out_client.ports[port_out_id]
		in_port = in_client.ports[port_in_id]
		connection = PatchbayConnection(connection_id, out_port, in_port)
		self._connections[connection_id] = connection
		out_port.connection_added(connection)
		in_port.connection_added(connection)
		out_client.output_connection_change(connection, True)
		in_client.input_connection_change(connection, True)
		self._alert_connection_added(connection)

	def cb_patchbay_connection_removed(self, connection_id, zero_1, zero_2):
		"""
		Handles patchbay changes. Passes notification of change to the clients.
		"""
		if connection_id in self._connections:
			connection = self._connections[connection_id]
			connection.out_port.connection_removed(connection)
			connection.in_port.connection_removed(connection)
			self._clients[connection.out_port.client_id].output_connection_change(connection, False)
			self._clients[connection.in_port.client_id].input_connection_change(connection, False)
			self._alert_connection_removed(connection)
			del self._connections[connection_id]
		else:
			logging.warning('cb_patchbay_connection_removed: Connection %s not in ._connections',
				connection_id)

	# ================================================================================
	# Top-level plugin functions
	# ================================================================================

	def add_plugin(self, plugin):
		self._plugin_by_uuid[plugin.uuid] = plugin
		if self.is_engine_running():
			if not self._add_plugin(						# Carla parameter
				# ----------------------------------------- # ---------------
				plugin.plugin_def['build'],					# btype
				plugin.plugin_def['type'],					# ptype
				plugin.plugin_def['filename'],				# filename
				plugin.uuid,								# name
				plugin.plugin_def['label'],					# label
				int(plugin.plugin_def['uniqueId'] or 0),	# uniqueId
				None,										# extraPtr
				PLUGIN_OPTIONS_NULL							# options
				# ----------------------------------------- # ---------------
			): raise Exception("Failed to add plugin")

	# -------------------------------------------------------------------
	# Plugin access funcs

	def plugins(self):
		"""
		Returns list of Plugin objects which have been added to Carla.
		"""
		return list(self._plugins.values())

	def plugin_count(self):
		"""
		Returns (int) number of plugins added to Carla.
		"""
		return len(self._plugins)

	def plugin(self, plugin_id):
		"""
		Returns Plugin.
		"plugin_id" is the integer plugin_id assigned by Carla.
		"""
		if plugin_id in self._plugins:
			return  self._plugins[plugin_id]
		raise IndexError()

	def plugin_from_uuid(self, uuid):
		"""
		Returns plugin.
		"uuid" is the uuid property of a Plugin object, generated by this class.
		"""
		return self._plugin_by_uuid[uuid] if uuid in self._plugin_by_uuid else None

	def client(self, client_id):
		"""
		Returns PatchbayClient, either a SystemPatchbayClient or Plugin.
		"client_id" is the integer client_id assigned by Carla.
		"""
		if client_id in self._clients:
			return  self._clients[client_id]
		raise IndexError()

	def named_client(self, client_name):
		for client in self._clients.values():
			if client.client_name == client_name:
				return client
		raise IndexError()

	def clients(self):
		"""
		Returns a list of PatchbayClient.
		Clients are either SystemPatchbayClient or Plugin.
		"""
		return list(self._clients.values())

	def system_client_by_name(self, client_name):
		"""
		Returns the PatchbayClient with the given client_name.
		"client_name" is the same value that JACK audio connection kit uses.
		"""
		if client_name in self._sys_clients:
			return self._sys_clients[client_name]
		return None

	def is_clear(self):
		"""
		Returns boolean True if no plugins are added to Carla.
		"""
		return self.plugin_count() == 0

	# -------------------------------------------------------------------
	# Generator functions for listing clients/ports

	def system_clients(self):
		"""
		Generator which yields SystemPatchbayClient
		"""
		for client in self._sys_clients.values():
			return client

	def system_audio_in_clients(self):
		"""
		Generator which yields SystemPatchbayClient
		"""
		for client in self._sys_clients.values():
			if client.audio_in_count > 0:
				yield client

	def system_audio_out_clients(self):
		"""
		Generator which yields SystemPatchbayClient
		"""
		for client in self._sys_clients.values():
			if client.audio_out_count > 0:
				yield client

	def system_audio_in_ports(self):
		"""
		Generator which yields PatchbayPort
		"""
		for client in self._sys_clients.values():
			for port in client.audio_ins():
				yield port

	def system_audio_out_ports(self):
		"""
		Generator which yields PatchbayPort
		"""
		for client in self._sys_clients.values():
			for port in client.audio_outs():
				yield port

	def system_midi_in_clients(self):
		"""
		Generator which yields SystemPatchbayClient
		"""
		for client in self._sys_clients.values():
			if client.midi_in_count > 0:
				yield client

	def system_midi_out_clients(self):
		"""
		Generator which yields SystemPatchbayClient
		"""
		for client in self._sys_clients.values():
			if client.midi_out_count > 0:
				yield client

	def system_midi_in_ports(self):
		"""
		Generator which yields PatchbayPort
		"""
		for client in self._sys_clients.values():
			for port in client.midi_ins():
				yield port

	def system_midi_out_ports(self):
		"""
		Generator which yields PatchbayPort
		"""
		for client in self._sys_clients.values():
			for port in client.midi_outs():
				yield port

	# -------------------------------------------------------------------
	# PatchbayConnection retrieval

	def connection(self, connection_id):
		"""
		Returns the PatchbayConnection with the given "connection_id"
		"connection_id" is assigned by Carla when the connection is made.
		"""
		return self._connections[connection_id]

	# -------------------------------------------------------------------
	# Per port connect/disconnect

	def connect(self, port1, port2):
		"""
		Connect two PatchbayPort objects.
		port1 must be an PatchbayPort which is an output.
		port2 must be an PatchbayPort which is an intput.
		"""
		if not self.patchbay_connect(True, port1.client_id, port1.port_id, port2.client_id, port2.port_id):
			logging.error('Patchbay connect FAILED! %s -> %s', port1, port2)

	# -------------------------------------------------------------------
	# Plugin filename autoload trick

	def autoload(self, plugin, filename, callback = None):
		"""
		liquidsfz does not have an input file parameter, but instead, requests the host to display an open file dialog from which the user may select an SFZ file to load. This function triggers the plugin's host gui display which will call __file_callback(). When there is a plugin to autoload on deck, __file_callback() will return the "autoload_filename" property of the plugin, instead of showing the file open dialog and returning the result.

		"""
		if self.__autoload_plugin is not None:
			raise Exception("Cannot set autoload plugin as it is already used by " + self.__autoload_plugin)
		self.__autoload_plugin = plugin
		self.__autoload_filename = filename
		#logging.debug('Autoloading "%s"', filename)
		self.show_custom_ui(plugin.plugin_id, True)
		self.__autoload_plugin = None
		self.__autoload_filename = None
		if callable(callback):
			callback()

	def file_callback(self, ptr, action, is_dir, title, filter):
		if self.__autoload_plugin is None:
			if self._file_callback_parent is None:
				raise Exception("Cannot open file dialog without parent window (see Carla.set_ui_parent)")
			title  = charPtrToString(title)
			filter = charPtrToString(filter)
			if action == FILE_CALLBACK_OPEN:
				ret, ok = QFileDialog.getOpenFileName(self._file_callback_parent, title, "", filter)
			elif action == FILE_CALLBACK_SAVE:
				ret, ok = QFileDialog.getSaveFileName(self._file_callback_parent, title, "", filter, QFileDialog.ShowDirsOnly if is_dir else 0x0)
			else:
				return None
		else:
			ret = self.__autoload_filename
		if ret:
			return_file = c_char_p(ret.encode("utf-8"))
			retval = cast(byref(return_file), POINTER(c_uintptr))
			return retval.contents.value
		return None

	# -------------------------------------------------------------------
	# Plugin autogenerate uuid / moniker helper

	def provide_identity(self, plugin):
		"""
		Helper function which generates a unique "uuid" string for internal plugin
		identification, and a unique "moniker" for human-readable identification.
		"""
		self._uuid += 1
		plugin.uuid = '%03d' % self._uuid
		while plugin.uuid in self._plugin_by_uuid:
			self._uuid += 1
			plugin.uuid = '%03d' % self._uuid
		monikers = [ existing_plugin.moniker \
			for existing_plugin in self._plugin_by_uuid.values() \
			if existing_plugin.original_plugin_name == plugin.original_plugin_name ]
		idx = 1
		plugin.moniker = '{} {}'.format(plugin.original_plugin_name, idx)
		while plugin.moniker in monikers:
			idx += 1
			plugin.moniker = '{} {}'.format(plugin.original_plugin_name, idx)


class Carla(_SimpleCarla):
	"""
	Object-oriented interface to CarlaHostDLL, using callbacks for event
	notifications.
	"""

	instance					= None		# Enforce singleton

	_cb_client_added			= None
	_cb_client_removed			= None
	_cb_port_added				= None
	_cb_port_removed			= None
	_cb_connection_added		= None
	_cb_connection_removed		= None
	_cb_plugin_removed			= None
	_cb_last_plugin_removed		= None
	_cb_engine_started			= None
	_cb_engine_stopped			= None
	_cb_process_mode_changed	= None
	_cb_transport_mode_changed	= None
	_cb_buffer_size_changed		= None
	_cb_sample_rate_changed		= None
	_cb_cancelable_action		= None
	_cb_info					= None
	_cb_error					= None
	_cb_quit					= None
	_cb_application_error		= None

	# -------------------------------------------------------------------
	# Setup callbacks
	# -------------------------------------------------------------------

	def on_client_added(self, callback):
		self._cb_client_added = callback

	def on_client_removed(self, callback):
		self._cb_client_removed = callback

	def on_port_added(self, callback):
		self._cb_port_added = callback

	def on_port_removed(self, callback):
		self._cb_port_removed = callback

	def on_connection_added(self, callback):
		self._cb_connection_added = callback

	def on_connection_removed(self, callback):
		self._cb_connection_removed = callback

	def on_plugin_removed(self, callback):
		self._cb_plugin_removed = callback

	def on_last_plugin_removed(self, callback):
		self._cb_last_plugin_removed = callback

	def on_engine_started(self, callback):
		self._cb_engine_started = callback

	def on_engine_stopped(self, callback):
		self._cb_engine_stopped = callback

	def on_process_mode_changed(self, callback):
		self._cb_process_mode_changed = callback

	def on_transport_mode_changed(self, callback):
		self._cb_transport_mode_changed = callback

	def on_buffersize_changed(self, callback):
		self._cb_buffersize_changed = callback

	def on_sample_rate_changed(self, callback):
		self._cb_sample_rate_changed = callback

	def on_cancelable_action(self, callback):
		self._cb_cancelable_action = callback

	def on_info(self, callback):
		self._cb_info = callback

	def on_error(self, callback):
		self._cb_error = callback

	def on_quit(self, callback):
		self._cb_quit = callback

	def on_application_error(self, callback):
		self._cb_application_error = callback

	# -------------------------------------------------------------------
	# Engine callback
	# -------------------------------------------------------------------

	def engine_callback(self, handle, action, plugin_id, value_1, value_2, value_3, float_val, string_val):

		string_val = charPtrToString(string_val)

		try:

			if action == ENGINE_CALLBACK_INLINE_DISPLAY_REDRAW:
				return self.cb_inline_display_redraw(plugin_id)

			if action == ENGINE_CALLBACK_DEBUG:
				return self.cb_debug(plugin_id, value_1, value_2, value_3, float_val, string_val)

			if action == ENGINE_CALLBACK_PLUGIN_ADDED:
				return self.cb_plugin_added(plugin_id, value_1, string_val)

			if action == ENGINE_CALLBACK_PLUGIN_REMOVED:
				return self.cb_plugin_removed(plugin_id)

			if action == ENGINE_CALLBACK_PLUGIN_RENAMED:
				return self.cb_plugin_renamed(plugin_id, string_val)

			if action == ENGINE_CALLBACK_PLUGIN_UNAVAILABLE:
				return self.cb_plugin_unavailable(plugin_id, string_val)

			if action == ENGINE_CALLBACK_PARAMETER_VALUE_CHANGED:
				return self.cb_parameter_value_changed(plugin_id, value_1, float_val)

			if action == ENGINE_CALLBACK_PARAMETER_DEFAULT_CHANGED:
				return self.cb_parameter_default_changed(plugin_id, value_1, float_val)

			if action == ENGINE_CALLBACK_PARAMETER_MAPPED_CONTROL_INDEX_CHANGED:
				return self.cb_parameter_mapped_control_index_changed(plugin_id, value_1, value_2)

			if action == ENGINE_CALLBACK_PARAMETER_MAPPED_RANGE_CHANGED:
				minimum, maximum = (float(v) for v in string_val.split(":", 2))
				return self.cb_parameter_mapped_range_changed(plugin_id, value_1, minimum, maximum)

			if action == ENGINE_CALLBACK_PARAMETER_MIDI_CHANNEL_CHANGED:
				return self.cb_parameter_midi_channel_changed(plugin_id, value_1, value_2)

			if action == ENGINE_CALLBACK_PROGRAM_CHANGED:
				return self.cb_program_changed(plugin_id, value_1)

			if action == ENGINE_CALLBACK_MIDI_PROGRAM_CHANGED:
				return self.cb_midi_program_changed(plugin_id, value_1)

			if action == ENGINE_CALLBACK_OPTION_CHANGED:
				return self.cb_option_changed(plugin_id, value_1, bool(value_2))

			if action == ENGINE_CALLBACK_UI_STATE_CHANGED:
				return self.cb_ui_state_changed(plugin_id, value_1)

			if action == ENGINE_CALLBACK_NOTE_ON:
				return self.cb_note_on(plugin_id, value_1, value_2, value_3)

			if action == ENGINE_CALLBACK_NOTE_OFF:
				return self.cb_note_off(plugin_id, value_1, value_2)

			if action == ENGINE_CALLBACK_UPDATE:
				return self.cb_update(plugin_id)

			if action == ENGINE_CALLBACK_RELOAD_INFO:
				return self.cb_reload_info(plugin_id)

			if action == ENGINE_CALLBACK_RELOAD_PARAMETERS:
				return self.cb_reload_parameters(plugin_id)

			if action == ENGINE_CALLBACK_RELOAD_PROGRAMS:
				return self.cb_reload_programs(plugin_id)

			if action == ENGINE_CALLBACK_RELOAD_ALL:
				return self.cb_reload_all(plugin_id)

			if action == ENGINE_CALLBACK_PATCHBAY_CLIENT_ADDED:
				return self.cb_patchbay_client_added(plugin_id, value_1, value_2, string_val)

			if action == ENGINE_CALLBACK_PATCHBAY_CLIENT_REMOVED:
				return self.cb_patchbay_client_removed(plugin_id)

			if action == ENGINE_CALLBACK_PATCHBAY_CLIENT_RENAMED:
				return self.cb_patchbay_client_renamed(plugin_id, string_val)

			if action == ENGINE_CALLBACK_PATCHBAY_CLIENT_DATA_CHANGED:
				return self.cb_patchbay_client_data_changed(plugin_id, value_1, value_2)

			if action == ENGINE_CALLBACK_PATCHBAY_CLIENT_POSITION_CHANGED:
				return self.cb_patchbay_client_position_changed(plugin_id, value_1, value_2, value_3, int(round(float_val)))

			if action == ENGINE_CALLBACK_PATCHBAY_PORT_ADDED:
				return self.cb_patchbay_port_added(plugin_id, value_1, value_2, value_3, string_val)

			if action == ENGINE_CALLBACK_PATCHBAY_PORT_REMOVED:
				return self.cb_patchbay_port_removed(plugin_id, value_1)

			if action == ENGINE_CALLBACK_PATCHBAY_PORT_CHANGED:
				return self.cb_patchbay_port_changed(plugin_id, value_1, value_2, value_3, string_val)

			if action == ENGINE_CALLBACK_PATCHBAY_PORT_GROUP_ADDED:
				return self.cb_patchbay_port_group_added(plugin_id, value_1, value_2, string_val)

			if action == ENGINE_CALLBACK_PATCHBAY_PORT_GROUP_REMOVED:
				return self.cb_patchbay_port_group_removed(plugin_id, value_1)

			if action == ENGINE_CALLBACK_PATCHBAY_PORT_GROUP_CHANGED:
				return self.cb_patchbay_port_group_changed(plugin_id, value_1, value_2, string_val)

			if action == ENGINE_CALLBACK_PATCHBAY_CONNECTION_ADDED:
				client_out_id, port_out_id, client_in_id, port_in_id = [int(i) for i in string_val.split(":")]
				return self.cb_patchbay_connection_added(plugin_id, client_out_id, port_out_id, client_in_id, port_in_id)

			if action == ENGINE_CALLBACK_PATCHBAY_CONNECTION_REMOVED:
				return self.cb_patchbay_connection_removed(plugin_id, value_1, value_2)

			if action == ENGINE_CALLBACK_ENGINE_STARTED:
				self.processMode = value_1
				self.transportMode = value_2
				return None \
					if self._cb_engine_started is None \
					else self._cb_engine_started(plugin_id, value_1, value_2, value_3, float_val, string_val)

			if action == ENGINE_CALLBACK_ENGINE_STOPPED:
				return None \
					if self._cb_engine_stopped is None \
					else self._cb_engine_stopped()

			if action == ENGINE_CALLBACK_PROCESS_MODE_CHANGED:
				self.processMode = value_1
				return None \
					if self._cb_process_mode_changed is None \
					else self._cb_process_mode_changed(value_1)

			if action == ENGINE_CALLBACK_TRANSPORT_MODE_CHANGED:
				self.transportMode = value_1
				self.transportExtra = string_val
				return None \
					if self._cb_transport_mode_changed is None \
					else self._cb_transport_mode_changed(value_1, string_val)

			if action == ENGINE_CALLBACK_BUFFER_SIZE_CHANGED:
				self.buffer_size = value_1
				return None \
					if self._cb_buffer_size_changed is None \
					else self._cb_buffer_size_changed(self.buffer_size)

			if action == ENGINE_CALLBACK_SAMPLE_RATE_CHANGED:
				self.sample_rate = float_val
				return None \
					if self._cb_sample_rate_changed is None \
					else self._cb_sample_rate_changed(self.sample_rate)

			if action == ENGINE_CALLBACK_CANCELABLE_ACTION:
				return None \
					if self._cb_cancelable_action is None \
					else self._cb_cancelable_action(plugin_id, bool(value_1 != 0), string_val)

			if action == ENGINE_CALLBACK_PROJECT_LOAD_FINISHED:
				return None

			if action == ENGINE_CALLBACK_NSM:
				return None

			if action == ENGINE_CALLBACK_IDLE:
				return None

			if action == ENGINE_CALLBACK_INFO:
				return None \
					if self._cb_info is None \
					else self._cb_info(string_val)

			if action == ENGINE_CALLBACK_ERROR:
				return None \
					if self._cb_error is None \
					else self._cb_error(string_val)

			if action == ENGINE_CALLBACK_QUIT:
				return None \
					if self._cb_quit is None \
					else self._cb_quit()

			logging.warning('Unhandled action %d', action)

		except Exception as e:
			print(traceback.format_exc())
			if self._cb_application_error is not None:
				self._cb_application_error(exc_type.__name__, str(e), fname, exc_tb.tb_lineno)

		return None

	# -------------------------------------------------------------------
	# Helper functions for callbacks
	# which vary depending on Qt or Not-Qt
	# -------------------------------------------------------------------

	def _alert_client_added(self, client):
		if self._cb_client_added is not None:
			self._cb_client_added(client)

	def _alert_client_removed(self, client):
		if self._cb_client_removed is not None:
			self._cb_client_removed(client)

	def _alert_port_added(self, port):
		if self._cb_port_added is not None:
			self._cb_port_added(port)

	def _alert_port_removed(self, port):
		if self._cb_port_removed is not None:
			self._cb_port_removed(port)

	def _alert_connection_added(self, connection):
		if self._cb_connection_added is not None:
			self._cb_connection_added(connection)

	def _alert_connection_removed(self, connection):
		if self._cb_connection_removed is not None:
			self._cb_connection_removed(connection)

	def _alert_plugin_removed(self, plugin):
		if self._cb_plugin_removed is not None:
			self._cb_plugin_removed(plugin)

	def _alert_last_plugin_removed(self):
		if self._cb_last_plugin_removed is not None:
			self._cb_last_plugin_removed()


# -------------------------------------------------------------------
# Patchbay clients, ports, connections:

class PatchbayClient:
	"""
	Patchbay client which has patchbay ports.

	This class is not instantiated directly, but is inherited by
	SystemPatchbayClient and Plugin

	Members of interest
	-------------------
	ports:        (dict)  PatchbayPort objects indexed on port_id
	client_id:    (int)   Assigned by Carla
	client_name:  (str)   JACK client name (i.e. "system")
	moniker:      (str)   May be client name, or assigned by other.
	-------------------
	"""

	def __init__(self):
		self.ports = {}
		self.client_id = None

	# -------------------------------------------------------------------
	# Methods which respond to patchbay changes

	def client_renamed(self, new_client_name):
		"""
		Called from Carla if renamed.
		"""
		self.client_name = new_client_name

	def client_removed(self):
		"""
		Called from Carla when this client is removed.
		"""

	def port_added(self, port_id, port_flags, group_id, port_name):
		"""
		Called from Carla when a port is added to this client.
		"""
		self.ports[port_id] = PatchbayPort(self.client_id, port_id, port_flags, group_id, port_name)

	def port_removed(self, port_id):
		"""
		Called from Carla when a port is removed from this client.
		"""
		del self.ports[port_id]

	def input_connection_change(self, connection, state):
		"""
		Called from the Carla host when a connection to one of this client's input
		ports is either made or broken.
		When "state" is boolean True, the connection was made.
		When "state" is boolean False, the connection was broken.
		"""

	def output_connection_change(self, connection, state):
		"""
		Called from the Carla host when a connection to one of this client's output
		ports is either made or broken.
		When "state" is boolean True, the connection was made.
		When "state" is boolean False, the connection was broken.
		"""

	# -------------------------------------------------------------------
	# Methods which initiate patchbay changes

	def connect_outputs_to(self, other_client):
		"""
		other_client: PatchbayClient (or class extending PatchbayClient)
		Connects audio and / or midi outputs to the "other_client" inputs.
		In the case of multiple (i.e. stereo) ports, the order in which they are
		connected is determined by the client.
		"""
		self.connect_audio_outputs_to(other_client)
		self.connect_midi_outputs_to(other_client)

	def connect_audio_outputs_to(self, other_client):
		"""
		Connects audio outputs to the "other_client" inputs.

		other_client: PatchbayClient (or class extending PatchbayClient)

		In the case of multiple (i.e. stereo) ports, the order in which they are
		connected is determined by the client.

		If a port is already connected, no new connection is made.
		"""
		for outport, inport in zip(self.audio_outs(), other_client.audio_ins()):
			outport.connect_to(inport)

	def connect_midi_outputs_to(self, other_client):
		"""
		Connects midi outputs to the "other_client" inputs.

		other_client: PatchbayClient (or class extending PatchbayClient)

		In the case of multiple ports, the order in which they are connected is
		determined by the client.

		If a port is already connected, no new connection is made.
		"""
		for outport, inport in zip(self.midi_outs(), other_client.midi_ins()):
			outport.connect_to(inport)

	def disconnect_all(self):
		"""
		Disconnects all input and output ports from all connections.
		"""
		self._disconnect_all(self.ports.values())

	def disconnect_inputs(self):
		"""
		Disconnects all input ports from all connections.
		"""
		self._disconnect_all(self.input_ports())

	def disconnect_midi_inputs(self):
		"""
		Disconnects all midi input ports from all connections.
		"""
		self._disconnect_all(self.midi_ins())

	def disconnect_audio_inputs(self):
		"""
		Disconnects all audio input ports from all connections.
		"""
		self._disconnect_all(self.audio_ins())

	def disconnect_cv_inputs(self):
		"""
		Disconnects all cv input ports from all connections.
		"""
		self._disconnect_all(self.cv_ins())

	def disconnect_outputs(self):
		"""
		Disconnects all output ports from all connections.
		"""
		self._disconnect_all(self.output_ports())

	def disconnect_midi_outputs(self):
		"""
		Disconnects all midi output ports from all connections.
		"""
		self._disconnect_all(self.midi_outs())

	def disconnect_audio_outputs(self):
		"""
		Disconnects all audio output ports from all connections.
		"""
		self._disconnect_all(self.audio_outs())

	def disconnect_cv_outputs(self):
		"""
		Disconnects all cv output ports from all connections.
		"""
		self._disconnect_all(self.cv_outs())

	def _disconnect_all(self, ports):
		"""
		Disconnects the given ports from all connections.
		ports:		(list) of PatchbayPort
		"""
		for port in ports:
			port.disconnect_all()

	# -------------------------------------------------------------------
	# Port lists by classification:

	def input_ports(self):
		"""
		Returns list of PatchbayPort;
		all ports owned by this client if the port is an input.
		"""
		return [ port for port in self.ports.values() if port.is_input ]

	def output_ports(self):
		"""
		Returns list of PatchbayPort;
		all ports owned by this client if the port is an output.
		"""
		return [ port for port in self.ports.values() if port.is_output ]

	def audio_ins(self):
		"""
		Returns list of PatchbayPort;
		all ports owned by this client if the port is an audio input.
		"""
		return [ port for port in self.ports.values() if port.is_audio and port.is_input ]

	def audio_outs(self):
		"""
		Returns list of PatchbayPort;
		all ports owned by this client if the port is an audio output.
		"""
		return [ port for port in self.ports.values() if port.is_audio and port.is_output ]

	def midi_ins(self):
		"""
		Returns list of PatchbayPort;
		all ports owned by this client if the port is a midi input.
		"""
		return [ port for port in self.ports.values() if port.is_midi and port.is_input ]

	def midi_outs(self):
		"""
		Returns list of PatchbayPort;
		all ports owned by this client if the port is a midi output.
		"""
		return [ port for port in self.ports.values() if port.is_midi and port.is_output ]

	def cv_ins(self):
		"""
		Returns list of PatchbayPort;
		all ports owned by this client if the port is a control value input.
		"""
		return [ port for port in self.ports.values() if port.is_cv and port.is_input ]

	def cv_outs(self):
		"""
		Returns list of PatchbayPort;
		all ports owned by this client if the port is a control value output.
		"""
		return [ port for port in self.ports.values() if port.is_cv and port.is_output ]

	# -------------------------------------------------------------------
	# Other port access funcs:

	def midi_input_port(self):
		"""
		Returns PatchbayPort;
		the first midi input port owned by this client.
		"""
		for port in self.ports.values():
			if port.is_midi and port.is_input:
				return port
		return None

	def named_port(self, port_name):
		"""
		Returns PatchbayPort;
		the port owned by this client whose "port_name" matches exactly.
		Note that the name does NOT include the client_name portion.
		"""
		for port in self.ports.values():
			if port.port_name == port_name:
				return port
		raise IndexError

	def input_clients(self):
		"""
		Returns list of PatchbayClient.
		Return all clients which are connected to all of this PatchbayClient's input ports.
		(May return classes extending PatchbayClient, i.e. SystemPatchbayClient / Plugin)
		"""
		return self._exclusive_clients(self.input_ports())

	def output_clients(self):
		"""
		Returns list of PatchbayClient.
		Return all clients which are connected to all of this PatchbayClient's output ports.
		(May return classes extending PatchbayClient, i.e. SystemPatchbayClient / Plugin)
		"""
		return self._exclusive_clients(self.output_ports())

	def _exclusive_clients(self, ports):
		"""
		Returns list of PatchbayClient.
		Implements the reduction of port clients to an exlusive set.
		Used by both "input_clients" and "output_clients" functions.
		"""
		return list(set( [
			client \
			for port in ports
			for client in port.connected_clients()
		 ] ))

	def connections(self):
		"""
		Returns a list of PatchbayConnection
		Returns all connections to all ports.
		"""
		return self._connections_to_ports(self.ports.values())

	def input_connections(self):
		"""
		Returns a list of PatchbayConnection
		Returns all connections to all of this client's input ports.
		"""
		return self._connections_to_ports(self.input_ports())

	def output_connections(self):
		"""
		Returns a list of PatchbayConnection
		Returns all connections to all of this client's output ports.
		"""
		return self._connections_to_ports(self.output_ports())

	def _connections_to_ports(self, ports):
		return [
			conn \
			for port in ports \
			for conn in port.connections()
		]

	def connections_to(self, client):
		"""
		Returns a list of all connections to the given client.
		"client": PatchbayClient
		"""
		return [
			conn \
			for conn in self.connections() \
			if conn.in_port.client_id == client.client_id \
			or conn.out_port.client_id == client.client_id
		]

	def is_connected_to(self, client):
		"""
		Returns boolean True if any port is connected to the given client.
		"client": PatchbayClient
		"""
		return any(
			conn.in_port.client_id == client.client_id or conn.out_port.client_id == client.client_id \
			for conn in self.connections()
		)


class SystemPatchbayClient(PatchbayClient):
	"""
	Represents a JACK client which is not a Plugin added to the Carla instance.
	"""

	def __init__(self, client_id, client_name):
		super().__init__()
		self.client_id		= client_id
		self.client_name	= client_name
		self.moniker		= client_name

	@property
	def audio_in_count(self):
		return len(self.audio_ins())

	@property
	def audio_out_count(self):
		return len(self.audio_outs())

	@property
	def midi_in_count(self):
		return len(self.midi_ins())

	@property
	def midi_out_count(self):
		return len(self.midi_outs())

	def __str__(self):
		return f'<SystemPatchbayClient "{self.moniker}" (client_id {self.client_id})>'


class PatchbayPort:
	"""
	Represents a JACK port, owned by a PatchbayClient.
	Owned by classes extending PatchbayClient, i.e. SystemPatchbayClient / Plugin.

	Members of interest
	-------------------
	client_id  (int)   Assigned by Carla
	port_id    (int)   Assigned by Carla
	is_audio   (bool)
	is_midi    (bool)
	is_cv      (bool)
	is_osc     (bool)
	is_input   (bool)
	is_output  (bool)
	port_name  (str)   Part of the jack port name.
	-------------------
	"""

	def __init__(self, client_id, port_id, port_flags, group_id, port_name):
		self._connections = {}
		self.client_id	= client_id
		self.port_id	= port_id
		self.is_audio	= port_flags & PATCHBAY_PORT_TYPE_AUDIO != 0
		self.is_midi	= port_flags & PATCHBAY_PORT_TYPE_MIDI != 0
		self.is_cv		= port_flags & PATCHBAY_PORT_TYPE_CV != 0
		self.is_osc		= port_flags & PATCHBAY_PORT_TYPE_OSC != 0
		self.is_input	= port_flags & PATCHBAY_PORT_IS_INPUT != 0
		self.is_output	= not self.is_input
		self.group_id	= group_id
		self.port_name	= port_name

	# -------------------------------------------------------------------
	# Functions called from Carla in response to host callbacks:

	def connection_added(self, connection):
		"""
		Called from Carla when connection is made.
		"""
		self._connections[connection.connection_id] = connection

	def connection_removed(self, connection):
		"""
		Called from Carla when connection is removed.
		"""
		del self._connections[connection.connection_id]

	# -------------------------------------------------------------------
	# Functions which are callable from outside

	def connect_to(self, other_port):
		"""
		other_port: PatchbayPort
		Connect to another port. Will not attempt to connect if already connected.
		"""
		if not self.is_connected_to(other_port):
			Carla.instance.connect(self, other_port)

	def disconnect_from(self, other_port):
		"""
		other_port: PatchbayPort
		Disconnect from another port. If not connected, does nothing.
		"""
		for conn in self._connections.values():
			if conn.in_port is other_port or conn.out_port is other_port:
				conn.disconnect()

	def disconnect_all(self):
		"""
		Disconnect from all other ports.
		"""
		for conn in self._connections.values():
			conn.disconnect()

	def client(self):
		"""
		Returns PatchbayClient.
		(May return class extending PatchbayClient, i.e. SystemPatchbayClient / Plugin)
		"""
		# TODO: Make this a cached property
		return Carla.instance.client(self.client_id)

	def client_name(self):
		"""
		Returns (str) the JACK client name of the PatchbayClient which "owns" this PatchbayPort.
		"""
		# TODO: Make this a property
		return self.client().client_name

	def jack_name(self):
		"""
		Returns (str) fully qualified name in the format that JACK uses.
		"""
		return "{0}:{1}".format(self.client().client_name, self.port_name)

	def connections(self):
		"""
		Returns a list of PatchbayConnection.
		"""
		return self._connections.values()

	def is_connected_to(self, other_port):
		"""
		other_port: PatchbayPort
		Returns boolean True if connected.
		"""
		return any(
			conn.in_port is other_port or conn.out_port is other_port \
			for conn in self._connections.values()
		)

	def connections_to(self, other_port):
		"""
		Returns a list of PatchbayConnection.
		other_port: PatchbayPort
		"""
		return [ conn for conn in self._connections.values() \
			if conn.in_port is other_port or conn.out_port is other_port ]

	def connections_to_client(self, client):
		"""
		Returns a list of PatchbayConnection.
		client: PatchbayClient
		"""
		return [ conn for conn in self._connections.values() \
			if conn.in_port.client_id == client.client_id \
			or conn.out_port.client_id == client.client_id ]

	def connected_ports(self):
		"""
		Returns list of PatchbayPort
		"""
		return [ conn.in_port if conn.out_port is self else conn.out_port for conn in self._connections.values() ]

	def connected_clients(self):
		"""
		Returns list of PatchbayClient
		(May return class extending PatchbayClient, i.e. SystemPatchbayClient / Plugin)
		"""
		return [ port.client() for port in self.connected_ports() ]

	def encode_saved_state(self):
		"""
		Returns a dict which is encoded to JSON when saving a project.
		"""
		client = self.client()
		return {
			"system"	: isinstance(client, SystemPatchbayClient),
			"moniker"	: f"{client.moniker}:{self.port_name}",
			"client"	: client.client_name if isinstance(client, SystemPatchbayClient) else client.uuid,
			"port"		: self.port_name
		}

	def __str__(self):
		return '<{0} {1} "{2}:{3}">'.format(
			("Audio" if self.is_audio else "MIDI" if self.is_midi else "CV"),
			("input" if self.is_input else "output"),
			self.client().moniker, self.port_name
		)


class PatchbayConnection:
	"""
	Tracks a connection by holding a reference to the in/out ports.
	"""

	def __init__(self, connection_id, out_port, in_port):
		self.connection_id = connection_id
		self.out_port = out_port
		self.in_port = in_port

	def encode_saved_state(self):
		"""
		Return an object comprised of only basic data types for serialization as JSON
		in prepration for saving the current project.
		"""
		return {
			"source"	: self.out_port.encode_saved_state(),
			"target"	: self.in_port.encode_saved_state()
		}

	def disconnect(self):
		"""
		Disconnects - this object will be deleted when carla registers the disconnection.
		"""
		if not Carla.instance.patchbay_disconnect(True, self.connection_id):
			logging.error('Patchbay disconnect failed %s -> %s',
				self.out_port, self.in_port)

	def __str__(self):
		return f'<PatchbayConnection {self.connection_id} {self.out_port} to {self.in_port}>'



# -------------------------------------------------------------------
# Plugins:


class Plugin(PatchbayClient):
	"""
	An abstraction of a carla plugin.

	You must provide a plugin definition either by declaring the "plugin_def"
	member in a derived class, or by passing a "plugin_def" to the constructor.
	Plugin definitions may be discoverd by using the "plugin_dialog.py" script,
	found in the "tests/" folder.
	"""

	plugin_def			= None
	has_user_interface	= False

	_cb_ready			= None
	_cb_removed			= None

	_save_state_keys	= [	'uuid', 'moniker',
							'active', 'volume', 'dry_wet', 'panning', 'balance_left', 'balance_right',
							'prefer_generic_dialog', 'send_all_sound_off', 'send_channel_pressure', 'send_control_changes',
							'send_note_aftertouch', 'send_pitchbend', 'send_program_changes', 'skip_sending_notes', 'force_stereo' ]

	def on_ready(self, callback):
		self._cb_ready = callback

	def on_removed(self, callback):
		self._cb_removed = callback

	# -------------------------------------------------------------------
	# Internal lifecycle events

	def __init__(self, plugin_def = None, saved_state = None):
		if plugin_def is None:
			if self.plugin_def is None:
				raise RuntimeError("No definition for plugin")
		else:
			self.plugin_def			= plugin_def
		super().__init__()
		self.saved_state			= saved_state
		self.original_plugin_name	= self.plugin_def['name']
		self.plugin_id				= None
		self.moniker				= None
		self.ports_ready			= False
		self.added_to_carla			= False
		self.removing_from_carla	= False
		self.is_ready				= False
		self.can_drywet				= False
		self.can_volume				= False
		self.can_balance			= False
		self.can_pan				= False
		self._active				= False
		self._dry_wet				= None
		self._volume				= None
		self._balance_left			= 0.0
		self._balance_right			= 0.0
		self._panning				= 0.0
		self._ctrl_channel			= None
		self._unmute_volume			= 1.0
		self._unbypass_wet			= 1.0
		self.parameters				= {}								# Parameter objects. Key is parameter_id.
		self._midi_notes			= np_zeros((16, 128), dtype=bool)	# array for determining whether midi active.

		if saved_state is None:
			Carla.instance.provide_identity(self)
		else:
			self.uuid = saved_state["vars"]["uuid"]
			self.moniker = saved_state["vars"]["moniker"]

	def add_to_carla(self):
		"""
		Tells Carla to add this plugin. At this point there is no plugin_id assigned,
		parameters setup, or ports setup.
		"""
		if self.added_to_carla:
			raise RuntimeWarning(f'Plugin {self} already added to Carla')
		self.added_to_carla = True
		Carla.instance.add_plugin(self)

	def post_embed_init(self, plugin_id):
		"""
		Called from Carla after this plugin has been added and ID'd.
		"""
		self.plugin_id = plugin_id

		carla = Carla.instance

		counts = carla.get_audio_port_count_info(self.plugin_id)
		self._audio_in_count = counts['ins']
		self._audio_out_count = counts['outs']
		counts = carla.get_midi_port_count_info(self.plugin_id)
		self._midi_in_count = counts['ins']
		self._midi_out_count = counts['outs']

		# basic info
		# 'type', 'category', 'hints', 'optionsAvailable', 'optionsEnabled', 'filename', 'name', 'label', 'maker', 'copyright', 'iconName', 'uniqueId'
		info = carla.get_plugin_info(self.plugin_id)
		for k,v in info.items():
			setattr(self, k, v)
		self.str_plugin_type = getPluginTypeAsString(self.type)

		self.is_bridge					= self.hints & PLUGIN_IS_BRIDGE != 0
		self.is_rtsafe					= self.hints & PLUGIN_IS_RTSAFE != 0
		self.is_synth					= self.hints & PLUGIN_IS_SYNTH != 0
		self.has_custom_ui				= self.hints & PLUGIN_HAS_CUSTOM_UI != 0
		self.can_drywet					= self.hints & PLUGIN_CAN_DRYWET != 0
		self.can_volume					= self.hints & PLUGIN_CAN_VOLUME != 0
		self.can_balance				= self.hints & PLUGIN_CAN_BALANCE != 0
		self.can_pan					= self.hints & PLUGIN_CAN_PANNING != 0
		self.needs_fixed_buffers		= self.hints & PLUGIN_NEEDS_FIXED_BUFFERS != 0
		self.needs_ui_main_thread		= self.hints & PLUGIN_NEEDS_UI_MAIN_THREAD != 0
		self.uses_multi_progs			= self.hints & PLUGIN_USES_MULTI_PROGS != 0
		self.has_inline_display			= self.hints & PLUGIN_HAS_INLINE_DISPLAY != 0

		self.can_fixed_buffers			= self.optionsAvailable & PLUGIN_OPTION_FIXED_BUFFERS != 0
		self.can_force_stereo			= self.optionsAvailable & PLUGIN_OPTION_FORCE_STEREO != 0
		self.can_map_program_changes	= self.optionsAvailable & PLUGIN_OPTION_MAP_PROGRAM_CHANGES != 0
		self.can_use_chunks				= self.optionsAvailable & PLUGIN_OPTION_USE_CHUNKS != 0
		self.can_send_control_changes	= self.optionsAvailable & PLUGIN_OPTION_SEND_CONTROL_CHANGES != 0
		self.can_send_channel_pressure	= self.optionsAvailable & PLUGIN_OPTION_SEND_CHANNEL_PRESSURE != 0
		self.can_send_note_aftertouch	= self.optionsAvailable & PLUGIN_OPTION_SEND_NOTE_AFTERTOUCH != 0
		self.can_send_pitchbend			= self.optionsAvailable & PLUGIN_OPTION_SEND_PITCHBEND != 0
		self.can_send_all_sound_off		= self.optionsAvailable & PLUGIN_OPTION_SEND_ALL_SOUND_OFF != 0
		self.can_send_program_changes	= self.optionsAvailable & PLUGIN_OPTION_SEND_PROGRAM_CHANGES != 0
		self.can_skip_sending_notes		= self.optionsAvailable & PLUGIN_OPTION_SKIP_SENDING_NOTES != 0

		self.fixed_buffers				= self.optionsEnabled & PLUGIN_OPTION_FIXED_BUFFERS != 0
		self.force_stereo				= self.optionsEnabled & PLUGIN_OPTION_FORCE_STEREO != 0
		self.map_program_changes		= self.optionsEnabled & PLUGIN_OPTION_MAP_PROGRAM_CHANGES != 0
		self.use_chunks					= self.optionsEnabled & PLUGIN_OPTION_USE_CHUNKS != 0
		self.send_control_changes		= self.optionsEnabled & PLUGIN_OPTION_SEND_CONTROL_CHANGES != 0
		self.send_channel_pressure		= self.optionsEnabled & PLUGIN_OPTION_SEND_CHANNEL_PRESSURE != 0
		self.send_note_aftertouch		= self.optionsEnabled & PLUGIN_OPTION_SEND_NOTE_AFTERTOUCH != 0
		self.send_pitchbend				= self.optionsEnabled & PLUGIN_OPTION_SEND_PITCHBEND != 0
		self.send_all_sound_off			= self.optionsEnabled & PLUGIN_OPTION_SEND_ALL_SOUND_OFF != 0
		self.send_program_changes		= self.optionsEnabled & PLUGIN_OPTION_SEND_PROGRAM_CHANGES != 0
		self.skip_sending_notes			= self.optionsEnabled & PLUGIN_OPTION_SKIP_SENDING_NOTES != 0

		if self.use_chunks:
			with StreamToLogger() as slog:
				print(carla.get_chunk_data(self.plugin_id), file = slog)

		# Parameters
		for parameter_id in range(carla.get_parameter_count(self.plugin_id)):
			param = Parameter(self.plugin_id, parameter_id)
			self.parameters[param.index] = param

		self.finalize_init()
		self.check_ports_ready()

	def finalize_init(self):
		"""
		Called at the end of post_embed_init()
		Override to execute other initialization code.

		Plugin ports might not be ready when this function is called. If you need to
		execute code when all ports are available, extend the Plugin.ready() function.
		"""

	def port_added(self, port_id, port_flags, group_id, port_name):
		"""
		Called in response to a port added event from the Carla host engine.

		Note that this function, like any function called from a Carla host engine
		event, may be called from a thread other than the main thread.
		"""
		self.ports[port_id] = PatchbayPort(self.client_id, port_id, port_flags, group_id, port_name)
		self.check_ports_ready()

	def check_ports_ready(self):
		"""
		Called in response to port added events from the Carla host engine.

		Checks that all defined ports have been registered by Carla.

		Note that this function may be called from a thread other than the main thread.
		"""
		if self.is_ready:
			return
		self.ports_ready =	len(self.audio_ins()) >= self._audio_in_count and \
							len(self.audio_outs()) >= self._audio_out_count and \
							len(self.midi_ins()) >= self._midi_in_count and \
							len(self.midi_outs()) >= self._midi_out_count
		if self.ports_ready:
			if self.saved_state is None:
				for param in self.parameters.values():
					param.get_internal_value()
			else:
				self.restore_saved_state()
			self.is_ready = True
			self.ready()

	def ready(self):
		"""
		Called after post_embed_init() and all ports ready.
		You can check the state of this plugin using the "Plugin.is_ready" property.
		"""
		logging.debug('%s ready', self)
		if self._cb_ready is not None:
			self._cb_ready()

	def remove_from_carla(self):
		"""
		Removes this plugin from Carla.

		(See also "got_removed")
		"""
		self.removing_from_carla = True
		Carla.instance.remove_plugin(self.plugin_id)

	def plugin_id_changed(self, new_plugin_id):
		"""
		Called from Carla.cb_plugin_removed; updates contained Parameters
		"""
		self.plugin_id = new_plugin_id
		for param in self.parameters.values():
			param.plugin_id = new_plugin_id

	# -------------------------------------------------------------------
	# Saved state (saving / loading) functions

	def encode_saved_state(self):
		"""
		Returns a dictionary which may be used for encoding an object's state in a way
		that it may be restored using "restore_saved_state".
		A typical use is to encode the saved state as JSON and save it in a file.
		"""
		return {
			"plugin_def"	: self.plugin_def,
			"vars"			: encode_properties(self, self._save_state_keys),
			"parameters"	: { key:param.value for key, param in self.parameters.items() if param.is_used }
		}

	def restore_saved_state(self):
		"""
		Restores the plugin from the saved_state passed to this plugin's __init__ function.
		This function is called from "check_ports_ready" before calling Plugin.ready()
		"""
		for key, value in self.saved_state["vars"].items():
			setattr(self, key, value)
		for key, value in self.saved_state["parameters"].items():
			if not value is None and int(key) in self.parameters:
				self.parameters[int(key)].value = value

	# -------------------------------------------------------------------
	# Port parameter counts

	@property
	def audio_in_count(self):
		"""
		Returns (int)
		"""
		return self._audio_in_count

	@property
	def audio_out_count(self):
		"""
		Returns (int)
		"""
		return self._audio_out_count

	@property
	def midi_in_count(self):
		"""
		Returns (int)
		"""
		return self._midi_in_count

	@property
	def midi_out_count(self):
		"""
		Returns (int)
		"""
		return self._midi_out_count

	@property
	def input_parameter_count(self):
		"""
		Returns (int)
		"""
		return len(self.input_parameters())

	@property
	def output_parameter_count(self):
		"""
		Returns (int)
		"""
		return len(self.output_parameters())

	def input_parameters(self):
		"""
		Returns a list of Parameter objects.
		"""
		return [ param for param in self.parameters.values() if param.is_used and param.is_input ]

	def output_parameters(self):
		"""
		Returns a list of Parameter objects.
		"""
		return [ param for param in self.parameters.values() if param.is_used and param.is_output ]

	def __str__(self):
		return '<{0} "{1}" (uuid {2}, client_id {3})>'.format(
			type(self).__name__, self.moniker, self.uuid, self.client_id)

	def idle_fast(self):
		"""
		Function which is called at a regular interval by client applications
		Although this function is not used anywhere in this package, it is included for
		your convenience.
		Use it like so:
			for plugin in Carla.instance.plugins():
				plugin.idle_fast()
		"""

	# -------------------------------------------------------------------
	# Functions called from Carla engine callbacks:

	def debug(self, value1, value2, value3, valuef, value_str):
		"""
		Function called from Carla host engine.
		"""
		logging.debug('debug - %s value1 %s value2 %s value3 %s valuef %s value_str %s',
			self, value1, value2, value3, valuef, value_str)

	def plugin_renamed(self, new_name):
		"""
		Function called from Carla host engine when this Plugin is renamed.
		"""
		logging.debug('plugin renamed - %s newName %s',
			self, new_name)
		self.name = new_name

	def plugin_unavailable(self, error_msg):
		"""
		Function called from Carla host engine when this Plugin became unavailable.
		"""
		logging.debug('plugin unavailable - %s errorMsg %s',
			self, error_msg)

	def got_removed(self):
		"""
		Function called from Carla host engine when this Plugin got removed.
		"""
		if self._cb_removed is not None:
			self._cb_removed()

	def parameter_internal_value_changed(self, parameter, value):
		"""
		Called by the Carla host engine when the internal value of a parameter has changed.
		"parameter" is a Parameter object.
		"value" is the new value of the Parameter.
		The value of the Parameter object will have already been set when this is called.
		"""

	def parameter_default_changed(self, index, value):
		logging.debug('parameter default value changed - %s index %s value %s',
			self, index, value)

	def parameter_mapped_control_index_changed(self, index, ctrl):
		logging.debug('parameter mapped control index changed - %s index %s ctrl %s',
			self, index, ctrl)

	def parameter_mapped_range_changed(self, index, minimum, maximum):
		logging.debug('parameter mapped range changed - %s index %s minimum %s maximum %s',
			self, index, minimum, maximum)

	def parameter_midi_channel_changed(self, index, channel):
		logging.debug('parameter MIDI channel changed - %s index %s channel %s',
			self, index, channel)

	def program_changed(self, index):
		logging.debug('program changed - %s index %s',
			self, index)

	def midi_program_changed(self, index):
		logging.debug('MIDI program changed - %s index %s',
			self, index)

	def option_changed(self, option, state):
		logging.debug('option changed - %s option %s state %s',
			self, option, state)

	def ui_state_changed(self, state):
		"""
		From carla_skin:
        if state == 0:
            self.b_gui.setChecked(False)
            self.b_gui.setEnabled(True)
        elif state == 1:
            self.b_gui.setChecked(True)
            self.b_gui.setEnabled(True)
        elif state == -1:
            self.b_gui.setChecked(False)
            self.b_gui.setEnabled(False)
		"""

	def note_on(self, channel, note, _):
		"""
		Called in from Carla when a MIDI "note on" event is received.
		Used to keep track of whether any MIDI notes are currently active.
		"""
		self._midi_notes[channel][note] = True
		self.midi_active(True)

	def note_off(self, channel, note):
		"""
		Called in from Carla when a MIDI "note off" event is received.
		Used to keep track of whether any MIDI notes are currently active.
		"""
		self._midi_notes[channel][note] = False
		self.midi_active(self._midi_notes.any())

	def midi_active(self, state):
		pass

	def update(self):
		logging.debug('%s update', self)

	def reload_info(self):
		logging.debug('%s reload info', self)

	def reload_parameters(self):
		logging.debug('%s reload parameters', self)

	def reload_programs(self):
		logging.debug('%s reload programs', self)

	def reload_all(self):
		logging.debug('%s reload all', self)

	def inline_display_redraw(self):
		pass

	# -------------------------------------------------------------------
	# Propery access functions which may trigger GUI changes
	# or require setting a parameter in the engine:

	@property
	def active(self):
		"""
		Gets the "active" state of this Plugin.
		"""
		return self._active

	@active.setter
	def active(self, value):
		"""
		Set the "active" state of this Plugin.
		"""
		if self.is_ready:
			self._active = value
			Carla.instance.set_active(self.plugin_id, bool(value))

	@property
	def dry_wet(self):
		"""
		Get the dry/wet mix.
		Returns a float value in the range 0.0 to 1.0.
		"""
		return self._dry_wet

	@dry_wet.setter
	def dry_wet(self, value):
		"""
		Sets the dry/wet mix.
		"value" must be a float value in the range 0.0 to 1.0.
		"""
		if isinstance(value, float):
			if value < 0.0 or value > 1.0:
				raise ValueError()
			self._dry_wet = value
			Carla.instance.set_drywet(self.plugin_id, value)

	@property
	def volume(self):
		"""
		Get the current (cached) value of this Plugin's volume.
		Returns a float value in the range 0.0 to 1.0.
		"""
		return self._volume

	@volume.setter
	def volume(self, value):
		"""
		Sets the volume.
		"value" must be a float value in the range 0.0 to 1.0.
		"""
		if isinstance(value, float):
			if value < 0.0 or value > 1.0:
				raise ValueError()
			self._volume = value
			Carla.instance.set_volume(self.plugin_id, value)

	@property
	def balance_left(self):
		"""
		Get the left balance value (if applicable).
		Returns a float value in the range 0.0 to 1.0.
		"""
		return self._balance_left

	@balance_left.setter
	def balance_left(self, value):
		"""
		Sets the balance of the left channel (if applicable).
		"value" must be a float value in the range 0.0 to 1.0.
		"""
		if isinstance(value, float):
			if value < -1.0 or value > 1.0:
				raise ValueError()
			self._balance_left = value
			Carla.instance.set_balance_left(self.plugin_id, value)

	@property
	def balance_right(self):
		"""
		Get the right balance value (if applicable).
		Returns a float value in the range 0.0 to 1.0.
		"""
		return self._balance_right

	@balance_right.setter
	def balance_right(self, value):
		"""
		Sets the balance of the right channel (if applicable).
		"value" must be a float value in the range 0.0 to 1.0.
		"""
		if isinstance(value, float):
			if value < -1.0 or value > 1.0:
				raise ValueError()
			self._balance_right = value
			Carla.instance.set_balance_right(self.plugin_id, value)

	@property
	def balance_center(self):
		"""
		Returns a computed balance "center" value.
		This Plugin must be able to provide a "balance_left" and "balance_right" value
		for this to be meaningful.
		Returns a float value in the range 0.0 to 1.0.
		"""
		return (self._balance_right - self._balance_left) / 2 + self._balance_left

	@property
	def panning(self):
		"""
		Get the pan value (if applicable).
		Returns a float value in the range 0.0 to 1.0.
		"""
		return self._panning

	@panning.setter
	def panning(self, value):
		"""
		Sets the pan value (if applicable).
		"value" must be a float value in the range 0.0 to 1.0.
		"""
		if isinstance(value, float):
			if value < -1.0 or value > 1.0:
				raise ValueError()
			self._panning = value
			Carla.instance.set_panning(self.plugin_id, value)

	@property
	def ctrl_channel(self):
		"""
		Not sure what this does.
		"""
		return self._ctrl_channel

	@ctrl_channel.setter
	def ctrl_channel(self, value):
		"""
		Not sure what this does.
		"""
		# logging.debug('set ctrl_channel %s', value)
		Carla.instance.set_ctrl_channel(self.plugin_id, value)
		self._ctrl_channel = value

	# -------------------------------------------------------------------
	# Functions called from outside

	def mute(self):
		"""
		Sets volume to 0.0 and saves the previous value.
		"""
		self._unmute_volume = self._volume
		self.volume = 0.0

	def unmute(self):
		"""
		Restores the volume prior to the last "mute" call.
		"""
		self.volume = self._unmute_volume

	def set_bypass(self, state):
		"""
		Bypasses this Plugin by setting dry_wet to 100% dry.
		"""
		if state:
			self._unbypass_wet = self._dry_wet
			self.dry_wet = 0
		else:
			self.dry_wet = self._unbypass_wet


class Parameter:
	"""
	Class which represents a Plugin parameter.
	"""

	def __init__(self, plugin_id, parameter_id):
		"""
		Arguments:
			plugin_id		Carla assigned plugin_id
			parameter_id	Parameter index assigned by Carla (is also ordinal)
		"""
		self.plugin_id = plugin_id
		self.parameter_id = parameter_id
		self.name = "[unused]"	# We do not call get_parameter_info for unused parameters
		self.__value = None
		carla = Carla.instance

		# Basic data (get_parameter_data)
		# 'type', 'hints', 'index', 'rindex', 'midiChannel', 'mappedControlIndex', 'mappedMinimum', 'mappedMaximum', 'mappedFlags'
		info = carla.get_parameter_data(self.plugin_id, self.parameter_id)
		for k,v in info.items():
			setattr(self, k, v)
		self.is_input				= self.type == PARAMETER_INPUT
		self.is_output				= self.type == PARAMETER_OUTPUT
		self.is_boolean				= self.hints & PARAMETER_IS_BOOLEAN != 0
		self.is_integer				= self.hints & PARAMETER_IS_INTEGER != 0
		self.is_logarithmic			= self.hints & PARAMETER_IS_LOGARITHMIC != 0
		self.is_enabled				= self.hints & PARAMETER_IS_ENABLED != 0
		self.is_automatable			= self.hints & PARAMETER_IS_AUTOMATABLE != 0
		self.is_read_only			= self.hints & PARAMETER_IS_READ_ONLY != 0
		self.uses_samplerate		= self.hints & PARAMETER_USES_SAMPLERATE != 0
		self.uses_scalepoints		= self.hints & PARAMETER_USES_SCALEPOINTS != 0
		self.uses_custom_text		= self.hints & PARAMETER_USES_CUSTOM_TEXT != 0
		self.can_be_cv_controlled	= self.hints & PARAMETER_CAN_BE_CV_CONTROLLED != 0
		self.is_not_saved			= self.hints & PARAMETER_IS_NOT_SAVED != 0

		self.is_used = self.is_enabled and (self.is_input or self.is_output)
		if self.is_used:

			# Info (get_parameter_info)
			# 'name', 'symbol', 'unit', 'comment', 'groupName', 'scalePointCount'
			info = carla.get_parameter_info(self.plugin_id, self.parameter_id)
			for k,v in info.items():
				setattr(self, k, v)

			# Ranges (get_parameter_ranges)
			# 'def', 'min', 'max', 'step', 'stepSmall', 'stepLarge'
			info = carla.get_parameter_ranges(self.plugin_id, self.parameter_id)
			for k,v in info.items():
				setattr(self, k, v)
			self.range = self.max - self.min

			# Scale points (get_parameter_scalepoint_info) if necessary
			self.scale_points = [ ( sp['label'], sp['value'] ) for sp in [
				carla.get_parameter_scalepoint_info(self.plugin_id, self.parameter_id, sc_idx) \
				for sc_idx in range(self.scalePointCount)
			]] if self.uses_scalepoints else None

	def internal_value_changed(self, value):
		"""
		Called from Carla engine when the value of this Parameter changed, as by a
		custom dialog rendered via carla.
		"""
		self.__value = value

	@property
	def value(self):
		"""
		Returns the (cached) value of this Parameter.
		(Does not request value from Carla)
		"""
		return self.__value

	@value.setter
	def value(self, value):
		"""
		Sets the value of this Parameter both in Carla and cached.
		"value" must be in the range of this Parameter's "min" and "max".
		"""
		if self.__value != value:
			if self.min <= value <= self.max:
				self.__value = value
				Carla.instance.set_parameter_value(self.plugin_id, self.parameter_id, value)
			else:
				logging.warning('Parameter "%s" (%s) out of range. Min: %s Max %s',
					self.name, value, self.min, self.max)

	def get_internal_value(self):
		"""
		Returns the current internal value of this Parameter from Carla, and updates the cached value.
		"""
		self.__value = Carla.instance.get_current_parameter_value(self.plugin_id, self.parameter_id)
		return self.__value

	def plugin(self):
		"""
		Returns the Plugin which "owns" this Parameter.
		"""
		return Carla.instance.plugin(self.plugin_id)

	def __str__(self):
		return '<Parameter [{0}] "{1}" {2} {3} value: {4}>'.format(
			self.index,
			self.name,
			("input" if self.is_input else "output" if self.is_output else "unused"),
			("integer" if self.is_integer else "Bool" if self.is_boolean else "log" if self.is_logarithmic else "float"),
			self.__value
		)



#  end simple_carla/__init__.py
