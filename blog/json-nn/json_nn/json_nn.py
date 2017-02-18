import tensorflow as tf
import numpy as np

def transpose(list_of_lists):
    """Returns the transposed version of a list of lists."""
    return [list(row) for row in zip(*list_of_lists)]

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

def codepoint_patterns_recognizer(input_layer):
    """
    Character pattern recognition network: input layer accepts a big-endian UTF-32 binary codepoint, output layer contains neurons that each activate if and only if the codepoint at the input layer matches the pattern associated with that neuron. Activated neurons have value 6, while deactivated neurons have value 0, and there are never any other values in the output layer.

    Network structure: Input (big-endian UTF-32 binary codepoint) -> Codepoint Layer -> RELU6 -> Pattern Layer -> RELU6 -> Output (patterns)
    """

    codepoint_neurons = [ # each entry in the list is a pair of the form `([weight_1, weight_2, ..., weight_n], bias)` (`n` is the number of neurons in the previous layer), and represents a single neuron in the current layer
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0000 0000"), # `\x00`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0010 0010"), # `"`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0101 1100"), # `\\`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   000x xxxx"), # `[\x00-\x1F]`, unicode special character
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0111 1111"), # `\x7F`, unicode special character

        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   100x xxxx"), # `[\x80-\x9F]`, unicode special character
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   01x0 0001"), # `[aA]`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   01x0 001x"), # `[b-cB-C]`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   01x0 010x"), # `[d-eD-E]`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   01x0 0110"), # `[fF]`

        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0010 1111"), # `/`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0110 0001"), # `a`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0110 0010"), # `b`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0110 0101"), # `e`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0110 0110"), # `f`

        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0110 1100"), # `l`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0110 1110"), # `n`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0111 0010"), # `r`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0111 0011"), # `s`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0111 0100"), # `t`

        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0111 0101"), # `u`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0011 0000"), # `0`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0011 0001"), # `1`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0011 001x"), # `[2-3]`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0011 01xx"), # `[4-7]`

        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0011 100x"), # `[8-9]`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0010 1101"), # `-`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0010 1011"), # `\+`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0010 1110"), # `\.`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   01x0 0101"), # `[eE]`

        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0010 1100"), # `,`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0011 1010"), # `:`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0101 1011"), # `[`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0101 1101"), # `]`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0111 1011"), # `{`

        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0111 1101"), # `}`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0000 1x01"), # `[\t\r]`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0000 1010"), # `\n`
        neuron_inputs_all_match("0000 0000   0000 0000   0000 0000   0010 0000"), # ` `
    ]
    codepoint_layer = tf.nn.relu6(
        tf.add(tf.matmul(input_layer, transpose(weights for weights, bias in codepoint_neurons)), [bias for weights, bias in codepoint_neurons])
    )
    
    pattern_neurons = [ # each entry in the list is a pair of the form `([weight_1, weight_2, ..., weight_n], bias)` (`n` is the number of neurons in the previous layer), and represents a single neuron in the current layer
        neuron_inputs_all_match("xxxxx xxxxxxxxx xxxxx xxxxx xxx1x xxxxx xxxxx"), # `\+`
        neuron_inputs_all_match("xxxxx xxxxxxxxx xxxxx xxxxx xxxxx x1xxx xxxxx"), # `,`
        neuron_inputs_all_match("xxxxx xxxxxxxxx xxxxx xxxxx xx1xx xxxxx xxxxx"), # `-`
        neuron_inputs_all_match("xxxxx xxxxxxxxx xxxxx xxxxx xxxx1 xxxxx xxxxx"), # `\.`
        neuron_inputs_all_match("xxxxx xxxxxxxxx xxxxx xx1xx xxxxx xxxxx xxxxx"), # `0`

        neuron_inputs_all_match("xxxxx xxxxxxxxx xxxxx xxxxx xxxxx xx1xx xxxxx"), # `:`
        neuron_inputs_all_match("xxxxx xxxxxxxxx xxxxx xxxxx xxxxx xxx1x xxxxx"), # `[`
        neuron_inputs_any_match("xxxxx xxxxxxxxx xxxxx xxxxx xxxxx xxxxx xx111"), # `[ \t\r\n]`
        neuron_inputs_any_match("xxxxx xxxxxxxxx xxxxx xxx11 11xxx xxxxx xxxxx"), # `[1-9]`
        neuron_inputs_all_match("x0000 0xxxxxxxx xxxxx xxxxx xxxxx xxxxx xxxxx"), # `[^"\\\x0000-\x001F\x007F\x0080-\x009F]`

        neuron_inputs_all_match("xxxxx xxxxxxxxx xxxxx xxxxx xxxxx 1xxxx xxxxx"), # `[eE]`
        neuron_inputs_all_match("x1xxx xxxxxxxxx xxxxx xxxxx xxxxx xxxxx xxxxx"), # `"`
        neuron_inputs_all_match("xx1xx xxxxxxxxx xxxxx xxxxx xxxxx xxxxx xxxxx"), # `\\`
        neuron_inputs_all_match("xxxxx xxxxx1xxx xxxxx xxxxx xxxxx xxxxx xxxxx"), # `/`
        neuron_inputs_any_match("xxxxx xxxxxxxxx xxxxx xx111 11xxx xxxxx xxxxx"), # `[0-9]`

        neuron_inputs_any_match("xxxxx x1111xxxx xxxxx xx111 11xxx xxxxx xxxxx"), # `[0-9a-fA-F]`
        neuron_inputs_all_match("1xxxx xxxxxxxxx xxxxx xxxxx xxxxx xxxxx xxxxx"), # `\x0000`
        neuron_inputs_all_match("xxxxx xxxxxxxxx xxxxx xxxxx xxxxx xxxx1 xxxxx"), # `]`
        neuron_inputs_all_match("xxxxx xxxxxx1xx xxxxx xxxxx xxxxx xxxxx xxxxx"), # `a`
        neuron_inputs_all_match("xxxxx xxxxxxx1x xxxxx xxxxx xxxxx xxxxx xxxxx"), # `b`

        neuron_inputs_all_match("xxxxx xxxxxxxx1 xxxxx xxxxx xxxxx xxxxx xxxxx"), # `e`
        neuron_inputs_all_match("xxxxx xxxxxxxxx 1xxxx xxxxx xxxxx xxxxx xxxxx"), # `f`
        neuron_inputs_all_match("xxxxx xxxxxxxxx x1xxx xxxxx xxxxx xxxxx xxxxx"), # `l`
        neuron_inputs_all_match("xxxxx xxxxxxxxx xx1xx xxxxx xxxxx xxxxx xxxxx"), # `n`
        neuron_inputs_all_match("xxxxx xxxxxxxxx xxx1x xxxxx xxxxx xxxxx xxxxx"), # `r`

        neuron_inputs_all_match("xxxxx xxxxxxxxx xxxx1 xxxxx xxxxx xxxxx xxxxx"), # `s`
        neuron_inputs_all_match("xxxxx xxxxxxxxx xxxxx 1xxxx xxxxx xxxxx xxxxx"), # `t`
        neuron_inputs_all_match("xxxxx xxxxxxxxx xxxxx x1xxx xxxxx xxxxx xxxxx"), # `u`
        neuron_inputs_all_match("xxxxx xxxxxxxxx xxxxx xxxxx xxxxx xxxxx 1xxxx"), # `{`
        neuron_inputs_all_match("xxxxx xxxxxxxxx xxxxx xxxxx xxxxx xxxxx x1xxx"), # `}`
    ]
    codepoint_patterns_layer = tf.nn.relu6(
        tf.add(tf.matmul(codepoint_layer, transpose(weights for weights, bias in pattern_neurons)), [bias for weights, bias in pattern_neurons])
    )

    return codepoint_patterns_layer

