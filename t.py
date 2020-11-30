from Chequeo_Semantico.inferencia_de_tipos import BaseDeInferencia
from cmp.semantic import Context
from Lenguaje import dicc_de_tipos_predefinidos, TipoPredefinidos

c = Context( dicc_de_tipos_predefinidos( TipoPredefinidos() ) )
c.built_in_type = TipoPredefinidos()
c.create_type("A")
c.create_type("B")
c.create_type("C")
c.create_type("D")
c.create_type("E")
c.create_type("F")
c.create_type("G")
c.create_type("H")
c.create_type("Q")
c.create_type("Y")

c.get_type("A").parent = c.get_type("F")
c.get_type("B").parent = c.get_type("F")
c.get_type("C").parent = c.get_type("D")
c.get_type("E").parent = c.get_type("D")
c.get_type("G").parent = c.get_type("C")
c.get_type("Y").parent = c.get_type("C")
c.get_type("H").parent = c.get_type("C")
c.get_type("Q").parent = c.get_type("E")


bi = BaseDeInferencia(c)
print(bi.arbol_de_tipos)
r,l = bi.componente_conexa(["D","C","B","Object","G","Q","Y","H"] )
print(r)
print(l)
print(bi.camino_recto_mas_largo(r,["D","C","B","Object","G","Q","Y","H"]))
print(bi.seleccion_deL_tipo_superior(["C","B","E","Q","F","Int","Bool","String","G","Y","H"]))