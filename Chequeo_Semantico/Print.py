import cmp.visitor as visitor
from Lenguaje import *

def ASTtoString(AST):
    return visit(None,AST,None,0)

def TabNVeces(n):
    return n*'\t'

caracter185=chr(185)
caracter186=chr(186)
caracter187=chr(187)

@visitor.on("node")
def visit(self, node, scope,nivel):
        pass

@visitor.when(Programa)
def visit (self,node,scope,nivel):
    
    cuerpo= ""
    for cl in node.lista_de_clases:
        cuerpo+="\n"+TabNVeces(nivel+1)+ visit(self,cl,scope,nivel+1)
    return str('@'+"Program {" 
               + cuerpo 
               +"\n"+TabNVeces(nivel)+"}")

@visitor.when(ClaseDeCool)
def visit (self,node,scope,nivel:int):
    cuerpo=""
    for cl in node.lista_de_miembros:
        cuerpo+="\n"+TabNVeces(nivel+1)+str( visit(self,cl,scope,(nivel+1)))
    return str(
    "class " +node.id + ("" if node.clase_base is None else (" inherits "+node.clase_base.id)) +" {"
    +cuerpo
    +"\n"+TabNVeces(nivel)+"}")

@visitor.when(DefAtributo)
def visit (self,node,scope,nivel):
    expresion="" if node.exprecion is None else (" "+ visit(self,node.exprecion,scope,(nivel+1)))
    return str(node.id + " :" + node.tipo +("" if expresion == "" else (" -> "+ expresion)))

@visitor.when(DefFuncion)
def visit (self,node,scope,nivel):
    parametros=""
    cuerpo=""
    for idx,tipo in node.parametros:
        parametros+= f"{idx} : {tipo}, "

    cuerpo+="\n"+TabNVeces(nivel+1)+visit(self,node.cuerpo,scope,(nivel+1))
    return str(node.id+"( "+parametros+" ): "+node.tipo+" {"
               +cuerpo
               +"\n"
               +TabNVeces(nivel)
               +"}")



@visitor.when(Invocacion)
def visit (self,node,scope,nivel):
    expresion=""
    for expre in node.lista_de_exp:
        expresion+= f" {visit(self,expre,scope,(nivel+1))},"
    
    return str(node.exp
               +"."
               +node.id
               +"("
               +expresion
               +")\n")

@visitor.when(InvocacionEstatica)
def visit (self,node,scope,nivel):
    expresion=""
    for expre in node.lista_de_exp:
        expresion+=", "+ visit(self,expre,scope,(nivel+1))
    expresion=expresion[2:]
    return str(node.exp+"@"+node.tipo_especifico+"."+node.id+"("+expresion+")\n")

@visitor.when(LetIn)
def visit (self,node,scope,nivel):
    cuerpo=""
    for cu in node.lista_de_acciones:
        cuerpo+="\n"+TabNVeces(nivel+1)+visit(self,cu,scope,(nivel+1))
    return str("Let "
               +cuerpo+
               "\n"+TabNVeces(nivel)+"in "+visit(self,node.exp,scope,(nivel+1))+"\n")


@visitor.when(Case)
def visit (self,node,scope,nivel):
    casos=""
    for caso in node.lista_de_casos:
        casos+= "\n"+TabNVeces(nivel+1)+str(caso.id +": "+ caso.tipo +" => " + visit(self,caso.exp,scope,(nivel+1))+";")
    return str("Case "+visit(node.exp)+" of"
               +casos
               +TabNVeces(nivel)+"esac\n")

@visitor.when(WhileLoop)
def visit (self,node,scope,nivel):
    return str("While "+visit(self,node.condicion,scope,(nivel+1))+"\n"
               +TabNVeces(nivel)+"Loop"+visit(self,node.exp,scope,(nivel+1))+"\n"
               +TabNVeces(nivel)+"Pool\n")

@visitor.when(IfThenElse)
def visit (self,node,scope,nivel):
        return str("If "+visit(self,node.condicion,scope,(nivel+1))+"\n"
               +TabNVeces(nivel)+"Then "+visit(self,node.exp_si_true,scope,(nivel+1))+"\n"
               +TabNVeces(nivel)+"Else "+visit(self,node.exp_si_false,scope,(nivel+1))+"\n"
               +TabNVeces(nivel)+"Fi\n")

@visitor.when(Block)
def visit (self,node,scope,nivel):
    expresiones=""
    for exp in node.lista_de_exp:
        expresiones+= "\n"+TabNVeces(nivel+1)+visit(self,exp,scope,(nivel+1))+";"
    return "{"+expresiones+"\n"+TabNVeces(nivel)+"}\n"

@visitor.when(Asignacion)
def visit (self,node,scope,nivel):
    return str(node.id+" <- "+visit(self,node.valor,scope,(nivel+1)))

@visitor.when(NuevoTipo)
def visit (self,node,scope,nivel):
    return "new "+node.tipo

@visitor.when(Negacion)
def visit (self,node,scope,nivel):
    return str("Not " + visit(self,node.exp,scope,(nivel+1)))

@visitor.when(FuncionIsVoid)
def visit (self,node,scope,nivel):
    return str("IsVoid " + visit(self,node.exp,scope,(nivel+1)))

@visitor.when(Complemento)
def visit (self,node,scope,nivel):
    return str("~" + visit(self,node.exp,scope,(nivel+1)))

@visitor.when(ExprEntreParantesis)
def visit (self,node,scope,nivel):
    return str("(" + visit(self,node.exp,scope,(nivel+1)) + ")")

@visitor.when(MenorOIqual)
def visit (self,node,scope,nivel):
    return str(visit(self,node.der,scope,(nivel+1))+ " <= "+ visit(self,node.izq,scope,(nivel+1)))

@visitor.when(Igual)
def visit (self,node,scope,nivel):
    return str(visit(self,node.der,scope,(nivel+1))+ " = "+ visit(self,node.izq,scope,(nivel+1)))

@visitor.when(Menor)
def visit (self,node,scope,nivel):
    return str(visit(self,node.der,scope,(nivel+1))+ " < "+ visit(self,node.izq,scope,(nivel+1)))

@visitor.when(Suma)
def visit (self,node,scope,nivel):
    return str(visit(self,node.der,scope,(nivel+1))+ " + "+ visit(self,node.izq,scope,(nivel+1)))

@visitor.when(Resta)
def visit (self,node,scope,nivel):
    return str(visit(self,node.der,scope,(nivel+1))+ " - "+ visit(self,node.izq,scope,(nivel+1)))

@visitor.when(Multiplicacion)
def visit (self,node,scope,nivel):
    return str(visit(self,node.der,scope,(nivel+1))+ " * "+ visit(self,node.izq,scope,(nivel+1)))

@visitor.when(Division)
def visit (self,node,scope,nivel):
    return str(visit(self,node.der,scope,(nivel+1))+ " / "+ visit(self,node.izq,scope,(nivel+1)))

@visitor.when(Int)
def visit (self,node,scope,nivel):
    return str(node.lex)

@visitor.when(String)
def visit (self,node,scope,nivel):
    return str(node.lex)

@visitor.when(Bool)
def visit (self,node,scope,nivel):
    return str(node.lex)

@visitor.when(Identificador)
def visit (self,node,scope,nivel):
    return str(node.lex)

#@visitor.when()
#def visit (self,node,scope):
#    pass
