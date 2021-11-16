"""Assigns Correct Sheet Scale to the Sheets"""

__title__ = 'Set Sheet Scale'

import clr
clr.AddReference('RevitAPI') 
clr.AddReference('RevitAPIUI') 
import datetime
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
start = datetime.datetime.now()

# Collect All Sheets from the current Model
all_sheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
# Collects Project Base Point for checking the Project Units
basePoint = list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ProjectBasePoint).ToElements())[0]
paramBasePoint = str(basePoint.LookupParameter("Elev").DisplayUnitType).ToLower()

# Start the Transaction
t1 = Transaction(doc, 'Set Sheet Scale')
t1.Start()
for sheet in all_sheets:
    # Get All Placed Views on the Sheet	
	placed_views_ids= sheet.GetAllPlacedViews()
	placed_views = [doc.GetElement(j) for j in placed_views_ids]
	views =[]
	validviews = [i for i in placed_views if str(i.ViewType) != "Legend"]
	# Check the units of the Project for collecting correct View Scale units
	if "meter" in paramBasePoint:
		view_scales =[i.get_Parameter(BuiltInParameter.VIEW_SCALE_PULLDOWN_METRIC).AsValueString() for i in validviews]
	else:
		view_scales =[i.get_Parameter(BuiltInParameter.VIEW_SCALE_PULLDOWN_IMPERIAL).AsValueString() for i in validviews]
	
	# QC data generated while this script was in dynamo
	# data = (validviews,view_scales,sheet.LookupParameter("Sheet Number").AsString())
	# if custom in view scales
	if "Custom" in view_scales:
		view_scales =[i.get_Parameter(BuiltInParameter.VIEW_SCALE).AsValueString() for i in validviews]
		# if more than 1 view on the sheet
		if len(validviews)>1:
			try:
				result = view_scales.count(view_scales[0]) == len(view_scales)
				if (result):
					# if views have same scale on the sheet
					s_scale = sheet.LookupParameter("Sheet Scale")
					s_scale.Set("1 : "+str(view_scales[0]))
				else:
					# if views have different scale on the sheet
					s_scale = sheet.LookupParameter("Sheet Scale")
					s_scale.Set("As Indicated")
			except: 
				pass
		# if 1 view on the sheet
		if len(validviews) == 1:
			try:
				s_scale = sheet.LookupParameter("Sheet Scale")
				s_scale.Set("1 : "+str(view_scales[0]))

			except:
				pass
		# if 0 views on the sheet
		if len(validviews) == None:
			sheet.LookupParameter("Sheet Scale").Set("")
	# For all non custom situations
	else:
			# if more than 1 view on the sheet
		if len(validviews)>1:
			try:
				result = view_scales.count(view_scales[0]) == len(view_scales)
				if (result):
					# if views have same scale on the sheet
					s_scale = sheet.LookupParameter("Sheet Scale")
					s_scale.Set(str(view_scales[0]))
				else:
					# if views have different scale on the sheet
					s_scale = sheet.LookupParameter("Sheet Scale")
					s_scale.Set("As Indicated")
			except:
				pass
		# if 1 view on the sheet
		if len(validviews) == 1:
			try:
				s_scale = sheet.LookupParameter("Sheet Scale")
				s_scale.Set(str(view_scales[0]))

			except:
				pass	
		# if 0 views on the sheet
		if len(validviews) == None:
			sheet.LookupParameter("Sheet Scale").Set("")
t1.Commit()

# calculates the time
end = datetime.datetime.now() - start
# SHows the Task Dialog
TaskDialog.Show("Sheet Scale Assignment","All Sheet Scales have been assigned{}".format(end))
