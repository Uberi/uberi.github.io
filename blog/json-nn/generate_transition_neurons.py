"""
Given the transitions in a state machine written in GraphViz DOT format and a list of states and a list of control variables in that state machine:

* Outputs one neuron definition per transition such that:
    * The neuron's inputs are the current state, transition patterns, control variables, and the inner container.
    * The transition patterns and inner container parts are just placeholders; those must be done by hand still.
    * The neuron is on if and only if the inputs imply that we should perform the neuron's corresponding state machine transition.
"""

import re

# obtain a list of lines that contain transitions
transitions = []
with open("json_fsm.dot", "r") as f:
    for line in f:
        if re.match(r"^\s*\w+\s*->\s*\w+", line):
            transitions.append(line.strip())
states = r"""
START
ARRAY_END
DICT_END
DICT_PAIR_VALUE
LITERAL_F
LITERAL_FA
LITERAL_FAL
LITERAL_FALS
LITERAL_N
LITERAL_NU
LITERAL_NUL
LITERAL_T
LITERAL_TR
LITERAL_TRU
NUMBER_DECIMAL
NUMBER_E
NUMBER_END
NUMBER_E_SIGN
NUMBER_EXPONENT
NUMBER_EXPONENT_APPLY
NUMBER_MANTISSA_FRACTIONAL
NUMBER_MANTISSA_FRACTIONAL_STEP_1
NUMBER_MANTISSA_FRACTIONAL_STEP_2
NUMBER_MANTISSA_FRACTIONAL_STEP_3
NUMBER_MANTISSA_INTERIOR
NUMBER_MANTISSA_INTERIOR_START
NUMBER_MANTISSA_ZERO
NUMBER_NEGATIVE
STRING
STRING_ESCAPE
STRING_ESCAPE_UNICODE_0
STRING_ESCAPE_UNICODE_1
STRING_ESCAPE_UNICODE_2
STRING_ESCAPE_UNICODE_3
STRING_ESCAPE_UNICODE_END
""".strip().split("\n")
variables = r"""
negative
negative_exponent
add_exponents
item_present
parsing_key
comma_used
position_stay
accept
""".strip().split("\n")

for transition in transitions:
    state_from, state_to, condition = re.match(r"^\s*(\w+)\s*->\s*(\w+)\s+\[label=\"(.*);", transition).groups()
    state_result = []
    state_index = states.index(state_from)
    for i, value in enumerate(states):
        if i % 5 == 0: state_result.append(" ")
        state_result.append("1" if i == state_index else "0")
    state = "".join(state_result)[1:]
    
    var_list = "|".join(variables)
    notted_vars = set(re.findall(r"\bnot\s+({})\b".format(var_list), condition))
    normal_vars = set(re.findall(r"\b({})\b".format(var_list), condition)) - notted_vars
    variable_result = []
    for var in variables:
        if var in notted_vars: variable_result.append("0")
        elif var in normal_vars: variable_result.append("1")
        else: variable_result.append("x")
    variable_pattern = "".join(variable_result)
    
    inner_container = ("1" if re.search(r"inner\s+container\s+is\s+list", condition) else "x") + ("1" if re.search(r"inner\s+container\s+is\s+dict", condition) else "x")
    
    print("neuron_inputs_all_match(\"{state}    TTTTT TTTTT TTTTT TTTTT TTTTT TTTTT T    {variables}    {inner_container}\"), # {state_from} -> {state_to}: {condition}".format(state=state, variables=variable_pattern, inner_container=inner_container, state_from=state_from, state_to=state_to, condition=condition))
