import FreeCAD as App
import Part
import Arch

# 1. Подготовка документа
doc = App.activeDocument() or App.newDocument("WireBasketTray")

# Параметры лотка
L = 2000.0      # Длина лотка
W = 300.0       # Ширина
H =  50.0      # Высота бортиков
wire_d = 3.0   # Диаметр проволоки
step_x = 25.0  # Шаг между поперечными прутками
r = wire_d / 2 # Радиус проволоки

#ФУНКЦИЯ ДЛЯ U-ОБРАЗНОЙ ПЕРЕКЛАДИНЫ 
def make_u_wire(w, h, radius):
    # Создаем три цилиндра: два борта и одно дно
    side1 = Part.makeCylinder(radius, h)
    
    bottom = Part.makeCylinder(radius, w)
    bottom.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90) # Кладем по оси Y
    
    side2 = Part.makeCylinder(radius, h)
    side2.translate(App.Vector(0, w, 0)) # Сдвигаем на другой край
    
    # Сплавляем их в одну деталь
    return side1.fuse(bottom).fuse(side2)

# 2. ГЕНЕРАЦИЯ ПОПЕРЕЧНЫХ ПРУТКОВ 
u_wires = []
for x in range(0, int(L) + 1, int(step_x)):
    u_shape = make_u_wire(W, H, r)
    u_shape.translate(App.Vector(x, 0, 0))
    u_wires.append(u_shape)

# 3. ГЕНЕРАЦИЯ ПРОДОЛЬНЫХ ПРУТКОВ 

long_wires = []

# Определяем позиции прутков по ширине в зависимости от W
if W == 300.0:
    y_positions = [0, W/2, W/3, W/3*2, W/4, W/4*3, W]
elif W == 100.0 or W == 150.0:
     y_positions = [0, W/2, W]
elif W == 200.0:
    y_positions = [0, W/2, W/3, W]
elif W == 50.0 :
    y_positions = [0, W/2, W]

for y in y_positions:
    w_long = Part.makeCylinder(r, L)
    w_long.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    w_long.translate(App.Vector(0, y, 0))
    long_wires.append(w_long)


# Прутки по верху бортиков
for y in [0, W]:
    w_top = Part.makeCylinder(r, L)
    w_top.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    w_top.translate(App.Vector(0, y, H))
    long_wires.append(w_top)

# --- 4. СБОРКА И ВЫВОД В ГРАФИКУ ---
# Объединяем все прутки в один составной объект
all_parts = u_wires + long_wires
basket_compound = Part.makeCompound(all_parts)

# Создаем базовый Feature
base_feature = doc.addObject("Part::Feature", "WireBasketShape")
base_feature.Shape = basket_compound

# Делаем из него BIM объект (Arch Structure)
basket_obj = Arch.makeStructure(base_feature)
basket_obj.Label = "Лоток проволочный"
base_feature.ViewObject.Visibility = False # Скрываем копию

doc.recompute()

# --- ВНЕШНИЙ ВИД И СВОЙСТВА ---
if basket_obj.ViewObject:
    basket_obj.ViewObject.ShapeColor = (0.7, 0.8, 0.9) # Голубоватый металл
    basket_obj.ViewObject.LineWidth = 2.0

# Добавляем Article
if not hasattr(basket_obj, "Article"):
    basket_obj.addProperty("App::PropertyString", "Article", "IFC")
    basket_obj.Article = f"WB-{W}-{H}-3"

doc.recompute()
print("Проволочный лоток с перекладинами успешно создан!")
