from .dependencias import *

class ChequeoSemantico:
    def __init__(self, contexto : Context, errores : list):
        self.contexto = contexto
        self.errores = errores
 

    @visitor.on("nodo")
    def visita(self, nodo, mi_ambiente = None):
        pass
    
    @visitor.when(Programa)
    def visita(self, nodo : Programa, mi_ambiente : Scope = None):
        mi_ambiente = Scope()
        for cl in nodo.lista_de_clases:
            self.visita(cl, mi_ambiente)
        
        return not any(self.errores), mi_ambiente
    
    @visitor.when(ClaseDeCool)
    def visita(self, nodo : ClaseDeCool, mi_ambiente : Scope):
        mi_ambiente = mi_ambiente.create_child( nodo )
        self.contexto.current_type = self.contexto.get_type(nodo.id)
        mi_ambiente.define_variable("self",self.contexto.current_type)

        clase_base : Type = self.contexto.current_type
        while clase_base.parent is not None:
            if clase_base.parent.is_auto_type:
                self.errores.append( f"ClassDefinitionError: Can't use {clase_base.parent.name} in herence")
                break
            clase_base = clase_base.parent.real_type(self.contexto.current_type)
            if clase_base.name == nodo.id:
                self.errores.append("ClassDefinitionError: " + MensajeDeError.herencia_circular(nodo.id))
                break
        
        for atri in self.contexto.current_type.attributes:
            mi_ambiente.define_variable( atri.name, atri.type)
        
        for atri, tipo  in reversed( self.contexto.current_type.all_attributes() ):
            if not mi_ambiente.is_local(atri.name):
                mi_ambiente.define_variable( atri.name, atri.type)
            
        for m in nodo.lista_de_miembros:
            self.visita(m, mi_ambiente)

    @visitor.when( DefAtributo)
    def visita(self, nodo : DefAtributo, mi_ambiente : Scope):
        tipo : Type = self.contexto.get_type( nodo.tipo ).real_type(self.contexto.current_type)
        if nodo.exprecion is not None:
            tipo_de_la_expr: Type = self.visita(nodo.exprecion, mi_ambiente)

        if self.contexto.current_type.parent is not None:
            try:
                atri_base = self.contexto.current_type.parent.get_attribute( nodo.id)
                if not tipo.conforms_to(atri_base.type):
                    self.errores.append("AttributeDefinitionError: " + MensajeDeError.atributo_heredado(nodo.id , atri_base.type.name ))

            except SemanticError:
                pass

        if nodo.exprecion is not None and not tipo_de_la_expr.conforms_to(tipo):
            self.errores.append("AttributeDefinitionError: " + MensajeDeError.asignacion(tipo.name,tipo_de_la_expr.name))

    @visitor.when( DefFuncion )
    def visita(self, nodo : DefFuncion, mi_ambiente : Scope):
        mi_ambiente = mi_ambiente.create_child( nodo )
        metodo = self.contexto.current_type.get_method(nodo.id)

        for i, nombre in enumerate(metodo.param_names):
            mi_ambiente.define_variable(nombre, metodo.param_types[i].real_type(self.contexto.current_type))

        tipo_de_retorno = self.visita(nodo.cuerpo, mi_ambiente)
        tipo_r = metodo.return_type.real_type(self.contexto.current_type)
        if not tipo_de_retorno.conforms_to(tipo_r):
            self.errores.append("FunctionDefinitionError: " + MensajeDeError.asignacion(tipo_r.name,tipo_de_retorno.name))

        if self.contexto.current_type.parent is not None:
            try:
                clase_base : Type = self.contexto.current_type.parent
                metodo_base = clase_base.get_method( nodo.id )
                _condicion = len(metodo_base.param_types) == len(metodo.param_types)
                _condicion = _condicion and tipo_r.conforms_to(metodo_base.return_type)
                if _condicion:
                    for i, tipo in enumerate( metodo.param_types ):
                        _condicion = _condicion and tipo.real_type(self.contexto.current_type).conforms_to(metodo_base.param_types[i])
                if not _condicion:
                    self.errores.append("FunctionDefinitionError: " + MensajeDeError.funcion_heredada(clase_base.name, metodo.name))

            except SemanticError:
                pass
    
    @visitor.when( Invocacion )
    def visita(self, nodo : Invocacion, mi_ambiente : Scope):
        if nodo.exp is not None:
            tipo_de_la_exp : Type = self.visita(nodo.exp, mi_ambiente)
        else:
            tipo_de_la_exp : Type = self.contexto.current_type
        
        lista_de_tipos = []
        for param in nodo.lista_de_exp:
            lista_de_tipos.append( self.visita(param, mi_ambiente))

        if tipo_de_la_exp.is_auto_type: return tipo_de_la_exp
        tipo_de_retorno = ErrorType()
        try:
            metodo = tipo_de_la_exp.get_method( nodo.id )
            tipo_de_retorno = metodo.return_type.real_type(tipo_de_la_exp)
            if not len(nodo.lista_de_exp) == len(metodo.param_names):
                self.errores.append("DispathError: " + MensajeDeError.numero_de_parametros(tipo_de_la_exp.name,metodo.name,len(nodo.lista_de_exp)))
            for i, tipo_exp in enumerate( lista_de_tipos ):
                tipo_p = metodo.param_types[i].real_type(tipo_de_la_exp)
                if i < len(metodo.param_types) and not tipo_p.conforms_to( tipo_exp ):
                    self.errores.append("DispathError: " + MensajeDeError.asignacion(tipo_p.name,tipo_exp.name))
        except SemanticError as se:
            self.errores.append("DispathError: " + se.text)
        
        return tipo_de_retorno

    @visitor.when( InvocacionEstatica )
    def visita(self, nodo : InvocacionEstatica, mi_ambiente : Scope):
        tipo_de_la_exp : Type = self.visita(nodo.exp,mi_ambiente)
        tipo_especifico : Type = self.contexto.get_type( nodo.tipo_especifico ).real_type(self.contexto.current_type)

        lista_de_tipos = []
        for param in nodo.lista_de_exp:
            lista_de_tipos.append( self.visita(param, mi_ambiente))
        if not tipo_de_la_exp.conforms_to(tipo_especifico):
                self.errores.append("DispathError: " + MensajeDeError.asignacionExplisista(tipo_de_la_exp.name,tipo_especifico.name))

        tipo_de_retorno = ErrorType()
        metodo = None
        tipo_para_errores = None
        try:
            if tipo_especifico.is_auto_type:
                self.errores.append(f"DispathError: Can't use {tipo_especifico.name} as a specific type")
                return tipo_de_retorno
            metodo = tipo_especifico.get_method( nodo.id )
            tipo_para_errores = tipo_especifico
        except SemanticError as se:
            self.errores.append("DispathWarning: " + se.text)
            try:
                if tipo_de_la_exp.is_auto_type: return tipo_de_la_exp
                metodo = tipo_de_la_exp.get_method( nodo.id )
                tipo_para_errores = tipo_de_la_exp
            except SemanticError as se:
                self.errores.append("DispathError: " + se.text)      
        
        if metodo is not None:
            tipo_de_retorno = metodo.return_type.real_type(tipo_especifico)
            if not len(nodo.lista_de_exp) == len(metodo.param_names):
                self.errores.append("DispathError: " + MensajeDeError.numero_de_parametros(tipo_para_errores.name,metodo.name,len(nodo.lista_de_exp)))
            for i, tipo_exp in enumerate( lista_de_tipos ):
                tipo_p = metodo.param_types[i].real_type(tipo_especifico)
                if i < len(metodo.param_types) and not tipo_p.conforms_to( tipo_exp ):
                    self.errores.append("DispathError: " + MensajeDeError.asignacion(tipo_p.name,tipo_exp.name))
      
        return tipo_de_retorno

    @visitor.when( Asignacion )
    def visita(self, nodo : Asignacion, mi_ambiente : Scope):
        if nodo.id == "self":
            self.errores.append("AssignationError: " + MensajeDeError.solo_lectura(nodo.id))
        
        var = mi_ambiente.find_variable(nodo.id)
        tipo_de_var = ErrorType()
        if var is None:
            self.errores.append("AssignationError: " + MensajeDeError.no_definida(nodo.id))
        else: tipo_de_var = var.type.real_type(self.contexto.current_type)

        tipo_de_la_exp = self.visita(nodo.valor, mi_ambiente)
        if not tipo_de_la_exp.conforms_to(tipo_de_var):
            self.errores.append("AssignationError: " + MensajeDeError.asignacion(tipo_de_var.name,tipo_de_la_exp.name))
        
        return tipo_de_la_exp
    
    @visitor.when(IfThenElse)
    def visita(self, nodo : IfThenElse, mi_ambiente: Scope):
        tipo_de_la_cond = self.visita(nodo.condicion,mi_ambiente)
        tipo_del_si = self.visita(nodo.exp_si_true,mi_ambiente)
        tipo_del_no = self.visita(nodo.exp_si_false,mi_ambiente)
        
        if not tipo_de_la_cond.conforms_to(self.contexto.built_in_type.bool):
            self.errores.append("CondictionError: " + MensajeDeError.asignacion(self.contexto.built_in_type.bool.name, tipo_de_la_cond.name))

        while True:
            if tipo_del_si.is_auto_type or tipo_del_si.is_error_type:
                return tipo_del_si
            if tipo_del_no.is_auto_type or tipo_del_no.is_error_type:
                return tipo_del_no
            if tipo_del_si.conforms_to(tipo_del_no):
                return tipo_del_no
            if tipo_del_no.conforms_to(tipo_del_si):
                return tipo_del_si
            
            tipo_del_si = tipo_del_si.parent if tipo_del_si.parent is not None else self.contexto.built_in_type.objeto
            tipo_del_no = tipo_del_no.parent if tipo_del_no.parent is not None else self.contexto.built_in_type.objeto
        

    @visitor.when( WhileLoop )
    def visita(self, nodo : WhileLoop, mi_ambiente : Scope):
        condicion = self.visita(nodo.condicion, mi_ambiente)
        _ = self.visita(nodo.exp,mi_ambiente)

        if not condicion.conforms_to( self.contexto.built_in_type.bool ):
            self.errores.append("CondictionError: " + MensajeDeError.asignacion(self.contexto.built_in_type.bool, condicion))

        return self.contexto.built_in_type.objeto

    @visitor.when(Block)
    def visita(self, nodo : Block, mi_ambiente: Scope):
        for exp in nodo.lista_de_exp[:-1]:
            _ = self.visita(exp,mi_ambiente)
        
        return self.visita(nodo.lista_de_exp[-1],mi_ambiente)
    
    @visitor.when(LetIn)
    def visita(self, nodo : LetIn, mi_ambiente: Scope):
        mi_ambiente = mi_ambiente.create_child( nodo )
        for nombre, tipo, exp in nodo.lista_de_acciones:
            tipo_var = ErrorType()
            try:
                temp = self.contexto.get_type(tipo)
                tipo_var = temp.real_type(self.contexto.current_type)
            except SemanticError as se:
                self.errores.append("LetError :" + se.text)
            if exp is not None:
                tipo_de_la_exp = self.visita(exp, mi_ambiente)
                if type(tipo_var) == type(ErrorType()):
                    tipo_var = tipo_de_la_exp
                if not tipo_de_la_exp.conforms_to(tipo_var):
                    self.errores.append("LetError :" + MensajeDeError.asignacion(tipo_var.name,tipo_de_la_exp.name) )
            if mi_ambiente.is_local(nombre):
                self.errores.append(f"{nombre} is already defined")
            else:
                mi_ambiente.define_variable(nombre,tipo_var) 
            

        return self.visita(nodo.exp, mi_ambiente)
    
    @visitor.when(Case)
    def visita(self, nodo : Case, mi_ambiente : Scope):
        _ = self.visita(nodo.exp, mi_ambiente)
        tipo_de_retorno = None
        for idx, tipo, exp in nodo.lista_de_casos:
            try:
                tipo_case = self.contexto.get_type(tipo).real_type(self.contexto.current_type)
            except SemanticError as se:
                tipo_case = ErrorType()
                self.errores.append(se.text)
            
            if tipo_case.is_auto_type:
                self.errores.append(f"CaseError: Can't use {tipo_case.name} as a specific type")

            nuevo = mi_ambiente.create_child(exp)
            nuevo.define_variable(idx, tipo_case)
            tipo_de_la_exp = self.visita( exp, nuevo)

            while True:
                if tipo_de_retorno is None:
                    tipo_de_retorno = tipo_de_la_exp
                    break
                if tipo_de_retorno.is_auto_type or tipo_de_retorno.is_error_type:
                    break
                if tipo_de_la_exp.is_auto_type or tipo_de_la_exp.is_error_type:
                    tipo_de_retorno = tipo_de_la_exp
                    break
                if tipo_de_retorno.conforms_to(tipo_de_la_exp):
                    tipo_de_retorno = tipo_de_la_exp
                    break
                if tipo_de_la_exp.conforms_to(tipo_de_retorno):
                    break
            
                tipo_de_retorno = tipo_de_retorno.parent if tipo_de_retorno.parent is not None else self.contexto.built_in_type.objeto
                tipo_de_la_exp = tipo_de_la_exp.parent if tipo_de_la_exp.parent is not None else self.contexto.built_in_type.objeto

        return tipo_de_retorno


    @visitor.when(Negacion)
    def visita(self, nodo : Negacion, mi_ambiente : Scope):
        tipo_de_la_exp = self.visita(nodo.exp, mi_ambiente)
        if not tipo_de_la_exp.conforms_to( self.contexto.built_in_type.bool ):
            self.errores.append("CaseError:" + MensajeDeError.asignacion(self.contexto.built_in_type.bool.name, tipo_de_la_exp.name))

        return self.contexto.built_in_type.bool

    @visitor.when(Complemento)
    def visita(self, nodo : Complemento, mi_ambiente : Scope):
        tipo_de_la_exp = self.visita(nodo.exp, mi_ambiente)
        if not tipo_de_la_exp.conforms_to( self.contexto.built_in_type.int ):
            self.errores.append("CaseError:" + MensajeDeError.asignacion(self.contexto.built_in_type.bool.name, tipo_de_la_exp.name))

        return self.contexto.built_in_type.bool

    @visitor.when(FuncionIsVoid)
    def visita(self, nodo : FuncionIsVoid, mi_ambiente : Scope):
        _ = self.visita(nodo.exp, mi_ambiente)
        return self.contexto.built_in_type.bool

    @visitor.when(ExprEntreParantesis)
    def visita(self, nodo : ExprEntreParantesis, mi_ambiente : Scope):
        return self.visita(nodo.exp, mi_ambiente)


    @visitor.when(NuevoTipo)
    def visita(self, nodo : NuevoTipo, mi_ambiente : Scope):
        tipo = "" if nodo.tipo in ["AUTO_TYPE","Void"] else nodo.tipo
        try: 
            return self.contexto.get_type(tipo)
        except SemanticError as se:
            self.errores.append(se.text)
            return ErrorType()

    @visitor.when(Aritmetica)
    def visita(self, nodo : Aritmetica, mi_ambiente : Scope):
        tipo_der = self.visita(nodo.der, mi_ambiente)
        tipo_isq = self.visita(nodo.isq, mi_ambiente)
        entero = self.contexto.built_in_type.int
        if not tipo_der.conforms_to(entero) or not tipo_isq.conforms_to(entero):
            self.errores.append(MensajeDeError.operacion_invalida(tipo_der.name,tipo_isq.name,str(nodo)))
        return self.contexto.built_in_type.int

    @visitor.when(Comparacion)
    def visita(self, nodo : Comparacion, mi_ambiente : Scope):
        tipo_der = self.visita(nodo.der, mi_ambiente)
        tipo_isq = self.visita(nodo.isq, mi_ambiente)
        entero = self.contexto.built_in_type.int
        if not tipo_der.conforms_to(entero) or not tipo_isq.conforms_to(entero):
            self.errores.append(MensajeDeError.operacion_invalida(tipo_der.name,tipo_isq.name,str(nodo)))
        return self.contexto.built_in_type.bool
    
    @visitor.when(Igual)
    def visita(self, nodo : Igual, mi_ambiente : Scope):
        tipo_der = self.visita(nodo.der, mi_ambiente)
        tipo_isq = self.visita(nodo.isq, mi_ambiente)
        tipos_basicos = [self.contexto.built_in_type.bool,self.contexto.built_in_type.int,self.contexto.built_in_type.string]
        if not (tipo_der.is_auto_type or tipo_der.is_error_type or tipo_isq.is_auto_type or tipo_isq.is_error_type):
            for t in tipos_basicos:
                if tipo_der.conforms_to(t) or tipo_isq.conforms_to(t):
                    if not (tipo_der.conforms_to(t) and tipo_isq.conforms_to(t)) :
                        self.errores.append(MensajeDeError.operacion_invalida(tipo_der.name,tipo_isq.name,str(nodo)))
                    break
        return self.contexto.built_in_type.bool
    
    @visitor.when(String)
    def visita(self, nodo, mi_ambiente):
        return self.contexto.built_in_type.string

    @visitor.when(Bool)
    def visita(self, nodo, mi_ambiente):
        return self.contexto.built_in_type.bool

    @visitor.when(Int)
    def visita(self, nodo, mi_ambiente):
        return self.contexto.built_in_type.int

    @visitor.when(Identificador)
    def visita(self, nodo: Identificador, mi_ambiente):
        var = mi_ambiente.find_variable(nodo.id)
        if var is None:
            self.errores.append(MensajeDeError.no_definida( nodo.id ))
            return ErrorType()
        return var.type.real_type(self.contexto.current_type)

class MensajeDeError:
    @staticmethod
    def asignacion(isq,der):
        return f"Cannot implicitly convert {der} to {isq}"
    @staticmethod
    def asignacionExplisista(isq,der):
        return f"Cannot explicitly convert {der} to {isq}"
    @staticmethod
    def funcion_heredada(clase_base, metodo):
        return f"Method '{metodo}' is inconsistent with its defined in base class {clase_base}"
    @staticmethod
    def atributo_heredado( atributo, tipo_base):
        return f"Attribute '{atributo}' is inconsistent with type { tipo_base } of the base class attributes"
    @staticmethod
    def numero_de_parametros( tipo, metodo, numero):
        return f"{tipo} has no defined method {metodo} with {numero} parametros"
    @staticmethod
    def solo_lectura( variable):
        return f"{variable} is read-only"
    @staticmethod
    def no_definida( variable):
        return f'Varible "{variable}" is not defined.'
    @staticmethod
    def operacion_invalida(der,isq,op):
        return f'Operation {op} is undefined between {der} and {isq}'
    @staticmethod
    def herencia_circular( desde):
        return f"There is a circular inheritance over the class {desde}"