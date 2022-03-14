from Lenguaje import *
from Lenguaje import dicc_de_tipos_predefinidos, Auto, TipoPredefinidos, Self
from Lenguaje.nodos_del_ast import Aritmetica,Comparacion, Unaria, Atomica, Binaria
import cmp.visitor as visitor
from cmp.semantic import Context, Scope, SemanticError, Type, ErrorType

def filtros_de_tipos(tipo : Type,contexto : Context):
    if tipo.is_self_type:
        return contexto.current_type
    return tipo