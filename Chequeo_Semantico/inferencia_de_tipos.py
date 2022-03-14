from .dependencias import *

class BaseDeInferencia:
    def __init__(self, contexto: Context):
        self.inferiormente_acotados_por = {}
        self.superiormente_acotados_por = {}
        self.acotados_por_el_metodo = {}
        self.retorno_del_metodo = {}
        self.hay_cambio = True
        self.contexto : Context = contexto
        self.lista_de_tipos = list(set(contexto.types.keys()) ^ set(["AUTO_TYPE","Object","Void"]))
        self.arbol_de_tipos = self.cambiar_a_no_dirigido()

        for tipo in self.lista_de_tipos + ["Object"]:
            tipo = self.contexto.get_type(tipo)
            self.contexto.current_type = tipo
            self.superiormente_acotados_por[tipo.name] = self.lista_de_superiormente_acotados_por(tipo)
            self.inferiormente_acotados_por[tipo.name] = self.lista_de_inferiormente_acotados_por(tipo)
            for metodo in tipo.methods:
                t = self.contexto.get_type(metodo.return_type.name)
                try:
                    self.acotados_por_el_metodo[(metodo.name,len(metodo.param_names))].add(tipo.name)
                except KeyError:
                    self.acotados_por_el_metodo[(metodo.name,len(metodo.param_names))] = set([tipo.name])
                if not t.is_auto_type:
                    try:
                        self.retorno_del_metodo[(metodo.name,len(metodo.param_names))].add(t.name)
                    except KeyError:
                        self.retorno_del_metodo[(metodo.name,len(metodo.param_names))] =set([t.name])
                        

        self.contexto.current_type = None

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

    def cambiar_a_no_dirigido(self):
        resultado = {}
        resultado["Object"] = []
        for nombre in self.lista_de_tipos:
            resultado[nombre] = []
        for nombre in self.lista_de_tipos:
            tipo = self.contexto.get_type(nombre)
            try:
                resultado[tipo.parent.name].append(nombre)
            except AttributeError:
                resultado["Object"].append(nombre) 
        return resultado
    
    def componente_conexa(self,lista):
        raiz = "Object"
        lista_aux : list = list(lista).copy()
        v = lista_aux[0]
        lista_aux.remove(v)
        cola = [v]
        for nodo in cola:
            try:
                padre = self.contexto.get_type(nodo).parent.name
            except AttributeError:
                padre = self.contexto.built_in_type.objeto.name    
            if padre in lista:
                l = self.arbol_de_tipos[nodo] + [padre]
            else:
                raiz = nodo
                l =  self.arbol_de_tipos[nodo]
            for u in l:
                if u in lista_aux:
                    cola.append(u)
                    lista_aux.remove(u)
    
        return raiz, lista_aux
    
    def camino_recto_mas_largo(self,raiz,lista):
        while any(self.arbol_de_tipos[raiz]):
            cont = 0
            pivot = None
            for hijo in self.arbol_de_tipos[raiz]:
                if hijo in lista:
                    cont += 1
                    pivot = hijo
            if cont == 1:
                raiz = pivot
            else:
                break
            
        return raiz
    
    def seleccion_deL_tipo_superior(self, tipos_posibles):
        if not any(tipos_posibles) or "nueva" in tipos_posibles: return None

        lista = tipos_posibles
        resultado = []
        while True:
            raiz, lista_aux = self.componente_conexa(lista)
            r = self.contexto.get_type(raiz)
            for t in lista_aux:
                t = self.contexto.get_type(t)
                if t.conforms_to(r): lista_aux.remove(t.name)
                
            lista = list( set(lista) ^ set(lista_aux) ) 
            resultado.append( self.camino_recto_mas_largo(raiz,lista))
            lista = lista_aux
            if not any(lista): break
        
        return resultado

    #implemntacion para que admita auto tipos
    def maxima_comun_cota(self, tipo1: Type,tipo2 : Type):
        if tipo2.is_auto_type and tipo1.is_auto_type:
            return Auto( list( set(tipo1.tipos_posibles) & set(tipo2.tipos_posibles)))
        if tipo2.is_auto_type or tipo1.is_auto_type:
            if tipo1.is_auto_type:
                el_tipo, el_auto = tipo2, tipo1
            else:
                el_tipo, el_auto = tipo1, tipo2
            rama = self.get_toda_la_rama_de(el_tipo)
            return Auto( self.acotacion( el_auto.tipos_posibles, rama, False ) )
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
        #print(posibles, "  ", cotas, "   ", nueva)
        
        self.hay_cambio = self.hay_cambio or (chequear_cambio and any(nueva ^ set( posibles )))
        
        return list( nueva )

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
    def auto_acotacion(self,tipo,tipo_auto):
        if not tipo_auto.is_auto_type:
            return tipo
        
        cotas = tipo_auto.tipos_posibles
        if not any(cotas) or "nueva" in cotas:
            return tipo
        
        nueva = self.acotacion(tipo.tipos_posibles, cotas)
        return Auto( nueva )

