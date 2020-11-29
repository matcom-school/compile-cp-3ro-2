class Nodo:
    pass


################ Nodos Principales #################
####################################################
class Programa(Nodo):
    def __init__(self, list_clases):
        self.lista_de_clases = list_clases

    def __str__(self):
        resultado = ""
        for cl in self.lista_de_clases:
            resultado += str(cl)
        return resultado

class ClaseDeCool(Nodo):
    def __init__(self, lista_de_miembros, nombre, clase_base=None):
        self.lista_de_miembros = lista_de_miembros
        self.id = nombre
        self.clase_base = clase_base

    def __str__(self):
        result = "class "
        result = result + f"{self.id} : {self.clase_base}" + "\n"
        for m in self.lista_de_miembros:
            result = result + "    " + str(m) + "\n"

        return result

############ Miembros de las Clasese ###############
####################################################
class Miembro(Nodo):
    pass


class DefAtributo(Miembro):
    def __init__(self, id, tipo, exprecion = None):
        self.id = id
        self.tipo = tipo
        self.exprecion = exprecion

    def __str__(self):
        return str(self.id + "," + self.tipo + " -> " + str(self.exprecion))


class DefFuncion(Miembro):
    def __init__(self, id, parametros, cuerpo, tipo):
        self.id = id
        self.parametros = parametros
        self.cuerpo = cuerpo
        self.tipo = tipo

    def __str__(self):
        return str(
            self.id
            + "("
            + str([ f"{i} : {t}" for i,t in self.parametros])
            + ")"
            + " : "
            + self.tipo
            + " -> "
            + str(self.cuerpo)
        )

################# Expreciones ######################
####################################################
class Exprecion(Nodo):
    pass

class Invocacion(Exprecion):
    def __init__(self, exp, id, lista_de_exp):
        self.id = id
        self.exp = exp
        self.lista_de_exp = lista_de_exp

    def __str__(self):
        return str("Invocacion")

class InvocacionEstatica(Exprecion):
    def __init__(self, exp, tipo_especifico, id, lista_de_exp):
        self.id = id
        self.exp = exp
        self.tipo_especifico = tipo_especifico
        self.lista_de_exp = lista_de_exp

    def __str__(self):
        result = f"{self.exp}({self.tipo_especifico}).{self.id}(\n"
        for e in self.lista_de_exp:
            result += str(e) + ",\n"

        return result + ")"

########### Expreciones Estilo Estructura ##########
####################################################
class Estructura(Exprecion):
    pass 

class Asignacion(Estructura):
    def __init__(self, id, valor):
        self.id = id
        self.valor = valor

    def __str__(self):
        return str("Assign")


class IfThenElse(Estructura):
    def __init__(self, condicion, exp_si_true, exp_si_false):
        self.condicion = condicion
        self.exp_si_true = exp_si_true
        self.exp_si_false = exp_si_false

    def __str__(self):
        return str("IfThenElse")


class WhileLoop(Estructura):
    def __init__(self, condicion, exp):
        self.condicion = condicion
        self.exp = exp

    def __str__(self):
        return str("While")

class Block(Estructura):
    def __init__(self, lista_de_exp):
        self.lista_de_exp = lista_de_exp

    def __str__(self):
        return str("block: " + str(self.lista_de_exp))

class LetIn(Estructura):
    def __init__(self, lista_de_acciones, exp):
        self.lista_de_acciones = lista_de_acciones
        self.exp = exp

    def __str__(self):
        return str("LetIn " + self.lista_de_acciones + ": " + str(self.exp))


class Case(Estructura):
    def __init__(self, exp, lista_de_casos):
        self.exp = exp
        self.lista_de_casos = lista_de_casos

    def __str__(self):
        return str("Case " + str(self.exp) + ": " + self.lista_de_casos)


################ Expreciones Unarias ###############
####################################################
class Unaria(Exprecion):
    def __init__(self, exp):
        self.exp = exp

        
class NuevoTipo(Exprecion):
    def __init__(self, tipo):
        self.tipo = tipo

    def __str__(self):
        return str("NuevoTipo")


class Negacion(Unaria):
    def __str__(self):
        return str("Not " + str(self.exp))


class FuncionIsVoid(Unaria):
    def __str__(self):
        return str("IsVoid? " + str(self.exp))


class Complemento(Unaria):
    def __str__(self):
        return str("~" + str(self.exp))


class ExprEntreParantesis(Unaria):
    def __str__(self):
        return str("(" + str(self.exp) + ")")


################ Expreciones Binarias ###############
#####################################################
class Binaria(Exprecion):
    def __init__(self, isq, der):
        self.der = der
        self.isq = isq


################ Comparaciones ######################
#####################################################
class Comparacion(Binaria):
    def __str__(self):
        pass

class MenorOIqual(Comparacion):
    def __str__(self):
        return str("<=")


class Igual(Comparacion):
    def __str__(self):
        return str("==")


class Menor(Comparacion):
    def __str__(self):
        return str("<")


################ Aritmeticas ######################
#####################################################
class Aritmetica(Binaria):
    def __str__(self):
        pass

class Suma(Aritmetica):
    def __str__(self):
        return str("+")


class Resta(Aritmetica):
    def __str__(self):
        return str("-")


class Multiplicacion(Aritmetica):
    def __str__(self):
        return str("*")


class Division(Aritmetica):
    def __str__(self):
        return str("/")


################ Expreciones Atomica 3###############
#####################################################
class Atomica(Exprecion):
    def __init__(self, lex):
        self.lex = lex


class Int(Atomica):
    def __str__(self):
        return str("Int")


class String(Atomica):
    def __str__(self):
        return str("String")


class Bool(Atomica):
    def __str__(self):
        return str("Bool")


class Identificador(Exprecion):
    def __init__(self, lex):
        self.id = lex

    def __str__(self):
        return str("Id")

