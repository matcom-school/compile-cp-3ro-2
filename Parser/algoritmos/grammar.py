from cmp.utils import ContainerSet
from itertools import islice

def compute_local_firsts(firsts, alpha):
    first_alpha = ContainerSet()
    try:
        alpha_is_epsilon = alpha.IsEpsilon
    except:
        alpha_is_epsilon = False
    
    if(alpha_is_epsilon):
        first_alpha.set_epsilon()
        return first_alpha
    
    containsE = False
    for i in alpha:
        if not firsts[i].contains_epsilon:
            containsE = True
            for j in firsts[i]:
                first_alpha.add(j)
            break
        else:
            for j in firsts[i]:
                first_alpha.add(j)

    if not containsE:
        first_alpha.set_epsilon()
    return first_alpha

def compute_firsts(G):
    firsts = {}
    change = True
    for terminal in G.terminals:
        firsts[terminal] = ContainerSet(terminal)
    for nonterminal in G.nonTerminals:
        firsts[nonterminal] = ContainerSet()
    while change:
        change = False
        for production in G.Productions:
            X = production.Left
            alpha = production.Right

            first_X = firsts[X]
            try:
                first_alpha = firsts[alpha]
            except:
                first_alpha = firsts[alpha] = ContainerSet()
            
            local_first = compute_local_firsts(firsts, alpha)
            
            change |= first_alpha.hard_update(local_first)
            change |= first_X.hard_update(local_first)
    return firsts

def compute_follows(G, firsts):
    follows = { }
    change = True
    
    local_firsts = {}
    for nonterminal in G.nonTerminals:
        follows[nonterminal] = ContainerSet()
    follows[G.startSymbol] = ContainerSet(G.EOF)
    
    while change:
        change = False
        for production in G.Productions:
            X = production.Left
            alpha = production.Right
            
            follow_X = follows[X]
            for i,symbol in enumerate(alpha):
                if symbol.IsNonTerminal:
                    follow_Y = follows[symbol]
                    
                    try:
                        first_beta = local_firsts[alpha, i]
                    except KeyError:
                        first_beta = local_firsts[alpha, i] = compute_local_firsts(firsts,islice(alpha, i+1, None))
                    
                    change |= follow_Y.update(first_beta)
                    
                    if(first_beta.contains_epsilon):
                        change |= follow_Y.update(follow_X)
        if alpha.IsEpsilon or alpha[-1].IsNonTerminal:
                change != follow_Y.update(follow_X)
    return follows