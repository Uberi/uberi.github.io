---
title: JSON Parsing with Tensorflow
date: 2017-02-17
description: Fun with Tensorflow, parsers, and JSON.
layout: post
---

[Tensorflow 1.0.0](https://github.com/tensorflow/tensorflow/releases/tag/v1.0.0) came out recently. Inspired by [Tensorflow FizzBuzz](http://joelgrus.com/2016/05/23/fizz-buzz-in-tensorflow/), I thought it would be fun to solve a simple problem using something more complicated than necessary:

![JSON-NN architecture diagram](architecture.svg)

To take the joke to its natural conclusion, the result is now [available on PyPI](https://pypi.python.org/pypi/json-nn): `pip install json-nn`.

Introduction
------------

Since JSON is a nonregular language, no program can parse all JSON strings using a constant amount of memory. By itself, a finite-sized neural network won't do the job.

Bottom-up parsers pair a finite state machine with a stack - the state machine encodes the rules of the language, while the stack acts like the state machine's "memory". For our JSON-parsing neural network, we'll try a similar approach.

A driver program will feed characters into the neural network, and the neural network will output stack operations. Here's a taste of what a parse result might look for the JSON string `{"abc": 5}`:

{% highlight python linenos=table %}
OP_PUSH_DICT             # encountered `{` character, push an empty dict onto the stack
OP_PUSH_STRING           # encountered `"` character, push an empty string onto the stack
OP_APPEND_CHAR("a")      # encountered `a` character, append the character "a" to the string
OP_APPEND_CHAR("b")      # encountered `b` character, append the character "b" to the string
OP_APPEND_CHAR("c")      # encountered `c` character, append the character "c" to the string
OP_NOP                   # encountered `"` character, do nothing
OP_NOP                   # encountered `:` character, do nothing
OP_NOP                   # encountered ` ` character, do nothing
OP_PUSH_NUMBER           # encountered `5` character, append the number 0 onto the stack
OP_SHIFT_DEC(5)          # encountered `5` character (again), decimal shift 5 to the number
OP_APPEND_PAIR_TO_DICT   # encountered `}` character, add the number to the dict under the string as the key
OP_COMPLETE_DICT         # encountered `}` character (again), mark the dictionary as completed (the complete/incomplete distinction is needed to properly compute the inner container)
{% endhighlight %}

By executing these operations, we get the parse result: a dictionary containing the key "abc", associated with the value 5.

State Machine
-------------

The [official JSON grammar](http://json.org/) is available online, so I converted this into a sort-of epsilon-NFA, making up the stack operations and control variables as I went along. Basically everything besides the array/object handling parts is taken from the railroad diagrams on that page.

Here's the [epsilon-NFA as a Graphviz DOT file](json_fsm.dot). We can render it with `dot -Tpng json_fsm.dot > json_fsm.png` to get the following:

[![Bitmap rendering of the JSON-parsing finite state machine](json_fsm.png)](json_fsm.png)

I defined a basic set of stack operations the parser would probably need to build a JSON parsing result. There were originally 18, but I added and removed a few to make things a little easier for myself:

| Operation                 | What it does                                                                                         |
|:--------------------------|:-----------------------------------------------------------------------------------------------------|
| `OP_NOP`                  | Do nothing.                                                                                          |
| `OP_SWAP`                 | Swap the top two stack items.                                                                        |
| `OP_PUSH_STRING`          | Push `""` onto the stack.                                                                            |
| `OP_APPEND_CHAR(K)`       | For any input character `K`, set `STACK[-1] += K`.                                                   |
| `OP_APPEND_CHAR_CODE`     | Pop the top of the stack as `K`, then set `STACK[-1] += chr(K)`.                                     |
| `OP_PUSH_NUMBER`          | Push `0` onto the stack.                                                                             |
| `OP_ADD`                  | Pop the top of the stack as `K`, then set `STACK[-1] += K`.                                          |
| `OP_INVERT`               | Set `STACK[-1] = -STACK[-1]`.                                                                        |
| `OP_DECREMENT`            | Decrement `STACK[-1] += 1`.                                                                          |
| `OP_SHIFT_DEC(K)`         | For the input character `K` (matching `[0-9]`), set `STACK[-1] = STACK[-1] * 10 + int(K)`.           |
| `OP_SHIFT_HEX(K)`         | For any input character `K` (matching `[0-9a-fA-F]`), set `STACK[-1] = STACK[-1] * 16 + int(K, 16)`. |
| `OP_EXPONENTIATE_NUMBERS` | Pop the top of the stack as `K`, then set `STACK[-1] = STACK[-1] * 10 ** K`.                         |
| `OP_PUSH_DICT`            | Push `{(): None}` onto the stack.                                                                    |
| `OP_APPEND_PAIR_TO_DICT`  | Set `STACK[-3][STACK[-2]] = STACK[-1]`.                                                              |
| `OP_COMPLETE_DICT`        | Do `del STACK[-1][()]`.                                                                              |
| `OP_PUSH_LIST`            | Push `[()]` onto the stack.                                                                          |
| `OP_APPEND_VALUE_TO_LIST` | Set `STACK[-2].append(STACK[-1])`.                                                                   |
| `OP_COMPLETE_LIST`        | Set `del STACK[-1][0]`.                                                                              |
| `OP_PUSH_TRUE`            | Push `True` onto the stack.                                                                          |
| `OP_PUSH_FALSE`           | Push `False` onto the stack.                                                                         |
| `OP_PUSH_NONE`            | Push `None` onto the stack.                                                                          |

The neural network needs to emit the correct instructions in the correct order to produce the parse result.

To check for errors in the state machine, I [implemented it directly in code](json_fsm.py). The following script can be used to test the FSM parser against Python's built-in `json` module with millions of generated JSON-like strings:

{% highlight python linenos=table %}
import itertools
from json import loads
from json_fsm import JsonFSM

#ALPHABET = ['"', '0', '5', '.', '-', '+', '\\', 'tr', 'u', 'e', '[', ']', ',', '{', ':', '}', '']; MAX_LENGTH = 5
#ALPHABET = ['"a"', ',', '{', ':', '}', '']; MAX_LENGTH = 8
#ALPHABET = ['1', ',', '[', ']', '']; MAX_LENGTH = 8
ALPHABET = ['5', '.', 'e', '-', '+', '']; MAX_LENGTH = 8

parser = JsonFSM()
def error(value): assert False # called for invalid numbers, just raise an error instead of NaN or whatever
for test_list in itertools.product(ALPHABET, repeat=MAX_LENGTH): # generate every possible arrangement of the strings in the slphabet
    test = "".join(test_list) # get the current test case
    try: expected = loads(test, parse_constant=error) # parse the test case with the built-in parser, record the result
    except: expected = ("<INVALID>",)
    try: actual = parser.parse(test) # parse the test case with our FSM parser, record the result
    except:
        actual = ("<INVALID>",)
    if actual != expected: # uh-oh, there's a bug in our FSM parser...
        print("FAIL: test case {!r} should be parsed to {!r}, but FSM parser gave {!r} instead".format(test, expected, actual))
print("Test completed.")
{% endhighlight %}

The last one uncovered an issue in my original design: when parsing a number like `32.10e64`, it would read in the number 123, multiply by \\(10^{-2}\\), then read in the exponent 64 and multiply the number by \\(10^{64}\\). However, the first exponentiation loses a bit of floating point precision while the second one magnifies it, giving us `3.2100000000000003e+65` as the result.

To fix this, I introduced the `add_exponents` control variable and changed the transitions around so that if there was a fractional exponent (specified by the placement of the decimal point) and an explicit exponent (specified by the `e<NUMBER>` notation), they get added together. This ensures that there's at most one exponentiation for each number we parse, allowing us to get `3.21e+65` as expected.

Layer Design
------------

The basic idea is that the layers will implement logic gates that, when arranged correctly, will implement the state machine.

Tensorflow has this neat activation function called RELU6, defined as \\(\mathrm{RELU6}(x) = \min(6, \max(0, x))\\) - it's the line \\(y = x\\), but bounded by the lines \\(y = 0\\) and \\(y = 6\\). The flat tails make this interesting, because with the correct weights, we can make it resemble a step function.

Let's denote a logical "high" value as 6, and a logical "low" value as 0. Let \\(x_1, \ldots, x_n\\) be the inputs to a given neuron, \\(w_1, \ldots, w_n\\) be the weights associated with those inputs, and \\(b\\) be the neuron's bias. Clearly, the value of the neuron is \\(\mathrm{RELU6}\left(b + \sum_{1 \le i \le n} w_i x_i\right)\\).

### AND/NOR gates

Suppose \\(n = 5\\) and we want an AND gate over inputs \\(x_1, x_3, x_5\\) - the neuron should output 6 if \\(x_1 = 6\\) and \\(x_3 = 6\\) and \\(x_5 = 6\\), otherwise it should output 0. 

This one's pretty easy - just let \\(w_1 = w_3 = w_5 = 1\\) and \\(w_2 = w_4 = 0\\) with \\(b = -12\\). For a NOR gate, we can instead set \\(b = 6\\), with \\(w_1 = w_3 = w_5 = -1\\) and \\(w_2 = w_4 = 0\\).

We can generalize this to get the following weight-and-bias-generating function:

{% highlight python linenos=table %}
def neuron_inputs_all_match(pattern):
    """
    Generate weights and a bias for a single RELU6 neuron such that it will fire if and only if all inputs corresponding to 0 or 1 in the pattern are deactivated or activated, respectively.

    Patterns are sequences of the following characters:

    * `1` means the input should be activated.
    * `0` means the input should be deactivated.
    * `x` means we don't care whether the input is activated or not.
    * ` ` (space) is ignored entirely.

    Common pattern styles:

    * Logical AND: `neuron_inputs_all_match("xx1x1")` specifies a neuron that will output 6 if and only if the third and fifth neuron in the previous layer output 6.
    * Logical NOR: `neuron_inputs_all_match("xx000")` specifies a neuron that will output 6 if and only if all of the last three neurons in the previous layer output 0.
    """
    pattern = pattern.replace(" ", "") # ignore spaces in the pattern
    weights = [
        1 if char == "1" else -len(pattern) if char == "0" else 0
        for char in pattern
    ]
    bias = 6 - 6 * sum(char == "1" for char in pattern)
    return weights, bias
{% endhighlight %}

### OR/NAND gates

Suppose \\(n = 5\\) and we want an OR gate over inputs \\(x_1, x_3, x_5\\) - the neuron should output 6 if \\(x_1 = 6\\) or \\(x_3 = 6\\) or \\(x_5 = 6\\), otherwise it should output 0. 

This one's also pretty easy - just let \\(w_1 = w_3 = w_5 = 1\\) and \\(w_2 = w_4 = 0\\) with \\(b = 0\\). For a NOR gate, we can instead set \\(b = 6\\), with \\(w_1 = w_3 = w_5 = -1\\) and \\(w_2 = w_4 = 0\\).

We can generalize this to get the following weight-and-bias-generating function:

{% highlight python linenos=table %}
def neuron_inputs_any_match(pattern):
    """
    Generate weights and a bias for a single RELU6 neuron such that it will fire if and only if any inputs corresponding to 0 or 1 in the pattern are deactivated or activated, respectively.

    The specified neurons are denoted by a pattern, which is a sequence of the following characters:

    * `1` - when the corresponding neuron on the previous layer activates, so does the current neuron.
    * `0` - when all of the neurons on the previous layer corresponding to `0`'s are activated, the current neuron is deactivated unless a `1` neuron activates the current neuron.
    * `x` means we don't care whether the neuron on the previous layer is activated or not.
    * ` ` (space) is ignored entirely.

    In other words, the neuron will be activated if and only if any of the 1 and 0 positions are matched by corresponding inputs.

    Common pattern styles:

    * Logical OR: `neuron_inputs_any_match("xx1x1")` specifies a neuron that will output 6 if and only if either the third ofifth neuron in the previous layer output 6.
    * Logical NAND: `neuron_inputs_any_match("xx000")` specifies a neuron that will output 6 if and only if any of the last three neurons in the previous layer output 0.
    """
    pattern = pattern.replace(" ", "") # ignore spaces in the pattern
    weights = [
        len(pattern) if char == "1" else -1 if char == "0" else 0
        for char in pattern
    ]
    bias = 6 * sum(char == "0" for char in pattern)
    return weights, bias
{% endhighlight %}

### Building layers

With these primitives in place, we can build simple recognizers. Here's one with 4 neurons, each capable of recognizing one letter of "true" given a UTF-32 codepoint:

{% highlight python linenos=table %}
true_recognizer_neurons = [
    neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0111 0100"), # activates if and only if the input is the UTF-32 codepoint for "t"
    neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0111 0010"), # activates if and only if the input is the UTF-32 codepoint for "r"
    neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0111 0101"), # activates if and only if the input is the UTF-32 codepoint for "u"
    neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0110 0101"), # activates if and only if the input is the UTF-32 codepoint for "e"
]
true_recognizer_layer = tf.nn.relu6(
    tf.add(
        tf.matmul(input_layer, transpose(weights for weights, bias in true_recognizer_neurons)),
        tf.constant([bias for weights, bias in true_recognizer_neurons])
    )
)
{% endhighlight %}

Note that this is just a cleaner way of writing the following:

{% highlight python linenos=table %}
weights = [
    #  t    r    u    e
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [-32, -32, -32, -32],
    [  1,   1,   1,   1],
    [  1,   1,   1,   1],
    [  1,   1,   1, -32],
    [-32, -32, -32, -32],
    [  1, -32,   1,   1],
    [-32,   1, -32, -32],
    [-32, -32,   1,   1],
]
biases = [
    # t    r    u    e
    -18, -18, -24, -18
]
true_recognizer_layer = tf.nn.relu6(tf.add(tf.matmul(input_layer, weights), biases))
{% endhighlight %}

These primitives can now be used to construct the layers of our network.

Network Architecture
--------------------

What do the network's inputs and outputs look like?

* Input layer (76 neurons):
    1. 32 neurons representing the current UTF-32 character in the input stream, as a 32-bit big-endian codepoint.
    2. 36 recurrent neurons `next_state` from output layer at previous iteration. Initially 0.
    3. Recurrent neuron `negative` from output layer at previous iteration. Initially 0.
    4. Recurrent neuron `negative_exponent` from output layer at previous iteration. Initially 0.
    5. Recurrent neuron `add_exponents` from output layer at previous iteration. Initially 0.
    6. Recurrent neuron `item_present` from output layer at previous iteration. Initially 0.
    7. Recurrent neuron `parsing_key` from output layer at previous iteration. Initially 0.
    8. Recurrent neuron `comma_used` from output layer at previous iteration. Initially 0.
    9. 2 neurons representing the type of the topmost incomplete container on the stack. The first neuron is activated when the inner container is a list, and the second neuron is activated when the inner container is a dict. An incomplete container is just a container that contains `()` (`[(), ...]` for lists, or `{(): None, ...}` for dicts).
* Output layer (97 neurons):
    1. 21 neurons `operation`, one for each kind of operation that can be performed.
    2. 32 neurons `operand` for a single parameter associated with `operation`, if applicable (commands like `OP_APPEND_CHAR` accept one parameter).
    3. 36 recurrent neurons `state` for one-hot encoded current state of the parser FSM. Retains its value if not changed.
    4. Recurrent neuron `negative` for whether the latest number parsed is negative or not. Retains its value if not changed.
    5. Recurrent neuron `negative_exponent` for whether the latest number parsed has a negative exponent or not. Retains its value if not changed.
    6. Recurrent neuron `add_exponents` for whether the latest number parsed has both a fractional exponent and an explicit exponent (e.g., `1.45e3` is just 145 with fractional exponent -2 and explicit exponent 3). Retains its value if not changed.
    7. Recurrent neuron `item_present` for whether the latest entry in a container isn't the first one or not (basically, whether we can use the comma operator). Retains its value if not changed.
    8. Recurrent neuron `parsing_key` for whether we are currently parsing a key in an object. Retains its value if not changed.
    9. Recurrent neuron `comma_used` for whether the last token we encountered (excluding non-container literals) was a comma operator. Retains its value if not changed.
    10. Neuron `position_stay` for whether we should stay in place within the input stream. Is 0 unless set.
    11. Neuron `accept` for whether we can accept the input if the current character is the last one. Is 0 unless set.

![JSON-NN architecture diagram](architecture.svg)

I wrote the weights/biases for the `CODEPOINT PATTERNS` layer by hand. An initial layer recognized specific ranges of characters (e.g., `e` and `E`), and a second layer recognizes certain patterns in the character (e.g., `[eE]`).

The weights/biases for the `OPERAND PATTERNS` layer is also written by hand. The operand should usually just be the input character, but some transitions require the operand to be set to certain values. Therefore, each bit of the operand has three possibilities: SET (current transition forces the operand bit to 1), RESET (current transition forces the operand bit to 0), and PASS (operand bit is just the corresponding bit in the input character).

We can represent this as \\(\text{operand bit} = \text{set operand bit} \lor (\text{input character bit is 1} \land \neg \text{reset operand bit})\\). Clearly, \\(\text{set operand bit} = S_1 \lor \ldots \lor S_k\\), where \\(S_1, \ldots, S_k\\) are the neuron inputs corresponding to the transitions that set the operand bit. Likewise, \\(\text{reset operand bit} = R_1 \lor \ldots \lor R_k\\), where \\(R_1, \ldots, R_k\\) are the neuron inputs corresponding to the transitions that reset the operand bit. Therefore, \\(\text{operand bit} = S_1 \lor \ldots \lor S_k \lor (\text{input character bit is 1} \land \neg (R_1 \lor \ldots \lor R_k))\\).

Note that this formula requires 3 levels of gates to implement, which means 3 layers. Applying DeMorgan's law, we can simplify it down to 2 (NOT gates don't count): \\(\text{operand bit} = S_1 \lor \ldots \lor S_k \lor \neg (\neg\text{input character bit is 1} \lor R_1 \lor \ldots \lor R_k)\\). We can now compute \\(\text{operand bit is tentatively 0} = \neg\text{input character bit is 1} \lor R_1 \lor \ldots \lor R_k\\) using the first layer, and then feed its output into a second layer that can then compute \\(\text{operand bit} = S_1 \lor \ldots \lor S_k \lor \neg \text{operand bit is tentatively 0}\\).

The `TRANSITIONS` layer is partially [generated by a pretty hacky script](generate_transition_neurons.py) - specifically, I filled in the transition patterns by hand. It's just a longer version of the recognizer example above. The `OPERATION/STATE` layer is actually generated by two hacky scripts, [one for the operations](generate_operation_neurons.py), and [one for the state](generate_state_neurons.py). Both of these are just longer versions of the recognizer example above.

The `VARIABLES` layer is [generated by a _really_ hacky script](generate_variable_neurons.py). It uses a technique very similar to that used for `OPERAND PATTERNS`, where there are SET/RESET/PASS states, but the PASS state passes on the previous value of the variable rather than a bit in the input character. That means depending on the transition, we can either SET a variable to 1, RESET it to 0, or PASS to make it keep its current value.

With the layers themselves done, connecting them turned out quite simple:

{% highlight python linenos=table %}
# layer inputs: (user supplied)
# layer outputs: current input character
input_layer = tf.placeholder(tf.int32, shape=[1, 32], name="character")

# layer inputs: (user supplied)
# layer outputs: inner container type
inner_container = tf.placeholder(tf.int32, shape=[1, 2], name="inner_container")

# layer inputs: (user supplied)
# layer outputs: current state machine state
state = tf.Variable(tf.constant([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]), name="state")

# layer inputs: (user supplied)
# layer outputs: control variables
variables = tf.Variable(tf.constant([[0, 0, 0, 0, 0, 0, 0, 0]]), name="variables")

# layer inputs: current input character
# layer outputs: current input character's pattern
codepoint_patterns_layer = codepoint_patterns_recognizer(input_layer)

# layer inputs: current state machine state, current input character's pattern, control variables, inner container type
# layer outputs: current state machine transition
transitions_layer = transitions_recognizer(state, codepoint_patterns_layer, variables, inner_container)

# layer inputs: current state machine transition
# layer outputs: operation at current step, next state machine state
operation_and_state_layer = operation_and_state_recognizer(transitions_layer)
operation_layer = tf.slice(operation_and_state_layer, [0, 0], [-1, 21])
updated_state = state.assign(tf.slice(operation_and_state_layer, [0, 21], [-1, -1]))

# layer inputs: current state machine transition, previous value of recurrent control variables
# layer outputs: values of control variables (recurrent and non-recurrent)
variables_layer = variables_recognizer(transitions_layer, variables)
updated_variables = variables.assign(variables_layer)

# layer inputs: current state machine transition, current input character
# layer outputs: operand (all 32 bits of it)
operand_patterns_layer = operand_patterns_recognizer(transitions_layer, input_layer)
{% endhighlight %}

Results
-------

Everything in one nice, self-contained Python library: [json_nn.py](json_nn/json_nn.py).

Here's a simple usage example:

{% highlight python linenos=table %}
from json_nn import JsonNN

parser = JsonNN()
print(parser.parse("""
{
    "classes": [
        {
            "dates":{
                "start_time": "11:30", "end_time": "12:50", "weekdays": "F",
                "start_date": null, "end_date": null,
                "is_tba": false, "is_cancelled": false, "is_closed": false
            },
            "location":{"building": "MC", "room": "3003"},
            "instructors": []
        }
    ]
}
"""))

# prints out the following:
# {'classes': [{'location': {'room': '3003', 'building': 'MC'}, 'dates': {'is_cancelled': False, 'start_time': '11:30', 'start_date': None, 'is_tba': False, 'end_date': None, 'end_time': '12:50', 'weekdays': 'F', 'is_closed': False}, 'instructors': []}]}
{% endhighlight %}

On my machine, `json.loads` takes about 60 microseconds to parse this. `JsonNN` does it in 160 _milliseconds_, or about three orders of magnitude slower. However, it's still a correct and fully functional parser. I'd call this one a success!

Loose Ends
----------

Files used for this project:

* [Neural network JSON parser implementation](json_nn/json_nn.py)
* [LibreOffice Draw source files for the architecture diagram](architecture.odg)
* [GraphViz DOT file for the JSON parsing finite state machine](json_fsm.dot)
* [Direct implementation of the JSON parsing finite state machine](json_fsm.py)
* [Script used to test the direct implementation of the JSON parsing finite state machine](json_fsm_test.py)
* [Script used to generate the transition layer neurons](generate_transition_neurons.py)
* [Script used to generate the operation layer neurons](generate_operation_neurons.py)
* [Script used to generate the state layer neurons](generate_state_neurons.py)
* [Script used to generate the variable layer neurons](generate_variable_neurons.py)
* [Some sample JSON from the uWaterloo Open Data API, for testing purposes](sample.json)

Other stuff:

* [All of the source files for the JSON-NN Python package](json_nn.zip)
* [JSON-NN page on PyPI](https://pypi.python.org/pypi/json-nn)
