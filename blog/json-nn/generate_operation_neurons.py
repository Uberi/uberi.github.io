"""
Given the transitions in a state machine written in GraphViz DOT format and a list of operations in that state machine:

* Outputs one neuron definition per entry in that list of operations such that:
    * The neuron's inputs are each defined transition.
    * The neuron is on if and only if the current transition invokes the neuron's corresponding action.
"""

import re

transitions = []
with open("json_fsm.dot", "r") as f:
    for line in f:
        if re.match(r"^\s*\w+\s*->\s*\w+", line):
            transitions.append(line.strip())
searches = r"""
OP_NOP
OP_SWAP
OP_PUSH_STRING
OP_APPEND_CHAR
OP_APPEND_CHAR_CODE
OP_PUSH_NUMBER
OP_ADD
OP_INVERT
OP_DECREMENT
OP_SHIFT_DEC
OP_SHIFT_HEX
OP_EXPONENTIATE_NUMBERS
OP_PUSH_DICT
OP_APPEND_PAIR_TO_DICT
OP_COMPLETE_DICT
OP_PUSH_LIST
OP_APPEND_VALUE_TO_LIST
OP_COMPLETE_LIST
OP_PUSH_TRUE
OP_PUSH_FALSE
OP_PUSH_NONE
""".strip().split("\n")
def find(search, value): return re.search(r"do {}\b".format(search), value)

for search in searches:
    result = []
    for i, value in enumerate(transitions):
        if i % 5 == 0: result.append(" ")
        result.append("1" if find(search, value) else "x")
    line = "".join(result)[1:]
    print("neuron_inputs_any_match(\"{line}\"), # {search}".format(line=line, search=search))
