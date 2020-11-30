class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'
    
    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()
    
    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w):
        stack = [ 0 ]
        cursor = 0
        output = []
        operations = []
        
        while True:
            state = stack[-1]
            lookahead = w[cursor].token_type
            try:
                action, tag = self.action[state, lookahead]
                if action == self.SHIFT:
                    operations.append(self.SHIFT)
                    stack.append(tag)
                    cursor += 1
                elif action == self.REDUCE:
                    operations.append(self.REDUCE)
                    l = len(tag.Right)
                    while l > 0:
                        stack.pop()
                        l -= 1
                    output.append(tag)
                    last = stack[-1]
                    stack.append(self.goto[last, tag.Left])
                elif action == self.OK:
                    return output, operations, True
                else:
                    return "ERROR! Conflicto en la Tabla Accion", operations, False
            except KeyError:
                return f"Error el texto no es reconocido por el lenguaje generado por la gramatica \n ", operations, False

    @staticmethod
    def _register(table, key, value, conflict_type: dict):
        if key in table and table[key] != value:
            if table[key][0] == 'SHIFT' and value[0] == 'REDUCE' or table[key][0] == 'REDUCE' and value[0] == 'SHIFT':
                conflict_type[key] = "SHIFT-REDUCE"

            elif table[key][0] == value[0] == 'REDUCE':
                conflict_type[key] = "REDUCE-REDUCE"

            else: conflict_type[key] = "Fuiste Engañado"
        else: 
            table[key] = value

def conflict_chain(p):
    q = [(0, [0], "")]
    visited = set()
    while len(q) > 0: 
        state, s_state, chain = q.pop()
        for t in p.G.terminals + [p.G.EOF]:
            s_copy = s_state.copy()
            chain += str(t)
            if (state, t) in p.conflictType:
                print("Conflictt")
                return chain, p.conflictType[state, t]
            try:
                action, tag = p.action[state, t]
            except KeyError: continue

            new_state = None
            if action == p.SHIFT:
                new_state = tag
            elif action == p.REDUCE:
                l = len(tag.Right)
                while l > 0:
                    s_copy.pop()
                    l -= 1
                last = s_copy[-1]
                new_state = p.goto[last, tag.Left]
            elif action == p.OK: continue
            else: return "", ""
            if new_state not in visited:
                s_copy.append(new_state)
                q.append((new_state, s_copy, chain))
                visited.add(new_state)
    return "", ""


