"""
Given the transitions in a state machine written in GraphViz DOT format and a list of states in that state machine:

* Outputs one neuron definition per entry in that list of states such that:
    * The neuron's inputs are each defined transition.
    * The neuron is on if and only if the current transition would transition into the neuron's corresponding state machine state.
"""

import re

# obtain a list of lines that contain transitions
transitions = []
with open("json_fsm.dot", "r") as f:
    for line in f:
        if re.match(r"^\s*\w+\s*->\s*\w+", line):
            transitions.append(line.strip())
searches = r"""
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
def find(search, value): return re.search(r"->\s+{}\b".format(search), value)

for search in searches:
    result = []
    for i, value in enumerate(transitions):
        if i % 5 == 0: result.append(" ")
        result.append("1" if find(search, value) else "x")
    line = "".join(result)[1:]
    print("neuron_inputs_any_match(\"{line}\"), # {search}".format(line=line, search=search))
