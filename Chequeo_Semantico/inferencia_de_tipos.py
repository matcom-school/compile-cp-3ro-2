from .dependencias import *

class BaseDeInferencia:
    def __init__(self, contexto: Context):
        self.inferiormente_acotados_por = {}
        self.superiormente_acotados_por = {}
        self.acotados_por_el_metodo = {}
        self.hay_cambio = True
        self.contexto : Context = contexto
        self.lista_de_tipos = list(set(contexto.types.keys()) ^ set(["AUTO_TYPE","SELF_TYPE","Object","Void"]))
        
        for tipo in self.lista_de_tipos + ["Object"]:
            tipo = self.contexto.get_type(tipo)
            self.superiormente_acotados_por[tipo.name] = self.lista_de_superiormente_acotados_por(tipo)
            self.inferiormente_acotados_por[tipo.name] = self.lista_de_inferiormente_acotados_por(tipo)
            for metodo in tipo.methods:
                try:
                    self.acotados_por_el_metodo[(metodo.name,len(metodo.param_names))].add(tipo.name)
                except KeyError:
                    self.acotados_por_el_metodo[(metodo.name,len(metodo.param_names))] = set([tipo.name])

    def lista_de_inferiormente_acotados_por(self,tipo : Type):
        resultado = []
        for t in self.lista_de_tipos:
            if self.contexto.get_type(t).conforms_to(tipo):
                resultado.append(t)

        return resultado

    def lista_de_superiormente_acotados_por(self,tipo : Type):
        resultado = []
        while tipo is not None:
            resultado.append(tipo.name)
            tipo = tipo.parent
        
        return resultado + ["Object"]
    
    def seleccion_deL_tipo_superior(self, tipos_posibles):
        resultado = None
        lista_auxiliar = []
        for tipo in tipos_posibles:
            if tipo in lista_auxiliar or tipo == "nueva": continue
            tipo = self.contexto.get_type(tipo)

            if resultado is not None and not tipo.conforms_to(resultado): return None
            else:
                lista_auxiliar = self.superiormente_acotados_por[ tipo.name ]
                resultado = tipo

        return resultado.name if resultado is not None else None


    #implemntacion para que admita auto tipos
    def maxima_comun_cota(self, tipo1: Type,tipo2 : Type):
        if tipo2.is_auto_type and tipo1.is_auto_type:
            return Auto( list( set(tipo1.tipos_posibles) & set(tipo2.tipos_posibles)))
        if tipo2.is_auto_type or tipo1.is_auto_type:
            if tipo1.is_auto_type:
                el_tipo, el_auto = tipo2, tipo1
            else:
                el_tipo, el_auto = tipo1, tipo2
                return Auto( self.acotacion( el_auto.tipos_posibles, (el_tipo,el_tipo,True)))
        while True:
            if tipo1 is None or tipo2 is None : return self.contexto.get_type("Object")
            if tipo1.conforms_to(tipo2) : return tipo2
            if tipo2.conforms_to(tipo1) : return tipo1
            
            tipo1 = tipo1.parent
            tipo2 = tipo2.parent
        
        
    def acotacion(self, posibles, cotas, chequear_cambio = True):
        if cotas is None:
            return posibles
        if "nueva" in posibles:
            self.hay_cambio = True
            return cotas

        nueva = set( posibles ) & set(cotas) 
        self.hay_cambio = self.hay_cambio and chequear_cambio and any(nueva ^ set( posibles ))
        
        return nueva

    def cota_es_auto(self,tipo : Type):
        if tipo.is_auto_type:
            if "nueva" in tipo.tipos_posibles:
                return True,None
            return True,tipo.tipos_posibles
        
        return False,None

    def get_toda_la_rama_de(self, tipo : Type):
        if tipo is None: return None
        _bool, lista = self.cota_es_auto(tipo)
        if _bool: return lista

        cota_inferior = self.inferiormente_acotados_por[ tipo.name ]
        cota_superior = self.superiormente_acotados_por[ tipo.name ]
        rama = set(cota_superior).union(set(cota_inferior))
        return list(rama)

    def cota_superior(self, tipo: Type):
        if tipo is None: return None
        _bool, lista = self.cota_es_auto(tipo)
        if _bool: return lista
        
        return self.superiormente_acotados_por[tipo.name]

    def cota_inferior(self, tipo: Type):
        if tipo is None: return None
        _bool, lista = self.cota_es_auto(tipo)
        if _bool: return lista
        
        return self.inferiormente_acotados_por[tipo.name]
  

