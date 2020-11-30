#cambiar y poner en la funcion que llama los cambios de lineas finales tambien, arreglar bien lo del llamado de las funciones estaticas

import cmp.visitor as visitor
from Lenguaje import *

def ASTtoString(AST):
    return visit(None,AST,None,-1)

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
        cuerpo+="\n"+TabNVeces(nivel+1)+ visit(self,cl,scope,nivel+1)+";"
    return str(cuerpo)

@visitor.when(ClaseDeCool)
def visit (self,node,scope,nivel:int):
    cuerpo=""
    for cl in node.lista_de_miembros:
        cuerpo+="\n"+TabNVeces(nivel+1)+str( visit(self,cl,scope,(nivel+1))+";")
    return str(
    "class " +node.id + ("" if node.clase_base is None else (" inherits "+node.clase_base)) +" {"
    +cuerpo
    +"\n"+TabNVeces(nivel)+"}")

@visitor.when(DefAtributo)
def visit (self,node,scope,nivel):
    expresion="" if node.exprecion is None else (" "+ visit(self,node.exprecion,scope,(nivel+1)))
    return str(node.id + " :" + node.tipo +("" if expresion == "" else (" <- "+ expresion)))

@visitor.when(DefFuncion)
def visit (self,node,scope,nivel):
    parametros=""
    cuerpo=""
    for Item1,Item2 in node.parametros:
        parametros+=" ,"+ Item1 + " : " +Item2
    if parametros != "":
        parametros=parametros[2:]
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
        expresion+= visit(self,expre,scope,(nivel+1))+" , "
    if expresion != "":
        text=expresion[:-3]
    else:
        text=""
    text=str(text)
    if node.exp is None:
        return str(node.id
               +"("
               +text
               +")")
    return str(visit(self,node.exp,scope,(nivel+1))
               +"."
               +node.id
               +"("
               +text
               +")")

@visitor.when(InvocacionEstatica)
def visit (self,node,scope,nivel):
    expresion=""
    for expre in node.lista_de_exp:
        expresion+=", "+ visit(self,expre,scope,nivel+1)
    expresion=expresion[2:]
    return str(visit(self,node.exp,scope,(nivel+1))+"@"+node.tipo_especifico+"."+node.id+"("+expresion+")")

@visitor.when(LetIn)
def visit (self,node,scope,nivel):
    cuerpo=""
    for id,id1,exp in node.lista_de_acciones:
        cuerpo+="\n"+TabNVeces(nivel+1)+id+" : "+ id1
        if not exp is None:
            cuerpo+= " <- "+ visit(self,exp,scope,nivel+1)
    return str("let "
               +cuerpo
               +"\n"+TabNVeces(nivel+1)+"in "+visit(self,node.exp,scope,(nivel+1)))


@visitor.when(Case)
def visit (self,node,scope,nivel):
    casos=""
    for Item1,Item2,Item3 in node.lista_de_casos:
        casos+= "\n"+TabNVeces(nivel+1)+str(Item1 +": "+ Item2 +" => " + visit(self,Item3,scope,(nivel+1))+";")
    return str("case "+visit(self,node.exp,scope,nivel+1)+" of"
               +casos
               +"\n"+TabNVeces(nivel)+"esac")

@visitor.when(WhileLoop)
def visit (self,node,scope,nivel):
    return str("while "+visit(self,node.condicion,scope,(nivel+1))+"\n"
               +TabNVeces(nivel)+"loop "+visit(self,node.exp,scope,(nivel+1))+"\n"
               +TabNVeces(nivel)+"pool")

@visitor.when(IfThenElse)
def visit (self,node,scope,nivel):
        return str("if "+visit(self,node.condicion,scope,(nivel+1))+"\n"
               +TabNVeces(nivel)+"then "+visit(self,node.exp_si_true,scope,(nivel+1))+"\n"
               +TabNVeces(nivel)+"else "+visit(self,node.exp_si_false,scope,(nivel+1))+"\n"
               +TabNVeces(nivel)+"fi")

@visitor.when(Block)
def visit (self,node,scope,nivel):
    expresiones=""
    for exp in node.lista_de_exp:
        expresiones+= "\n"+TabNVeces(nivel+1)+visit(self,exp,scope,(nivel+1))+";"
    return "{"+expresiones+"\n"+TabNVeces(nivel)+"}"

@visitor.when(Asignacion)
def visit (self,node,scope,nivel):
    return str(node.id+" <- "+visit(self,node.valor,scope,(nivel+1)))

@visitor.when(NuevoTipo)
def visit (self,node,scope,nivel):
    return "new "+node.tipo

@visitor.when(Negacion)
def visit (self,node,scope,nivel):
    return str("not " + visit(self,node.exp,scope,(nivel+1)))

@visitor.when(FuncionIsVoid)
def visit (self,node,scope,nivel):
    return str("isVoid " + visit(self,node.exp,scope,(nivel+1)))

@visitor.when(Complemento)
def visit (self,node,scope,nivel):
    return str("~" + visit(self,node.exp,scope,(nivel+1)))

@visitor.when(ExprEntreParantesis)
def visit (self,node,scope,nivel):
    return str("(" + visit(self,node.exp,scope,(nivel+1)) + ")")

@visitor.when(MenorOIqual)
def visit (self,node,scope,nivel):
    return str(visit(self,node.isq,scope,(nivel+1))+ " <= "+ visit(self,node.der,scope,(nivel+1)))

@visitor.when(Igual)
def visit (self,node,scope,nivel):
    return str(visit(self,node.isq,scope,(nivel+1))+ " = "+ visit(self,node.der,scope,(nivel+1)))

@visitor.when(Menor)
def visit (self,node,scope,nivel):
    return str(visit(self,node.isq,scope,(nivel+1))+ " < "+ visit(self,node.der,scope,(nivel+1)))

@visitor.when(Suma)
def visit (self,node,scope,nivel):
    return str(visit(self,node.isq,scope,(nivel+1))+ " + "+ visit(self,node.der,scope,(nivel+1)))

@visitor.when(Resta)
def visit (self,node,scope,nivel):
    return str(visit(self,node.isq,scope,(nivel+1))+ " - "+ visit(self,node.der,scope,(nivel+1)))

@visitor.when(Multiplicacion)
def visit (self,node,scope,nivel):
    return str(visit(self,node.isq,scope,(nivel+1))+ " * "+ visit(self,node.der,scope,(nivel+1)))

@visitor.when(Division)
def visit (self,node,scope,nivel):
    return str(visit(self,node.isq,scope,(nivel+1))+ " / "+ visit(self,node.der,scope,(nivel+1)))

@visitor.when(Int)
def visit (self,node,scope,nivel):
    return str(node.lex)

@visitor.when(String)
def visit (self,node,scope,nivel):
    return node.lex

@visitor.when(Bool)
def visit (self,node,scope,nivel):
    return str(node.lex)

@visitor.when(Identificador)
def visit (self,node,scope,nivel):
    return str(node.id)


