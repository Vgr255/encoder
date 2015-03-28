"""This module provides access to various encoding methods.

This is used as a proxy around the hashlib and base64 modules,
for more advanced use, refer to these modules. Each function and
method returns a string, uppercase for hashes.
"""

__all__ = ["base64", "morse", "rot13"]

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

import hashlib
for name in hashlib.algorithms_guaranteed:
    def hasher(line, *, func=getattr(hashlib, name)):
        try:
            return func(line).hexdigest().upper()
        except TypeError:
            return func(bytes(line, "utf-8")).hexdigest().upper()

    __all__.append(name)
    globals()[name] = hasher

del hasher, name

if hasattr(hashlib, "pbkdf2_hmac"):
    _pbk = hashlib.pbkdf2_hmac
    import binascii as _binascii

    def pbkdf2_hmac(*args, **kwargs):
        return _binascii.hexlify(_pbk(*args, **kwargs)).upper()

    __all__.append("pbkdf2_hmac")

del hashlib

class base64:
    import base64

    @staticmethod
    def encode(line, *, func=base64.b64encode):
        try:
            return func(line).decode("utf-8")
        except TypeError:
            return func(bytes(line, "utf-8")).decode("utf-8")

    @staticmethod
    def decode(line, *, func=base64.b64decode):
        try:
            return func(line).decode("utf-8")
        except TypeError:
            return func(bytes(line, "utf-8")).decode("utf-8")

    del base64

class morse:
    @staticmethod
    def encode(line):
        return " ".join((_morse_enc[c.upper()] for c in line))

    @staticmethod
    def decode(line):
        return "".join((_morse_dec[c].lower() for c in line.split(" ")))

def rot13(line):
    return "".join((_rot13.get(c, c) for c in line))
