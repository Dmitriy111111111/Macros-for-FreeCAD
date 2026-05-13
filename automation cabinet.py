import FreeCAD as App
import Part
import Arch

doc = App.activeDocument() or App.newDocument("ASUTP_Cabinet")

# --- 1. ПАРАМЕТРЫ ШКАФА ---
width = 800.0
height = 1200.0
depth = 300.0
thickness = 1.5

# --- 2. КОРПУС ШКАФА ---
# Создаем внешний и внутренний бокс для получения пустотелого корпуса
outer = Part.makeBox(width, depth, height)
inner = Part.makeBox(width - 2*thickness, depth - thickness, height - 2*thickness)
inner.translate(App.Vector(thickness, 0, thickness))
body_shape = outer.cut(inner)

# --- 3. МОНТАЖНАЯ ПАНЕЛЬ (внутри шкафа) ---
mp_w = width - 50.0
mp_h = height - 50.0
mp_t = 2.0
mount_panel = Part.makeBox(mp_w, mp_t, mp_h)
# Сдвигаем её к задней стенке
mount_panel.translate(App.Vector((width - mp_w)/2, depth - thickness - mp_t - 10, (height - mp_h)/2))

# --- 4. DIN-РЕЙКИ (3 штуки на монтажной панели) ---
din_rails = []
rail_w = mp_w - 20.0
rail_h = 35.0 # Стандарт DIN-рейки
rail_t = 1.0

for i in range(3):
    rail = Part.makeBox(rail_w, 7.0, rail_h) # 7мм - глубина рейки
    # Располагаем по высоте с шагом 200мм
    rail.translate(App.Vector((width - rail_w)/2, depth - thickness - mp_t - 17, 150 + i*200))
    din_rails.append(rail)

# --- 5. СБОРКА И ВЫВОД ---
cabinet_compound = Part.makeCompound([body_shape, mount_panel] + din_rails)

# Создаем объект в дереве
base_obj = doc.addObject("Part::Feature", "CabinetShape")
base_obj.Shape = cabinet_compound

cabinet_obj = Arch.makeStructure(base_obj)
cabinet_obj.Label = "Шкаф АСУТП"
base_obj.ViewObject.Visibility = False

doc.recompute()

# --- ВНЕШНИЙ ВИД ---
if cabinet_obj.ViewObject:
    cabinet_obj.ViewObject.ShapeColor = (0.8, 0.8, 0.8) # Светло-серый (RAL 7035)
    cabinet_obj.ViewObject.Transparency = 10 # Полупрозрачный, чтобы видеть начинку

# --- СВОЙСТВА IFC ---
if not hasattr(cabinet_obj, "Article"):
    cabinet_obj.addProperty("App::PropertyString", "Article", "IFC")
    cabinet_obj.Article = "ASU-600-800-250"
    
    cabinet_obj.addProperty("App::PropertyString", "Manufacturer", "IFC")
    cabinet_obj.Manufacturer = "Default_Systems"

# --- 6. СОЗДАНИЕ ДВЕРИ ---
door_w = width
door_h = height
door_t = 1.5  # Толщина металла двери

# Создаем геометрию двери
door_shape = Part.makeBox(door_w, door_t, door_h)

# Точка вращения (левый передний угол шкафа)
pivot_point = App.Vector(0, 0, 0)
# Ось вращения (вертикальная ось Z)
pivot_axis = App.Vector(0, 0, 1)
# Угол поворота (например, 45 градусов для полуоткрытого состояния)
angle = -90 

# Поворачиваем дверь
door_shape.rotate(pivot_point, pivot_axis, angle)

# Создаем объект двери в FreeCAD
door_base = doc.addObject("Part::Feature", "CabinetDoor")
door_base.Shape = door_shape

door_obj = Arch.makeStructure(door_base)
door_obj.Label = "Дверь шкафа"
door_base.ViewObject.Visibility = False # Скрываем исходную форму

# Настройка вида двери
if door_obj.ViewObject:
    door_obj.ViewObject.ShapeColor = (0.8, 0.8, 0.8)
    door_obj.ViewObject.Transparency = 60 # прозрачность



doc.recompute()
print("Шкаф АСУТП создан!")
