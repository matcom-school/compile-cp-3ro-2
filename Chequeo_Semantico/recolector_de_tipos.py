from .dependencias import visitor # patron visitor
from .dependencias import Programa, ClaseDeCool # nodos del ast
from .dependencias import dicc_de_tipos_predefinidos, TipoPredefinidos
from .dependencias import Context, SemanticError

class RecolectorDeTipos():
    def __init__(self, errores : list):
        self.contexto = None
        self.errores = errores
    
    @visitor.on("nodo")
    def visita(self,nodo):
        pass

    @visitor.when(Programa)
    def visita(self,nodo : Programa):
        tp = TipoPredefinidos()
        self.contexto = Context( dicc_de_tipos_predefinidos( tp ) )
        self.contexto.built_in_type = tp

        for cl in nodo.lista_de_clases:
            self.visita(cl)
        
        return not any(self.errores)

    @visitor.when(ClaseDeCool)
    def visita(self, nodo : ClaseDeCool):
        try:
            self.contexto.create_type( nodo.id )
        except SemanticError as se:
            self.errores.append(se.text)
