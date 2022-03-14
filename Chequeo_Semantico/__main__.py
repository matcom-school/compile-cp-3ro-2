from test.ast import control_de_tipos
from test.ast1 import herence,expr
from test.ast2 import inf
from test.ast3 import ultimo
from .recolector_de_tipos import RecolectorDeTipos
from .creador_de_tipos import CreadorDeTipos
from .chequeo_semantico import ChequeoSemantico
from .inferencia_de_tipos import Inferencia
from .cambiador_de_tipos import CambiadorDeTipos
from .Print import ASTtoString

for a in ultimo:
    print("################## Recoleccion ############################")
    errores = []
    re = RecolectorDeTipos(errores)
    re.visita(a)
    #print(re.contexto,"\n")
    #print(errores,"\n")
    print("################## Creacion ############################")
    #errores = []
    ct = CreadorDeTipos(re.contexto, errores)
    ct.visita(a)
    print(ct.contexto,"\n")
    print(errores,"\n")
    print("################## Semantico ############################")
    errores = []
    cs = ChequeoSemantico(ct.contexto, errores)
    b, s = cs.visita(a)
    for error in errores:
        print(error)
    print("################## Inferencia ############################")
    i = Inferencia(cs.contexto)
    i.visita(a, s)
    c = CambiadorDeTipos(cs.contexto, errores)
    t = c.visita(a,s)
    for error in errores:
        print(error)
   