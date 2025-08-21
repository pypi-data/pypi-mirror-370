#  simple_carla/qt.py
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
Qt -enabled classes which utilize signals rather than callbacks.
"""
import logging, traceback, os, sys
import qt_extras.autofit
from PyQt5.QtCore import	QObject, pyqtSignal
from simple_carla import	_SimpleCarla, Plugin, Parameter, \
							PatchbayClient, PatchbayPort, PatchbayConnection

from carla_backend import (

	charPtrToString,

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

)


class CarlaQt(_SimpleCarla, QObject):
	"""
	Object-oriented interface to CarlaHostDLL, using Qt signals for event
	notifications.
	"""

	sig_patchbay_client_added = pyqtSignal(PatchbayClient)
	sig_patchbay_client_removed = pyqtSignal(PatchbayClient)
	sig_patchbay_port_added = pyqtSignal(PatchbayPort)
	sig_patchbay_port_removed = pyqtSignal(PatchbayPort)
	sig_connection_added = pyqtSignal(PatchbayConnection)
	sig_connection_removed = pyqtSignal(PatchbayConnection)
	sig_plugin_removed = pyqtSignal(QObject)
	sig_last_plugin_removed = pyqtSignal()
	sig_engine_started = pyqtSignal(int, int, int, int, float, str)
	sig_engine_stopped = pyqtSignal()
	sig_process_mode_changed = pyqtSignal(int)
	sig_transport_mode_changed = pyqtSignal(int, str)
	sig_buffer_size_changed = pyqtSignal(int)
	sig_sample_rate_changed = pyqtSignal(float)
	sig_cancelable_action = pyqtSignal(int, bool, str)
	sig_info = pyqtSignal(str)
	sig_error = pyqtSignal(str)
	sig_quit = pyqtSignal()
	sig_application_error = pyqtSignal(str, str, str, int)


	def __init__(self, client_name):
		QObject.__init__(self)
		_SimpleCarla.__init__(self, client_name)

	# -----------------------------
	# Engine callback
	# -----------------------------

	def engine_callback(self, _, action, plugin_id, value_1, value_2, value_3, float_val, string_val):

		string_val = charPtrToString(string_val)

		try:

			if action == ENGINE_CALLBACK_INLINE_DISPLAY_REDRAW:
				#return self.cb_inline_display_redraw(plugin_id)
				return None

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
				return self.sig_engine_started.emit(plugin_id, value_1, value_2, value_3, float_val, string_val)

			if action == ENGINE_CALLBACK_ENGINE_STOPPED:
				return self.sig_engine_stopped.emit()

			if action == ENGINE_CALLBACK_PROCESS_MODE_CHANGED:
				self.processMode = value_1
				return self.sig_process_mode_changed.emit(value_1)

			if action == ENGINE_CALLBACK_TRANSPORT_MODE_CHANGED:
				self.transportMode = value_1
				self.transportExtra = string_val
				return self.sig_transport_mode_changed.emit(value_1, string_val)

			if action == ENGINE_CALLBACK_BUFFER_SIZE_CHANGED:
				return self.sig_buffer_size_changed.emit(value_1)

			if action == ENGINE_CALLBACK_SAMPLE_RATE_CHANGED:
				return self.sig_sample_rate_changed.emit(float_val)

			if action == ENGINE_CALLBACK_CANCELABLE_ACTION:
				return self.sig_cancelable_action.emit(plugin_id, bool(value_1 != 0), string_val)

			if action == ENGINE_CALLBACK_PROJECT_LOAD_FINISHED:
				return

			if action == ENGINE_CALLBACK_NSM:
				return

			if action == ENGINE_CALLBACK_IDLE:
				return

			if action == ENGINE_CALLBACK_INFO:
				return self.sig_info.emit(string_val)

			if action == ENGINE_CALLBACK_ERROR:
				return self.sig_error.emit(string_val)

			if action == ENGINE_CALLBACK_QUIT:
				return self.sig_quit.emit()

			logging.warning('Unhandled action %d', action)

		except Exception as e:
			print(traceback.format_exc())
			exc_type, _, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			self.sig_application_error.emit(exc_type.__name__, str(e), fname, exc_tb.tb_lineno)

	# -----------------------------
	# Helper functions for callbacks
	# which vary depending on Qt or Not-Qt
	# -----------------------------

	def _alert_client_added(self, client):
		self.sig_patchbay_client_added.emit(client)

	def _alert_client_removed(self, client):
		self.sig_patchbay_client_removed.emit(client)

	def _alert_port_added(self, port):
		self.sig_patchbay_port_added.emit(port)

	def _alert_port_removed(self, port):
		self.sig_patchbay_port_removed.emit(port)

	def _alert_connection_added(self, connection):
		self.sig_connection_added.emit(connection)

	def _alert_connection_removed(self, connection):
		self.sig_connection_removed.emit(connection)

	def _alert_plugin_removed(self, plugin):
		self.sig_plugin_removed.emit(plugin)

	def _alert_last_plugin_removed(self):
		self.sig_last_plugin_removed.emit()



class AbstractQtPlugin(Plugin):
	"""
	This is an abstract class for use by classes which you wish to inherit from a
	class which itself already inherits from QObject.

	Qt does not allow inheriting from multiple classes which extend QObject, so
	extending QObject in THIS class would make it impossible for you to use it as
	a base class.

	For example:

	class MyVisualPlugin(QFrame, AbstractQtPlugin):

		# You must define these signals!
		sig_ready				= pyqtSignal(Plugin)
		sig_removed 			= pyqtSignal(Plugin)
		sig_connection_change	= pyqtSignal(PatchbayPort, PatchbayPort, bool)
		sig_parameter_changed	= pyqtSignal(Plugin, Parameter, float)

		plugin_def = {...}

		def __init__(self, parent, plugin_def, saved_state = None):
			QFrame.__init__(self, parent)
			AbstractQtPlugin.__init__(self, plugin_def, saved_state)

	plugin = MyVisualPlugin()
	plugin.sig_ready.connect(self.plugin_ready)
	plugin.add_to_carla()
	layout.addWidget(plugin)
	"""

	def ready(self):
		"""
		Called after post_embed_init() and all ports ready.
		You can check the state of this plugin using the "Plugin.is_ready" property.
		"""
		self.sig_ready.emit(self)

	def got_removed(self):
		self.sig_removed.emit(self)

	def input_connection_change(self, connection, state):
		if not self.removing_from_carla:
			self.sig_connection_change.emit(connection.in_port, connection.out_port, state)

	def output_connection_change(self, connection, state):
		if not self.removing_from_carla:
			self.sig_connection_change.emit(connection.out_port, connection.in_port, state)

	def parameter_internal_value_changed(self, parameter, value):
		"""
		Called by the Carla host engine when the internal value of a parameter has changed.
		"parameter" is a Parameter object.
		"value" is the new value of the Parameter.

		The value of the Parameter object will have already been set when this is called.
		"""
		self.sig_parameter_changed.emit(self, parameter, value)



class QtPlugin(AbstractQtPlugin, QObject):
	"""
	A class which inherits from both Plugin and QObject. It can be used by plugins
	which have no direct user-interface, but still need to emit signals.

	For example:

	plugin = QtPlugin(plugin_def)
	plugin.sig_ready.connect(self.plugin_ready)
	plugin.add_to_carla()

	"""

	sig_ready				= pyqtSignal(Plugin)
	sig_removed 			= pyqtSignal(Plugin)
	sig_connection_change	= pyqtSignal(PatchbayPort, PatchbayPort, bool)
	sig_parameter_changed	= pyqtSignal(Plugin, Parameter, float)

	def __init__(self, plugin_def=None, saved_state=None):
		QObject.__init__(self)
		Plugin.__init__(self, plugin_def, saved_state)



#  end simple_carla/qt.py
