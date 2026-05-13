import FreeCAD as App
import Part
import FreeCADGui as Gui
import math

# --- 1. ПАРАМЕТРЫ (в мм) ---
width = 1500.0      # Ширина основного канала
height = 1500.0/2     # Высота основного канала
length_main = (width + height) * 2 # Общая длина основной трубы
length_branch = (width/2)+ 50 # Длина ответвления (от центра основной трубы)
thickness = 2.0     # Толщина стенки

# Параметры фланцев
f_size = 20.0       # Вылет фланца
f_thick = 5.0       # Толщина фланца
hole_r = 4.5        # Радиус отверстий (под M8)
target_step = 150.0 # Рекомендуемый шаг отверстий

doc = App.activeDocument() or App.newDocument("T_Duct_Pro")

# --- 2. ФУНКЦИЯ СОЗДАНИЯ ЗАГОТОВКИ ТРУБЫ (ПОЛНОТЕЛОЙ) ---
def make_duct_solid(l, w, h):
    return Part.makeBox(l, w, h, App.Vector(0, -w/2, -h/2))

# --- 3. ГЕОМЕТРИЯ ТРОЙНИКА ---
# Основная магистраль
main_outer = make_duct_solid(length_main, width + 2*thickness, height + 2*thickness)
main_inner = make_duct_solid(length_main + 2, width, height)
main_inner.translate(App.Vector(-1, 0, 0))

# Ответвление (перпендикулярно)
branch_outer = make_duct_solid(length_branch, width + 2*thickness, height + 2*thickness)
branch_outer.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 90)
branch_outer.translate(App.Vector(length_main/2, 0, 0))

branch_inner = make_duct_solid(length_branch + 2, width, height)
branch_inner.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 90)
branch_inner.translate(App.Vector(length_main/2, 0, 0))

# Сборка стенок
duct_walls = main_outer.fuse(branch_outer).cut(main_inner.fuse(branch_inner))

# --- 4. ФУНКЦИЯ СОЗДАНИЯ ФЛАНЦА ---
def create_flange(w_int, h_int):
    # Внешний и внутренний контуры
    tw, th = w_int + 2*thickness + 2*f_size, h_int + 2*thickness + 2*f_size
    f_out = Part.makeBox(f_thick, tw, th, App.Vector(0, -tw/2, -th/2))
    f_in = Part.makeBox(f_thick + 4, w_int, h_int, App.Vector(-2, -w_int/2, -h_int/2))
    flange = f_out.cut(f_in)
    
    # Авто-расчет отверстий
    nx = max(2, int(math.ceil(tw / target_step)) + 1)
    ny = max(2, int(math.ceil(th / target_step)) + 1)
    
    off = thickness + f_size/2
    y_min, y_max = -(w_int/2 + off), (w_int/2 + off)
    z_min, z_max = -(h_int/2 + off), (h_int/2 + off)
    
    hole_pts = []
    for i in range(nx):
        curr_y = y_min + i * (y_max - y_min) / (nx - 1)
        hole_pts.append((curr_y, z_min))
        hole_pts.append((curr_y, z_max))
    for j in range(1, ny - 1):
        curr_z = z_min + j * (z_max - z_min) / (ny - 1)
        hole_pts.append((y_min, curr_z))
        hole_pts.append((y_max, curr_z))
        
    for py, pz in hole_pts:
        h_cyl = Part.makeCylinder(hole_r, f_thick + 10, App.Vector(-5, py, pz), App.Vector(1, 0, 0))
        flange = flange.cut(h_cyl)
    return flange

# --- 5. УСТАНОВКА ФЛАНЦЕВ ---
# Фланец 1 (начало магистрали)
fl1 = create_flange(width, height)

# Фланец 2 (конец магистрали)
fl2 = fl1.copy()
fl2.translate(App.Vector(length_main - f_thick, 0, 0))

# Фланец 3 (ответвление)
fl3 = fl1.copy()
fl3.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 90)
fl3.translate(App.Vector(length_main/2, length_branch - f_thick, 0))

# --- 6. ФИНАЛЬНАЯ СБОРКА ---
final_shape = duct_walls.fuse(fl1).fuse(fl2).fuse(fl3)

obj = doc.addObject("Part::Feature", "T_Duct")
obj.Shape = final_shape

if Gui.runMode() != "Console":
    obj.ViewObject.ShapeColor = (0.7, 0.8, 0.7)
    Gui.SendMsgToActiveView("ViewFit")

doc.recompute()
print("Тройник успешно создан!")
