from Lexer import lexer
from Parser import Parsear
from Chequeo_Semantico import Chequeo_Semantico
from Chequeo_Semantico.Print import ASTtoString

print("aaaaaaaaaaaaaaa")

test = """
class A
{
    b : A;
    c : AUTO_TYPE;
    a : AUTO_TYPE <- c=b;
};
"""

print("################### Lexer ###########################")
tokens = lexer(test)
print("################### Parser ###########################")
ast, errores, _bool = Parsear(tokens)

print(errores)
print("################### CH ###########################")
a, errores, _bool = Chequeo_Semantico(ast)

print(ASTtoString(a))
print(errores)