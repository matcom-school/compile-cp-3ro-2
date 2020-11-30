from cmp.semantic import Type, IntType, VoidType

def dicc_de_tipos_predefinidos( clase ):
    return {
        "Object": clase.objeto,
        "Int": clase.int,
        "Bool": clase.bool,
        "Void": clase.void,
        "AUTO_TYPE" : Auto(),
        "String" : clase.string,
        "IO": clase.io
    }
    
class TipoPredefinidos:
    def __init__(self):
        self.objeto = Objeto()
        self.bool = Bool()
        self.string = String()
        self.int = IntType()
        self.void = VoidType()
        self.io = IO()
        self.self = Self()

class Objeto(Type):
    def __init__(self):
        Type.__init__(self, "Object")
        
        self.define_method(
            name = "abort",
            param_names = [],
            param_types = [],
            return_type = self
        )
        
        self.define_method(
            name = "type_name",
            param_names = [],
            param_types = [],
            return_type = self
        )
        
        self.define_method(
            name = "copy",
            param_names = [],
            param_types = [],
            return_type = Self()
        )
    def bypass(self):
        return True
    def conforms_to(self,other):
        return other.bypass() or self == other

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, Objeto)
class IO(Type):
    def __init__(self):
        Type.__init__(self,"IO")

        self.define_method(
            name = "out_string",
            param_names = ["x"],
            param_types = [String()],
            return_type = Self()
        )
        self.define_method(
            name = "out_int",
            param_names = ["x"],
            param_types = [IntType()],
            return_type = Self()
        )
        self.define_method(
            name = "in_string",
            param_names = [],
            param_types = [],
            return_type = String()
        )
        self.define_method(
            name = "in_int",
            param_names = [],
            param_types = [],
            return_type = IntType()
        )

class Bool(Type):
    def __init__(self):
        Type.__init__(self, "Bool")

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, Bool)


class String(Type):
    def __init__(self):
        Type.__init__(self, "String")

        self.define_method(
            name = "length",
            param_names = [],
            param_types = [],
            return_type = IntType()
        )

        self.define_method(
            name = "concat",
            param_names = ["s"],
            param_types = [self],
            return_type = self
        )

        self.define_method(
            name = "substr",
            param_names = ["i","l"],
            param_types = [IntType(),IntType()],
            return_type = self
        )
    def __eq__(self, other):
        return other.name == self.name or isinstance(other, String)

class Self(Type):
    def __init__(self):
        Type.__init__(self, "SELF_TYPE")

    @property
    def is_self_type(self):
        return True
    def real_type(self, possible):
        return possible

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
    
