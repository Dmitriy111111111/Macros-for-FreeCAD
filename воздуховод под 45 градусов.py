import FreeCAD as App
import Part
import math

# --- 1. ПАРАМЕТРЫ КАНАЛА ---
w = 200.0        # Внутренняя ширина (мм)
h = 400.0          # Внутренняя высота (мм)
thick = 5.0        # Толщина стенки трубы
rad_inner = 150.0  # Радиус изгиба (внутренний)
g_twist = 120      # Угол колена

# --- 2. ПАРАМЕТРЫ ФЛАНЦА ---
f_size = 25.0      # Ширина полки фланца
f_thick = 5.0      # Толщина пластины фланца
hole_d = 9.0       # Диаметр под болт M8

# --- 3. АВТОМАТИЧЕСКИЙ РАСЧЕТ ОТВЕРСТИЙ (ПО НОРМАМ) ---
# Рекомендуемый шаг между болтами ~150 мм
target_step = 150.0 

# Рассчитываем количество отверстий (минимум 2 на сторону — по углам)
holes_x = max(2, int(math.ceil(w / target_step)) + 1)
holes_y = max(2, int(math.ceil(h / target_step)) + 1)

doc = App.activeDocument() or App.newDocument("Duct_90_Pro")

# Начальная точка
x_start = rad_inner 

# --- 4. ГЕОМЕТРИЯ ТРУБЫ ---
# Внешний контур
face_out = Part.makePlane(w + 2*thick, h + 2*thick, 
                          App.Vector(x_start - thick, -(h/2 + thick), 0), 
                          App.Vector(0, 0, 1))
duct_outer = face_out.revolve(App.Vector(0,0,0), App.Vector(0,1,0), g_twist)

# Внутренняя полость
face_in = Part.makePlane(w, h, 
                         App.Vector(x_start, -h/2, 0), 
                         App.Vector(0, 0, 1))
duct_inner = face_in.revolve(App.Vector(0,0,0), App.Vector(0,1,0), g_twist)

duct = duct_outer.cut(duct_inner)

# --- 5. ФУНКЦИЯ СОЗДАНИЯ ФЛАНЦА ---
def make_flange():
    # Габариты заготовки фланца
    total_w = w + 2*thick + 2*f_size
    total_h = h + 2*thick + 2*f_size
    
    # Центрирование внешней рамки
    f_corner_x = x_start - thick - f_size
    f_corner_y = -(h/2 + thick + f_size)
    
    f_outer = Part.makePlane(total_w, total_h, App.Vector(f_corner_x, f_corner_y, 0), App.Vector(0, 0, 1))
    
    # Внутренний вырез под трубу
    f_inner = Part.makePlane(w, h, App.Vector(x_start, -h/2, 0), App.Vector(0, 0, 1))
    flange_face = f_outer.cut(f_inner)
    
    # Выдавливаем пластину вниз
    flange_solid = flange_face.extrude(App.Vector(0, 0, -f_thick))
    
    # Координаты сетки отверстий (по центру полки фланца)
    margin = thick + f_size/2
    x_min, x_max = x_start - margin, x_start + w + margin
    y_min, y_max = -(h/2 + margin), (h/2 + margin)
    
    hole_pts = []
    # Горизонтальные ряды
    for i in range(holes_x):
        cx = x_min + i * (x_max - x_min) / (holes_x - 1)
        hole_pts.append((cx, y_min))
        hole_pts.append((cx, y_max))
        
    # Вертикальные ряды (без углов, чтобы не дублировать)
    for j in range(1, holes_y - 1):
        cy = y_min + j * (y_max - y_min) / (holes_y - 1)
        hole_pts.append((x_min, cy))
        hole_pts.append((x_max, cy))
        
    # Прорезание отверстий
    for px, py in hole_pts:
        # Цилиндр с запасом по высоте для чистого булевого вычитания
        cyl = Part.makeCylinder(hole_d/2, f_thick + 4, App.Vector(px, py, 2), App.Vector(0,0,-1))
        flange_solid = flange_solid.cut(cyl)
        
    return flange_solid

# --- 6. СБОРКА ---
fl1 = make_flange()
fl2 = fl1.copy()
fl2.rotate(App.Vector(0,0,0), App.Vector(0,1,0), g_twist)

# Соединяем трубу и два фланца
final_shape = duct.fuse(fl1).fuse(fl2)

# Добавление в FreeCAD
obj = doc.addObject("Part::Feature", "Vent_Duct_90")
obj.Shape = final_shape

# Настройка вида
if App.GuiUp:
    import FreeCADGui as Gui
    obj.ViewObject.ShapeColor = (0.7, 0.7, 0.8)
    obj.ViewObject.LineColor = (0.1, 0.1, 0.1)
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")

doc.recompute()
print(f"Готово! Расстояние между отверстиями: ~{target_step} мм.")
print(f"Всего отверстий на фланце: {len(range(holes_x))*2 + (len(range(holes_y))-2)*2}")
