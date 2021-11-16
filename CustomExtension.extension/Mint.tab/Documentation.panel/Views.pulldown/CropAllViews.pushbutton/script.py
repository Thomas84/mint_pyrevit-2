"""Sets Crop Region to True for all Views in the project."""

__title__ = 'Crop all Views'

import clr
clr.AddReference('RevitAPI') 
clr.AddReference('RevitAPIUI') 
import datetime
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *
from pyrevit import script
output = script.get_output()
from pyrevit import forms
count = 1



uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
start = datetime.datetime.now()
all_Views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()

t1 = Transaction(doc, 'Crop All Views')
t1.Start()
output.print_md("Views that cant be cropped :")
out=[]
error=[]
#Do some action in a Transaction
with forms.ProgressBar(title='Adding Crop to the Views',cancellable=True, steps=10) as pb: 
	for view in all_Views :
		try:
			view.CropBoxActive = True
			out.append(view)
	
		
		except Exception as e:
			output.print_md("{}|{}|{}|{}".format(view.LookupParameter('View Name'),e,view.ViewType,output.linkify(view.Id)))
		
		
		pb.update_progress(count, len(all_Views))
	   	count += 1
	if pb.cancelled:
		pass

t1.Commit()


end = datetime.datetime.now() - start

output.print_md("{} views have been cropped in {}".format(len(out),end))