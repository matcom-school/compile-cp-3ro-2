from .evaluacion import evaluate_reverse_parse
from .LR1_Parser import LR1Parser
from Lenguaje import G
 
parser = LR1Parser(G)

def Parsear(tokens):
    parse, operaciones, resultado = parser(tokens)
    if not resultado:
        return None,parse,False
    return evaluate_reverse_parse(parse, operaciones, tokens),"",True


