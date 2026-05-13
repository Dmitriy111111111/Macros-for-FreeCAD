import FreeCAD as App
import Part

# --- ПАРАМЕТРЫ ---
D = 400.0       # Внешний диаметр
wall = 2.0      # Толщина стенки
length = 4500.0  # Длина трубы
# -----------------

# Создаем новый документ или чистим текущий
doc = App.activeDocument() or App.newDocument("SimpleDuct")
for obj in doc.Objects:
    doc.removeObject(obj.Name)

# 1. Создаем внешний цилиндр
outer_cyl = Part.makeCylinder(D / 2, length)

# 2. Создаем внутренний цилиндр (пустота)
inner_cyl = Part.makeCylinder((D / 2) - wall, length)

# 3. Вычитаем внутренний из внешнего (Boolean Cut)
pipe_shape = outer_cyl.cut(inner_cyl)

# 4. Выводим результат в документ
duct_obj = doc.addObject("Part::Feature", "SimplePipe")
duct_obj.Shape = pipe_shape

# Обновляем вид
doc.recompute()
Gui.SendMsgToActiveView("ViewFit")

print(f"Труба готова: D={D}, стенка={wall}, длина={length}")
