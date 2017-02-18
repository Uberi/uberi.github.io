import re

"""
JSON parser, implemented with an FSM and a stack machine. I really hope you're not using this in production...

Usage:

    >>> parser = JsonFSM()
    >>> parser.parse('"hello\\nworld!"')
    "hello\nworld!"
    >>> parser.parse('1234567.5e5')
    123456750000.0
    >>> parser.parse('0.5e5000')
    inf
    >>> parser.parse('true')
    True
    >>> parser.parse('false')
    False
    >>> parser.parse('null')
    None
    >>> parser.parse('["abc",123]')
    ["abc", 123]
    >>> parser.parse('[]')
    []
    >>> parser.parse('{"a":1,"b":2}')
    {"a": 1, "b": 2}
    >>> parser.parse('{"a":{}}')
    {"a": {}}
"""

class JsonFSM:
    def reset(self):
        self.stack = []
        self.negative = 0
        self.negative_exponent = 0
        self.add_exponents = 0
        self.item_present = 0
        self.parsing_key = 0
        self.comma_used = 0
        self.position_stay = 0
        self.accept = 0

    def parse(self, value):
        value += "\x00"
        self.reset()
        current_state = "START"
        position = 0
        while position < len(value):
            previous_state = current_state
            current_state = self.step(current_state, value[position])
            #print("{} -{}-> {} (inner {});        negative={}, negative_exponent={}, add_exponents={}, item_present={}, parsing_key={}, comma_used={}        {}".format(previous_state, repr(value[position]), current_state, self.get_inner_container(), self.negative, self.negative_exponent, self.add_exponents, self.item_present, self.parsing_key, self.comma_used, self.stack))
            assert current_state is not None
            if not self.position_stay:
                position += 1
        assert self.accept
        assert len(self.stack) == 1
        assert self.is_complete(self.stack[0])
        return self.stack[0]

    def get_inner_container(self):
        # find the topmost incomplete container on the stack
        for entry in reversed(self.stack):
            if isinstance(entry, list) and len(entry) > 0 and entry[0] == ():
                return "list"
            elif isinstance(entry, dict) and () in entry:
                return "dict"
        return "none"

    def step(self, current_state, c):
        self.position_stay = 0
        self.accept = 0

        inner_container = self.get_inner_container()

        # ignore whitespace between tokens
        if current_state == "START" and re.match(r"[ \t\r\n]", c):
            self.OP_NOP()
            return "START"
        if current_state == "DICT_PAIR_VALUE" and re.match(r"[ \t\r\n]", c):
            self.OP_NOP()
            return "DICT_PAIR_VALUE"

        # end of input scanning
        if current_state == "START" and c == "\x00":
            self.OP_NOP()
            self.accept = 1
            return "START"

        # string scanning
        if current_state == "START" and c == "\"" and not self.item_present:
            self.OP_PUSH_STRING()
            return "STRING"
        if current_state == "STRING" and c not in {"\"", "\\"} and ord(c) > 0x001F and not (0x007F <= ord(c) <= 0x009F):
            self.OP_APPEND_CHAR_K(c)
            return "STRING"
        if current_state == "STRING" and c == "\\":
            self.OP_NOP()
            return "STRING_ESCAPE"
        if current_state == "STRING_ESCAPE" and re.match(r"[\"\\/bfnrt]", c):
            self.OP_APPEND_CHAR_K({"\"": "\"", "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}[c])
            return "STRING"
        if current_state == "STRING_ESCAPE" and c == "u":
            self.OP_PUSH_NUMBER()
            return "STRING_ESCAPE_UNICODE_0"
        if current_state == "STRING_ESCAPE_UNICODE_0" and re.match(r"[a-fA-F0-9]", c):
            self.OP_SHIFT_HEX(c)
            return "STRING_ESCAPE_UNICODE_1"
        if current_state == "STRING_ESCAPE_UNICODE_1" and re.match(r"[a-fA-F0-9]", c):
            self.OP_SHIFT_HEX(c)
            return "STRING_ESCAPE_UNICODE_2"
        if current_state == "STRING_ESCAPE_UNICODE_2" and re.match(r"[a-fA-F0-9]", c):
            self.OP_SHIFT_HEX(c)
            return "STRING_ESCAPE_UNICODE_3"
        if current_state == "STRING_ESCAPE_UNICODE_3" and re.match(r"[a-fA-F0-9]", c):
            self.OP_SHIFT_HEX(c)
            self.position_stay = 1
            return "STRING_ESCAPE_UNICODE_END"
        if current_state == "STRING_ESCAPE_UNICODE_END":
            self.OP_APPEND_CHAR_CODE()
            return "STRING"
        if current_state == "STRING" and c == "\"" and not self.parsing_key:
            self.OP_NOP()
            self.item_present = 1
            return "START"
        if current_state == "STRING" and c == "\"" and self.parsing_key:
            self.OP_NOP()
            return "DICT_PAIR_VALUE"

        # number mantissa scanning
        if current_state == "START" and re.match(r"[1-9]", c) and not self.item_present and not self.parsing_key:
            self.OP_PUSH_NUMBER()
            self.position_stay = 1
            return "NUMBER_MANTISSA_INTERIOR_START"
        if current_state == "NUMBER_MANTISSA_INTERIOR_START":
            self.OP_SHIFT_DEC(c)
            self.negative = 0
            return "NUMBER_MANTISSA_INTERIOR"
        if current_state == "NUMBER_MANTISSA_INTERIOR" and re.match(r"[0-9]", c):
            self.OP_SHIFT_DEC(c)
            return "NUMBER_MANTISSA_INTERIOR"
        if current_state == "START" and c == "0" and not self.item_present and not self.parsing_key:
            self.OP_PUSH_NUMBER()
            self.negative = 0
            return "NUMBER_MANTISSA_ZERO"
        if current_state == "START" and c == "-" and not self.item_present and not self.parsing_key:
            self.OP_PUSH_NUMBER()
            self.negative = 1
            return "NUMBER_NEGATIVE"
        if current_state == "NUMBER_NEGATIVE" and re.match(r"[1-9]", c):
            self.OP_SHIFT_DEC(c)
            return "NUMBER_MANTISSA_INTERIOR"
        if current_state == "NUMBER_NEGATIVE" and c == "0":
            self.OP_NOP()
            return "NUMBER_MANTISSA_ZERO"
        if current_state == "NUMBER_MANTISSA_INTERIOR" and re.match(r"[^0-9\.eE]", c):
            self.OP_NOP()
            self.position_stay = 1
            return "NUMBER_END"
        if current_state == "NUMBER_MANTISSA_ZERO" and re.match(r"[^0-9\.eE]", c):
            self.OP_NOP()
            self.position_stay = 1
            return "NUMBER_END"
        if current_state == "NUMBER_END" and not self.negative:
            self.OP_NOP()
            self.position_stay = 1
            self.item_present = 1
            return "START"
        if current_state == "NUMBER_END" and self.negative:
            self.OP_INVERT()
            self.position_stay = 1
            self.item_present = 1
            return "START"

        # number fraction scanning
        if current_state == "NUMBER_MANTISSA_INTERIOR" and c == ".":
            self.OP_PUSH_NUMBER()
            return "NUMBER_DECIMAL"
        if current_state == "NUMBER_MANTISSA_ZERO" and c == ".":
            self.OP_PUSH_NUMBER()
            return "NUMBER_DECIMAL"
        if current_state == "NUMBER_DECIMAL" and re.match(r"[0-9]", c):
            self.OP_DECREMENT()
            self.position_stay = 1
            return "NUMBER_MANTISSA_FRACTIONAL_STEP_1"
        if current_state == "NUMBER_MANTISSA_FRACTIONAL_STEP_1":
            self.OP_SWAP()
            self.position_stay = 1
            return "NUMBER_MANTISSA_FRACTIONAL_STEP_2"
        if current_state == "NUMBER_MANTISSA_FRACTIONAL_STEP_2":
            self.OP_SHIFT_DEC(c)
            self.position_stay = 1
            return "NUMBER_MANTISSA_FRACTIONAL_STEP_3"
        if current_state == "NUMBER_MANTISSA_FRACTIONAL_STEP_3":
            self.OP_SWAP()
            return "NUMBER_MANTISSA_FRACTIONAL"
        if current_state == "NUMBER_MANTISSA_FRACTIONAL" and re.match(r"[0-9]", c):
            self.OP_DECREMENT()
            self.position_stay = 1
            return "NUMBER_MANTISSA_FRACTIONAL_STEP_1"
        if current_state == "NUMBER_MANTISSA_FRACTIONAL" and re.match(r"[^0-9eE]", c):
            self.OP_EXPONENTIATE_NUMBERS()
            self.position_stay = 1
            return "NUMBER_END"

        # number exponent scanning
        if current_state == "NUMBER_MANTISSA_INTERIOR" and re.match(r"[eE]", c):
            self.OP_PUSH_NUMBER()
            self.add_exponents = 0
            return "NUMBER_E"
        if current_state == "NUMBER_MANTISSA_ZERO" and re.match(r"[eE]", c):
            self.OP_PUSH_NUMBER()
            self.add_exponents = 0
            return "NUMBER_E"
        if current_state == "NUMBER_MANTISSA_FRACTIONAL" and re.match(r"[eE]", c):
            self.OP_PUSH_NUMBER()
            self.add_exponents = 1
            return "NUMBER_E"
        if current_state == "NUMBER_E" and c == "+":
            self.OP_NOP()
            self.negative_exponent = 0
            return "NUMBER_E_SIGN"
        if current_state == "NUMBER_E" and c == "-":
            self.OP_NOP()
            self.negative_exponent = 1
            return "NUMBER_E_SIGN"
        if current_state == "NUMBER_E" and re.match(r"[0-9]", c):
            self.OP_SHIFT_DEC(c)
            self.negative_exponent = 0
            return "NUMBER_EXPONENT"
        if current_state == "NUMBER_E_SIGN" and re.match(r"[0-9]", c):
            self.OP_SHIFT_DEC(c)
            return "NUMBER_EXPONENT"
        if current_state == "NUMBER_EXPONENT" and re.match(r"[0-9]", c):
            self.OP_SHIFT_DEC(c)
            return "NUMBER_EXPONENT"
        if current_state == "NUMBER_EXPONENT" and re.match(r"[^0-9]", c) and not self.negative_exponent:
            self.OP_NOP()
            self.position_stay = 1
            return "NUMBER_EXPONENT_APPLY"
        if current_state == "NUMBER_EXPONENT" and re.match(r"[^0-9]", c) and self.negative_exponent:
            self.OP_INVERT()
            self.position_stay = 1
            return "NUMBER_EXPONENT_APPLY"
        if current_state == "NUMBER_EXPONENT_APPLY" and self.add_exponents:
            self.OP_ADD()
            self.position_stay = 1
            self.add_exponents = 0
            return "NUMBER_EXPONENT_APPLY"
        if current_state == "NUMBER_EXPONENT_APPLY" and not self.add_exponents:
            self.OP_EXPONENTIATE_NUMBERS()
            self.position_stay = 1
            return "NUMBER_END"

        # true scanning
        if current_state == "START" and c == "t" and not self.item_present and not self.parsing_key:
            self.OP_NOP()
            return "LITERAL_T"
        if current_state == "LITERAL_T" and c == "r":
            self.OP_NOP()
            return "LITERAL_TR"
        if current_state == "LITERAL_TR" and c == "u":
            self.OP_NOP()
            return "LITERAL_TRU"
        if current_state == "LITERAL_TRU" and c == "e":
            self.OP_PUSH_TRUE()
            self.item_present = 1
            return "START"

        # false scanning
        if current_state == "START" and c == "f" and not self.item_present and not self.parsing_key:
            self.OP_NOP()
            return "LITERAL_F"
        if current_state == "LITERAL_F" and c == "a":
            self.OP_NOP()
            return "LITERAL_FA"
        if current_state == "LITERAL_FA" and c == "l":
            self.OP_NOP()
            return "LITERAL_FAL"
        if current_state == "LITERAL_FAL" and c == "s":
            self.OP_NOP()
            return "LITERAL_FALS"
        if current_state == "LITERAL_FALS" and c == "e":
            self.OP_PUSH_FALSE()
            self.item_present = 1
            return "START"

        # null scanning
        if current_state == "START" and c == "n" and not self.item_present and not self.parsing_key:
            self.OP_NOP()
            return "LITERAL_N"
        if current_state == "LITERAL_N" and c == "u":
            self.OP_NOP()
            return "LITERAL_NU"
        if current_state == "LITERAL_NU" and c == "l":
            self.OP_NOP()
            return "LITERAL_NUL"
        if current_state == "LITERAL_NUL" and c == "l":
            self.OP_PUSH_NONE()
            self.item_present = 1
            return "START"

        # array scanning
        if current_state == "START" and c == "[" and not self.item_present and not self.parsing_key:
            self.OP_PUSH_LIST()
            self.item_present = 0
            self.comma_used = 0
            return "START"
        if current_state == "START" and c == "," and inner_container == "list" and self.item_present:
            self.OP_APPEND_VALUE_TO_LIST()
            self.item_present = 0
            self.comma_used = 1
            return "START"
        if current_state == "START" and c == "]" and inner_container == "list" and not self.item_present and not self.comma_used:
            self.OP_NOP()
            self.position_stay = 1
            return "LIST_END"
        if current_state == "START" and c == "]" and inner_container == "list" and self.item_present:
            self.OP_APPEND_VALUE_TO_LIST()
            self.position_stay = 1
            return "LIST_END"
        if current_state == "LIST_END":
            self.OP_COMPLETE_LIST()
            self.item_present = 1
            self.comma_used = 0
            return "START"

        # object scanning
        if current_state == "START" and c == "{" and not self.item_present and not self.parsing_key:
            self.OP_PUSH_DICT()
            self.item_present = 0
            self.parsing_key = 1
            self.comma_used = 0
            return "START"
        if current_state == "DICT_PAIR_VALUE" and c == ":":
            self.OP_NOP()
            self.item_present = 0
            self.parsing_key = 0
            return "START"
        if current_state == "START" and c == "," and inner_container == "dict" and self.item_present and not self.parsing_key:
            self.OP_APPEND_PAIR_TO_DICT()
            self.item_present = 0
            self.parsing_key = 1
            self.comma_used = 1
            return "START"
        if current_state == "START" and c == "}" and inner_container == "dict" and not self.item_present and not self.comma_used:
            self.OP_NOP()
            self.position_stay = 1
            return "DICT_END"
        if current_state == "START" and c == "}" and inner_container == "dict" and not self.parsing_key and self.item_present:
            self.OP_APPEND_PAIR_TO_DICT()
            self.position_stay = 1
            return "DICT_END"
        if current_state == "DICT_END":
            self.OP_COMPLETE_DICT()
            self.item_present = 1
            self.parsing_key = 0
            self.comma_used = 0
            return "START"

        #print("BAD", current_state, c)
        return None

    def OP_NOP(self):
        pass
    def OP_SWAP(self):
        assert len(self.stack) >= 2
        self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
    def OP_PUSH_STRING(self):
        self.stack.append("")
    def OP_APPEND_CHAR_K(self, K):
        self.stack[-1] += K
    def OP_APPEND_CHAR_CODE(self):
        assert len(self.stack) >= 2
        code = self.stack.pop()
        assert 0 <= code <= 0xFFFFFFFF
        self.stack[-1] += chr(code)
    def OP_PUSH_NUMBER(self):
        self.stack.append(0)
    def OP_ADD(self):
        assert len(self.stack) >= 2
        addend = self.stack.pop()
        self.stack[-1] += addend
    def OP_INVERT(self):
        self.stack[-1] = -self.stack[-1]
    def OP_DECREMENT(self):
        self.stack[-1] -= 1
    def OP_SHIFT_DEC(self, K):
        self.stack[-1] = self.stack[-1] * 10 + int(K)
    def OP_SHIFT_HEX(self, K):
        self.stack[-1] = self.stack[-1] * 16 + int(K, 16)
    def OP_EXPONENTIATE_NUMBERS(self):
        assert len(self.stack) >= 2
        exponent = self.stack.pop()
        try: # improve numerical precision by using integer exponents when possible
            self.stack[-1] = float(self.stack[-1] * 10 ** exponent) if exponent > 0 else float(self.stack[-1] / 10 ** -exponent)
        except OverflowError as e:
            if exponent < 0: # tiny exponent, round to 0
                self.stack[-1] = 0.0
            elif self.stack[-1] > 0: # factor is positive, we have a positive result
                self.stack[-1] = float("inf")
            elif self.stack[-1] < 0: # factor is negative, we have a negative result
                self.stack[-1] = float("-inf")
            else: # factor is zero, so is the result
                self.stack[-1] = 0
    def OP_PUSH_DICT(self): self.stack.append({(): None})
    def OP_APPEND_PAIR_TO_DICT(self):
        value = self.stack.pop()
        key = self.stack.pop()
        assert self.is_complete(value)
        self.stack[-1][key] = value
    def OP_COMPLETE_DICT(self):
        del self.stack[-1][()]
    def OP_PUSH_LIST(self):
        self.stack.append([()])
    def OP_APPEND_VALUE_TO_LIST(self):
        item = self.stack.pop()
        assert self.is_complete(item)
        self.stack[-1].append(item)
    def OP_COMPLETE_LIST(self):
        del self.stack[-1][0]
    def OP_PUSH_TRUE(self):
        self.stack.append(True)
    def OP_PUSH_FALSE(self):
        self.stack.append(False)
    def OP_PUSH_NONE(self):
        self.stack.append(None)
    
    def is_complete(self, value):
        if isinstance(value, list):
            return len(value) == 0 or value[0] != ()
        if isinstance(value, dict):
            return () not in value
        return True
