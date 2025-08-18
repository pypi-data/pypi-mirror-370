from __future__ import annotations
import re
from sqlglot import tokenize, TokenType, Parser as GlotParser, exp
from typing import (
    Optional, List, Any, Tuple,
    Generic, Callable
)
from syncraft.algebra import (
    Either, Left, Right, Error, Insptectable, Algebra
)
from dataclasses import dataclass, field, replace
from enum import Enum
from functools import reduce
from syncraft.dsl import DSL

from syncraft.ast import Token, TokenSpec, AST, T









@dataclass(frozen=True)
class ParserState(Generic[T], Insptectable):
    input: Tuple[T, ...] = field(default_factory=tuple)
    index: int = 0
    
    def token_sample_string(self)-> str:
        def encode_tokens(*tokens:T) -> str:
            return ",".join(f"{token.token_type.name}({token.text})" for token in tokens)
        return encode_tokens(*self.input[self.index:self.index + 2])

    def before(self, length: Optional[int] = 5)->str:
        length = min(self.index, length) if length is not None else self.index
        return " ".join(token.text for token in self.input[self.index - length:self.index])
    
    def after(self, length: Optional[int] = 5)->str:
        length = min(length, len(self.input) - self.index) if length is not None else len(self.input) - self.index
        return " ".join(token.text for token in self.input[self.index:self.index + length])
 
    def to_string(self, interested: Callable[[Any], bool])->str:
        return f"ParserState(\n"\
               f"index={self.index}, \n"\
               f"input({len(self.input)})=[{self.token_sample_string()}, ...]), \n"\
               f"before=({self.before()}), \n"\
               f"after=({self.after()})"  


    def current(self)->T:
        if self.ended():
            raise IndexError("Attempted to access token beyond end of stream")
        return self.input[self.index]
    
    def ended(self) -> bool:
        return self.index >= len(self.input)

    def advance(self) -> ParserState[T]:
        return replace(self, index=min(self.index + 1, len(self.input)))
            
    def delta(self, new_state: ParserState[T]) -> Tuple[T, ...]:
        assert self.input is new_state.input, "Cannot calculate differences between different input streams"
        assert 0 <= self.index <= new_state.index <= len(self.input), "Segment indices out of bounds"
        return self.input[self.index:new_state.index]
    
    def copy(self) -> ParserState[T]:
        return self.__class__(input=self.input, index=self.index)

    @classmethod
    def from_tokens(cls, tokens: Tuple[T, ...]) -> ParserState[T]:
        return cls(input=tokens, index=0)




    
@dataclass(frozen=True)
class Parser(Algebra[Tuple[T,...] | T, ParserState[T]]):
    @classmethod
    def token(cls, 
              token_type: Optional[Enum] = None, 
              text: Optional[str] = None, 
              case_sensitive: bool = False,
              regex: Optional[re.Pattern[str]] = None
              )-> Algebra[Tuple[T,...] | T, ParserState[T]]:
        spec = TokenSpec(token_type=token_type, text=text, case_sensitive=case_sensitive, regex=regex)
        def token_run(state: ParserState[T], use_cache:bool) -> Either[Any, Tuple[Tuple[T,...] | T, ParserState[T]]]:
            if state.ended():
                return Left(state)
            token = state.current()
            if token is None or not spec.is_valid(token):
                return Left(state)
            return Right((Token(token_type = token.token_type, text=token.text), state.advance()))  # type: ignore
        captured: Algebra[Tuple[T,...] | T, ParserState[T]] = cls(token_run, name=cls.__name__ + f'.token({token_type}, {text})')
        def error_fn(err: Any) -> Error:
            if isinstance(err, ParserState):
                return Error(message=f"Cannot match token at {err}", this=captured, state=err)            
            else:
                return Error(message="Cannot match token at unknown state", this=captured)
        # assign the updated parser(with description) to bound variable so the Error.this could be set correctly
        captured = captured.map_error(error_fn)
        return captured        


    @classmethod
    def until(cls, 
              *open_close: Tuple[Algebra[Any, ParserState[T]], Algebra[Any, ParserState[T]]],
              terminator: Optional[Algebra[Any, ParserState[T]]] = None,
              inclusive: bool = True, 
              strict: bool = True) -> Algebra[Any, ParserState[T]]:
        def until_run(state: ParserState[T], use_cache:bool) -> Either[Any, Tuple[Any, ParserState[T]]]:
            counters = [0] * len(open_close)
            tokens: List[Any] = []
            if not terminator and len(open_close) == 0:
                return Left(Error(this=until_run, message="No terminator and no open/close parsers, nothing to parse", state=state))  
            def run_oc(s: ParserState[T], 
                       sign: int, 
                       *oc: Algebra[Any, ParserState[T]])->Tuple[bool, ParserState[T]]:
                matched = False
                for i, p in enumerate(oc):
                    new = p.run(s, use_cache)
                    if isinstance(new, Right):
                        matched = True
                        counters[i] += sign
                        if inclusive:
                            tokens.append(new.value[0])
                        s = new.value[1]
                return matched, s
            opens, closes = zip(*open_close) if len(open_close) > 0 else ((), ())
            tmp_state: ParserState[T] = state.copy()
            if strict:
                c = reduce(lambda a, b: a.or_else(b), opens).run(tmp_state)
                if c.is_left():
                    return Left(Error(
                        this=until_run,
                        message="No opening parser matched",
                        state=tmp_state
                    ))
            while not tmp_state.ended():
                mopen, tmp_state = run_oc(tmp_state, 1, *opens)
                mclose, tmp_state = run_oc(tmp_state, -1, *closes)
                matched = mopen or mclose
                if all(c == 0 for c in counters):
                    if terminator :
                        new = terminator.run(tmp_state, use_cache)
                        if isinstance(new, Right):
                            matched = True
                            if inclusive:
                                tokens.append(new.value[0])
                            return Right((tuple(tokens), new.value[1]))
                    else:
                        return Right((tuple(tokens), tmp_state))
                elif any(c < 0 for c in counters):
                    return Left(Error(this=until_run, message="Unmatched closing parser", state=tmp_state))
                if not matched:
                    tokens.append(tmp_state.current())
                    tmp_state = tmp_state.advance()
            return Right((tuple(tokens), tmp_state))
        return cls(until_run, name=cls.__name__ + '.until')

