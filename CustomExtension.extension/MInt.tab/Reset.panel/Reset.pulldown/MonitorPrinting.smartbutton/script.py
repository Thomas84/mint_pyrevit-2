import Logger, CommandUtils
import getpass
from pyrevit import script
from pyrevit.coreutils.ribbon import ICON_MEDIUM
from System import Guid
from os.path import expanduser
import ConfigParser, FamilyCheck
import clr, sys, datetime, os
import os.path, hashlib
from os import path
from pyrevit import HOST_APP, framework
from pyrevit import script
from pyrevit import DB, UI
from pyrevit import framework, forms
from System import EventHandler, Uri
from pyrevit.coreutils import envvars
import rpw
import System.Windows.Media
import System.Windows.Media.Imaging
import Autodesk.Windows
ribbon = Autodesk.Windows.ComponentManager.Ribbon
from Autodesk.Revit.UI import TaskDialog
from pyrevit.revit import tabs
from Autodesk.Revit.DB import Transaction
clr.AddReference('System')
from System.Collections.Generic import List
#from Autodesk.Revit.DB.Events import DocumentChangedEventArgs, DocumentOpenedEventArgs
__title__ = 'PrintMonitor'
__context__ = 'zero-doc'

# Set system path

import os
#print(os.getenv('APPDATA') + "\\pyRevit\\pyRevit_config.ini")
def GetNoPlotElement(doc, view):
    ids = []
    filter = DB.ElementOwnerViewFilter(view.Id)
    eles = DB.FilteredElementCollector(doc, view.Id).WherePasses(filter).WhereElementIsNotElementType().ToElements()
    lines = DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_Lines).WhereElementIsNotElementType().ToElements()
    for ele in eles:
        if ele.ViewSpecific:
            try:
                type = ele.LookupParameter("Type").AsValueString()
                if "NPLT" in type:
                    ids.append(ele.Id)
            except:
                pass
    for line in lines:
        if line.ViewSpecific:
            try:
                name = line.LineStyle.Name
                if "NPLT" in name:
                    ids.append(line.Id)
            except:
                pass
    return List[DB.ElementId](ids)

config = script.get_config()


# FIXME: need to figure out a way to fix the icon sizing of toggle buttons
def __selfinit__(script_cmp, ui_button_cmp, __rvt__):
    global collector
    collector = []
    script.set_envvar('PrintMonitor', False)
    button_icon = script_cmp.get_bundle_file('off.png')
    ui_button_cmp.set_icon(button_icon, icon_size=ICON_MEDIUM)

    #script.toggle_icon(script.set_envvar('FamilyMonitor', True))
    def viewprinting_function(sender, args):
        global collector
        collector = []
        if script.get_envvar('PrintMonitor'):
            t = Transaction(args.Document, 'Hide NPLT Elements')
            t.Start()
            sheets = args.GetViewElementIds()
            for sheet in sheets:
                view = args.Document.GetElement(sheet)
                view.HideElementsTemporary(GetNoPlotElement(args.Document, view))
                collector.append(view)
                try:
                    placedViews = view.GetAllPlacedViews()
                    for placedView in placedViews:
                        args.Document.GetElement(placedView).HideElementsTemporary(
                            GetNoPlotElement(args.Document, args.Document.GetElement(placedView)))
                        collector.append(args.Document.GetElement(placedView))
                        # doc.GetElement(placedView).HideElements(GetNoPlotElement(doc, doc.GetElement(placedView)))
                except:
                    pass
            t.Commit()
            script.set_envvar('PrintCollector', collector)


    def viewprinted_function(sender, args):
        global collector
        if script.get_envvar('PrintMonitor'):
            t = Transaction(args.Document, 'Unhide NPLT Elements')
            t.Start()
            for sheet in collector:
                #TaskDialog.Show("Sheet", str(sheet))
                view = sheet
                view.DisableTemporaryViewMode(DB.TemporaryViewMode.TemporaryHideIsolate)
                try:
                    placedViews = view.GetAllPlacedViews()
                    for placedView in placedViews:
                        args.Document.GetElement(placedView).DisableTemporaryViewMode(DB.TemporaryViewMode.TemporaryHideIsolate)
                except:
                    pass

            t.Commit()
            collector = []

    __rvt__.Application.DocumentPrinting += EventHandler[DB.Events.DocumentPrintingEventArgs](viewprinting_function)
    __rvt__.Application.DocumentPrinted += EventHandler[DB.Events.DocumentPrintedEventArgs](viewprinted_function)
    return True


1

if __name__ == '__main__':

    state = not script.get_envvar('PrintMonitor')
    script.set_envvar('PrintMonitor', state)
    script.toggle_icon(script.get_envvar('PrintMonitor'))
