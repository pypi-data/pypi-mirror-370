"""This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""
from libopensesame.py3compat import *
from libqtopensesame.widgets.base_widget import BaseWidget
from pyqt_code_editor.code_editors import create_editor
from libqtopensesame.misc.translate import translation_context
from pathlib import Path
import sys
_ = translation_context('updater', category='extension')


class UpdateWidget(BaseWidget):
    
    def __init__(self, parent, updater):
        super().__init__(parent, ui='extensions.updater.update_widget')
        self._editor = create_editor(language='markdown', parent=self)
        self._updater = updater
        self.ui.vertical_layout.addWidget(self._editor)
        if self._has_write_access():
            self.ui.label_administrator.hide()
        else:
            self.ui.button_update.setEnabled(False)
        self.ui.button_update.clicked.connect(self._run_script)
        self.extension_manager.fire('register_editor', editor=self._editor)
        
    def set_script(self, script):
        self._editor.setPlainText(script)
        
    def _run_script(self):
        self.extension_manager.fire('jupyter_run_code',
                                    code=self._editor.toPlainText())
        self.extension_manager.fire(
            'notify', message=_('Running update script'),
            always_show=True)
        self._updater.action.setVisible(False)
        self.tabwidget.close_current()

    def _has_write_access(self):
        # We only check for write access on Windows, because on Mac OS the
        # package has write access in itself, and on Linux there is write
        # access to the user-packages folder.
        if sys.platform != 'win32':
            return True
        # On Windows, the only failsafe way to check if there are write
        # permissions appears to be actually perform a write operation.
        test_path = Path(__file__).parent / 'test.txt'
        try:
            test_path.write_text('test')
        except PermissionError:
            return False
        try:
            test_path.unlink()
        except Exception:
            pass
        return True
