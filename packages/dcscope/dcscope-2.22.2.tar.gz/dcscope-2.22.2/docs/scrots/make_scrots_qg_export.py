"""Screenshots for quick guide statistics"""
import sys

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication
from dcscope.gui.main import DCscope
from dcscope.gui import export

app = QApplication(sys.argv)

QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.Language.C))

mw = DCscope()
mw.settings.setValue("check for updates", 0)
mw.settings.setValue("advanced/user confirm clear", 0)
mw.settings.setValue("paths/export data", ".")

# build up a session
mw.add_dataslot(paths=["Figure3_Blood_Initial.rtdc"])
mw.reload_pipeline()

# open the dialog window
dlg = export.ExportData(mw, pipeline=mw.pipeline)
dlg.lineEdit_path.setText("/home/user/DCscope-Exports")
dlg.show()
QApplication.processEvents(QtCore.QEventLoop.ProcessEventsFlag.AllEvents, 300)
dlg.grab().save("_qg_export_data.png")

mw.close()
