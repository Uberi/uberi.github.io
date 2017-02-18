"""
Given the transitions in a state machine written in GraphViz DOT format and a list of control variables in that state machine:

* Outputs one neuron definition per entry in that list of control variables such that:
    * The neuron's inputs are each defined transition.
    * The neuron is on if and only if the current transition would set the neuron's corresponding variable, or if not specified, it retains its previous value.
"""

import re

transitions = []
with open("json_fsm.dot", "r") as f:
    for line in f:
        if re.match(r"^\s*\w+\s*->\s*\w+", line):
            transitions.append(line.strip())
searches = r"""
negative
negative_exponent
add_exponents
item_present
parsing_key
comma_used
position_stay
accept
""".strip().split("\n")
def find_true(search, value): return re.search(r"set\s+{}\s+to\s+true".format(search), value)
def find_false(search, value): return re.search(r"set\s+{}\s+to\s+false".format(search), value)

print("variable is tentatively false:")
for variable_index, search in enumerate(searches):
    result = []
    for i, value in enumerate(transitions):
        if i % 5 == 0: result.append(" ")
        result.append("1" if find_false(search, value) else "x")
    line = "".join(result)[1:]
    previous_values = ["x"] * len(searches)
    previous_values[variable_index] = "0"
    previous_value_was_false = "".join(previous_values)
    print("neuron_inputs_any_match(\"{line}    {previous_value_was_false}\"), # {search} is tentatively false".format(line=line, previous_value_was_false=previous_value_was_false, search=search))
print("variable is true:")
for variable_index, search in enumerate(searches):
    result = []
    for i, value in enumerate(transitions):
        if i % 5 == 0: result.append(" ")
        result.append("1" if find_true(search, value) else "x")
    line = "".join(result)[1:]
    previous_values = ["x"] * len(searches)
    previous_values[variable_index] = "0"
    previous_value_was_false = "".join(previous_values)
    print("neuron_inputs_any_match(\"{line}    {previous_value_was_false}\"), # {search}".format(line=line, previous_value_was_false=previous_value_was_false, search=search))