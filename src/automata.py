def load_automata(filename):
    """
    Lê os dados de um autômato finito a partir de um arquivo.

    A estrutura do arquivo deve ser:

    <lista de símbolos do alfabeto, separados por espaço (' ')>
    <lista de nomes de estados>
    <lista de nomes de estados finais>
    <nome do estado inicial>
    <lista de regras de transição, com "origem símbolo destino">

    Um exemplo de arquivo válido é:

    ```
    a b
    q0 q1 q2 q3
    q0 q3
    q0
    q0 a q1
    q0 b q2
    q1 a q0
    q1 b q3
    q2 a q3
    q2 b q0
    q3 a q1
    q3 b q2
    ```

    Caso o arquivo seja inválido uma exceção Exception é gerada.

    """
    with open(filename, "rt") as file:
        try:
            alphabet = file.readline().strip().split()
            states = file.readline().strip().split()
            final_states = file.readline().strip().split()
            initial_state = file.readline().strip()
            transitions = {}

            for line in file:
                parts = line.strip().split()
                if len(parts) != 3:
                    raise ValueError("Formato de transição inválido.")
                origin, symbol, destination = parts
                if origin not in transitions:
                    transitions[origin] = {}
                if symbol not in transitions[origin]:
                    transitions[origin][symbol] = []
                transitions[origin][symbol].append(destination)

            if initial_state not in states:
                raise ValueError("Estado inicial não está presente no conjunto de estados.")
            for final_state in final_states:
                if final_state not in states:
                    raise ValueError("Estado final não está presente no conjunto de estados.")
            for origin in transitions:
                if origin not in states:
                    raise ValueError("Transição parte de estado que não está no conjunto de estados.")
                for symbol in transitions[origin]:
                    if symbol not in alphabet:
                        raise ValueError("Transição utiliza símbolo inválido.")
                    for destination in transitions[origin][symbol]:
                        if destination not in states:
                            raise ValueError("Transição leva a estado que não está no conjunto de estados.")

            return {
                "alphabet": alphabet,
                "states": states,
                "final_states": final_states,
                "initial_state": initial_state,
                "transitions": transitions
            }
        except ValueError as e:
            raise ValueError(f"Erro ao ler o arquivo: {e}")

def process(automata, words):
    """
    Processa a lista de palavras e retorna o resultado.
    
    Os resultados válidos são ACEITA, REJEITA, INVALIDA.
    """
    results = []
    for word in words:
        current_state = automata["initial_state"]
        is_valid = True

        for symbol in word:
            if symbol not in automata["alphabet"]:
                results.append("INVALIDA")
                is_valid = False
                break

            if current_state in automata["transitions"] and symbol in automata["transitions"][current_state]:
                current_state = automata["transitions"][current_state][symbol][0]
            else:
                results.append("REJEITA")
                is_valid = False
                break

        if is_valid:
            if current_state in automata["final_states"]:
                results.append("ACEITA")
            else:
                results.append("REJEITA")

    return results

def convert_to_dfa(automata):
    """Converte um NFA num DFA."""
    new_states = {}
    dfa_transitions = {}
    dfa_final_states = set()
    state_counter = 0

    def get_state_name(states_set):
        nonlocal state_counter
        name = ','.join(sorted(states_set))
        if name not in new_states:
            new_states[name] = f'q{state_counter}'
            state_counter += 1
        return new_states[name]

    initial_state = get_state_name([automata["initial_state"]])
    states_to_process = [initial_state]
    processed_states = set()

    while states_to_process:
        current = states_to_process.pop()
        processed_states.add(current)

        if any(state in automata["final_states"] for state in current.split(',')):
            dfa_final_states.add(current)

        current_states = current.split(',')
        dfa_transitions[current] = {}

        for symbol in automata["alphabet"]:
            next_states = set()
            for state in current_states:
                if state in automata["transitions"] and symbol in automata["transitions"][state]:
                    next_states.update(automata["transitions"][state][symbol])

            if next_states:
                next_state_name = get_state_name(next_states)
                dfa_transitions[current][symbol] = next_state_name
                if next_state_name not in processed_states:
                    states_to_process.append(next_state_name)

    return {
        "alphabet": automata["alphabet"],
        "states": list(new_states.values()),
        "final_states": list(dfa_final_states),
        "initial_state": initial_state,
        "transitions": dfa_transitions
    }
