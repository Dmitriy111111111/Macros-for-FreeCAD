import FreeCAD as App
import Part
import FreeCADGui as Gui
import math

# --- 1. ПАРАМЕТРЫ (в мм) ---
length = 4500.0      # Длина трубы
width = 100.0       # Ширина канала
height = 100     # Высота канала
thickness = 2.0     # Толщина стенки трубы

# Параметры фланцев
flange_size = 20.0  # На сколько фланец выступает наружу
flange_thick = 5.0  # Толщина самой рамки
hole_r = 4.5        # Радиус отверстий (под болт M8-M9)

# --- НОРМЫ ---
target_step = 150.0 # Желаемый шаг между болтами по ГОСТ/DIN

# --- 2. СОЗДАНИЕ ДОКУМЕНТА И ТРУБЫ ---
doc = App.activeDocument() or App.newDocument("Duct_Pro_Straight")

outer_box = Part.makeBox(length, width, height)
inner_box = Part.makeBox(length + 2, width - 2*thickness, height - 2*thickness, App.Vector(-1, thickness, thickness))
duct = outer_box.cut(inner_box)

# --- 3. ФУНКЦИЯ СОЗДАНИЯ РАМКИ С АВТО-ОТВЕРСТИЯМИ ---
def create_flange():
    # 1. Внешний контур рамки
    f_outer = Part.makeBox(
        flange_thick, 
        width + 2 * flange_size, 
        height + 2 * flange_size, 
        App.Vector(0, -flange_size, -flange_size)
    )
    # 2. Внутренний вырез (по внутреннему размеру трубы)
    f_inner = Part.makeBox(
        flange_thick + 4, 
        width - 2*thickness, 
        height - 2*thickness, 
        App.Vector(-2, thickness, thickness)
    )
    flange = f_outer.cut(f_inner)
    
    # --- АВТОМАТИЧЕСКИЙ РАСЧЕТ КОЛИЧЕСТВА ОТВЕРСТИЙ ---
    # Считаем по внешнему габариту фланца
    nx = max(2, int(math.ceil((width + 2*flange_size) / target_step)) + 1)
    ny = max(2, int(math.ceil((height + 2*flange_size) / target_step)) + 1)
    
    # Отступ отверстий (по центру полки фланца)
    offset = flange_size / 2
    y_min, y_max = -flange_size + offset, width + flange_size - offset
    z_min, z_max = -flange_size + offset, height + flange_size - offset

    hole_pts = []

    # Горизонтальные ряды (верх/низ)
    for i in range(nx):
        curr_y = y_min + i * (y_max - y_min) / (nx - 1)
        hole_pts.append((curr_y, z_min))
        hole_pts.append((curr_y, z_max))
        
    # Вертикальные ряды (бока, без углов)
    for j in range(1, ny - 1):
        curr_z = z_min + j * (z_max - z_min) / (ny - 1)
        hole_pts.append((y_min, curr_z))
        hole_pts.append((y_max, curr_z))
    
    # 3. Прорезаем отверстия
    for py, pz in hole_pts:
        # Цилиндр лежит вдоль оси X (направление 1, 0, 0)
        hole = Part.makeCylinder(hole_r, flange_thick + 10, App.Vector(-5, py, pz), App.Vector(1, 0, 0))
        flange = flange.cut(hole)
        
    return flange, nx, ny

# --- 4. УСТАНОВКА РАМОК ---
flange1, nx, ny = create_flange()

flange2 = flange1.copy()
flange2.translate(App.Vector(length - flange_thick, 0, 0))

# --- 5. ОБЪЕДИНЕНИЕ ---
final_shape = duct.fuse(flange1).fuse(flange2)

obj = doc.addObject("Part::Feature", "Duct_Straight_Pro")
obj.Shape = final_shape

# Визуализация
if Gui.runMode() != "Console":
    obj.ViewObject.ShapeColor = (0.6, 0.7, 0.8)
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")

doc.recompute()

print("--- ОТЧЕТ ---")
print(f"Размеры канала: {width}x{height} мм")
print(f"Авто-сетка отверстий: {nx} по горизонтали, {ny} по вертикали")
print(f"Всего отверстий на одном фланце: {len(range(nx))*2 + (len(range(ny))-2)*2}")
