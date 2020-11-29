from cmp.pycompiler import Grammar

from . import *

G = Grammar()
# non-terminals
programa = G.NonTerminal('<programa>', startSymbol=True)
lista_clases, def_Clases = G.NonTerminals('<lista_clases> <def_Clases>')
lista_caract, def_Atributo, def_Func = G.NonTerminals('<lista_caract> <def_Atributo> <def_Func>')
lista_Param, Param, lista_expre, decla_variable, lista_decla_variable = G.NonTerminals('<lista_Param> <Param> <lista_expre> <decla_variable,> <lista_decla_variable>')
case_var_list, case_var = G.NonTerminals("<case-var-list> <case-var>")
expr, cond, arith, term, factor, atom = G.NonTerminals('<expr> <cond> <arith> <term> <factor> <atom>')
inv_func, lista_argum  = G.NonTerminals('<inv_func> <lista_argum>')
# terminals
clase_t, decla, in_t, comentario = G.Terminals('class let in comment')
semi, colon, comma, dot, opar, cpar, ocur, ccur = G.Terminals('; : , . ( ) { }')
equal, plus, minus, star, div = G.Terminals('= + - * /')
id_t, num, string, new, hyphen = G.Terminals('id int string new ˜')
if_t, then, else_t, fi, case, of, esac, while_t, loop, pool = G.Terminals("if then else fi case of esac while loop pool")
lesser, greater, at, inherits, isVoid, not_t, true, false, larrow, rarrow = G.Terminals("< > @ inherits isVoid not true false <- =>")


