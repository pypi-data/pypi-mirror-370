#!/usr/bin/env python3
# encoding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__version__ = (0, 0, 4)
__all__ = [
    "FStringPart", "BlockAny", "Block", "FString", "String", 
    "fstring_part_iter", "parse", "render", 
]

from abc import ABC, abstractmethod
from ast import parse as ast_parse, FormattedValue, JoinedStr
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pprint import pformat
from re import compile as re_compile, IGNORECASE
from typing import cast, Final


CRE_UNICODE_ESCAPE_sub: Final = re_compile(r"[\\0-9a-z]+", flags=IGNORECASE).sub
TOKEN_SPECIFICATION: Final[list[tuple[str, str]]] = [
    ("left_brace", r"\{\{"), 
    ("right_brace", r"\}\}"), 
    ("less_than", r"\\<"), 
    ("greater_than", r"\\>"), 
    ("vertical_line", r"\\\|"), 
    ("left_block_with_name", r"<(?P<lbq>\?)?\{\{(?!\d)(?P<lbn>\w+)\}\}"), 
    ("left_block", r"<"), 
    ("right_block", r">"), 
    ("block_or", r"\|\|"), 
]
token_find: Final = re_compile("|".join(f"(?P<{group}>{token})" for group, token in TOKEN_SPECIFICATION)).search


def unrepr(s: str, /) -> str:
    return eval("'%s'" % s.replace("'", "\'"))


@dataclass(slots=True, frozen=True)
class FStringPart:
    start: int
    stop: int
    value: str
    is_placeholder: bool = False

    def __bool__(self, /) -> bool:
        return self.is_placeholder


class Render(ABC):

    @abstractmethod
    def render(self, ns: Mapping, /) -> str:
        ...

    def __call__(self, ns: Mapping, /) -> str:
        return self.render(ns)


class Block(list[Render], Render):

    def __init__(
        self, 
        /, 
        name: None | str = None, 
        *, 
        hide: bool = False, 
        throw: bool = True, 
    ):
        self.name = name
        self.hide = hide
        self.throw = throw

    def __repr__(self, /) -> str:
        return f"{type(self).__qualname__}({pformat(list(self))})"

    def render(self, ns: Mapping, /) -> str:
        try:
            s = "".join(render.render(ns) for render in self)
        except Exception:
            if self.throw:
                raise
            s = ""
        if name := self.name:
            ns[name] = s # type: ignore
        if self.hide:
            s = ""
        return s


class BlockAny(Block):

    def render(self, ns: Mapping, /) -> str:
        excs: list[Exception] = []
        for render in self:
            try:
                s = render.render(ns)
            except Exception as e:
                excs.append(e)
            else:
                if name := self.name:
                    ns[name] = s # type: ignore
                if self.hide:
                    s = ""
                return s
        if excs and self.throw:
            raise ExceptionGroup("render error", excs)
        return ""


class String(str, Render):

    def render(self, _, /) -> str:
        return self


class FString(str, Render):

    def __init__(self, s: str, /):
        self.code = compile("f%r"%s, "", "eval")

    def render(self, ns: Mapping, /) -> str:
        return eval(self.code, {}, ns)


def fstring_part_iter(template: str, /) -> Iterator[FStringPart]:
    """Decompose the fstring template, and distinguish between plain text and placeholders.

    :param template: The fstring template

    :return: An iterator, yield object is either plain text or a placeholder (however complex it is). 
    """
    fs = ("f%r" % template).encode("utf-8")
    tree = cast(JoinedStr, ast_parse(fs, "", 'eval').body)
    start = stop = 0
    for part in tree.values:
        value = unrepr(fs[part.col_offset:part.end_col_offset].decode("utf-8"))
        stop = start + len(value)
        yield FStringPart(start, stop, value, isinstance(part, FormattedValue))
        start = stop


