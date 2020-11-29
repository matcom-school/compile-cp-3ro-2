import re
from cmp.utils import Token, UnknownToken
from Lenguaje.lenguaje import *

def lexer(programa:str):
    programa = remove_comentarios(programa)
    programa = from_strsym_to_code(programa)

    keywords = r"\bclase_t\b|\bdecla\b|\bin\b|\bnew\b|\bif\b|\bthen\b|\belse\b|\bfi\b|\bcase\b|\bof\b|\besac\b|\bwhile\b|\bloop\b|\bpool\b|\binherits\b|isVoid\b|not\b|true\b|false\b|"
    nums = r"\d+\.\d+|\d+|"
    string=r"\".*?\"|"
    idex = r"[a-zA-Z]\w*|"
    symbols = r",|;|:|\{|\}|\(|\)|<-|=>|\.|=|\+|-|\*|/|<|>|@|�"
    #special = r"|\n"
    regex = re.compile(keywords + nums + string + idex + symbols,re.DOTALL)
    text = regex.findall(programa)
    return tokenizer(text)

def tokenizer(text):
    fixed_tokens = { t.Name: Token(t.Name, t) for t in G.terminals if t not in { id_t, num, string }}
    tokens = []
    for lex in text:
        try:
            token = fixed_tokens[lex]
        except KeyError:
            token = UnknownToken(lex)
            try:
                token = analize_token(token)
            except TypeError:
                pass
        tokens.append(token)

    tokens.append(Token('$', G.EOF))
    return tokens

def analize_token(token):
    lex = token.lex
    if token.lex[0] == token.lex[-1] == "\"":
        token.lex = from_code_to_strsym(lex)
        return token.transform_to(string)
    try:
        float(lex)
        return token.transform_to(num)
    except ValueError:
        return token.transform_to(id_t)

def remove_comentarios(text):
    inside_str = False
    mod = ""
    i = 0
    while i < len(text):
        char = text[i]
        if char == "\\":
            mod += char
            escaping = True
            j = i + 1
            while text[j] == "\\":
                mod += text[j]
                escaping = not escaping
                j += 1
            mod += text[j]
            i = j
            if not escaping and text[i] == "\"":
                inside_str = False
        elif char == "\"":
            mod += char
            inside_str = not inside_str
        elif not inside_str and i + 1 < len(text) and (char == "(" and text[i + 1] == "*"):
            j = i + 2
            balance = 1
            while j + 1 < len(text) and balance!=0:
                if text[j] == "(" and text[j + 1] == "*":
                    balance += 1
                if text[j] == "*" and text[j + 1] == ")":
                    balance -= 1
                j += 1
            i = j
        elif not inside_str and i + 1 < len(text) and char == text[i + 1] == "-":
            j = i + 2
            while j < len(text) and text[j] != "\n":
                j += 1
            i = j
        else:
            mod += char  
        i += 1
    return mod

def from_strsym_to_code(programa):
    programa = re.compile(r"\\\\").sub("�bb�", programa)
    programa = re.compile(r"\\\"").sub("�bc�", programa)
    return programa

def from_code_to_strsym(programa):
    programa = re.compile("�bb�").sub(r"\\\\", programa)
    programa = re.compile("�bc�").sub(r"\"", programa)
    return programa

def pprint_tokens(tokens):
    indent = 0
    pending = []
    for token in tokens:
        pending.append(token)
        if token.token_type in { ocur, ccur, semi, of, in_t, esac, loop, decla }:
            if token.token_type in {ccur, esac, pool, in_t}:
                indent -= 1
            print('    '*indent + ' '.join(str(t.token_type) for t in pending))
            pending.clear()
            if token.token_type in {of, ocur, loop, decla}:
                indent += 1
    print(' '.join([str(t.token_type) for t in pending]))

def reform_text(tokens):
    indent = 0
    text = []
    line = ""
    i = 0
    while i < len(tokens):
        token = tokens[i]
        line += token.lex + " "
        if token.lex in {"{", ";", "}"}:
            text.append(line)
            if token.lex in {"{"}:
                indent += 1
            if token.lex in {"}"}:
                indent -= 1
            line = "     "*indent