## PRODUCTIONS ##
programa %= lista_clases, lambda h,s: Programa(s[1])
# <lista_clases>
lista_clases %= def_Clases + semi, lambda h,s: [s[1]]
lista_clases %= def_Clases + semi + lista_clases, lambda h,s: [s[1]] + s[3]
# <def_Clases> 
def_Clases %= clase_t + id_t + ocur + lista_caract + ccur, lambda h,s: ClaseDeCool( s[4],s[2])              #Clase sin herencia simple
def_Clases %= clase_t + id_t + inherits + id_t + ocur + lista_caract + ccur, lambda h,s: ClaseDeCool( s[6],s[2], s[4])
# <lista_caract>
lista_caract %= def_Atributo + semi + lista_caract, lambda h,s: [s[1]] + s[3]
lista_caract %= def_Func + semi + lista_caract, lambda h,s: [s[1]] + s[3]
lista_caract %= G.Epsilon, lambda h,s: []
# <def_Atributo>
def_Atributo %= id_t + colon + id_t, lambda h,s: DefAtributo(s[1], s[3])
def_Atributo %= id_t + colon + id_t + larrow + expr, lambda h,s: DefAtributo(s[1], s[3], s[5])
# <def_Func>
def_Func %= id_t + opar + lista_Param + cpar + colon + id_t + ocur + expr + ccur, lambda h,s: DefFuncion(s[1], s[3],s[8], s[6])
# <lista_Param>
lista_Param %= G.Epsilon, lambda h,s: []
lista_Param %= Param, lambda h,s: [ s[1] ]
lista_Param %= Param + comma + lista_Param, lambda h,s: [ s[1] ] + s[3]
# <Param>  
Param %= id_t + colon + id_t, lambda h,s: (s[1], s[3])
# <lista_expre>
lista_expre %= expr + semi, lambda h,s: [s[1]]
lista_expre %= expr + semi + lista_expre, lambda h,s: [s[1]] + s[3]
# <expr>
expr %= id_t + larrow + expr, lambda h,s: Asignacion(s[1], s[3])
expr %= ocur + lista_expre + ccur, lambda h,s: Block(s[2])
expr %= decla + lista_decla_variable + in_t + expr, lambda h,s: LetIn(s[2], s[4])
expr %= case + expr + of + case_var_list + esac, lambda h,s: Case(s[2], s[4])#
#expr %= if_t + expr + then + expr + else_t + expr + fi, lambda h,s: IfDeclarationNode(s[2], s[4], s[6])#
expr %= while_t + expr + loop + expr + pool, lambda h,s: WhileLoop(s[2], s[4])#
#expr %= id_t + opar + lista_argum + cpar, lambda h,s: CallNode(s[3][0], s[1], s[3])
#expr %= expr + dot + id_t + opar + lista_argum + cpar, lambda h,s: CallNode(s[1], s[3], s[5])
#expr %= expr + at + id_t + dot + id_t + opar + lista_argum + cpar, lambda h,s: CallNode((s[1], s[3]), s[5], s[7])#Verificar s[3] sea subclase de s[1]
#expr %= new + id_t, lambda h,s: InstantiateNode(s[2])
expr %= isVoid + expr, lambda h,s: FuncionIsVoid(s[2])
expr %= hyphen + expr, lambda h,s: Complemento(s[2])
#expr %= expr + plus + expr, lambda h,s: PlusNode(s[1], s[3])#
#expr %= expr + minus + expr, lambda h,s: MinusNode(s[1], s[3])#
#expr %= expr + star + expr, lambda h,s: StarNode(s[1], s[3])#
#expr %= expr + div + expr, lambda h,s: Division(s[1], s[3])#
#expr %= expr + lesser + expr, lambda h,s: LesserNode(s[1], s[3])#
#expr %= expr + equal + expr, lambda h,s: EqualNode(s[1], s[3])#
#expr %= expr + lesser + equal + expr, lambda h,s: LesserEqualNode(s[1], s[4])#
expr %= not_t + expr, lambda h,s: Negacion(s[2])
#expr %= opar + expr + cpar, lambda h,s: s[2]
#expr %= id_t, lambda h,s: VariableNode(s[2])
#expr %= num, lambda h, s: ConstantNumNode(s[1])
expr %= cond, lambda h,s: s[1]
# <decla_variable,-list>
lista_decla_variable %= decla_variable + comma + lista_decla_variable, lambda h,s: [s[1]] + s[3]  
lista_decla_variable %= decla_variable, lambda h,s: [s[1]]                                        
# <decla_variable,>
decla_variable %= id_t + colon + id_t, lambda h,s: (s[1], s[3], None)           
decla_variable %= id_t + colon + id_t + larrow + expr, lambda h,s: (s[1], s[3], s[5])   
# <case-var-list>
case_var_list %= case_var + semi + case_var_list, lambda h,s: [s[1]] + s[3]
case_var_list %= case_var + semi, lambda h,s: [s[1]]
# <case_var>
case_var %= id_t + colon + id_t + rarrow + expr, lambda h,s: (s[1], s[3], s[5])
# <lista_argum>
lista_argum %= G.Epsilon, lambda h,s: []
lista_argum %= expr, lambda h,s: [ s[1] ]
lista_argum %= expr + comma + lista_argum, lambda h,s: [ s[1] ] + s[3]
# <arith>       
arith %= arith + plus + term, lambda h,s: Suma(s[1], s[3])
arith %= arith + minus + term, lambda h,s: Resta(s[1], s[3])
arith %= term, lambda h,s: s[1]
# <term>     
term %= term + star + factor, lambda h, s: Multiplicacion(s[1], s[3])
term %= term + div + factor, lambda h, s: Division(s[1], s[3])
term %= factor, lambda h, s: s[1]
# <cond>
cond %= cond + equal + arith, lambda h,s: Igual(s[1], s[3]) 
cond %= cond + lesser + arith, lambda h,s: Menor(s[1], s[3])
cond %= cond + lesser + equal + arith, lambda h,s: MenorOIqual(s[1],s[4])
cond %= arith, lambda h,s: s[1]
# <factor>      
factor %= atom, lambda h, s: s[1]
factor %= opar + expr + cpar, lambda h, s: s[2]
factor %= if_t + expr + then + expr + else_t + expr + fi, lambda h,s: IfThenElse(s[2], s[4], s[6])
factor %= id_t + opar + lista_argum + cpar, lambda h,s: Invocacion(None, s[1], s[3])
factor %= factor + dot + id_t + opar + lista_argum + cpar, lambda h,s: Invocacion(s[1], s[3], s[5])
factor %= factor + at + id_t + dot + id_t + opar + lista_argum + cpar, lambda h,s: InvocacionEstatica((s[1], s[3]), s[5], s[7])#Verificar s[3] sea subclase de s[1]
#factor %= factor + inv_func, lambda h,s: CallNode(s[1], s[2][0], s[2][1])
# <atom>
atom %= true, lambda h,s: Bool(True)
atom %= false, lambda h,s: Bool(False) 
atom %= string, lambda h, s: String(s[1])
atom %= num, lambda h, s: Entero(s[1])
atom %= id_t, lambda h, s: Identificador(s[1])
atom %= new + id_t, lambda h,s: NuevoTipo(s[2])

# <inv_func>
#inv_func %= dot + id_t + opar + lista_argum + cpar, lambda h, s: (s[2], s[4])        
