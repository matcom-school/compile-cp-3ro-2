from .recolector_de_tipos import RecolectorDeTipos
from .creador_de_tipos import CreadorDeTipos
from .chequeo_semantico import ChequeoSemantico
from .inferencia_de_tipos import Inferencia
from .cambiador_de_tipos import CambiadorDeTipos

def Chequeo_Semantico(ast):
    errores = []
    
    print("################## Recoleccion ############################")
    re = RecolectorDeTipos(errores)
    _bool = re.visita(ast)

    print("################## Creacion ############################")
    ct = CreadorDeTipos(re.contexto, errores)
    _bool1 = ct.visita(ast)

    if any(errores):
        return None, errores, False
    
    print("################## Chequeo Semantico ############################")
    cs = ChequeoSemantico(ct.contexto, errores)
    _bool, scope = cs.visita(ast)
    if any(errores):
        return None, errores, False
    
    print("################## Inferencia ############################")
    i = Inferencia(cs.contexto)
    i.visita(ast, scope)
    c = CambiadorDeTipos(cs.contexto, errores)
    nuevo_ast = c.visita(ast,scope)
    print(errores)

    errores = []
    re = RecolectorDeTipos(errores)
    _bool = re.visita(nuevo_ast)
    ct = CreadorDeTipos(re.contexto, errores)
    _bool1 = ct.visita(nuevo_ast)
    if any(errores):
        return nuevo_ast, errores, True
    
    cs = ChequeoSemantico(ct.contexto, errores)
    _bool, scope = cs.visita(nuevo_ast)

    return nuevo_ast, errores, True


