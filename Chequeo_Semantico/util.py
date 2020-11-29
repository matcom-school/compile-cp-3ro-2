from .dependencias import Context, Type



def ASC(tipo1 : Type,tipo2 : Type):
    while True:
        if tipo1 is None or tipo2 is None:
            return "Object"
        if tipo1.conforms_to(tipo2):
            return tipo1
        if tipo2.conforms_to(tipo1):
            return tipo2
        
        tipo1 = tipo1.parent
        tipo2 = tipo2.parent

def seleccionador_de_tipo(lista, contexto : Context):
    if "nueva" in lista or not any(lista) : return None
    lista_aux = lista.copy()
    error = set()

    while len(lista_aux) > 1:
        tipo1, tipo2 = lista_aux[:2]
        tipo1 = contexto.get_type(tipo1)
        tipo2 = contexto.get_type(tipo2)
        asc = ASC(tipo1,tipo2).name
        if asc in lista:
            error.add(asc)
        else:
            lista_aux = [asc] + lista_aux[2:]



