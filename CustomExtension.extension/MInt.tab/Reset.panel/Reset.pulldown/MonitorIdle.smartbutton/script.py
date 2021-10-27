from pyrevit import script
from pyrevit import DB, UI
from pyrevit import framework, forms
import Autodesk.Windows
ribbon = Autodesk.Windows.ComponentManager.Ribbon
from pyrevit.coreutils.ribbon import ICON_MEDIUM
import time
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.Exceptions import InvalidOperationException
from System import EventHandler, Uri
from threading import Thread
from Autodesk.Revit.UI import TaskDialog
from System import TimeSpan
from System.Windows.Threading import DispatcherTimer
from System.Windows.Forms import MessageBox
import clr, sys, datetime, os
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.Exceptions import InvalidOperationException
import rpw
from pyrevit.forms import WPFWindow
from System import TimeSpan
from System.Windows.Threading import DispatcherTimer
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent, TaskDialog
from System import EventHandler, Uri
from pyrevit import script
import SyncUtility
import os.path, hashlib
from os.path import expanduser
import os
#from Autodesk.Revit.DB.Events import DocumentChangedEventArgs, DocumentOpenedEventArgs
__title__ = 'IdleMonitor'

doc = rpw.revit.doc
uidoc = rpw.revit.uidoc
home = expanduser("~")
__persistentengine__ = True


class ReValueWindow(forms.WPFWindow):
    def __init__(self, xaml_file_name):
        # create pattern maker window and process options
        forms.WPFWindow.__init__(self, xaml_file_name)

    @property
    def word_string(self):
        return self.stringValue_tb.Text

    def select(self, sender, args):
        global key
        self.Close()
        key = self.stringValue_tb.Password

    def string_value_changed(self, sender, args):
        pass


key = "None"
def __selfinit__(script_cmp, ui_button_cmp, __rvt__):
    # global familyMonitor
    script.set_envvar('IdleOver', True)
    button_icon = script_cmp.get_bundle_file('on.png')
    ui_button_cmp.set_icon(button_icon, icon_size=ICON_MEDIUM)

if __name__ == '__main__':
    global key
    hash = "9d7eee23e27d436284560152c36d4b04"
    if script.get_envvar('IdleOver'):
        #password = forms.ask_for_string(title="Please input master password")
        ReValueWindow('PasswordWindow.xaml').show(modal=True)
        salt = "2B9s"
        code = str(key) + salt
        h = hashlib.md5(code.encode())
        if h.hexdigest() == hash:
            state = not script.get_envvar('IdleOver')
            script.set_envvar('IdleOver', state)
            script.toggle_icon(script.get_envvar('IdleOver'))
            TaskDialog.Show("Success", "Idle Monitoring disabled")
        else:
            TaskDialog.Show("Failed", "Failed to disable idle monitoring")

    else:
        state = not script.get_envvar('IdleOver')
        script.set_envvar('IdleOver', state)
        script.toggle_icon(script.get_envvar('IdleOver'))

    # script.set_envvar('LastActiveTime', datetime.datetime.now() - datetime.timedelta(minutes=180))
    # print(script.get_envvar('LastActiveTime') + datetime.timedelta(minutes=1))
    # print(script.get_envvar('LastActiveTime'))