class Inferencia(BaseDeInferencia):
    def __init__(self, contexto : Context):
        BaseDeInferencia.__init__(self,contexto)
   
    def infiere_y_sigue_el_recorrido(self, tipo : Type, exp, mi_ambiente : Scope, acotacion : list = None):
            if tipo.is_auto_type:
                tipo_de_la_exp = self.visita( exp , mi_ambiente, acotacion)
                cota_superior = self.cota_superior(tipo_de_la_exp)
                nueva = self.acotacion(tipo.tipos_posibles, cota_superior)
                return True, Auto( nueva ), tipo_de_la_exp
            else: 
                cota_inferior = self.cota_inferior(tipo)
                cota_inferior = self.acotacion(cota_inferior, acotacion, False)
                tipo = self.visita( exp, mi_ambiente, cota_inferior )
                return False, None, tipo

    @visitor.on("nodo")
    def visita(self, nodo, mi_ambiente, acotacion = None):
        pass
    
    @visitor.when(Programa)
    def visita(self, nodo : Programa, mi_ambiente : Scope, acotacion = None):
        
        while self.hay_cambio:
            self.hay_cambio = False
            for cl in nodo.lista_de_clases:
                self.visita(cl, mi_ambiente, None)
        
        return mi_ambiente
    
    @visitor.when(ClaseDeCool)
    def visita(self, nodo : ClaseDeCool, mi_ambiente : Scope, acotacion = None):
        mi_ambiente = mi_ambiente.children[nodo]
        self.clase_actual = self.contexto.get_type( nodo.id )
        for m in nodo.lista_de_miembros:
            self.visita(m , mi_ambiente, None)
    
    @visitor.when(DefAtributo)
    def visita(self, nodo : DefAtributo, mi_ambiente : Scope, acotacion = None):
        if nodo.exprecion is not None: 
            var = mi_ambiente.find_variable( nodo.id )
            _bool, tipo, _ = self.infiere_y_sigue_el_recorrido( var.type, nodo.exprecion, mi_ambiente)
            if _bool :
                var.type = tipo
            
    @visitor.when(DefFuncion)
    def visita(self, nodo : DefFuncion, mi_ambiente : Scope, acotacion = None):
        mi_ambiente = mi_ambiente.children[nodo]
        metodo = self.contexto.current_type.get_method( nodo.id )
        
        _bool, tipo, _ = self.infiere_y_sigue_el_recorrido( metodo.return_type, nodo.cuerpo, mi_ambiente)
        if _bool:
            metodo.return_type = tipo
               

    @visitor.when(Invocacion)
    def visita(self, nodo : Invocacion, mi_ambiente : Scope, acotacion = None):
        if nodo.exp is not None:
            cota_por_nombre_de_f = self.acotados_por_el_metodo[(nodo.id,len(nodo.lista_de_exp))]
            tipo_de_la_exp = self.visita(nodo.exp, mi_ambiente, list(cota_por_nombre_de_f) )
        else:
            tipo_de_la_exp = self.contexto.current_type

        if tipo_de_la_exp.is_auto_type:
            clase_superior = self.seleccion_deL_tipo_superior(tipo_de_la_exp.tipos_posibles)
            if clase_superior is not None: tipo_de_la_exp = self.contexto.get_type(clase_superior)
        
    
        try:
            metodo = tipo_de_la_exp.get_method( nodo.id )
        
            for i, exp in enumerate( nodo.lista_de_exp ):
                _bool, tipo, _ = self.infiere_y_sigue_el_recorrido( metodo.param_types[i], exp, mi_ambiente )
                if _bool:
                    metodo.param_types[i] = tipo
            

            if metodo.return_type.is_auto_type:
                nueva = self.acotacion(metodo.return_type.tipos_posibles, acotacion)
                metodo.return_type = Auto( nueva )

            return metodo.return_type
        except SemanticError :
            for exp in nodo.lista_de_exp:
                self.visita(exp, mi_ambiente)

            resultado = Auto( self.acotacion(self.lista_de_tipos, acotacion, False)) 
            return resultado
            

    @visitor.when(InvocacionEstatica)
    def visita(self, nodo : InvocacionEstatica, mi_ambiente : Scope, acotacion = None):
        tipo_especifico : Type = self.contexto.get_type( nodo.tipo_especifico )
        cota_inferior = self.cota_inferior( tipo_especifico )
        _ = self.visita( nodo.exp, mi_ambiente, cota_inferior )
        metodo = tipo_especifico.get_method( nodo.id )

        for i, exp in enumerate( nodo.lista_de_exp ):
            _bool, tipo, _ = self.infiere_y_sigue_el_recorrido( metodo.param_types[i], exp, mi_ambiente )
            if _bool:
                metodo.param_types[i] = tipo
        
        if metodo.return_type.is_auto_type:
            nueva = self.acotacion(metodo.return_type.tipos_posibles, acotacion)
            metodo.return_type = Auto( nueva )

        return metodo.return_type

    @visitor.when(Asignacion)
    def visita(self, nodo : Asignacion, mi_ambiente : Scope, acotacion = None):
        var = mi_ambiente.find_variable( nodo.id )
        _bool, tipo, tipo_de_la_exp = self.infiere_y_sigue_el_recorrido( var.type, nodo.valor, mi_ambiente, acotacion )
        if _bool:
            var.type = tipo

        return tipo_de_la_exp

    @visitor.when( IfThenElse )
    def visita(self, nodo : IfThenElse, mi_ambiente : Scope, acotacion = None):
        cota_inferior = self.cota_inferior(self.contexto.built_in_type.bool)
        self.visita (nodo.condicion, mi_ambiente, cota_inferior )

        tipo_s = self.visita( nodo.exp_si_true, mi_ambiente, acotacion)
        tipo_n = self.visita( nodo.exp_si_false, mi_ambiente, acotacion)

        if tipo_s.is_auto_type or tipo_n.is_auto_type:
            if not tipo_n.is_auto_type:
                acotacion_por_rama = self.get_toda_la_rama_de(tipo_n)
                return self.visita( nodo.exp_si_true, mi_ambiente, acotacion_por_rama )
            elif not tipo_s.is_auto_type:
                acotacion_por_rama = self.get_toda_la_rama_de(tipo_s)
                return self.visita( nodo.exp_si_false, mi_ambiente, acotacion_por_rama )
            else:
                return Auto( set(tipo_s.tipos_posibles).union(set(tipo_n.tipos_posibles)) )
        
        return self.maxima_comun_cota(tipo_s,tipo_n)

    @visitor.when(WhileLoop)
    def visita(self, nodo : WhileLoop, mi_ambiente : Scope, acotacion = None):
        cota_inferior = self.cota_inferior(self.contexto.built_in_type.bool)
        _ = self.visita (nodo.condicion, mi_ambiente, cota_inferior )
        _ = self.visita (nodo.exp, mi_ambiente)

        return self.contexto.built_in_type.objeto

    @visitor.when(Block)
    def visita(self, nodo : Invocacion, mi_ambiente : Scope, acotacion = None):
        for exp in nodo.lista_de_exp[:-1]:
            _ = self.visita(exp,mi_ambiente) 
        return self.visita( nodo.lista_de_exp[-1], mi_ambiente, acotacion)
    
    @visitor.when(LetIn)
    def visita(self, nodo : LetIn, mi_ambiente : Scope, acotacion = None):
        mi_ambiente : Scope = mi_ambiente.children[nodo]
        
        for nombre, tipo, exp in nodo.lista_de_acciones:
            var = mi_ambiente.find_variable( nombre )
            _bool, tipo, _ = self.infiere_y_sigue_el_recorrido( var.type, exp, mi_ambiente)
            if _bool:
                var.type = tipo
        
        return self.visita(nodo.exp, mi_ambiente, acotacion)
            
    @visitor.when(Case)
    def visita(self, nodo : Case, mi_ambiente : Scope, acotacion = None):
        conjunto_de_tipos = set()
        tipo_de_retorno = None
        for _, tipo, exp in nodo.lista_de_casos:
            cota_inferior = self.cota_inferior(tipo)
            conjunto_de_tipos.union( set(cota_inferior) )
            nuevo_tipo = self.visita(exp,mi_ambiente.children[exp],acotacion)
            tipo_de_retorno = self.maxima_comun_cota(tipo_de_retorno,nuevo_tipo)

        self.visita( nodo.exp, mi_ambiente, list(conjunto_de_tipos) )

        return tipo_de_retorno
    
    @visitor.when(NuevoTipo)
    def visita(self, nodo : NuevoTipo, mi_ambiente : Scope, acotacion = None):
        return self.contexto.get_type(nodo.tipo)

    @visitor.when(Negacion)
    def visita(self, nodo : Negacion, mi_ambiente : Scope, acotacion = None):
        cota_inferior = self.cota_inferior(self.contexto.built_in_type.bool)
        _ = self.visita(nodo.exp, mi_ambiente, cota_inferior )

        return self.contexto.built_in_type.bool

    @visitor.when(Complemento)
    def visita(self, nodo : Complemento, mi_ambiente : Scope, acotacion = None):
        cota_inferior = self.cota_inferior(self.contexto.built_in_type.int)
        _ = self.visita(nodo.exp, mi_ambiente, cota_inferior )

        return self.contexto.built_in_type.int

    @visitor.when(FuncionIsVoid)
    def visita(self, nodo : FuncionIsVoid, mi_ambiente : Scope, acotacion = None):
        _ = self.visita(nodo.exp, mi_ambiente)
        return self.contexto.built_in_type.bool

    @visitor.when(ExprEntreParantesis)
    def visita(self, nodo : ExprEntreParantesis, mi_ambiente : Scope, acotacion = None):
        return self.visita(nodo.exp, mi_ambiente, acotacion)


    @visitor.when(Aritmetica)
    def visita(self, nodo : Aritmetica, mi_ambiente : Scope, acotacion = None):
        cota_inferior = self.cota_inferior(self.contexto.built_in_type.int)
        _ = self.visita(nodo.der, mi_ambiente, cota_inferior )
        _ = self.visita(nodo.isq, mi_ambiente, cota_inferior )

        return self.contexto.built_in_type.int

    @visitor.when(Comparacion)
    def visita(self, nodo : Comparacion, mi_ambiente : Scope, acotacion = None):
        cota_inferior = self.cota_inferior(self.contexto.built_in_type.int)
        _ = self.visita(nodo.der, mi_ambiente, cota_inferior )
        _ = self.visita(nodo.isq, mi_ambiente, cota_inferior )

        return self.contexto.built_in_type.bool
    
    @visitor.when(Igual)
    def visita(self, nodo : Igual, mi_ambiente : Scope, acotacion = None):
        tipo_der = self.visita(nodo.der, mi_ambiente)
        tipo_isq = self.visita(nodo.isq, mi_ambiente)
        if tipo_isq.is_auto_type and tipo_der.is_auto_type: return self.contexto.built_in_type.bool
        if not tipo_isq.is_auto_type and not tipo_der.is_auto_type: return self.contexto.built_in_type.bool
        
        if tipo_der.is_auto_type:
            el_tipo = tipo_isq
        else:
            el_tipo = tipo_der

        tipos_basicos = [self.contexto.built_in_type.bool, self.contexto.built_in_type.int, self.contexto.built_in_type.string]
        for t in tipos_basicos:
            if el_tipo.conforms_to(t):
                cota_inferior = self.cota_inferior( el_tipo )     
                if tipo_der.is_auto_type:
                    tipo_der = self.visita(nodo.der, mi_ambiente, cota_inferior)
                else:
                    tipo_isq = self.visita(nodo.isq, mi_ambiente, cota_inferior)
                break
        return self.contexto.built_in_type.bool
    
    @visitor.when(String)
    def visita(self, nodo, mi_ambiente, acotacion = None):
        return self.contexto.built_in_type.string

    @visitor.when(Bool)
    def visita(self, nodo, mi_ambiente, acotacion = None):
        return self.contexto.built_in_type.bool

    @visitor.when(Int)
    def visita(self, nodo, mi_ambiente, acotacion = None):
        return self.contexto.built_in_type.int


    @visitor.when(Identificador)
    def visita(self, nodo, mi_ambiente, acotacion = None):
        var = mi_ambiente.find_variable(nodo.id)
        if var.type.is_auto_type:
            nueva = self.acotacion( var.type.tipos_posibles, acotacion)
            var.type = Auto( nueva )
        return var.type