class Inferencia(BaseDeInferencia):
    def __init__(self, contexto : Context):
        BaseDeInferencia.__init__(self,contexto)
   
    def infiere_y_sigue_el_recorrido(self, tipo : Type, exp, mi_ambiente : Scope, acotacion : list = None):
            if tipo.is_auto_type:
                if "nueva" in tipo.tipos_posibles:
                    acotacion = acotacion
                else : acotacion = self.acotacion(tipo.tipos_posibles,acotacion,False)
                tipo_de_la_exp = self.visita( exp , mi_ambiente, acotacion)
                cota_superior = self.cota_superior(tipo_de_la_exp)

                return True, cota_superior, tipo_de_la_exp
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
        self.contexto.current_type = self.contexto.get_type( nodo.id )
        for m in nodo.lista_de_miembros:
            self.visita(m , mi_ambiente, None)
    
    @visitor.when(DefAtributo)
    def visita(self, nodo : DefAtributo, mi_ambiente : Scope, acotacion = None):
        if nodo.exprecion is not None: 
            var = mi_ambiente.find_variable( nodo.id )
            tipo = var.type.real_type(self.contexto.current_type)
            _bool, cotas, _ = self.infiere_y_sigue_el_recorrido( tipo, nodo.exprecion, mi_ambiente)
            if _bool :
                nueva = self.acotacion(var.type.tipos_posibles, cotas )
                var.type = Auto( nueva )
            
    @visitor.when(DefFuncion)
    def visita(self, nodo : DefFuncion, mi_ambiente : Scope, acotacion = None):
        mi_ambiente : Scope = mi_ambiente.children[nodo]
        metodo = self.contexto.current_type.get_method( nodo.id )
        
        tipo = metodo.return_type.real_type(self.contexto.current_type)
        _bool, cotas, _ = self.infiere_y_sigue_el_recorrido( tipo, nodo.cuerpo, mi_ambiente)
        if _bool:
            nueva = self.acotacion( metodo.return_type.tipos_posibles, cotas )
            metodo.return_type = Auto( nueva )
        
        for i, nombre in enumerate(metodo.param_names):
            if metodo.param_types[i].is_auto_type:
                var = mi_ambiente.find_variable(nombre)
                metodo.param_types[i] = self.auto_acotacion(metodo.param_types[i],var.type)

    @visitor.when(Invocacion)
    def visita(self, nodo : Invocacion, mi_ambiente : Scope, acotacion = None):
        if nodo.exp is not None:
            cota_por_nombre_de_f = self.acotados_por_el_metodo[(nodo.id,len(nodo.lista_de_exp))]
            tipo_de_la_exp = self.visita(nodo.exp, mi_ambiente, list(cota_por_nombre_de_f) )
        else:
            tipo_de_la_exp = self.contexto.current_type

        if tipo_de_la_exp.is_auto_type:
            clase_superior = self.seleccion_deL_tipo_superior(tipo_de_la_exp.tipos_posibles)
            if clase_superior is not None and len(clase_superior) == 1 : tipo_de_la_exp = self.contexto.get_type(clase_superior[0])
        
    
        try:
            metodo = tipo_de_la_exp.get_method( nodo.id )
        
            for i, exp in enumerate( nodo.lista_de_exp ):
                tipo = metodo.param_types[i].real_type(tipo_de_la_exp)
                _bool, cotas, _ = self.infiere_y_sigue_el_recorrido( tipo, exp, mi_ambiente )
                if _bool:
                    nueva = self.acotacion( metodo.param_types[i].tipos_posibles, cotas )
                    metodo.param_types[i] = Auto( nueva )            

            if metodo.return_type.is_auto_type:
                nueva = self.acotacion(metodo.return_type.tipos_posibles, acotacion)
                metodo.return_type = Auto( nueva )

            return metodo.return_type.real_type(tipo_de_la_exp)
        except SemanticError :
            for exp in nodo.lista_de_exp:
                self.visita(exp, mi_ambiente)
            try:
                posibles = self.retorno_del_metodo[nodo.id,len(nodo.lista_de_exp)]
                resultado = Auto( self.acotacion(list(posibles), acotacion, False))
            except KeyError:
                resultado = Auto( self.acotacion(self.lista_de_tipos, acotacion, False)) 
            return resultado
            

    @visitor.when(InvocacionEstatica)
    def visita(self, nodo : InvocacionEstatica, mi_ambiente : Scope, acotacion = None):
        tipo_especifico : Type = self.contexto.get_type( nodo.tipo_especifico )
        cota_inferior = self.cota_inferior( tipo_especifico )
        _ = self.visita( nodo.exp, mi_ambiente, cota_inferior )
        metodo = tipo_especifico.get_method( nodo.id )

        for i, exp in enumerate( nodo.lista_de_exp ):
            tipo = metodo.param_types[i].real_type(tipo_especifico)
            _bool, cotas, _ = self.infiere_y_sigue_el_recorrido( tipo, exp, mi_ambiente )
            if _bool:
                nueva = self.acotacion( metodo.param_types[i].tipos_posibles, cotas )
                metodo.param_types[i] = Auto( nueva )            
        
        if metodo.return_type.is_auto_type:
            nueva = self.acotacion(metodo.return_type.tipos_posibles, acotacion)
            metodo.return_type = Auto( nueva )

        return metodo.return_type.real_type(tipo_especifico)

    @visitor.when(Asignacion)
    def visita(self, nodo : Asignacion, mi_ambiente : Scope, acotacion = None):
        var = mi_ambiente.find_variable( nodo.id )
        tipo = var.type.real_type(self.contexto.current_type)
        _bool, cotas, tipo_de_la_exp = self.infiere_y_sigue_el_recorrido( tipo , nodo.valor, mi_ambiente, acotacion )
        if _bool:
            nueva = self.acotacion( var.type.tipos_posibles, cotas )
            var.type = Auto( nueva )            

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
                auto = self.visita( nodo.exp_si_true, mi_ambiente, acotacion_por_rama )
            elif not tipo_s.is_auto_type:
                acotacion_por_rama = self.get_toda_la_rama_de(tipo_s)
                auto = self.visita( nodo.exp_si_false, mi_ambiente, acotacion_por_rama )
            else:
                auto = Auto( set(tipo_s.tipos_posibles).union(set(tipo_n.tipos_posibles)) )
            
            return auto

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
        
        for nombre, _, exp in nodo.lista_de_acciones:
            var = mi_ambiente.find_variable( nombre )
            tipo = var.type.real_type(self.contexto.current_type)
            _bool, cotas, _ = self.infiere_y_sigue_el_recorrido( tipo, exp, mi_ambiente)
            if _bool:
                nueva = self.acotacion( var.type.tipos_posibles, cotas )
                var.type = Auto( nueva )   

        
        return self.visita(nodo.exp, mi_ambiente, acotacion)
            
    @visitor.when(Case)
    def visita(self, nodo : Case, mi_ambiente : Scope, acotacion = None):
        conjunto_de_tipos = set()
        tipo_de_retorno = None
        for _, tipo, exp in nodo.lista_de_casos:
            tipo = self.contexto.get_type(tipo).real_type(self.contexto.current_type)
            cota_inferior = self.cota_inferior(tipo)
            conjunto_de_tipos = conjunto_de_tipos.union( set(cota_inferior) )
            nuevo_tipo = self.visita(exp,mi_ambiente.children[exp],acotacion)
            if tipo_de_retorno is None:
                tipo_de_retorno = nuevo_tipo
            else:
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
        return var.type.real_type(self.contexto.current_type)



