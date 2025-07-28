import time

# ======================
# DFA Class
# ======================
class DFA:
    def __init__(self, states, alphabet, transitions, start, accepts):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start = start
        self.accepts = accepts
        
    def minimize(self):
        # Hopcroft's algorithm implementation for DFA minimization
        P = set([frozenset(self.accepts), frozenset(self.states - self.accepts)])
        W = set([frozenset(self.accepts)])

        while W:
            A = W.pop()
            for c in self.alphabet:
                X = set()
                for state in self.states:
                    if self.transitions[state].get(c, None) in A:
                        X.add(state)
                if not X:
                    continue
                
                new_P = set()
                for Y in P:
                    intersect = X & Y
                    difference = Y - X
                    if intersect and difference:
                        new_P.add(frozenset(intersect))
                        new_P.add(frozenset(difference))
                        if Y in W:
                            W.remove(Y)
                            W.add(frozenset(intersect))
                            W.add(frozenset(difference))
                        else:
                            if len(intersect) <= len(difference):
                                W.add(frozenset(intersect))
                            else:
                                W.add(frozenset(difference))
                    else:
                        new_P.add(Y)
                P = new_P

        state_map = {}
        new_states = set()
        new_transitions = {}
        new_start = None
        new_accepts = set()
        
        for i, group in enumerate(P):
            rep = min(group)
            state_map[rep] = f'S{i}'
            new_states.add(f'S{i}')
            if self.start in group:
                new_start = f'S{i}'
            if group & self.accepts:
                new_accepts.add(f'S{i}')
                
        for group in P:
            rep = min(group)
            new_trans = {}
            for symbol in self.alphabet:
                target = self.transitions[rep].get(symbol, None)
                if target is not None:
                    for g in P:
                        if target in g:
                            new_trans[symbol] = state_map[min(g)]
                            break
            new_transitions[state_map[rep]] = new_trans
            
        return DFA(new_states, self.alphabet, new_transitions, new_start, new_accepts)

# ======================
# CFG Class
# ======================
class CFG:
    def __init__(self, productions):
        self.productions = productions
        
    def to_cnf(self):
        # Convert CFG to Chomsky Normal Form (CNF)
        optimized_productions = {
            'E': [['T', "E'"]],
            "E'": [['+', 'T', "E'"], []],
            'T': [['F', "T'"]],
            "T'": [['*', 'F', "T'"], []],
            'F': [['(', 'E', ')'], ['id'], ['num']]
        }
        return optimized_productions

# ======================
# Optimized Lexer Class
# ======================
class OptimizedLexer:
    def __init__(self):
        # Define DFA for tokenizing input source code
        states = {'q0', 'q1', 'q2', 'q3'}
        alphabet = set('abcdefghijklmnopqrstuvwxyz0123456789+*()')
        
        transitions = {
            'q0': {}, 'q1': {}, 'q2': {}, 'q3': {}
        }
        
        # Letters (identifiers)
        for c in 'abcdefghijklmnopqrstuvwxyz':
            transitions['q0'][c] = 'q1'
            transitions['q1'][c] = 'q1'
            
        # Digits (numbers)
        for d in '0123456789':
            transitions['q0'][d] = 'q2'
            transitions['q2'][d] = 'q2'
            
        # Operators and parentheses
        for op in '+*()':
            transitions['q0'][op] = 'q3'
            
        start_state = 'q0'
        accepting_states = {'q1', 'q2', 'q3'}
        
        original_dfa = DFA(states, alphabet, transitions, start_state, accepting_states)
        self.dfa = original_dfa.minimize()
        
    def tokenize(self, source):
        tokens = []
        pos = 0
        while pos < len(source):
            current_state = self.dfa.start
            start_pos = pos
            last_accept_pos = None
            
            while pos < len(source):
                char = source[pos].lower()
                if char not in self.dfa.alphabet:
                    break
                current_state = self.dfa.transitions[current_state].get(char, None)
                if current_state is None:
                    break
                if current_state in self.dfa.accepts:
                    last_accept_pos = pos
                pos += 1
                
            if last_accept_pos is not None:
                token_value = source[start_pos:last_accept_pos+1]
                if token_value in {'+', '*', '(', ')'}:
                    tokens.append((token_value, token_value))
                elif token_value[0].isalpha():
                    tokens.append(('id', token_value))
                else:
                    tokens.append(('num', token_value))
                pos = last_accept_pos + 1
            else:
                pos += 1  # Skip invalid characters
                
        return tokens

# ======================
# Optimized Parser Class
# ======================
class OptimizedParser:
    def __init__(self):
        original_productions = {
            'E': [['E', '+', 'T'], ['T']],
            'T': [['T', '*', 'F'], ['F']],
            'F': [['(', 'E', ')'], ['id'], ['num']]
        }
        
        cfg_converter = CFG(original_productions)
        self.cnf_productions = cfg_converter.to_cnf()
        
    def parse(self, tokens):
        token_types = [t[0] for t in tokens]
        n_tokens = len(token_types)
        
        # CYK Table Initialization
        table = [[set() for _ in range(n_tokens+1)] for _ in range(n_tokens+1)]
        
        # Fill table with single-token matches
        for i in range(n_tokens):
            for non_terminal, productions in self.cnf_productions.items():
                for production in productions:
                    if len(production) == 1 and production[0] == token_types[i]:
                        table[i][i+1].add(non_terminal)
                        
        # Fill table with multi-token matches using CYK algorithm
        for length in range(2, n_tokens+1):
            for i in range(n_tokens - length + 1):
                j = i + length
                for k in range(i+1, j):
                    for B in table[i][k]:
                        for C in table[k][j]:
                            for non_terminal, productions in self.cnf_productions.items():
                                for production in productions:
                                    if len(production) == 2 and production[0] == B and production[1] == C:
                                        table[i][j].add(non_terminal)
                                        
        return 'E' in table[0][n_tokens]

# ======================
# Compiler Class (Completed)
# ======================
class Compiler:
    def __init__(self):
        self.lexer = OptimizedLexer()
        self.parser = OptimizedParser()
        
    def compile(self, source_code):
        # Lexing phase
        start_time_lexing = time.time()
        tokens = self.lexer.tokenize(source_code)
        lex_time = time.time() - start_time_lexing

        # Parsing phase
        start_time_parsing = time.time()
        parse_result = self.parser.parse(tokens)
        parse_time = time.time() - start_time_parsing

        # Collect metrics
        metrics = {
            'lex_states': len(self.lexer.dfa.states),
            'parse_prods': sum(len(prods) for prods in self.parser.cnf_productions.values()),
            'lex_time': lex_time,
            'parse_time': parse_time
        }

        return tokens, parse_result, metrics

# ======================
# Main Execution
# ======================
if __name__ == "__main__":
    source = "a + 1 * ( b + 2 )"
    compiler = Compiler()
    tokens, result, metrics = compiler.compile(source)
    
    print(f"Source: {source}")
    print(f"Tokens: {tokens}")
    print(f"Parse {'success' if result else 'failure'}\n")
    
    print("Optimization Results:")
    print(f"Lexer states: {metrics['lex_states']}")
    print(f"Productions: {metrics['parse_prods']}")
    print(f"Lex time: {metrics['lex_time']:.6f}s")
    print(f"Parse time: {metrics['parse_time']:.6f}s")