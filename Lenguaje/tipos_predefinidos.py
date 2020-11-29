from cmp.semantic import Type, IntType, VoidType

def dicc_de_tipos_predefinidos( clase ):
    return {
        "Object": clase.objeto,
        "Int": clase.int,
        "Bool": clase.bool,
        "Void": clase.void,
        "AUTO_TYPE" : Auto(),
        "String" : clase.string
    }
    
class TipoPredefinidos:
    def __init__(self):
        self.objeto = Objeto()
        self.bool = Bool()
        self.string = String()
        self.int = IntType()
        self.void = VoidType()
class Objeto(Type):
    def __init__(self):
        Type.__init__(self, "Object")
    
    def bypass(self):
        return True
    def conforms_to(self,other):
        return self == other

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, Objeto)

class Bool(Type):
    def __init__(self):
        Type.__init__(self, "Bool")

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, Bool)


class String(Type):
    def __init__(self):
        Type.__init__(self, "String")

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, String)


class Auto(Type):
    def __init__(self, tipos_posibles = ["nueva"]):
        Type.__init__(self, "AUTO_TYPE")
        self.tipos_posibles = tipos_posibles
    def bypass(self):
        return True
    def conforms_to(self,other):
        return True

    @property
    def is_auto_type(self):
        return True

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, Auto)
    
    def redefinir(self, lista):
        pass