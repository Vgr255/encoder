"""This module provides access to various encoding methods.

This is used as a proxy around the hashlib and base64 modules,
for more advanced use, refer to these modules. Each function and
method returns a string, uppercase for hashes.
"""

import hashlib as _hashlib
import base64 as _base64

__all__ = ["base64", "morse", "brainfuck", "rot13"]

_rot13 = {}

for c in (65, 97):
    for i in range(26):
        _rot13[chr(i+c)] = chr((i+13) % 26 + c)

del c, i

_morse_enc = dict({         " ": "",
"0": "-----", "1": ".----", "2": "..---", "3": "...--",
"4": "....-", "5": ".....", "6": "-....", "7": "--...",
"8": "---..", "9": "----."}, A = ".-",     B = "-...",
C =  "-.-.",   D = "-..",    E = ".",      F = "..-.",
G =  "--.",    H = "....",   I = "..",     J = ".---",
K =  "-.",     L = ".-..",   M = "--",     N = "-.",
O =  "---",    P = ".--.",   Q = "--.-",   R = ".-.",
S =  "...",    T = "-",      U = "..-",    V = "...-",
W =  ".--",    X = "-..-",   Y = "-.--",   Z = "--..")

_morse_dec = {v:k for k,v in _morse_enc.items()}

for name in _hashlib.algorithms_guaranteed:
    def hasher(line, *, func=getattr(_hashlib, name)):
        try:
            return func(line).hexdigest().upper()
        except TypeError:
            return func(bytes(line, "utf-8")).hexdigest().upper()

    __all__.append(name)
    globals()[name] = hasher

del hasher, name

if hasattr(_hashlib, "pbkdf2_hmac"):
    _pbk = _hashlib.pbkdf2_hmac
    import binascii as _binascii

    def pbkdf2_hmac(*args, **kwargs):
        return _binascii.hexlify(_pbk(*args, **kwargs)).upper()

    __all__.append("pbkdf2_hmac")

class base64:
    @staticmethod
    def encode(line, *, func=_base64.b64encode):
        try:
            return func(line).decode("utf-8")
        except TypeError:
            return func(bytes(line, "utf-8")).decode("utf-8")

    @staticmethod
    def decode(line, *, func=_base64.b64decode):
        try:
            return func(line).decode("utf-8")
        except TypeError:
            return func(bytes(line, "utf-8")).decode("utf-8")

class morse:
    @staticmethod
    def encode(line):
        return " ".join((_morse_enc[c.upper()] for c in line))

    @staticmethod
    def decode(line):
        return "".join((_morse_dec[c].lower() for c in line.split(" ")))

class BFHandler:
    def __init__(self):
        self.handler = [0]
        self.pointer = 0
        self.brackets = {}

    def open_bracket(self, pointer):
        self.brackets[pointer] = None

    def close_bracket(self, pointer):
        toget = sorted(self.brackets)[-1]
        self.brackets[toget] = pointer

    def move_right(self):
        self.pointer += 1
        if len(self.handler) <= self.pointer:
            self.handler.append(0)

    def move_left(self):
        self.pointer -= 1

    def inc(self):
        self.handler[self.pointer] += 1
        if self.handler[self.pointer] == 256:
            self.handler[self.pointer] = 0

    def dec(self):
        self.handler[self.pointer] -= 1
        if self.handler[self.pointer] == -1:
            self.handler[self.pointer] = 255

    def get_value(self):
        return chr(self.handler[self.pointer])

    def set_value(self, inp):
        self.handler[self.pointer] = ord(inp)

    def get_current(self):
        return self.handler[self.pointer]

    def reverse_brackets(self):
        return {v:k for k,v in self.brackets.items()}

class brainfuck:

    _allowed = "+-.,[]<>"

    @staticmethod
    def offset(run, items):
        off = 0
        if run == 0:
            return 0
        runner = 1
        while runner < run:
            if runner not in items:
                off += 1
            runner += 1
        return off

    @classmethod
    def decode(cls, line):
        new = ""
        for char in line:
            if char in cls._allowed:
                new += char
        if not new:
            return ""
        cells = BFHandler()
        pointer = 0
        for char in new:
            if char == "[":
                cells.open_bracket(pointer)
            elif char == "]":
                cells.close_bracket(pointer)
            pointer += 1
        pointer = 0
        chars = ""
        while True:
            char = new[pointer]
            if char == "+":
                cells.inc()
            elif char == "-":
                cells.dec()
            elif char == "[":
                if not cells.get_current():
                    pointer = cells.brackets[pointer]
            elif char == "]":
                if cells.get_current():
                    pointer = cells.reverse_brackets()[pointer]
            elif char == "<":
                cells.move_left()
            elif char == ">":
                cells.move_right()
            elif char == ".":
                chars += cells.get_value()
            elif char == ",":
                print("Comma found.")
                while True:
                    c = input("Please enter a single character and hit Enter: ").strip()
                    if len(c) == 1:
                        break
                    print("Too many characters, please try again.")
                cells.set_value(c)
            pointer += 1
            if pointer == len(new):
                break
        return chars

    @classmethod
    def encode(cls, line, maxlen=10):
        if maxlen < 1:
            maxlen = 1
        maxlen = maxlen // 1
        runner = 0
        #items = [0, (256 // maxlen), False]
        items = {}
        ords = []
        new = ""
        while runner < len(line):
            ords.append(ord(line[runner]))
            items[ord(line[runner]) // maxlen] = True
            runner += 1
        if maxlen <= max(ords) and maxlen > 1:
            new += "+" * maxlen + "["
        runner = 0
        for key, value in items.items():
            if key == 0 or not value:
                continue
            new += ">" + "+" * key
            runner += 1
        while runner > 0:
            new += "<"
            runner -= 1
        if maxlen <= max(ords) and maxlen > 1:
            new += "-]"
        runner = 1
        values = {}
        while runner < (256 // maxlen) + 1:
            offset = cls.offset(runner, items)
            if runner > offset:
                values[runner - offset] = maxlen * runner
            runner += 1
        runner = 0
        run = 0
        while runner < len(line):
            r = ord(line[runner])
            num = r // maxlen
            offset = cls.offset(num, items)
            num -= offset
            val = values[num]
            if num > run:
                new += ">" * (num - run)
            elif num < run:
                new += "<" * (run - num)
            run = num
            if r > val:
                new += "+" * (r - val)
            elif r < val:
                new += "-" * (val - r)
            new += "."
            values[num] = r
            runner += 1
        return new

def rot13(line):
    return "".join((_rot13.get(c, c) for c in line))
