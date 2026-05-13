import FreeCAD as App
import Part

doc  = App.activeDocument() # 1. Получаем текущий активный документ

#size = 10.0 #Внешний размер
thickness = 1.0 #Толщина стенок

outer_box = Part.makeBox(10.0, 10.0, 10.0) # Внешний куб
inner_box = Part.makeBox(10.0 - 2*thickness, 10.0 - 2*thickness, 10.0 - 2*thickness) # Внутренний куб



hollow_cube = outer_box.cut(inner_box)

obj = doc.addObject("Part::Feature", "hollow_Cube")
obj.Shape = hollow_cube
doc.recompute() # 3. Обновляем вид, чтобы куб появился
