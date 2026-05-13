import FreeCAD as App
import Part


doc = App.activeDocument() # 1. Получаем текущий активный документ

if not doc:
    doc = App.newDocument("CubeDocument") # Если документа нет, создаем новый

box = doc.addObject("Part::Box", "MyCube")
box.Length = 10.0
box.Width = 10.0
box.Height = 10.0

doc.recompute() # 3. Обновляем вид, чтобы куб появился