#
#   HEAD
#

# HEAD -> DATACLASSES
from dataclasses import dataclass
from .parser import (
    # DATACLASSES -> 1ºLEVEL
    Level1,
    Sheet, 
    # DATACLASSES -> 2ºLEVEL
    Level2,
    Declaration,
    Node,
    Equation,
    Comment,
    # DATACLASSES -> 3ºLEVEL
    Level3,
    Expression, 
    # DATACLASSES -> 4ºLEVEL
    Level4,
    Term, 
    # DATACLASSES -> 5ºLEVEL
    Level5,
    Variable,
    Nest,
    Vector,
    Number
)


#
#   NODES
#

# NODES -> U8
def u8(value: int = None) -> bytes:
    if not 0 < value <= 2**8 - 1: raise Exception()
    return bytes([value])

# NODES -> U32
def u32(value: int) -> bytes:
    if not 0 < value <= 2**32 - 1: raise Exception()
    return bytes([
        value & 0xFF,
        (value >> 8) & 0xFF,
        (value >> 16) & 0xFF,
        (value >> 24) & 0xFF
    ])

# NODES -> NAMESPACE
class Sequence:
    code: u8

# NODES -> JOIN
def join(binary: list[bytes]) -> bytes:
    result = b""
    for data in binary:
        result += data
    return result

# NODES -> NULL BYTE
null8 = b"\x00"
null32 = b"\x00\x00\x00\x00"


#
#   1ºLEVEL
#

# 1ºLEVEL -> SHEET
@dataclass
class IRSheet(Sequence):
    code = u8(0x01)
    location: u32
    statements: list[u32]
    def __bytes__(self) -> bytes:
        return self.code + self.location + (join(self.statements) + null32)


#
#   2ºLEVEL
#

# 2ºLEVEL -> DECLARATION
@dataclass
class IRDeclaration(Sequence):
    code = u8(0x02)
    location: u32
    pointer: u32
    characters: list[u8]
    def __bytes__(self) -> bytes:
        return self.code + self.location + self.pointer + (join(self.characters) + null8)

# 2ºLEVEL -> NODE
@dataclass
class IRNode(Sequence):
    code = u8(0x03)
    location: u32
    pointer: u32
    def __bytes__(self) -> bytes:
        return self.code + self.location + self.pointer

# 2ºLEVEL -> EQUATION
@dataclass
class IREquation(Sequence):
    code = u8(0x04)
    location: u32
    left: u32
    right: u32
    def __bytes__(self) -> bytes:
        return self.code + self.location + self.left + self.right

# 2ºLEVEL -> COMMENT
@dataclass
class IRComment(Sequence):
    code = u8(0x05)
    location: u32
    characters: list[u8]
    def __bytes__(self) -> bytes:
        return self.code + self.location + (join(self.characters) + null8)


#
#   3ºLEVEL
#

# 3ºLEVEL -> EXPRESSION
@dataclass
class IRExpression(Sequence):
    code = u8(0x06)
    location: u32
    terms: list[u32]
    def __bytes__(self) -> bytes:
        return self.code + self.location + (join(self.terms) + null32)


#
#   4ºLEVEL
#

# 4ºLEVEL -> TERM
@dataclass
class IRTerm(Sequence):
    code = u8(0x07)
    location: u32
    numerator: list[u32]
    denominator: list[u32]
    def __bytes__(self) -> bytes:
        return self.code + self.location + (join(self.numerator) + null32) + (join(self.denominator) + null32)


#
#   5ºLEVEL
#

# 5ºLEVEL -> VARIABLE
@dataclass
class IRVariable(Sequence):
    code = u8(0x08)
    location: u32
    sign: u8
    exponent: u32 or null32
    characters: list[u8]
    def __bytes__(self) -> bytes:
        return self.code + self.location + self.sign + self.exponent + (join(self.characters) + null8)

# 5ºLEVEL -> NEST
@dataclass
class IRNest(Sequence):
    code = u8(0x09)
    location: u32
    sign: u8
    exponent: u32 or null32
    pointer: u32
    def __bytes__(self) -> bytes:
        return self.code + self.location + self.sign + self.exponent + self.pointer

# 5ºLEVEL -> VECTOR
@dataclass
class IRVector(Sequence):
    code = u8(0x0A)
    location: u32
    sign: u8
    exponent: u32 or null32
    pointers: list[u32]
    def __bytes__(self) -> bytes:
        return self.code + self.location + self.sign + self.exponent + (join(self.pointers) + null32)

# 5ºLEVEL -> NUMBER
@dataclass
class IRNumber(Sequence):
    code = u8(0x0B)
    location: u32
    sign: u8
    exponent: u32 or null32
    value: u32 or null32
    decimal: u32 or null32
    def __bytes__(self) -> bytes:
        return self.code + self.location + self.sign + self.exponent + self.value + self.decimal



#
#   IR
#

