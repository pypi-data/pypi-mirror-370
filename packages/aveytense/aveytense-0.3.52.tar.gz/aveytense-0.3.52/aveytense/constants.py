"""
**AveyTense Constants** \n
@lifetime >= 0.3.26rc3 \\
© 2023-Present Aveyzan // License: MIT \\
https://aveyzan.xyz/aveytense#aveytense.constants

Constants wrapper for AveyTense. Extracted from former `tense.tcs` module
"""
from __future__ import annotations
from ._ᴧv_collection._constants import (
    AbroadHexMode as _AbroadHexMode,
    BisectMode as _BisectMode,
    InsortMode as _InsortMode,
    ProbabilityLength as _ProbabilityLength,
    ModeSelection as _ModeSelection
)

#################################### OTHER CONSTANTS ####################################

JS_MIN_SAFE_INTEGER = -9007199254740991
"""
@lifetime >= 0.3.26b3

`-(2^53 - 1)` - the smallest safe integer in JavaScript
"""
JS_MAX_SAFE_INTEGER = 9007199254740991
"""
@lifetime >= 0.3.26b3

`2^53 - 1` - the biggest safe integer in JavaScript
"""
JS_MIN_VALUE = 4.940656458412465441765687928682213723650598026143247644255856825006755072702087518652998363616359923797965646954457177309266567103559397963987747960107818781263007131903114045278458171678489821036887186360569987307230500063874091535649843873124733972731696151400317153853980741262385655911710266585566867681870395603106249319452715914924553293054565444011274801297099995419319894090804165633245247571478690147267801593552386115501348035264934720193790268107107491703332226844753335720832431936092382893458368060106011506169809753078342277318329247904982524730776375927247874656084778203734469699533647017972677717585125660551199131504891101451037862738167250955837389733598993664809941164205702637090279242767544565229087538682506419718265533447265625e-324
"""
@lifetime >= 0.3.26b3

`2^-1074` - the smallest possible number in JavaScript \\
Precision per digit
"""
JS_MAX_VALUE = 17976931348623139118889956560692130772452639421037405052830403761197852555077671941151929042600095771540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368
"""
@lifetime >= 0.3.26b3

`2^1024 - 2^971` - the biggest possible number in JavaScript \\
Precision per digit
"""

ABROAD_HEX_INCLUDE = _AbroadHexMode.INCLUDE # 0.3.35
ABROAD_HEX_HASH = _AbroadHexMode.HASH # 0.3.35
ABROAD_HEX_EXCLUDE = _AbroadHexMode.EXCLUDE # 0.3.35

BISECT_LEFT = _BisectMode.LEFT # 0.3.35
BISECT_RIGHT = _BisectMode.RIGHT # 0.3.35

INSORT_LEFT = _InsortMode.LEFT # 0.3.35
INSORT_RIGHT = _InsortMode.RIGHT # 0.3.35

PROBABILITY_MIN = _ProbabilityLength.MIN # 0.3.35
PROBABILITY_MAX = _ProbabilityLength.MAX # 0.3.35
PROBABILITY_COMPUTE = _ProbabilityLength.COMPUTE # 0.3.35
PROBABILITY_DEFAULT = _ProbabilityLength.DEFAULT # 0.3.35

STRING_LOWER = "abcdefghijklmnopqrstuvwxyz" # 0.3.36
STRING_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" # 0.3.36
STRING_LETTERS = STRING_LOWER + STRING_UPPER # 0.3.36
STRING_HEXADECIMAL = "0123456789abcdefABCDEF" # 0.3.36
STRING_DIGITS = "0123456789" # 0.3.36
STRING_OCTAL = "01234567" # 0.3.36
STRING_BINARY = "01" # 0.3.36
STRING_SPECIAL = r"""`~!@#$%^&*()-_=+[]{};:'"\|,.<>/?""" # 0.3.36

MODE_AND = _ModeSelection.AND # 0.3.36
MODE_OR = _ModeSelection.OR # 0.3.36

RGB_MIN = 0 # 0.3.37
RGB_MAX = 2 ** 24 - 1 # 0.3.37

__all__ = [k for k in globals() if not k.startswith("_")]
"""
@lifetime >= 0.3.41
"""
__all_deprecated__ = sorted([n for n in globals() if hasattr(globals()[n], "__deprecated__")])
"""
@lifetime >= 0.3.41

Returns all deprecated declarations within this module.
"""

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error