import FreeCAD as App
import Part

# --- ПАРАМЕТРЫ ---
D = 160.0        # Основная труба
D_branch = 160.0 # Ответвление
wall = 1.0       
L_main = 500.0   
L_branch = 200.0 # Длина ответвления от центра
# -----------------

doc = App.activeDocument() or App.newDocument("CleanTee")
for obj in doc.Objects:
    doc.removeObject(obj.Name)

# Векторы направлений
up = App.Vector(0, 0, 1)
side = App.Vector(1, 0, 0)
center = App.Vector(0, 0, L_main / 2)

# 1. Готовим заготовки для основной трубы
main_out = Part.makeCylinder(D/2, L_main, App.Vector(0,0,0), up)
main_in = Part.makeCylinder(D/2 - wall, L_main, App.Vector(0,0,0), up)

# 2. Готовим заготовки для ответвления
branch_out = Part.makeCylinder(D_branch/2, L_branch + D/2, center, side)
branch_in = Part.makeCylinder(D_branch/2 - wall, L_branch + D/2, center, side)

# 3. ЛОГИКА ВЫРЕЗА (чтобы не было сопротивления):
# Сначала вычитаем внутренний объем основной трубы из внешней заготовки ответвления,
# чтобы ответвление не торчало внутрь.
branch_clean = branch_out.cut(main_in)
# Теперь делаем из ответвления трубу (вычитаем его внутренность)
branch_pipe = branch_clean.cut(branch_in)

# 4. Делаем дырку в основной трубе
# Вырезаем внутренним диаметром ответвления стенку основной трубы
hole = Part.makeCylinder(D_branch/2 - wall, D, center, side)
main_pipe = main_out.cut(main_in).cut(hole)

# 5. Соединяем всё в один монолит
final_tee = main_pipe.fuse(branch_pipe)

# Вывод
tee_obj = doc.addObject("Part::Feature", "Tee_Clean_Flow")
tee_obj.Shape = final_tee

doc.recompute()
Gui.SendMsgToActiveView("ViewFit")

print("Тройник готов. Внутреннее пространство чистое, сопротивление минимально.")