# IR -> GENERATOR
class IR:
    # IR -> VARIABLES
    ir: list[Sequence]
    counter: int
    # IR -> INIT
    def __init__(self) -> None:
        self.ir = []
        self.counter = 0
    # IR -> RUN
    def run(self, sheet: Sheet) -> bytes:
        self.ir = []
        self.counter = 0
        self.sheet(sheet)
        return join([bytes(sequence) for sequence in self.ir])
    # IR -> 1 SHEET GENERATION
    def sheet(self, sheet: Sheet) -> bytes:
        statements = []
        for statement in sheet.statements:
            match statement:
                case Declaration(): statements.append(self.declaration(statement))
                case Node(): statements.append(self.node(statement))
                case Equation(): statements.append(self.equation(statement))
                case Comment(): statements.append(self.comment(statement))
        register = self.new()
        self.ir.append(IRSheet(
            register,
            statements    
        ))
        return register
    # GENERATOR -> 2 DECLARATION GENERATION
    def declaration(self, declaration: Declaration) -> bytes:
        pointer = self.expression(declaration.expression)
        register = self.new()
        self.ir.append(IRDeclaration(
            register,
            pointer,
            [declaration.identifier.encode()]
        ))
        return register
    # GENERATOR -> 2 NODE GENERATION
    def node(self, node: Node) -> bytes:
        pointer = self.expression(node.expression)
        register = self.new()
        self.ir.append(IRNode(
            register,
            pointer
        ))
        return register
    # GENERATOR -> 2 EQUATION GENERATION
    def equation(self, equation: Equation) -> bytes:
        left = self.expression(equation.left)
        right = self.expression(equation.right)
        register = self.new()
        self.ir.append(IREquation(
            register,
            left,
            right
        ))
        return register
    # GENERATOR -> 2 COMMENT GENERATION
    def comment(self, comment: Comment) -> bytes:
        register = self.new()
        self.ir.append(IRComment(
            register,
            [comment.text.encode()]
        ))
        return register
    # GENERATOR -> 3 EXPRESSION GENERATION
    def expression(self, expression: Expression) -> bytes:
        terms = []
        for term in expression.terms:
            terms.append(self.term(term))
        register = self.new()
        self.ir.append(IRExpression(
            register,
            terms
        ))
        return register
    # GENERATOR -> 4 TERM GENERATION
    def term(self, term: Term) -> bytes:
        numerator = []
        denominator = []
        for index in range(len(term.factors)):
            if index == 0: 
                dump = numerator
            else:
                match term.operators[index - 1]:
                    case "*" | "·": dump = numerator
                    case "/": dump = denominator
            match term.factors[index]:
                case Variable(): dump.append(self.variable(term.factors[index]))
                case Nest(): dump.append(self.nest(term.factors[index]))
                case Vector(): dump.append(self.vector(term.factors[index]))
                case Number(): dump.append(self.number(term.factors[index]))
        register = self.new()
        self.ir.append(IRTerm(
            register,
            numerator,
            denominator
        ))
        return register
    # GENERATOR -> 5 VARIABLE GENERATION
    def variable(self, variable: Variable) -> bytes:
        exponent = self.expression(variable.exponent) if variable.exponent is not None else null32
        register = self.new()
        self.ir.append(IRVariable(
            register,
            u8(variable.signs.count("-")) if variable.signs is not None and variable.signs.count("-") != 0 else null8,
            exponent,
            [variable.representation.encode()]
        ))
        return register
    # GENERATOR -> 5 NEST GENERATION
    def nest(self, nest: Nest) -> bytes:
        exponent = self.expression(nest.exponent) if nest.exponent is not None else null32
        pointer = self.expression(nest.expression)
        register = self.new()
        self.ir.append(IRNest(
            register,
            u8(nest.signs.count("-")) if nest.signs is not None and nest.signs.count("-") != 0 else null8,
            exponent,
            pointer
        ))
        return register
    # GENERATOR -> 5 VECTOR GENERATION
    def vector(self, vector: Vector) -> bytes:
        exponent = self.expression(vector.exponent) if vector.exponent is not None else null32
        pointers = []
        for value in vector.values:
            pointers.append(self.expression(value))
        register = self.new()
        self.ir.append(IRVector(
            register,
            u8(vector.signs.count("-")) if vector.signs is not None and vector.signs.count("-") != 0 else null8,
            exponent,
            pointers
        ))
        return register
    # GENERATOR -> 5 NUMBER GENERATION
    def number(self, number: Number) -> bytes:
        exponent = self.expression(number.exponent) if number.exponent is not None else null32
        register = self.new()
        self.ir.append(IRNumber(
            register,
            u8(number.signs.count("-")) if number.signs is not None and number.signs.count("-") != 0 else null8,
            exponent,
            u32(int(number.representation.split(".")[0]) if "." in number.representation else int(number.representation)) if float(number.representation) != 0 else null32,
            u32(int(number.representation.split(".")[1])) if "." in number.representation else null32
        ))
        return register
    # GENERATOR -> VARIABLE GENERATOR
    def new(self) -> u32:
        self.counter += 1
        return u32(self.counter)