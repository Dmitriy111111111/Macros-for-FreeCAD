import FreeCAD as App
import Part
import Arch

# Крышка для лотка

cover_L = L
cover_W = W + 1.0
cover_H = -5.0 # Высота крышки, можно изменить по желанию
cover_T = 0.5 # Толщина крышки, можно изменить по желанию

cover_outer = Part.makeBox(cover_L, cover_W, cover_H)
c_inner = Part.makeBox(cover_L, cover_W - 2 * cover_T, cover_H - cover_T)
c_inner.translate(App.Vector(0, cover_T, cover_T)) # Внутренняя часть крышки, вычитаемая из внешней
cover_shape = cover_outer.cut(c_inner)

cover_shape.rotate(App.Vector(0, cover_W/2, 0), App.Vector(1, 0, 0), 180)
cover_shape.translate(App.Vector(0, -0.5, H)) # Размещаем крышку над лотком

cover_base = doc.addObject("Part::Feature", "TrayCoverBase")
cover_base.Shape = cover_shape

cover_base = doc.addObject("Part::Feature", "TrayCoverBase")
cover_base.Shape = cover_shape

cover_obj = Arch.makeStructure(cover_base)
cover_obj.Label = "Крышка лотка"
cover_base.ViewObject.Visibility = False


# настройки вида для крышки
if not hasattr(cover_obj,"Arctile"):
    cover_obj.Arctile = "CТС -300-50-ST"

doc.recompute()
print ('Крышка для лотка создана')