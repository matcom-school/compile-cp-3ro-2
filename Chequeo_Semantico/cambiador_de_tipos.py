from .dependencias import *
from .inferencia_de_tipos import BaseDeInferencia

caracter = chr(185)
caracterWarning = chr(186)

class CambiadorDeTipos(BaseDeInferencia):
    def __init__(self, contexto : Context, errores : list):
        BaseDeInferencia.__init__(self,contexto)
        self.errores = errores
        
    def nombre_de(self, tipo : Type, nombre):
        if tipo.is_auto_type:
            tipos = self.seleccion_deL_tipo_superior(tipo.tipos_posibles)
            if tipos is None:
                self.errores.append(f"InferenceWarning: {nombre} The set of inferred types is empty")
                return caracterWarning + self.contexto.built_in_type.objeto.name
            if len(tipos) > 1:
                texto = ""
                for t in tipos:
                    texto += t + ", "
                self.errores.append(f"InferenceWarning: {nombre} Could not infer between {texto[:-2]}")
                return caracterWarning + tipos[0]
            
            return caracter + tipos[0]
        else:
            return tipo.name

    @visitor.on("nodo")
    def visita(self, nodo, mi_ambiente):
        pass
    
    @visitor.when(Programa)
    def visita(self, nodo : Programa, mi_ambiente : Scope):
        lista_de_clase = []
        for cl in nodo.lista_de_clases:
            clase = self.visita(cl, mi_ambiente)
            lista_de_clase.append(clase)
        

        return Programa(lista_de_clase)
    
    @visitor.when(ClaseDeCool)
    def visita(self, nodo : ClaseDeCool, mi_ambiente : Scope):
        mi_ambiente = mi_ambiente.children[nodo]
        self.contexto.current_type = self.contexto.get_type( nodo.id )
        lista_de_miembros = []
        
        for m in nodo.lista_de_miembros:
            m = self.visita(m , mi_ambiente)
            lista_de_miembros.append(m)

        return ClaseDeCool(lista_de_miembros, self.contexto.current_type.name, nodo.clase_base)
    
    @visitor.when(DefAtributo)
    def visita(self, nodo : DefAtributo, mi_ambiente : Scope):
        var = mi_ambiente.find_variable( nodo.id )

        tipo = self.nombre_de( var.type, f"Attribute {nodo.id}" )
        if nodo.exprecion is not None:
            exp = self.visita(nodo.exprecion, mi_ambiente)
        else:
            exp = None

        return DefAtributo(nodo.id, tipo, exp)
    
    @visitor.when(DefFuncion)
    def visita(self, nodo : DefFuncion, mi_ambiente : Scope):
        mi_ambiente = mi_ambiente.children[nodo]
        metodo = self.contexto.current_type.get_method( nodo.id )

        tipo_de_retorno = self.nombre_de( metodo.return_type, f"Return to {nodo.id}" )

        lista_de_parametros = []
        for i, param_tipo in enumerate( metodo.param_types ):
            tipo = self.nombre_de( param_tipo, f"Parameter {metodo.param_names[i]} in {nodo.id}"  )
            lista_de_parametros.append(( metodo.param_names[i], tipo ))

        cuerpo = self.visita(nodo.cuerpo, mi_ambiente)
        return DefFuncion( nodo.id, lista_de_parametros, cuerpo, tipo_de_retorno)
    
    @visitor.when(Asignacion)
    def visita(self, nodo : Asignacion, mi_ambiente : Scope):
        return Asignacion(nodo.id, self.visita(nodo.valor,mi_ambiente))


    @visitor.when(Invocacion)
    def visita(self, nodo : Invocacion, mi_ambiente : Scope):
        if nodo.exp is not None:
            exp = self.visita(nodo.exp, mi_ambiente)
        else:
            exp = None

        lista_de_exp = []
        for param in nodo.lista_de_exp: 
            lista_de_exp.append(self.visita(param,mi_ambiente))
        
        return Invocacion(exp,nodo.id,lista_de_exp)
    
    @visitor.when(InvocacionEstatica)
    def visita(self, nodo : InvocacionEstatica, mi_ambiente : Scope):
        exp = self.visita(nodo.exp, mi_ambiente)

        lista_de_exp = []
        for param in nodo.lista_de_exp: 
            lista_de_exp.append(self.visita(param,mi_ambiente))
        
        return InvocacionEstatica(exp, nodo.tipo_especifico , nodo.id , lista_de_exp)
    
    @visitor.when(IfThenElse)
    def visita(self, nodo : IfThenElse, mi_ambiente : Scope):
        condicion = self.visita( nodo.condicion, mi_ambiente )
        nodo_t = self.visita ( nodo.exp_si_true, mi_ambiente )
        nodo_f = self.visita ( nodo.exp_si_false, mi_ambiente )

        return IfThenElse( condicion, nodo_t, nodo_f )
    
    @visitor.when(WhileLoop)
    def visita(self, nodo : WhileLoop, mi_ambiente : Scope):
        condicion = self.visita( nodo.condicion, mi_ambiente )
        exp = self.visita ( nodo.exp, mi_ambiente )

        return WhileLoop( condicion, exp )

    @visitor.when(Block)
    def visita(self, nodo : Block, mi_ambiente : Scope):
        lista = []
        for exp in nodo.lista_de_exp:
            lista.append( self.visita(exp,mi_ambiente) ) 
        
        return Block( lista )

    @visitor.when( LetIn )
    def visita(self, nodo : LetIn , mi_ambiente : Scope):
        mi_ambiente : Scope = mi_ambiente.children[nodo]
        lista = []
        for nombre, tipo, exp in nodo.lista_de_acciones:
            var = mi_ambiente.find_variable( nombre )
            t = self.nombre_de(var.type, f"Let declaration {nombre} variable")
            if exp is not None: e = self.visita(exp,mi_ambiente)
            else: e = None
            lista.append( ( nombre, t, e ) )

        exp = self.visita( nodo.exp, mi_ambiente )
        return LetIn( lista, exp )

    @visitor.when(Case)
    def visita(self, nodo : Case, mi_ambiente : Scope):
        exp0 = self.visita(nodo.exp, mi_ambiente)
        
        lista = []
        for nombre, tipo, exp in nodo.lista_de_casos:
            expk = self.visita( exp, mi_ambiente.children[exp])
            lista.append( (nombre, tipo, exp) )

        return Case( exp0, lista )

    @visitor.when( NuevoTipo )
    def visita(self, nodo : NuevoTipo, mi_ambiente : Scope):
        return NuevoTipo(nodo.tipo)

    @visitor.when(Negacion)
    def visita(self, nodo : Negacion, mi_ambiente : Scope):
        exp = self.visita( nodo.exp, mi_ambiente )
        return Negacion(exp)
    
    @visitor.when(Complemento)
    def visita(self, nodo : Complemento, mi_ambiente : Scope):
        exp = self.visita( nodo.exp, mi_ambiente )
        return Complemento(exp)
    
    @visitor.when(FuncionIsVoid)
    def visita(self, nodo : FuncionIsVoid, mi_ambiente : Scope):
        exp = self.visita( nodo.exp, mi_ambiente )
        return FuncionIsVoid(exp)
    
    @visitor.when(Negacion)
    def visita(self, nodo : Negacion, mi_ambiente : Scope):
        exp = self.visita( nodo.exp, mi_ambiente )
        return Negacion(exp)
        
    @visitor.when(ExprEntreParantesis)
    def visita(self, nodo : ExprEntreParantesis, mi_ambiente : Scope):
        exp = self.visita( nodo.exp, mi_ambiente )
        return ExprEntreParantesis(exp)
        
    @visitor.when(Suma)
    def visita(self, nodo : Suma, mi_ambiente : Scope):
        der = self.visita( nodo.der, mi_ambiente )
        izq = self.visita( nodo.isq, mi_ambiente )

        return Suma( izq, der )
    
    @visitor.when(Resta)
    def visita(self, nodo : Resta, mi_ambiente : Scope):
        der = self.visita( nodo.der, mi_ambiente )
        izq = self.visita( nodo.isq, mi_ambiente )

        return Resta( izq, der )
    
    @visitor.when(Multiplicacion)
    def visita(self, nodo : Multiplicacion, mi_ambiente : Scope):
        der = self.visita( nodo.der, mi_ambiente )
        izq = self.visita( nodo.isq, mi_ambiente )

        return Multiplicacion( izq, der )
    
    @visitor.when(Division)
    def visita(self, nodo : Division, mi_ambiente : Scope):
        der = self.visita( nodo.der, mi_ambiente )
        izq = self.visita( nodo.isq, mi_ambiente )

        return Division( izq, der )
    
    @visitor.when(Menor)
    def visita(self, nodo : Menor, mi_ambiente : Scope):
        der = self.visita( nodo.der, mi_ambiente )
        izq = self.visita( nodo.isq, mi_ambiente )

        return Menor( izq, der )
    
    @visitor.when(MenorOIqual)
    def visita(self, nodo : MenorOIqual, mi_ambiente : Scope):
        der = self.visita( nodo.der, mi_ambiente )
        izq = self.visita( nodo.isq, mi_ambiente )

        return MenorOIqual( izq, der )
    
    @visitor.when(Igual)
    def visita(self, nodo : Igual, mi_ambiente : Scope):
        der = self.visita( nodo.der, mi_ambiente )
        izq = self.visita( nodo.isq, mi_ambiente )

        return Igual( izq, der )
    
    @visitor.when(Int)
    def visita(self, nodo : Int, mi_ambiente : Scope):
        return Int(nodo.lex)

    @visitor.when(String)
    def visita(self, nodo : String, mi_ambiente : Scope):
        return String(nodo.lex)

    @visitor.when(Bool)
    def visita(self, nodo : Bool, mi_ambiente : Scope):
        return Bool(nodo.lex)

    @visitor.when(Identificador)
    def visita(self, nodo : Identificador, mi_ambiente : Scope):
        return Identificador(nodo.id)
