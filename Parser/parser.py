from cmp.evaluation import evaluate_reverse_parse
from cmp.tools.parsing import LR1Parser
from Lenguaje import G

parser = LR1Parser(G)

def Parsear(tokens):
    parse, operations, result = parser(tokens)
    if not result:
        return
    return evaluate_reverse_parse(parse, operations, tokens)


