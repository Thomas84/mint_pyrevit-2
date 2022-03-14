from pyrevit import script
from pyrevit import DB, UI
from pyrevit import framework, forms
import Autodesk.Windows
ribbon = Autodesk.Windows.ComponentManager.Ribbon
import time, clr
clr.AddReferenceByPartialName('System.Windows.Forms')
from System.Windows.Forms import SendKeys
import clr, sys, datetime, os
from Autodesk.Revit.Exceptions import InvalidOperationException
import rpw
from pyrevit.forms import WPFWindow
from System import TimeSpan
from System.Windows.Threading import DispatcherTimer
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent, TaskDialog
from System import EventHandler, Uri
from pyrevit import script
import SyncUtility
import WhiteList
import getpass
from os.path import expanduser

doc = rpw.revit.doc
uidoc = rpw.revit.uidoc
home = expanduser("~")
__persistentengine__ = True

# Simple function we want to run


def yes_click():
    # Refresh Time
    script.set_envvar('IdleShow', 1)
    script.set_envvar('IdleOverwrite', 0)
    script.set_envvar('LastActiveTime', datetime.datetime.now())
'''
def no_click():
    script.set_envvar('IdleShow', 0)
    script.set_envvar('IdleOverwrite', 7)
    SyncUtility.SyncandCloseRevit(__revit__, home)
    script.set_envvar('LastActiveTime', datetime.datetime.now())
'''
def no_click():
    script.set_envvar('IdleShow', 0)
    script.set_envvar('IdleOverwrite', 7)
    todayEnd = datetime.datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
    today9pm = datetime.datetime.now().replace(hour=20, minute=50, second=0, microsecond=0)
    if todayEnd >= datetime.datetime.now() >= today9pm:
        SyncUtility.SyncandCloseRevit(__revit__, home)
    else:
        # SyncUtility.SyncandCloseRevit(__revit__, home)
        SyncUtility.SyncandSaveRevit(__revit__, home)
        script.set_envvar('IdleShow', 1)
        script.set_envvar('IdleOverwrite', 0)
    script.set_envvar('LastActiveTime', datetime.datetime.now())



# Create a subclass of IExternalEventHandler
class SimpleEventHandler(IExternalEventHandler):
    """
    Simple IExternalEventHandler sample
    """

    # __init__ is used to make function from outside of the class to be executed by the handler. \
    # Instructions could be simply written under Execute method only
    def __init__(self, do_this):
        self.do_this = do_this

    # Execute method run in Revit API environment.
    def Execute(self, uiapp):
        try:
            self.do_this()
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print(InvalidOperationException.Message)

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"