def sqlglot(parser: DSL[Any, Any], 
            dialect: str) -> DSL[List[exp.Expression], ParserState[Any]]:
    gp = GlotParser(dialect=dialect)
    return parser.map(lambda tokens: [e for e in gp.parse(raw_tokens=tokens) if e is not None])


def parse(parser: Algebra[Any, ParserState[Token]], 
          sql: str, 
          dialect: str) -> AST[Any] | Any:
    input: ParserState[Token] = token_state(sql, dialect=dialect)
    result = parser.run(input, True)
    if isinstance(result, Right):
        return AST(result.value[0])
    assert isinstance(result, Left), "Parser must return Either[E, Tuple[A, S]]"
    return result.value


def token_state(sql: str, dialect: str) -> ParserState[Token]:
    tokens = tuple([Token(token_type=token.token_type, text=token.text) for token in tokenize(sql, dialect=dialect)])
    return ParserState.from_tokens(tokens) 

def token(token_type: Optional[Enum] = None, 
          text: Optional[str] = None, 
          case_sensitive: bool = False,
          regex: Optional[re.Pattern[str]] = None
          ) -> DSL[Any, Any]:
    token_type_txt = token_type.name if token_type is not None else None
    token_value_txt = text if text is not None else None
    msg = 'token(' + ','.join([x for x in [token_type_txt, token_value_txt, str(regex)] if x is not None]) + ')'
    return DSL(
        lambda cls: cls.factory('token', token_type=token_type, text=text, case_sensitive=case_sensitive, regex=regex)
        ).describe(name=msg, fixity='prefix') 

    
def identifier(value: str | None = None) -> DSL[Any, Any]:
    if value is None:
        return token(TokenType.IDENTIFIER)
    else:
        return token(TokenType.IDENTIFIER, text=value)

def variable(value: str | None = None) -> DSL[Any, Any]:
    if value is None:
        return token(TokenType.VAR)
    else:
        return token(TokenType.VAR, text=value)

def literal(lit: str) -> DSL[Any, Any]:
    return token(token_type=None, text=lit, case_sensitive=True)

def regex(regex: re.Pattern[str]) -> DSL[Any, Any]:
    return token(token_type=None, regex=regex, case_sensitive=True)

def lift(value: Any)-> DSL[Any, Any]:
    if isinstance(value, str):
        return literal(value)
    elif isinstance(value, re.Pattern):
        return token(regex=value)
    elif isinstance(value, Enum):
        return token(value)
    else:
        return DSL(lambda cls: cls.success(value))

def number() -> DSL[Any, Any]:
    return token(TokenType.NUMBER)


def string() -> DSL[Any, Any]:
    return token(TokenType.STRING)



def until(*open_close: Tuple[DSL[Tuple[T, ...] | T, ParserState[T]], DSL[Tuple[T, ...] | T, ParserState[T]]],
          terminator: Optional[DSL[Tuple[T, ...] | T, ParserState[T]]] = None,
          inclusive: bool = True, 
          strict: bool = True) -> DSL[Any, Any]:
    return DSL(
        lambda cls: cls.factory('until', 
                           *[(left.alg(cls), right.alg(cls)) for left, right in open_close], 
                           terminator=terminator.alg(cls) if terminator else None, 
                           inclusive=inclusive, 
                           strict=strict)
        ).describe(name="until", fixity='prefix') 

