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