def parse(template: str, /) -> Block:
    """Template parsing.

    :param template: The template string.

    :return: The parsing result.

    Syntax Overview::
        1. A string surrounded by "<" and ">" is called a block, and blocks can be nested, e.g., "<...>".
        2. The string inside a block is treated as a Python f-string for interpolation. 
           If interpolation fails, the block returns an empty string "".
        3. Blocks can have names (similar to capture groups in regular expressions), placed inside "{{" and "}}". 
           The syntax is "<{{name}}...>", and the value of this block can be referenced repeatedly using "{name}".
        4. Named blocks can be defined without output, allowing later references. The syntax is "<?{{name}}...>".
        5. If you want to use "<" and ">", but not as block indicators, write them as "\\<" and "\\>".
        6. Supports the binary operator "||". The syntax is "part1||part2". 
           If ``part1`` doesn't raise an error, its value will be used; otherwise, ``part2`` is executed, and its value 
           will be used or raises an error. This operator can be chained indefinitely. 

    Introduction to Python's f-strings::
        - https://docs.python.org/3/reference/lexical_analysis.html#formatted-string-literals
        - https://peps.python.org/pep-0498/
        - https://peps.python.org/pep-0701/

    Usage Example::

        1. When scraping with MoviePilot, files can be moved and renamed using Jinja2 syntax. 
           If you use this module, you can write about 2/3 fewer lines.

            Jinja2 Example:

                {{title}}{% if year %} ({{year}}){% endif %}{% if tmdbid %} [tmdbid={{tmdbid}}]{% endif %}/Season {{season}}/{{title}} - {{season_episode}}{% if part %}-{{part}}{% endif %}{% if episode %} - 第{{episode}}集{% endif %}{% if videoFormat %} - {{videoFormat}}{% endif %}{% if edition %}.{{edition}}{% endif %}{% if videoCodec %}.{{videoCodec}}{% endif %}{% if audioCodec %}.{{audioCodec}}{% endif %}{% if releaseGroup %}-{{releaseGroup}}{% endif %}{{fileExt}}

            Syntax of this module:

                {title}< ({year})>< [tmdbid={tmdbid}]>/Season {season}/{title} - {season_episode}<-{part}>< - 第{episode}集>< - {videoFormat}><.{edition}><.{videoCodec}><.{audioCodec}><-{releaseGroup}>{fileExt}

            ----

            Jinja2 Example:

                {{title}}{% if year %} ({{year}}){% endif %}{% if tmdbid %} [tmdbid={{tmdbid}}]{% endif %}/{{title}}{% if year %} ({{year}}){% endif %}{% if part %}-{{part}}{% endif %}{% if videoFormat %} - {{videoFormat}}{% endif %}{% if edition %}.{{edition}}{% endif %}{% if videoCodec %}.{{videoCodec}}{% endif %}{% if audioCodec %}.{{audioCodec}}{% endif %}{% if releaseGroup %}-{{releaseGroup}}{% endif %}{{fileExt}}

            Syntax of this module:

                <{{prefix}}{title}< ({year})>>< [tmdbid={tmdbid}]>/{prefix}<-{part}>< - {videoFormat}><.{edition}><.{videoCodec}><.{audioCodec}><-{releaseGroup}>{fileExt}
    """
    block: Block = Block(throw=True)
    stack: list[Block] = [block]
    depth = 0
    for part in fstring_part_iter(template):
        value = part.value
        if part:
            block.append(FString(value))
        else:
            start = 0
            while match := token_find(value, start):
                if start != match.start():
                    block.append(String(value[start:match.start()]))
                match group := match.lastgroup:
                    case "left_block" | "left_block_with_name":
                        if group == "left_block":
                            block = Block()
                        else:
                            block = Block(match["lbn"], hide=bool(match["lbq"]))
                        block.throw = False
                        stack[depth].append(block)
                        depth += 1
                        try:
                            stack[depth] = block
                        except IndexError:
                            stack.append(block)
                    case "right_block":
                        depth -= 1
                        if depth and isinstance(stack[depth], BlockAny):
                            depth -= 1
                        if depth < 0:
                            raise SyntaxError(f"unmatched '>' at {part.start + match.start()}")
                        block = stack[depth]
                    case "block_or":
                        if depth and isinstance(stack[depth-1], BlockAny):
                            block = stack[depth] = Block()
                            stack[depth-1].append(block)
                        else:
                            block_any = BlockAny(name=block.name, hide=block.hide, throw=block.throw)
                            block.__dict__.update(name=None, hide=False, throw=True)
                            block_any.append(block)
                            stack[depth] = block_any
                            block = Block()
                            block_any.append(block)
                            depth += 1
                            try:
                                stack[depth] = block
                            except IndexError:
                                stack.append(block)
                    case _:
                        block.append(String(match[0].replace("\\", "")))
                start = match.end()
            if start < len(value):
                block.append(String(value[start:]))
    if depth and not (depth == 1 and isinstance(stack[0], BlockAny)):
        raise SyntaxError(f"{depth} '<' not closed")
    return stack[0]


def render(block: str | Block, ns: Mapping, /) -> str:
    """Template interpolation.

    :param block: If it's a `str`, it is treated as the template string; otherwise, it's treated as the template parsing result object.
    :param ns: The namespace, which contains the values to be referenced.

    :return: The result string after template interpolation (replacing placeholders).
    """
    if isinstance(block, str):
        block = parse(block)
    return block.render(ns)

