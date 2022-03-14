from .dependencias import visitor
from .dependencias import Programa, ClaseDeCool, DefAtributo, DefFuncion
from .dependencias import Context, SemanticError, Type, ErrorType, Self

class CreadorDeTipos:
    def __init__(self, contexto : Context, errores : list):
        self.contexto = contexto
        self.errores = errores
    
    @visitor.on("nodo")
    def visita(self, nodo):
        pass
    
    @visitor.when(Programa)
    def visita(self, nodo : Programa):
        for cl in nodo.lista_de_clases:
            self.visita(cl)

        return not any(self.errores)

    @visitor.when(ClaseDeCool)
    def visita(self, nodo : ClaseDeCool):
        self.contexto.current_type = self.contexto.get_type( nodo.id ) 
        tipo_actual = self.contexto.current_type

        if nodo.clase_base is not None:
            if nodo.clase_base in ["Int","Bool","String"]:
                self.errores.append(f"Can't inherit or redifine {nodo.clase_base}")
            else:
                def funcion( tipo_encontrado ):
                    tipo_actual.set_parent( tipo_encontrado )
                
                self.busca_el_tipo_y_evalua_la_funcion(
                    tipo = nodo.clase_base,
                    funcion = funcion
                )

        for m in nodo.lista_de_miembros:
            self.visita(m)            

    @visitor.when(DefAtributo)
    def visita(self, nodo : DefAtributo):
        def funcion( tipo_encontrado ):
            nombre = nodo.id
            self.contexto.current_type.define_attribute( nombre, tipo_encontrado )

        self.busca_el_tipo_y_evalua_la_funcion(
            tipo = nodo.tipo,
            funcion = funcion
        )
        
    @visitor.when(DefFuncion)
    def visita(self, nodo : DefFuncion):
        nombres = [idx for idx, tipo in nodo.parametros]
        nombre_de_tipos = [tipo for idx, tipo in nodo.parametros]
        tipos = []
        def funcion( tipo_encontrado ):
            nonlocal tipos
            tipos.append( tipo_encontrado )
        
        for nt in nombre_de_tipos:
            self.busca_el_tipo_y_evalua_la_funcion(
                tipo = nt,
                funcion = funcion
            )
        
        def func ( tipo_encontrado ):
            nonlocal nombres, nodo, tipos
            self.contexto.current_type.define_method(nodo.id, nombres, tipos, tipo_encontrado )
        
        self.busca_el_tipo_y_evalua_la_funcion(
            tipo = nodo.tipo,
            funcion = func
        )

######################################## Metodos Privados y Auxiliares ############################################
    def busca_el_tipo_y_evalua_la_funcion (self, tipo , funcion ):
        try:
            if tipo == "SELF_TYPE":
                tipo_encontrado = Self()
            else: tipo_encontrado = self.contexto.get_type( tipo )
        except SemanticError as se:
            tipo_encontrado = ErrorType()
            self.errores.append(se.text)
        try:
            funcion ( tipo_encontrado )
        except SemanticError as se:
            self.errores.append( se.text ) 