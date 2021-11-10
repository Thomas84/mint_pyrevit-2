"""Centers All Rooms and Rooms Tags."""

__title__ = 'Center Rooms and Room Tags'

import clr
clr.AddReference('RevitAPI') 
clr.AddReference('RevitAPIUI') 
import datetime
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
start = datetime.datetime.now()
moved_rooms = []
moved_room_tags=[]

room_tags = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_RoomTags).WhereElementIsNotElementType().ToElements()
elems = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

elems = [i for i in elems if i.Location != None]
z = room_tags[0]

tg = TransactionGroup(doc,'Centers the Room and Room Tags')
tg.Start()
try:
	t1 = Transaction(doc, 'Move Center of Room Location')
	t1.Start()

	for e in elems:
		elevation = e.Level.Elevation
		geoelem = e.GetGeometryObjectFromReference(Reference(e))
		geoobj = geoelem.GetEnumerator()
		for obj in geoobj:
			try:
				point = obj.ComputeCentroid()
				if e.IsPointInRoom(point):
					pt1 = Point.Create(XYZ(point.X,point.Y,elevation)).Coord
					pt2 = e.Location.Point
					translation1 = XYZ(pt1.X-pt2.X,pt1.Y-pt2.Y,elevation)
					e.Location.Move(translation1)
					moved_rooms.append(e)
				else:
					pass
			except:
				pass
	t1.Commit()

	t2 = Transaction(doc, 'Move Room Tags on Room Points')
	t2.Start()
	for room_tag in room_tags:
		try:
			room_tag_pt = room_tag.Location.Point
			room = room_tag.Room
			room_pt = room.Location.Point

			translation2 = room_pt - room_tag_pt
			room_tag.Location.Move(translation2)
		except :
			pass
	t2.Commit()
	end = datetime.datetime.now() - start

	TaskDialog.Show("Center Rooms and Room Tags","{} Room/s have been centered and it took {} seconds".format(len(moved_rooms),end.total_seconds()))

except Exception as e:
	TaskDialog.Show("Error",e.message)

tg.Assimilate()