def transitions_recognizer(state, codepoint_patterns_layer, variables_layer, inner_container):
    transition_neurons = [
        # each entry in this list represents a neuron that fires if and only if a specific transition should be made

        # the first 35 bits of the inputs represent the "from" state of the transition:
        # START                          ARRAY_END                         DICT_END                          DICT_PAIR_VALUE                   LITERAL_F
        # LITERAL_FA                     LITERAL_FAL                       LITERAL_FALS                      LITERAL_N                         LITERAL_NU
        # LITERAL_NUL                    LITERAL_T                         LITERAL_TR                        LITERAL_TRU                       NUMBER_DECIMAL
        # NUMBER_E                       NUMBER_END                        NUMBER_E_SIGN                     NUMBER_EXPONENT                   NUMBER_EXPONENT_APPLY
        # NUMBER_MANTISSA_FRACTIONAL     NUMBER_MANTISSA_FRACTIONAL_STEP_1 NUMBER_MANTISSA_FRACTIONAL_STEP_2 NUMBER_MANTISSA_FRACTIONAL_STEP_3 NUMBER_MANTISSA_INTERIOR
        # NUMBER_MANTISSA_INTERIOR_START NUMBER_MANTISSA_ZERO              NUMBER_NEGATIVE                   STRING                            STRING_ESCAPE
        # STRING_ESCAPE_UNICODE_0        STRING_ESCAPE_UNICODE_1           STRING_ESCAPE_UNICODE_2           STRING_ESCAPE_UNICODE_3           STRING_ESCAPE_UNICODE_END

        # the next 31 bits represent the transition's pattern:
        # \+             ,         -            \.       0
        # :              [         [ \t\r\n]    [1-9]    [^"\\\x0000-\x001F\x007F\x0080-\x009F]
        # [eE]           "         \\           /        [0-9]
        # [0-9a-fA-F]    \x0000    ]            a        b
        # e              f         l            n        r
        # s              t         u            {        }

        # the next 8 bits represent the control variables:
        # negative    negative_exponent    add_exponents    item_present     parsing_key     comma_used     position_stay     accept

        # the next 2 bits represent the inner container:
        # (inner container is a list)    (inner container is a dict)
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xxxxx xx1xx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # START -> START: `[ \t\r\n]`
        neuron_inputs_all_match("00010 00000 00000 00000 00000 00000 00000    xxxxx xx1xx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # DICT_PAIR_VALUE -> DICT_PAIR_VALUE: `[ \t\r\n]`
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx x1xxx xxxxx xxxxx    xxxx0xxx    xx"), # START -> START: `\x0000` and not parsing_key
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xxxxx xxxxx x1xxx xxxxx xxxxx xxxxx    xxx0xxxx    xx"), # START -> STRING: `"` and not item_present
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00010 00000    xxxxx xxxx1 xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # STRING -> STRING: `[^"\x0000-\x001F\x007F\x0080-\x009F]`

        neuron_inputs_all_match("00000 00000 00000 00000 00000 00010 00000    xxxxx xxxxx xx1xx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # STRING -> STRING_ESCAPE: `\\`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00001 00000    xxxxx xxxxx x1xxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # STRING_ESCAPE -> STRING: `"`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00001 00000    xxxxx xxxxx xx1xx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # STRING_ESCAPE -> STRING: `\\`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00001 00000    xxxxx xxxxx xxx1x xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # STRING_ESCAPE -> STRING: `/`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00001 00000    xxxxx xxxxx xxxxx xxxx1 xxxxx xxxxx    xxxxxxxx    xx"), # STRING_ESCAPE -> STRING: `b`

        neuron_inputs_all_match("00000 00000 00000 00000 00000 00001 00000    xxxxx xxxxx xxxxx xxxxx x1xxx xxxxx    xxxxxxxx    xx"), # STRING_ESCAPE -> STRING: `f`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00001 00000    xxxxx xxxxx xxxxx xxxxx xxx1x xxxxx    xxxxxxxx    xx"), # STRING_ESCAPE -> STRING: `n`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00001 00000    xxxxx xxxxx xxxxx xxxxx xxxx1 xxxxx    xxxxxxxx    xx"), # STRING_ESCAPE -> STRING: `r`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00001 00000    xxxxx xxxxx xxxxx xxxxx xxxxx x1xxx    xxxxxxxx    xx"), # STRING_ESCAPE -> STRING: `t`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00001 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xx1xx    xxxxxxxx    xx"), # STRING_ESCAPE -> STRING_ESCAPE_UNICODE_0: `u`

        neuron_inputs_all_match("00000 00000 00000 00000 00000 00000 10000    xxxxx xxxxx xxxxx 1xxxx xxxxx xxxxx    xxxxxxxx    xx"), # STRING_ESCAPE_UNICODE_0 -> STRING_ESCAPE_UNICODE_1: `[0-9a-fA-F]`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00000 01000    xxxxx xxxxx xxxxx 1xxxx xxxxx xxxxx    xxxxxxxx    xx"), # STRING_ESCAPE_UNICODE_1 -> STRING_ESCAPE_UNICODE_2: `[0-9a-fA-F]`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00000 00100    xxxxx xxxxx xxxxx 1xxxx xxxxx xxxxx    xxxxxxxx    xx"), # STRING_ESCAPE_UNICODE_2 -> STRING_ESCAPE_UNICODE_3: `[0-9a-fA-F]`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00000 00010    xxxxx xxxxx xxxxx 1xxxx xxxxx xxxxx    xxxxxxxx    xx"), # STRING_ESCAPE_UNICODE_3 -> STRING_ESCAPE_UNICODE_END: `[0-9a-fA-F]`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00000 00001    xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # STRING_ESCAPE_UNICODE_END -> STRING: `.`

        neuron_inputs_all_match("00000 00000 00000 00000 00000 00010 00000    xxxxx xxxxx x1xxx xxxxx xxxxx xxxxx    xxxx0xxx    xx"), # STRING -> START: `"` and not parsing_key
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00010 00000    xxxxx xxxxx x1xxx xxxxx xxxxx xxxxx    xxxx1xxx    xx"), # STRING -> DICT_PAIR_VALUE: `"` and parsing_key
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xxxxx xxx1x xxxxx xxxxx xxxxx xxxxx    xxx00xxx    xx"), # START -> NUMBER_MANTISSA_INTERIOR_START: `[1-9]` and not item_present and not parsing_key
        neuron_inputs_all_match("00000 00000 00000 00000 00000 10000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_MANTISSA_INTERIOR_START -> NUMBER_MANTISSA_INTERIOR: `.`
        neuron_inputs_all_match("00000 00000 00000 00000 00001 00000 00000    xxxxx xxxxx xxxx1 xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_MANTISSA_INTERIOR -> NUMBER_MANTISSA_INTERIOR: `[0-9]`

        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xxxx1 xxxxx xxxxx xxxxx xxxxx xxxxx    xxx00xxx    xx"), # START -> NUMBER_MANTISSA_ZERO: `0` and not item_present and not parsing_key
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xx1xx xxxxx xxxxx xxxxx xxxxx xxxxx    xxx00xxx    xx"), # START -> NUMBER_NEGATIVE: `-` and not item_present and not parsing_key
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00100 00000    xxxxx xxx1x xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_NEGATIVE -> NUMBER_MANTISSA_INTERIOR: `[1-9]`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 00100 00000    xxxx1 xxxxx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_NEGATIVE -> NUMBER_MANTISSA_ZERO: `0`
        neuron_inputs_all_match("00000 00000 00000 00000 00001 00000 00000    xxx0x xxxxx 0xxx0 xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_MANTISSA_INTERIOR -> NUMBER_END: `[^0-9\.eE]`

        neuron_inputs_all_match("00000 00000 00000 00000 00000 01000 00000    xxx0x xxxxx 0xxx0 xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_MANTISSA_ZERO -> NUMBER_END: `[^0-9\.eE]`
        neuron_inputs_all_match("00000 00000 00000 01000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx    0xxxxxxx    xx"), # NUMBER_END -> START: `.` and not negative
        neuron_inputs_all_match("00000 00000 00000 01000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx    1xxxxxxx    xx"), # NUMBER_END -> START: `.` and negative
        neuron_inputs_all_match("00000 00000 00000 00000 00001 00000 00000    xxx1x xxxxx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_MANTISSA_INTERIOR -> NUMBER_DECIMAL: `\.`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 01000 00000    xxx1x xxxxx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_MANTISSA_ZERO -> NUMBER_DECIMAL: `\.`

        neuron_inputs_all_match("00000 00000 00001 00000 00000 00000 00000    xxxxx xxxxx xxxx1 xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_DECIMAL -> NUMBER_MANTISSA_FRACTIONAL_STEP_1: `[0-9]`
        neuron_inputs_all_match("00000 00000 00000 00000 01000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_MANTISSA_FRACTIONAL_STEP_1 -> NUMBER_MANTISSA_FRACTIONAL_STEP_2: `.`
        neuron_inputs_all_match("00000 00000 00000 00000 00100 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_MANTISSA_FRACTIONAL_STEP_2 -> NUMBER_MANTISSA_FRACTIONAL_STEP_3: `.`
        neuron_inputs_all_match("00000 00000 00000 00000 00010 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_MANTISSA_FRACTIONAL_STEP_3 -> NUMBER_MANTISSA_FRACTIONAL: `.`
        neuron_inputs_all_match("00000 00000 00000 00000 10000 00000 00000    xxxxx xxxxx xxxx1 xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_MANTISSA_FRACTIONAL -> NUMBER_MANTISSA_FRACTIONAL_STEP_1: `[0-9]`

        neuron_inputs_all_match("00000 00000 00000 00000 10000 00000 00000    xxxxx xxxxx 0xxx0 xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_MANTISSA_FRACTIONAL -> NUMBER_END: `[^0-9eE]`
        neuron_inputs_all_match("00000 00000 00000 00000 00001 00000 00000    xxxxx xxxxx 1xxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_MANTISSA_INTERIOR -> NUMBER_E: `[eE]`
        neuron_inputs_all_match("00000 00000 00000 00000 00000 01000 00000    xxxxx xxxxx 1xxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_MANTISSA_ZERO -> NUMBER_E: `[eE]`
        neuron_inputs_all_match("00000 00000 00000 00000 10000 00000 00000    xxxxx xxxxx 1xxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_MANTISSA_FRACTIONAL -> NUMBER_E: `[eE]`
        neuron_inputs_all_match("00000 00000 00000 10000 00000 00000 00000    1xxxx xxxxx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_E -> NUMBER_E_SIGN: `\+`

        neuron_inputs_all_match("00000 00000 00000 10000 00000 00000 00000    xx1xx xxxxx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_E -> NUMBER_E_SIGN: `-`
        neuron_inputs_all_match("00000 00000 00000 10000 00000 00000 00000    xxxxx xxxxx xxxx1 xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_E -> NUMBER_EXPONENT: `[0-9]`
        neuron_inputs_all_match("00000 00000 00000 00100 00000 00000 00000    xxxxx xxxxx xxxx1 xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_E_SIGN -> NUMBER_EXPONENT: `[0-9]`
        neuron_inputs_all_match("00000 00000 00000 00010 00000 00000 00000    xxxxx xxxxx xxxx1 xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # NUMBER_EXPONENT -> NUMBER_EXPONENT: `[0-9]`
        neuron_inputs_all_match("00000 00000 00000 00010 00000 00000 00000    xxxxx xxxxx xxxx0 xxxxx xxxxx xxxxx    x0xxxxxx    xx"), # NUMBER_EXPONENT -> NUMBER_EXPONENT_APPLY: `[^0-9]` and not negative_exponent

        neuron_inputs_all_match("00000 00000 00000 00010 00000 00000 00000    xxxxx xxxxx xxxx0 xxxxx xxxxx xxxxx    x1xxxxxx    xx"), # NUMBER_EXPONENT -> NUMBER_EXPONENT_APPLY: `[^0-9]` and negative_exponent
        neuron_inputs_all_match("00000 00000 00000 00001 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx    xx1xxxxx    xx"), # NUMBER_EXPONENT_APPLY -> NUMBER_EXPONENT_APPLY: `.` and add_exponents
        neuron_inputs_all_match("00000 00000 00000 00001 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx    xx0xxxxx    xx"), # NUMBER_EXPONENT_APPLY -> NUMBER_END: `.` and not add_exponents
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx x1xxx    xxx00xxx    xx"), # START -> LITERAL_T: `t` and not item_present and not parsing_key
        neuron_inputs_all_match("00000 00000 01000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxx1 xxxxx    xxxxxxxx    xx"), # LITERAL_T -> LITERAL_TR: `r`

        neuron_inputs_all_match("00000 00000 00100 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xx1xx    xxxxxxxx    xx"), # LITERAL_TR -> LITERAL_TRU: `u`
        neuron_inputs_all_match("00000 00000 00010 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx 1xxxx xxxxx    xxxxxxxx    xx"), # LITERAL_TRU -> START: `e`
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx x1xxx xxxxx    xxx00xxx    xx"), # START -> LITERAL_F: `f` and not item_present and not parsing_key
        neuron_inputs_all_match("00001 00000 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxx1x xxxxx xxxxx    xxxxxxxx    xx"), # LITERAL_F -> LITERAL_FA: `a`
        neuron_inputs_all_match("00000 10000 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xx1xx xxxxx    xxxxxxxx    xx"), # LITERAL_FA -> LITERAL_FAL: `l`

        neuron_inputs_all_match("00000 01000 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx 1xxxx    xxxxxxxx    xx"), # LITERAL_FAL -> LITERAL_FALS: `s`
        neuron_inputs_all_match("00000 00100 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx 1xxxx xxxxx    xxxxxxxx    xx"), # LITERAL_FALS -> START: `e`
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxx1x xxxxx    xxx00xxx    xx"), # START -> LITERAL_N: `n` and not item_present and not parsing_key
        neuron_inputs_all_match("00000 00010 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xx1xx    xxxxxxxx    xx"), # LITERAL_N -> LITERAL_NU: `u`
        neuron_inputs_all_match("00000 00001 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # LITERAL_NU -> LITERAL_NUL: `l`

        neuron_inputs_all_match("00000 00000 10000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xx1xx xxxxx    xxxxxxxx    xx"), # LITERAL_NUL -> START: `l`
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xxxxx x1xxx xxxxx xxxxx xxxxx xxxxx    xxx00xxx    xx"), # START -> START: `\[` and not item_present and not parsing_key
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    x1xxx xxxxx xxxxx xxxxx xxxxx xxxxx    xxx1xxxx    1x"), # START -> START: `,` and inner container is list and item_present
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xx1xx xxxxx xxxxx    xxx0x0xx    1x"), # START -> ARRAY_END: `\]` and inner container is list and not item_present and not comma_used
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xx1xx xxxxx xxxxx    xxx1xxxx    1x"), # START -> ARRAY_END: `\]` and inner container is list and item_present

        neuron_inputs_all_match("01000 00000 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # ARRAY_END -> START: `.`
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xxx1x    xxx00xxx    xx"), # START -> START: `\{` and not item_present and not parsing_key
        neuron_inputs_all_match("00010 00000 00000 00000 00000 00000 00000    xxxxx 1xxxx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # DICT_PAIR_VALUE -> START: `:`
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    x1xxx xxxxx xxxxx xxxxx xxxxx xxxxx    xxx10xxx    x1"), # START -> START: `,` and inner container is dict and item_present and not parsing_key
        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xxxx1    xxx0x0xx    x1"), # START -> DICT_END: `\}` and inner container is dict and not item_present and not comma_used

        neuron_inputs_all_match("10000 00000 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xxxx1    xxx10xxx    x1"), # START -> DICT_END: `\}` and inner container is dict and item_present and not parsing_key
        neuron_inputs_all_match("00100 00000 00000 00000 00000 00000 00000    xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx    xxxxxxxx    xx"), # DICT_END -> START: `.`
    ]
    transition_layer_inputs = tf.concat([
        state,
        codepoint_patterns_layer,
        variables_layer,
        inner_container,
    ], 1)
    transitions_layer = tf.nn.relu6(
        tf.add(tf.matmul(transition_layer_inputs, transpose(weights for weights, bias in transition_neurons)), [bias for weights, bias in transition_neurons])
    )

    return transitions_layer

def operation_and_state_recognizer(transitions_layer):
    operation_and_state_neurons = [
        # each entry in this list represents a neuron, associated with a stack operation, that fires if and only if that operation should be performed at this step
        # this can be generated automatically using the `generate_operation_neurons.py` script
        neuron_inputs_any_match("111xx 1xxxx xxxxx xxxxx 11xxx xxx11 11xxx xxxxx xxxx1 1xxx1 xxx11 1x111 1x111 xxx1x xx1x1 xx"), # OP_NOP
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx x1x1x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # OP_SWAP
        neuron_inputs_any_match("xxx1x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # OP_PUSH_STRING
        neuron_inputs_any_match("xxxx1 x1111 1111x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # OP_APPEND_CHAR
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxx1 xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # OP_APPEND_CHAR_CODE
        neuron_inputs_any_match("xxxxx xxxxx xxxx1 xxxxx xx1xx 11xxx xxx11 xxxxx x111x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # OP_PUSH_NUMBER
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx x1xxx xxxxx xxxxx xxxxx xxxxx xx"), # OP_ADD
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx1xx xxxxx xxxxx xxxxx 1xxxx xxxxx xxxxx xxxxx xxxxx xx"), # OP_INVERT
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx 1xxx1 xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # OP_DECREMENT
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxx11 xx1xx xxxxx xx1xx xxxxx x111x xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # OP_SHIFT_DEC
        neuron_inputs_any_match("xxxxx xxxxx xxxxx 1111x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # OP_SHIFT_HEX
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx 1xxxx xxxxx xx1xx xxxxx xxxxx xxxxx xxxxx xx"), # OP_EXPONENTIATE_NUMBERS
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx x1xxx xx"), # OP_PUSH_DICT
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxx1x 1x"), # OP_APPEND_PAIR_TO_DICT
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx x1"), # OP_COMPLETE_DICT
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx x1xxx xxxxx xx"), # OP_PUSH_LIST
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx1x1 xxxxx xx"), # OP_APPEND_VALUE_TO_LIST
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx 1xxxx xx"), # OP_COMPLETE_LIST
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx x1xxx xxxxx xxxxx xxxxx xx"), # OP_PUSH_TRUE
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx x1xxx xxxxx xxxxx xx"), # OP_PUSH_FALSE
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx 1xxxx xxxxx xx"), # OP_PUSH_NONE

        # each entry in this list represents a neuron, associated with a state, that fires if and only if that state should be the next one
        # this can be generated automatically using the `generate_state_neurons.py` script
        neuron_inputs_any_match("1x1xx xxxxx xxxxx xxxxx 1xxxx xxxxx x11xx xxxxx xxxxx xxxxx xxxxx x1xxx x1xxx 111xx 1111x x1"), # START
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxx11 xxxxx xx"), # ARRAY_END
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxx1 1x"), # DICT_END
        neuron_inputs_any_match("x1xxx xxxxx xxxxx xxxxx x1xxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # DICT_PAIR_VALUE
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx1xx xxxxx xxxxx xxxxx xx"), # LITERAL_F
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxx1x xxxxx xxxxx xxxxx xx"), # LITERAL_FA
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxx1 xxxxx xxxxx xxxxx xx"), # LITERAL_FAL
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx 1xxxx xxxxx xxxxx xx"), # LITERAL_FALS
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx1xx xxxxx xxxxx xx"), # LITERAL_N
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxx1x xxxxx xxxxx xx"), # LITERAL_NU
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxx1 xxxxx xxxxx xx"), # LITERAL_NUL
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxx1x xxxxx xxxxx xxxxx xxxxx xx"), # LITERAL_T
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxx1 xxxxx xxxxx xxxxx xxxxx xx"), # LITERAL_TR
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx 1xxxx xxxxx xxxxx xxxxx xx"), # LITERAL_TRU
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxx11 xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # NUMBER_DECIMAL
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx x111x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # NUMBER_E
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxx1 1xxxx xxxxx 1xxxx xxxxx xx1xx xxxxx xxxxx xxxxx xxxxx xx"), # NUMBER_END
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxx1 1xxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # NUMBER_E_SIGN
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx x111x xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # NUMBER_EXPONENT
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxx1 11xxx xxxxx xxxxx xxxxx xxxxx xx"), # NUMBER_EXPONENT_APPLY
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxx1x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # NUMBER_MANTISSA_FRACTIONAL
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx 1xxx1 xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # NUMBER_MANTISSA_FRACTIONAL_STEP_1
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx x1xxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # NUMBER_MANTISSA_FRACTIONAL_STEP_2
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx1xx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # NUMBER_MANTISSA_FRACTIONAL_STEP_3
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxx11 xx1xx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # NUMBER_MANTISSA_INTERIOR
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xx1xx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # NUMBER_MANTISSA_INTERIOR_START
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx 1xx1x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # NUMBER_MANTISSA_ZERO
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx x1xxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # NUMBER_NEGATIVE
        neuron_inputs_any_match("xxx11 x1111 1111x xxxx1 xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # STRING
        neuron_inputs_any_match("xxxxx 1xxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # STRING_ESCAPE
        neuron_inputs_any_match("xxxxx xxxxx xxxx1 xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # STRING_ESCAPE_UNICODE_0
        neuron_inputs_any_match("xxxxx xxxxx xxxxx 1xxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # STRING_ESCAPE_UNICODE_1
        neuron_inputs_any_match("xxxxx xxxxx xxxxx x1xxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # STRING_ESCAPE_UNICODE_2
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xx1xx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # STRING_ESCAPE_UNICODE_3
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxx1x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx"), # STRING_ESCAPE_UNICODE_END
    ]
    operation_and_state_layer = tf.nn.relu6(
        tf.add(tf.matmul(transitions_layer, transpose(weights for weights, bias in operation_and_state_neurons)), [bias for weights, bias in operation_and_state_neurons])
    )

    return operation_and_state_layer

def operand_patterns_recognizer(transitions_layer, input_codepoint):
    # layer inputs: current state machine transition, current input character
    # layer outputs: values of most significant 25 bits of the operand, whether the input bit was (originally false or should be set to false) for the least significant 7 bits
    operand_intermediate_neurons = [
        # whenever the operation doesn't have an operand, like `OP_SWAP`, we don't care what the operand output value is
        # whenever the operation has an operand, it's actually usually just the codepoint, except the character escape transitions - it needs to convert, for example, the `t` in `\t` into an actual tab character
        # to do this, we can use the same pattern we used for the control variable neurons - two layers implement an SR latch, where the initial value of the latch is taken from the codepoint, and S and R are taken from the transition
        # we already know that whenever these character escape transitions are used, the upper 25 bits are always 0, because the highest codepoint, `\`, uses only the least significant 7 bits, so those upper 25 bits just get set to 0 whenever those transitions are used
        # for the remaining least significant 7 bits, the S and R values for transitions can simply be read off from the binary values of each escape character:
        # * `\"` becomes `010 0010` (forming the column `00000000000000000000000001x111x1`)
        # * `\\` becomes `101 1100` (forming the column `0000000000000000000000000x1xxx11`)
        # * `\/` becomes `010 1111` (forming the column `00000000000000000000000001x1xxxx`)
        # * `\b` becomes `000 1000` (forming the column `0000000000000000000000000111x111`)
        # * `\f` becomes `000 1100` (forming the column `0000000000000000000000000111xx11`)
        # * `\n` becomes `000 1010` (forming the column `0000000000000000000000000111x1x1`)
        # * `\r` becomes `000 1101` (forming the column `0000000000000000000000000111xx1x`)
        # * `\t` becomes `000 1001` (forming the column `0000000000000000000000000111x11x`)
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    1xxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    x1xx xxxx xxxx xxxx xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xx1x xxxx xxxx xxxx xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxx1 xxxx xxxx xxxx xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx 1xxx xxxx xxxx xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx x1xx xxxx xxxx xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xx1x xxxx xxxx xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxx1 xxxx xxxx xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx 1xxx xxxx xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx x1xx xxxx xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xx1x xxxx xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxx1 xxxx xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx 1xxx xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx x1xx xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xx1x xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxx1 xxxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx 1xxx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx x1xx xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx xx1x xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx xxx1 xxxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx xxxx 1xxx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx xxxx x1xx xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx xxxx xx1x xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx xxxx xxx1 xxxx xxxx"),
        neuron_inputs_all_match("xxxxx x0000 0000x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx xxxx xxxx 1xxx xxxx"),
        neuron_inputs_any_match("xxxxx x1x11 1111x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx xxxx xxxx x0xx xxxx"), # bit 7 is tenatively false
        neuron_inputs_any_match("xxxxx xx1x1 1111x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx xxxx xxxx xx0x xxxx"), # bit 6 is tenatively false
        neuron_inputs_any_match("xxxxx x1x11 1111x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx xxxx xxxx xxx0 xxxx"), # bit 5 is tenatively false
        neuron_inputs_any_match("xxxxx x1xxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx xxxx xxxx xxxx 0xxx"), # bit 4 is tenatively false
        neuron_inputs_any_match("xxxxx x1xx1 x1x1x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx xxxx xxxx xxxx x0xx"), # bit 3 is tenatively false
        neuron_inputs_any_match("xxxxx xx1x1 1x11x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xx0x"), # bit 2 is tenatively false
        neuron_inputs_any_match("xxxxx x11x1 11xxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxx0"), # bit 1 is tenatively false
    ]
    operand_intermediate_layer_inputs = tf.concat([transitions_layer, input_codepoint], 1)
    operand_intermediate_layer = tf.nn.relu6(
        tf.add(tf.matmul(operand_intermediate_layer_inputs, transpose(weights for weights, bias in operand_intermediate_neurons)), [bias for weights, bias in operand_intermediate_neurons])
    )

    # layer inputs: transition, values of most significant 25 bits of the operand, whether the input bit was (originally false or should be set to false) for the least significant 7 bits
    # layer outputs: operand (all 32 bits of it)
    operand_neurons = [
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    1xxxxxxxxxxxxxxxxxxxxxxxx xxxxxxx"), # bit 32
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    x1xxxxxxxxxxxxxxxxxxxxxxx xxxxxxx"), # bit 31
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xx1xxxxxxxxxxxxxxxxxxxxxx xxxxxxx"), # bit 30
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxx1xxxxxxxxxxxxxxxxxxxxx xxxxxxx"), # bit 29
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxx1xxxxxxxxxxxxxxxxxxxx xxxxxxx"), # bit 28
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxx1xxxxxxxxxxxxxxxxxxx xxxxxxx"), # bit 27
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxx1xxxxxxxxxxxxxxxxxx xxxxxxx"), # bit 26
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxx1xxxxxxxxxxxxxxxxx xxxxxxx"), # bit 25
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxx1xxxxxxxxxxxxxxxx xxxxxxx"), # bit 24
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxx1xxxxxxxxxxxxxxx xxxxxxx"), # bit 23
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxx1xxxxxxxxxxxxxx xxxxxxx"), # bit 22
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxx1xxxxxxxxxxxxx xxxxxxx"), # bit 21
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxx1xxxxxxxxxxxx xxxxxxx"), # bit 20
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxx1xxxxxxxxxxx xxxxxxx"), # bit 19
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxx1xxxxxxxxxx xxxxxxx"), # bit 18
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxx1xxxxxxxxx xxxxxxx"), # bit 17
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxx1xxxxxxxx xxxxxxx"), # bit 16
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxx1xxxxxxx xxxxxxx"), # bit 15
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxxx1xxxxxx xxxxxxx"), # bit 14
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxxxx1xxxxx xxxxxxx"), # bit 13
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxxxxx1xxxx xxxxxxx"), # bit 12
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxxxxxx1xxx xxxxxxx"), # bit 11
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxxxxxxx1xx xxxxxxx"), # bit 10
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxxxxxxxx1x xxxxxxx"), # bit 9
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxxxxxxxxx1 xxxxxxx"), # bit 8
        neuron_inputs_any_match("xxxxx xx1xx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxxxxxxxxxx 0xxxxxx"), # bit 7
        neuron_inputs_any_match("xxxxx x1x1x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxxxxxxxxxx x0xxxxx"), # bit 6
        neuron_inputs_any_match("xxxxx xx1xx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxxxxxxxxxx xx0xxxx"), # bit 5
        neuron_inputs_any_match("xxxxx xx111 1111x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxxxxxxxxxx xxx0xxx"), # bit 4
        neuron_inputs_any_match("xxxxx xx11x 1x1xx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxxxxxxxxxx xxxx0xx"), # bit 3
        neuron_inputs_any_match("xxxxx x1x1x x1xxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxxxxxxxxxx xxxxx0x"), # bit 2
        neuron_inputs_any_match("xxxxx xxx1x xx11x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxxxxxxxxxxxxxxxxxxxx xxxxxx0"), # bit 1
    ]
    operand_layer_inputs = tf.concat([transitions_layer, operand_intermediate_layer], 1)
    operand_patterns_layer = tf.nn.relu6(
        tf.add(tf.matmul(operand_layer_inputs, transpose(weights for weights, bias in operand_neurons)), [bias for weights, bias in operand_neurons])
    )

    return operand_patterns_layer

def variables_recognizer(transitions_layer, variables):
    # layer inputs: current state machine transition, previous value of recurrent control variables
    # layer outputs: whether recurrent control variables are (originally false or explicitly set to false), values of non-recurrent control variables
    variable_intermediate_neurons = [
        # each variable's value can have three possibilities here: SET (variable's new value is true), RESET (variable's new value is false), and HOLD (variable's new value is old value)
        # we can represent this as VARIABLE(t + 1) = SET or (VARIABLE(t) and not RESET)
        # clearly, SET = S_1 or ... or S_n, where S_i is the i-th input that can set the neuron to true
        # clearly, RESET = R_1 or ... or R_n, where R_i is the i-th input that can set the neuron to false
        # therefore, VARIABLE(t + 1) = S_1 or ... or S_n or (VARIABLE(t) and not (R_1 or ... or R_n))
        # the above expression has 3 levels of gates (i.e., neuron layers); by applying DeMorgan's law we can get it down to 2: `VARIABLE(t + 1) = S_1 or ... or S_n or not (R_1 or ... or R_n or not VARIABLE(t))`
        # now we split this into two layers: `VARIABLE_INTERMEDIATE(t + 1) = R_1 or ... or R_n or not VARIABLE(t)` and `VARIABLE(t + 1) = S_1 or ... or S_n or not VARIABLE_INTERMEDIATE(t + 1)`
        # each entry in this list represents a neuron that activates if and only if `VARIABLE_INTERMEDIATE(t + 1)`
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxx1x 1xxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    0xxxxxxx"), # negative is tentatively false
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxx1 x1xxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    x0xxxxxx"), # negative_exponent is tentatively false
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx x11xx xxxxx x1xxx xxxxx xxxxx xxxxx xxxxx xx    xx0xxxxx"), # add_exponents is tentatively false
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx x11xx x111x xx    xxx0xxxx"), # item_present is tentatively false
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx1xx x1    xxxx0xxx"), # parsing_key is tentatively false
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx x1xxx 11xxx x1    xxxxx0xx"), # comma_used is tentatively false

        # for the variables `position_stay` and `accept`, which are always 0 unless a transition is currently setting them to 1,
        # we instead set the inputs such that every input that doesn't set the neuron to true to set it to false
        # (i.e., reverse the corresponding transition inputs for `position_stay` and `accept` from `variable_neurons`)
        neuron_inputs_any_match("11111 11111 11111 111x1 11x11 1111x xxx11 xxx1x x1111 1111x xxx11 11111 11111 111xx 1111x x1    xxxxxx0x"), # position_stay is tentatively false
        neuron_inputs_any_match("11x11 11111 11111 11111 11111 11111 11111 11111 11111 11111 11111 11111 11111 11111 11111 11    xxxxxxx0"), # accept is tentatively false
    ]
    variable_intermediate_layer_inputs = tf.concat([
        transitions_layer,
        variables,
    ], 1)
    variable_intermediate_layer = tf.nn.relu6(
        tf.add(tf.matmul(variable_intermediate_layer_inputs, transpose(weights for weights, bias in variable_intermediate_neurons)), [bias for weights, bias in variable_intermediate_neurons])
    )

    # layer inputs: current state machine transition, whether recurrent control variables are (originally false or explicitly set to false), values of non-recurrent control variables
    # layer outputs: values of control variables (recurrent and non-recurrent)
    variable_neurons = [
        # we can now implement the rest of the `VALUE(t + 1) = S_1 or ... or S_n or not (R_1 or ... or R_n or not VALUE(t))` formula, given that the previous layer computed `R_1 or ... or R_n or not VALUE(t)` already
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx x1xxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    0xxxxxxx"), # negative
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx 1xxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    x0xxxxxx"), # negative_exponent
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxx1x xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xx0xxxxx"), # add_exponents
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx 1xxxx xxxxx x11xx xxxxx xxxxx xxxxx xxxxx x1xxx x1xxx 1xxxx 1xxxx x1    xxx0xxxx"), # item_present
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx x1x1x xx    xxxx0xxx"), # parsing_key
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx1xx xxx1x xx    xxxxx0xx"), # comma_used
        neuron_inputs_any_match("xxxxx xxxxx xxxxx xxx1x xx1xx xxxx1 111xx 111x1 1xxxx xxxx1 111xx xxxxx xxxxx xxx11 xxxx1 1x    xxxxxx0x"), # position_stay
        neuron_inputs_any_match("xx1xx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xx    xxxxxxx0"), # accept
    ]
    variable_layer_inputs = tf.concat([transitions_layer, variable_intermediate_layer], 1)
    variables_layer = tf.nn.relu6(
        tf.add(tf.matmul(variable_layer_inputs, transpose(weights for weights, bias in variable_neurons)), [bias for weights, bias in variable_neurons])
    )

    return variables_layer

# layer inputs: (user supplied)
# layer outputs: current input character
input_layer = tf.placeholder(tf.int32, shape=[1, 32], name="character")

# layer inputs: (user supplied)
# layer outputs: inner container type
inner_container = tf.placeholder(tf.int32, shape=[1, 2], name="inner_container")

# layer inputs: (user supplied)
# layer outputs: current state machine state
state = tf.Variable(tf.constant([[
    1, # START
    0, # ARRAY_END
    0, # DICT_END
    0, # DICT_PAIR_VALUE
    0, # LITERAL_F
    0, # LITERAL_FA
    0, # LITERAL_FAL
    0, # LITERAL_FALS
    0, # LITERAL_N
    0, # LITERAL_NU
    0, # LITERAL_NUL
    0, # LITERAL_T
    0, # LITERAL_TR
    0, # LITERAL_TRU
    0, # NUMBER_DECIMAL
    0, # NUMBER_E
    0, # NUMBER_END
    0, # NUMBER_E_SIGN
    0, # NUMBER_EXPONENT
    0, # NUMBER_EXPONENT_APPLY
    0, # NUMBER_MANTISSA_FRACTIONAL
    0, # NUMBER_MANTISSA_FRACTIONAL_STEP_1
    0, # NUMBER_MANTISSA_FRACTIONAL_STEP_2
    0, # NUMBER_MANTISSA_FRACTIONAL_STEP_3
    0, # NUMBER_MANTISSA_INTERIOR
    0, # NUMBER_MANTISSA_INTERIOR_START
    0, # NUMBER_MANTISSA_ZERO
    0, # NUMBER_NEGATIVE
    0, # STRING
    0, # STRING_ESCAPE
    0, # STRING_ESCAPE_UNICODE_0
    0, # STRING_ESCAPE_UNICODE_1
    0, # STRING_ESCAPE_UNICODE_2
    0, # STRING_ESCAPE_UNICODE_3
    0, # STRING_ESCAPE_UNICODE_END
]]), name="state")

# layer inputs: (user supplied)
# layer outputs: control variables
variables = tf.Variable(tf.constant([[
    0, # negative
    0, # negative_exponent
    0, # add_exponents
    0, # item_present
    0, # parsing_key
    0, # comma_used
    0, # position_stay
    0, # accept
]]), name="variables")

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

def is_complete(value):
    if isinstance(value, list):
        return len(value) == 0 or value[0] != ()
    if isinstance(value, dict):
        return () not in value
    return True

def get_inner_container_type(stack):
    for entry in reversed(stack):
        if isinstance(entry, list) and len(entry) >= 1 and entry[0] == ():
            return (1, 0)
        if isinstance(entry, dict) and () in entry:
            return (0, 1)
    return (0, 0)

def OP_NOP(stack, K):
    pass
def OP_SWAP(stack, K):
    assert len(stack) >= 2
    stack[-1], stack[-2] = stack[-2], stack[-1]
def OP_PUSH_STRING(stack, K):
    stack.append("")
def OP_APPEND_CHAR(stack, K):
    stack[-1] += K
def OP_APPEND_CHAR_CODE(stack, K):
    assert len(stack) >= 2
    code = stack.pop()
    assert 0 <= code <= 0xFFFFFFFF
    stack[-1] += chr(code)
def OP_PUSH_NUMBER(stack, K):
    stack.append(0)
def OP_ADD(stack, K):
    assert len(stack) >= 2
    addend = stack.pop()
    stack[-1] += addend
def OP_INVERT(stack, K):
    stack[-1] = -stack[-1]
def OP_DECREMENT(stack, K):
    stack[-1] -= 1
def OP_SHIFT_DEC(stack, K):
    stack[-1] = stack[-1] * 10 + int(K)
def OP_SHIFT_HEX(stack, K):
    stack[-1] = stack[-1] * 16 + int(K, 16)
def OP_EXPONENTIATE_NUMBERS(stack, K):
    assert len(stack) >= 2
    exponent = stack.pop()
    try: # improve numerical precision by using integer exponents when possible
        stack[-1] = float(stack[-1] * 10 ** exponent) if exponent > 0 else float(stack[-1] / 10 ** -exponent)
    except OverflowError as e:
        if exponent < 0: # tiny exponent, round to 0
            stack[-1] = 0.0
        elif stack[-1] > 0: # factor is positive, we have a positive result
            stack[-1] = float("inf")
        elif stack[-1] < 0: # factor is negative, we have a negative result
            stack[-1] = float("-inf")
        else: # factor is zero, so is the result
            stack[-1] = 0.0
def OP_PUSH_DICT(stack, K):
    stack.append({(): None})
def OP_APPEND_PAIR_TO_DICT(stack, K):
    value = stack.pop()
    key = stack.pop()
    assert is_complete(value)
    stack[-1][key] = value
def OP_COMPLETE_DICT(stack, K):
    del stack[-1][()]
def OP_PUSH_LIST(stack, K):
    stack.append([()])
def OP_APPEND_VALUE_TO_LIST(stack, K):
    item = stack.pop()
    assert is_complete(item)
    stack[-1].append(item)
def OP_COMPLETE_LIST(stack, K):
    del stack[-1][0]
def OP_PUSH_TRUE(stack, K):
    stack.append(True)
def OP_PUSH_FALSE(stack, K):
    stack.append(False)
def OP_PUSH_NONE(stack, K):
    stack.append(None)

class JsonNN:
    OPERATIONS = [
        OP_NOP,         OP_SWAP,                 OP_PUSH_STRING,   OP_APPEND_CHAR,         OP_APPEND_CHAR_CODE,
        OP_PUSH_NUMBER, OP_ADD,                  OP_INVERT,        OP_DECREMENT,           OP_SHIFT_DEC,
        OP_SHIFT_HEX,   OP_EXPONENTIATE_NUMBERS, OP_PUSH_DICT,     OP_APPEND_PAIR_TO_DICT, OP_COMPLETE_DICT,
        OP_PUSH_LIST,   OP_APPEND_VALUE_TO_LIST, OP_COMPLETE_LIST, OP_PUSH_TRUE,           OP_PUSH_FALSE,
        OP_PUSH_NONE,
    ]

    def parse(self, value):
        value += "\x00" # append a null character to represent the end of input
        self.stack = []
        position = 0

        with tf.Session() as session:
            session.run(tf.global_variables_initializer()) # initialize all variables
            while position < len(value):
                # convert the character to an array of binary digits representing the codepoint
                binary_char = [6 if digit == "1" else 0 for digit in "{0:>032b}".format(ord(value[position]))]

                operation_value, state_value, operand_value, variable_value = session.run([operation_layer, updated_state, operand_patterns_layer, updated_variables], feed_dict={
                    input_layer: np.array([binary_char]),
                    inner_container: np.array([get_inner_container_type(self.stack)])
                })

                # interpret the output of the neural network
                assert sum(operation_value[0]) == 6 and max(operation_value[0]) == 6, operation_value
                assert sum(state_value[0]) == 6 and max(state_value[0]) == 6, state_value
                operation_index = next(i for i, value in enumerate(operation_value[0]) if value > 0)
                operand = chr(sum(1 << (31 - i) if value > 0 else 0 for i, value in enumerate(operand_value[0])))
                position_stay, accept = variable_value[0][-2:]

                self.OPERATIONS[operation_index](self.stack, operand)

                # move ahead in the input if necessary
                if not position_stay:
                    position += 1

        assert accept
        assert len(self.stack) == 1
        assert is_complete(self.stack[0])
        return self.stack[0]

if __name__ == "__main__":
    parser = JsonNN()
    print(parser.parse('{"a\u0020b c": [123, -32.10e64]}'))
    #with open("sample.json", "r") as f: value = f.read()
    #import json; print(parser.parse(value) == json.loads(value))
