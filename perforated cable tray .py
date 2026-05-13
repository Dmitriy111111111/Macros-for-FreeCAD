import FreeCAD as App
import Part
import Arch

doc = App.activeDocument() or App.newDocument("CableTray")

# 1. Создаем основу лотка
L, W, H, T = 300.0, 50.0, 15.0, 0.5 # Длина, ширина, высота и толщина стенок лотка
outer = Part.makeBox(L, W, H)
inner = Part.makeBox(L, W - 2*T, H - T)
inner.translate(App.Vector(0, T, T))
tray_shape = outer.cut(inner)


def make_oval_solid(length, rad, height): # Функция для создания овального отверстия
    rect = Part.makeBox(length, rad*2, height)
    c1 = Part.makeCylinder(rad, height) # Полукруг в начале
    c2 = Part.makeCylinder(rad, height)
    c2.translate(App.Vector(length, 0, 0)) 
    c1.translate(App.Vector(0, rad, 0))
    c2.translate(App.Vector(0, rad, 0))
    return rect.fuse(c1).fuse(c2)

hole_rad, hole_dist, step = 1.5, 5.0, 20.0
hole_list = []

for x in range(int(step), int(L-step), int(step)):
    for y in [W*0.25, W*0.5, W*0.75]:
        h_solid = make_oval_solid(hole_dist, hole_rad, T + 2.0)
        h_solid.translate(App.Vector(x - hole_dist/2, y - hole_rad, -1.0))
        hole_list.append(h_solid)


if hole_list:
    tray_shape = tray_shape.cut(Part.makeCompound(hole_list))


temp_obj = doc.addObject("Part::Feature", "TrayBase") # Временный объект для хранения формы лотка
temp_obj.Shape = tray_shape # Присваиваем форму лотка временному объекту

# 2. Создаем Arch элемент, передавая созданный объект
tray_obj = Arch.makeStructure(temp_obj) 
tray_obj.Label = "Перфорированный кабельный лоток"

# 3. ПЕРЕСЧИТЫВАЕМ ДОКУМЕНТ
doc.recompute()

# Настройки вида
tray_obj.ViewObject.DisplayMode = "Flat Lines"
tray_obj.ViewObject.ShapeColor = (0.8, 0.8, 0.8)
tray_obj.ViewObject.Transparency = 10
App.ActiveDocument.recompute()

# --- ИСПРАВЛЕНИЕ 3: Исправлен только синтаксис присвоения свойств ---
if not hasattr(tray_obj, "Article"):
    tray_obj.addProperty("App::PropertyString", "Article", "IFC")
    tray_obj.Article = "CT-300-50-ST"
    
    tray_obj.addProperty("App::PropertyString", "Manufacturer", "IFC")
    tray_obj.Manufacturer = "Default"
    
    tray_obj.addProperty("App::PropertyFloat", "Weight", "IFC")
    tray_obj.Weight = 1.25

tray_obj.Description = "Лоток {}x{}x{}".format(300, 50, 15)
doc.recompute()
print("Готово! Объект и свойства созданы.")
