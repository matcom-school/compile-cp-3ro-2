from Lexer import lexer
from Parser import Parsear
from Chequeo_Semantico import Chequeo_Semantico
from Chequeo_Semantico.Print import ASTtoString

print("aaaaaaaaaaaaaaa")

test = """
class Main inherits IO {
    main(a : AUTO_TYPE, b : AUTO_TYPE) : AUTO_TYPE {
		{
			if b then not b else a fi;
			case 3 + 5 of
				n : Bool => a.me();
				n : Int => 0;
				n : String => "Yay!";
			esac;
			a.you();
			a.she();
		}
	}; 
};

class A { 
	me():SELF_TYPE
		{
			self
		};
	you():SELF_TYPE
		{
			self
		};
	he():SELF_TYPE
		{
			self
		};
};

class B inherits A { };

class C inherits B { };

class D inherits C { };

class E inherits D { };


class F inherits C { };

class G inherits F { };

class H inherits G { };


class I{ 
	me():SELF_TYPE
		{
			self
		};
	you():SELF_TYPE
		{
			self
		};
	she():SELF_TYPE
		{
			self
		};
};

class J inherits I { };

class K inherits J { };


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