windowCheckInterval = 10  # Interval to check time
# WPF for Idle Monitoring
# WPF for Idle Monitoring
class ModelessForm(WPFWindow):
    idleTime = 10  # Time span allowed to be idle in minutes
    idleWindowCountdown = 300  # Idle Window show time in seconds
    windowTimer = DispatcherTimer()
    handler = ()

    def __init__(self, xaml_file_name):
        WPFWindow.__init__(self, xaml_file_name)
        # if script.get_envvar('IdleShow') == 1:
        # if datetime.datetime.now() > script.get_envvar('LastActiveTime') + datetime.timedelta(minutes=1):
        #and script.get_envvar('IdleShow') == 1
        todayEnd = datetime.datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
        today9pm = datetime.datetime.now().replace(hour=20, minute=50, second=0, microsecond=0)
        weekno = datetime.datetime.today().weekday()

        def OnWindowTimerTick(sender, args):
            t = script.get_envvar('IdleWindowTimer')
            if t >= 0:
                self.close_text.Text = "This Window will close in {0} seconds.".format(str(t))
                script.set_envvar('IdleWindowTimer', t - 1)
            else:
                self.windowTimer.Stop()
                self.Close()
                #self.Hide()
                no_ext_event.Raise()

        def OnWindowTimerTickSync(sender, args):
            t = script.get_envvar('IdleWindowTimer')
            if t >= 0:
                if todayEnd >= datetime.datetime.now() >= today9pm:
                    self.close_text.Text = "Revit will sync & close in {0} seconds.".format(str(t))
                    self.no_button.Content = "No, Sync and Close"
                else:
                    self.close_text.Text = "Revit will sync & save in {0} seconds.".format(str(t))
                    self.no_button.Content = "No, Sync and Save"
                script.set_envvar('IdleWindowTimer', t - 1)
            else:
                self.windowTimer.Stop()
                self.Close()
                #self.Hide()
                no_ext_event.Raise()

        if script.get_envvar('IdleShow') == 1 and script.get_envvar('IdleOver') is True and \
                (datetime.datetime.now() >= script.get_envvar('LastActiveTime') + datetime.timedelta(minutes=self.idleTime)):
            if today9pm <= datetime.datetime.now() <= todayEnd is True:
                #SendKeys.SendWait("{ESC}")
                script.set_envvar('IdleWindowTimer', self.idleWindowCountdown)
                self.simple_text.Text = "Are you still there?"
                self.close_text.Text = "Revit will sync & close in {0} seconds.".format(str(self.idleWindowCountdown))
                self.no_button.Content = "No, Sync and Close"
                # self.simple_text.Text = script.get_envvar('IdleTest')
                self.Show()
                self.handler = EventHandler(OnWindowTimerTick)
                self.windowTimer.Tick += self.handler
                self.windowTimer.Interval = TimeSpan(0, 0, 1)
                self.windowTimer.Start()

                script.set_envvar('IdleShow', 0)  # Show Parameter to prevent the window showing twice
                script.set_envvar('IdleOverwrite', 7)  # Overwrite Dialog result for sync workset tool
            else:
                script.set_envvar('IdleWindowTimer', self.idleWindowCountdown)
                self.simple_text.Text = "Are you still there?"
                self.close_text.Text = "Revit will sync & save in {0} seconds.".format(str(self.idleWindowCountdown))
                self.no_button.Content = "No, Sync and Save"
                # self.simple_text.Text = script.get_envvar('IdleTest')
                self.Show()
                self.handler = EventHandler(OnWindowTimerTickSync)
                self.windowTimer.Tick += self.handler
                self.windowTimer.Interval = TimeSpan(0, 0, 1)
                self.windowTimer.Start()

                script.set_envvar('IdleShow', 0)  # Show Parameter to prevent the window showing twice
                script.set_envvar('IdleOverwrite', 7)  # Overwrite Dialog result for sync workset tool

    def yes_click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        # script.set_envvar('IdleShow', 1)
        self.windowTimer.Stop()
        self.windowTimer.Tick -= self.handler
        yes_ext_event.Raise()
        #self.Close()
        self.Hide()
        script.set_envvar('IdleWindowTimer', self.idleWindowCountdown)

    def no_click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.windowTimer.Stop()
        self.windowTimer.Tick -= self.handler
        no_ext_event.Raise()
        #self.Close()
        self.Hide()
        script.set_envvar('IdleWindowTimer', self.idleWindowCountdown)

    def window_close(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        # script.set_envvar('IdleShow', 1)
        self.windowTimer.Stop()
        self.windowTimer.Tick -= self.handler
        yes_ext_event.Raise()
        # self.Close()
        self.Hide()
        script.set_envvar('IdleWindowTimer', self.idleWindowCountdown)


# Let's launch our beautiful and useful form !

def OnCheckActivityTick(sender, args):
    modeless_form = ModelessForm("ModelessForm.xaml")


def DialogShowing(sender, args):
    if script.get_envvar('IdleOverwrite') != 0:
        args.OverrideResult(script.get_envvar('IdleOverwrite'))

def update_time():
    script.set_envvar('LastActiveTime', datetime.datetime.now())

def document_changed_idle_function(sender, args):
    update_time()

def document_opened_idle_function(sender, args):
    update_time()

def document_synced_idle_function(sender, args):
    update_time()

def view_activated_idle_function(sender, args):
    update_time()

yes_event_handler = SimpleEventHandler(yes_click)
yes_ext_event = ExternalEvent.Create(yes_event_handler)

no_event_handler = SimpleEventHandler(no_click)
no_ext_event = ExternalEvent.Create(no_event_handler)

user = getpass.getuser()
if not user in WhiteList.WhiteList:
    inactivityCheckTimer = DispatcherTimer()
    inactivityCheckTimer.Tick += EventHandler(OnCheckActivityTick)
    inactivityCheckTimer.Interval = TimeSpan(0, windowCheckInterval, 0)
    inactivityCheckTimer.Start()
    script.set_envvar('IdleShow', 1)
    script.set_envvar('IdleOver', True)
    update_time()

__revit__.DialogBoxShowing += EventHandler[UI.Events.DialogBoxShowingEventArgs](DialogShowing)
__revit__.Application.DocumentChanged += EventHandler[DB.Events.DocumentChangedEventArgs](document_changed_idle_function)
__revit__.ViewActivated += EventHandler[UI.Events.ViewActivatedEventArgs](view_activated_idle_function)
__revit__.Application.DocumentOpened += EventHandler[DB.Events.DocumentOpenedEventArgs](document_opened_idle_function)
__revit__.Application.DocumentSynchronizedWithCentral += EventHandler[
    DB.Events.DocumentSynchronizedWithCentralEventArgs](document_synced_idle_function)

#modeless_form = ModelessForm("ModelessForm.xaml")