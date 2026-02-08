# Copyright (C) 2015-2017 YouCompleteMe contributors.
#
# This file is part of YouCompleteMe.
#
# YouCompleteMe is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YouCompleteMe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YouCompleteMe.  If not, see <http://www.gnu.org/licenses/>.

import sys
import vim


# Not caching the result of this function; users shouldn't have to restart Vim
# after running the install script or setting the
# `g:ycm_server_python_interpreter` option.
def PathToPythonInterpreter():
  python_interpreter = vim.eval( 'g:ycm_server_python_interpreter' )
  if not python_interpreter:
    return sys.executable

  # Not calling the Python interpreter to check its version as it significantly
  # impacts startup time.
  from ycmd import utils
  python_interpreter = utils.FindExecutable( python_interpreter )
  if python_interpreter:
    return python_interpreter

  raise RuntimeError( "Path in 'g:ycm_server_python_interpreter' option "
                      "does not point to a valid Python 3.6+." )


def _EndsWithPython( path ):
  """Check if given path ends with a python 3.6+ name."""
  return path and PYTHON_BINARY_REGEX.search( path ) is not None


def PathToServerScript():
  return "/usr/bin/ycmd"
