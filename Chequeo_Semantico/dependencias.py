from Lenguaje import *
from Lenguaje import dicc_de_tipos_predefinidos, Auto, TipoPredefinidos
from Lenguaje.nodos_del_ast import Aritmetica,Comparacion, Unaria, Atomica, Binaria
import cmp.visitor as visitor
from cmp.semantic import Context, Scope, SemanticError, Type, ErrorType
