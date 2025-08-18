#  simple_carla/scripts/sc_plugin_def.py
#
#  Copyright 2025 Leon Dionne <ldionne@dridesign.sh.cn>
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
Allows the user to select a plugin using Carla's plugin dialog and writes it's
plugin_def usable by simple_carla.Plugin to STDOUT.
"""
import argparse, logging, sys
from pretty_repr import Repr
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer
from simple_carla.plugin_dialog import CarlaPluginDialog

ESSENTIALS = ['name', 'build', 'type', 'filename', 'label', 'uniqueId']


class MainWindow(QMainWindow):

	def __init__(self, options):
		super().__init__()
		self.options = options

	def show_dialog(self):
		self.plugin_def = CarlaPluginDialog(self).exec_dialog()
		if self.plugin_def is not None:
			if self.options.full:
				print(Repr(self.plugin_def))
			else:
				print(Repr({ k:self.plugin_def[k] for k in ESSENTIALS }))
		self.close()

def main():
	p = argparse.ArgumentParser()
	p.epilog = __doc__
	p.add_argument("--full", "-f", action="store_true",
		help="Spit out the full plugin definition.")
	p.add_argument("--verbose", "-v", action="store_true",
		help="Show detailed debug information")
	options = p.parse_args()
	logging.basicConfig(
		level = logging.DEBUG if options.verbose else logging.ERROR,
		format = "[%(filename)24s:%(lineno)-4d] %(levelname)-8s %(message)s"
	)
	app = QApplication([])
	window = MainWindow(options)
	window.show_dialog()


if __name__ == "__main__":
	main()


#  end simple_carla/scripts/sc_plugin_def.py
