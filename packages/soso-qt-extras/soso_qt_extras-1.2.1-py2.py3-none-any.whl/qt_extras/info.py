#  qt_extras/qt_extras/info.py
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
Provides a command-line tool which accepts a PyQT class name and provides:
1. A list of all class members
-- or --
2. An import statement
"""
import sys, argparse, importlib

def print_members_of(class_name):
	for qtmodule in ['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets']:
		module = importlib.import_module(qtmodule)
		for qtclass in dir(module):
			if qtclass.lower() == class_name:
				for member in dir(getattr(module, qtclass)):
					if member[0] != '_':
						print(member)
				return

def main():

	parser = argparse.ArgumentParser()
	parser.epilog = """
	Routines to show info from Qt classes.
	By default, shows all public members of the given class.
	"""
	parser.add_argument('ClassName', type=str, nargs='+', help='Class to inspect')
	parser.add_argument('--import-statement', '-i', action='store_true', help="Show import statement")
	options = parser.parse_args()
	if options.import_statement:
		imports = {}
		for qtmodule in ['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets']:
			module = importlib.import_module(qtmodule)
			for qtclass in dir(module):
				if qtclass[0] != '_':
					imports[ str(qtclass).lower() ] = f'from {module.__name__} import {qtclass}'
	for class_name in options.ClassName:
		class_name = class_name.lower()
		if options.import_statement:
			if class_name in imports:
				print(imports[class_name])
		else:
			print_members_of(class_name)
	return 0

if __name__ == "__main__":
	sys.exit(main())

#  end qt_extras/qt_extras/info.py
