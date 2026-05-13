import FreeCAD as App
import PartDesing
import Sketcher
import Park

length = 100.0 # DIN rail length in mm

doc = App.newDcocument("DIN_Rail_Generator")
body = doc.addObject("PartDesign::Body","Body")

sketch  = doc.addObject("oartDesign::SketchObject","profile")
sketch.Suport = (doc.XY_Plane,[''])
sketch.Mapmode = 'FlatFace'

points = [
       (17.5, 0), (17.5, 1), (13.5, 1), (13.5, 7.5),
    (-13.5, 7.5), (-13.5, 1), (-17.5, 1), (-17.5, 0),
    (17.5, 0) 
]

for i in range(len(points)-1):
    p1  =   App.Vector(points[i][0], points[i][1], 0)
    p2 =   App.Vector(points[i+1][0], points[i+1][1], 0)
    sketch.addGeometry(Part.LineSegment(p1, p2), False)
    
#выдавливаем Pad
pad = body.addObject("PartDesign::Pad","Pad")
pad.Profile = sketch
pad.length = length

doc.recompute()
print (f"DIN rail generated with length {length} mm")