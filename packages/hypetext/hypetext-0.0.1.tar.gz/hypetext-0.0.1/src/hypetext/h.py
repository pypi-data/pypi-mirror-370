import re
from collections import deque
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
from string.templatelib import Interpolation, Template
from types import NoneType
from typing import Any, Collection, Literal
from uuid import uuid4

from ovld import Medley, ovld, recurse
from ovld.types import HasMethod

from .utils import ResourceFilter

default_template = """
<html>
  <head>
    {resources}
  </head>
  <body>
    {body}
  </body>
</html>
"""


class HypeHTMLParser(HTMLParser):
    def __init__(self):
        self.acc = []
        super().__init__()

    def parse_endtag(self, i):
        if self.rawdata[i : i + 3] == "</>":
            self.handle_endtag("")
            return i + 3
        else:
            return super().parse_endtag(i)

    def handle_starttag(self, tag, attrs):
        self.acc.append(("starttag", tag, attrs, False))

    def handle_endtag(self, tag):
        self.acc.append(("endtag", tag))

    def handle_startendtag(self, tag, attrs):
        self.acc.append(("starttag", tag, attrs, True))

    def handle_data(self, data):
        self.acc.append(("data", data))

    def handle_comment(self, data):
        self.acc.append(("comment", data))

    def handle_entityref(self, name):
        self.acc.append(("entityref", name))

    def handle_charref(self, name):
        self.acc.append(("charref", name))

    def handle_decl(self, decl):
        self.acc.append(("decl", decl))

    def handle_pi(self, data):
        self.acc.append(("pi", data))

    def iterate(self, html):
        self.feed(html)
        acc, self.acc = self.acc, []
        yield from acc
        if self.rawdata:
            yield ("partial", self.rawdata)


@dataclass
class Node:
    tag: str
    attrs: list
    children: list
    self_closing: bool = False

    def __str__(self):
        return "".join(Interpreter().string_parts(self))

    def page(self):
        return Interpreter().page(self)


class Constructor:
    def gen(self, interpreter):
        yield ("lit", "boof")

    @classmethod
    def make(cls, attrs, children):
        attrs = {k: v.value if isinstance(v, Interpolation) else v for k, v in attrs}
        return cls(*children, **attrs)


@ovld
def html(s: str):
    return recurse(Template(s))


@ovld
def html(o: object):
    return recurse(Template(Interpolation(o, "")))


@ovld
def html(tpl: Template):
    mark = uuid4().hex
    pattern = re.compile(f"(hype_[0-9_]+{mark})")
    mappings = {}

    parser = HypeHTMLParser()
    stack = [Node(None, [], [])]
    is_partial = False

    def _retemplate(part):
        if part is None:
            return None
        new_parts = [mappings.get(x, x) for x in pattern.split(part) if x]
        match new_parts:
            case [str() as v]:
                return v
            case [Interpolation() as ip]:
                return ip
            case _:
                return Template(*new_parts)

    def _feed(part):
        match part:
            case ("starttag", tag, attrs, self_closing):
                if is_partial:
                    attrs = [(_retemplate(k), _retemplate(v)) for k, v in attrs]
                    tag = _retemplate(tag)

                match tag:
                    case (str() as s) | Interpolation(str() as s, _, None, ""):
                        new_node = Node(s, attrs, [], self_closing)
                    case Interpolation(type() as cons, _, None, "") if issubclass(
                        cons, Constructor
                    ):
                        new_node = cons.make(attrs, [])
                    case _:  # pragma: no cover
                        raise ValueError(f"Invalid interpolation in tag name: {tag}")

                if self_closing:
                    stack[-1].children.append(new_node)
                else:
                    stack.append(new_node)
            case ("endtag", tag):
                top = stack.pop()
                if is_partial:
                    match _retemplate(tag):
                        case (str() as s) | Interpolation(str() as s, _, None, ""):
                            tag = s
                        case Interpolation(type() as cons, _, None, "") if issubclass(
                            cons, Constructor
                        ):
                            tag = cons
                        case _:  # pragma: no cover
                            raise ValueError(f"Invalid interpolation in tag name: {tag}")
                toptag = top.tag if isinstance(top, Node) else type(top)
                if tag != "" and tag != toptag:
                    raise ValueError(f"End tag {tag!r} does not match start tag {toptag!r}")
                stack[-1].children.append(top)
            case ("data", data):
                stack[-1].children.append(data)
            case ("partial", _):
                return True
        return False

    q = deque(tpl)
    while q:
        entry = q.popleft()
        match entry:
            case str():
                for part in parser.iterate(entry):
                    is_partial = _feed(part)

            case Interpolation(subvalue, _, conv, fmt):
                if is_partial:
                    h = abs(hash((id(subvalue), conv, fmt)))
                    ph = f"hype_{h}_{mark}"
                    mappings[ph] = entry
                    q.appendleft(ph)
                else:
                    stack[-1].children.append(entry)
    while len(stack) > 1:
        stack[-2].children.append(stack.pop())
    (node,) = stack
    assert not node.attrs
    match node.children:
        case (Node() as child,):
            return child
        case _:
            return node


class Interpreter(Medley):
    # def parse(self, value: object, conv: Literal["r"], fmt: Literal[""], attr: object):
    #     yield from recurse(hrepr(value, None, ""))

    def gen(self, value: object, conv: Literal["s"], fmt: Literal[""], attr: object):
        yield ("lit", escape(str(value)))

    def gen(self, value: object, conv: Literal["a"], fmt: Literal[""], attr: object):
        yield ("lit", escape(ascii(value)))

    def gen(self, value: object, conv: None, fmt: Literal["res"], attr: object):
        yield ("res", value)

    def gen(self, value: object, conv: None, fmt: Literal["extra"], attr: object):
        yield ("extra", value)

    def gen(self, value: str, conv: None, fmt: Literal["raw"], attr: object):
        yield ("lit", value)

    def gen(self, value: str, conv: None, fmt: str, attr: object):
        assert not fmt  # TODO: apply fmt
        yield ("lit", escape(value))

    def gen(self, value: HasMethod["__h__"], conv: None, fmt: Literal[""], attr: object):  # noqa: F821
        if hres := getattr(value, "__hresources__", None):
            yield ("res", hres)
        yield from recurse(value.__h__(), conv, fmt, attr)

    def gen(self, value: Collection, conv: None, fmt: str, attr: object):
        joiner = " " if attr else ""
        if m := re.fullmatch(pattern=r"<([a-zA-Z_-]+)?(\.[a-zA-Z_-]+)?>", string=fmt):
            tag, cls = m.groups()
            if not tag:
                tag = "div"
            if cls:
                value = [t'<{tag} class="{cls[1:]}">{x}</{tag}>' for x in value if x is not None]
            else:
                value = [t"<{tag}>{x}</{tag}>" for x in value if x is not None]
            fmt = ""
        elif m := re.fullmatch(pattern=r"j(.*)", string=fmt):
            (joiner,) = m.groups()
        if joiner:
            for i, x in enumerate(value):
                if i > 0:
                    yield ("lit", joiner)
                yield from recurse(x, conv, fmt, attr)
        else:
            for x in value:
                yield from recurse(x, conv, fmt, attr)

    def gen(self, value: NoneType, conv: None, fmt: str, attr: object):
        return []

    def gen(self, value: object, conv: None, fmt: str, attr: object):
        yield ("lit", escape(str(value)))

    def gen(self, value: Interpolation, conv: None, fmt: Literal[""], attr: object):
        yield from recurse(value.value, value.conversion, value.format_spec, attr)

    def gen(self, value: Template, conv: None, fmt: Literal[""], attr: object):
        yield from recurse(html(value), conv, fmt, attr)

    def gen(self, value: Constructor, conv: None, fmt: Literal[""], attr: object):
        yield from value.gen(self)

    def gen(self, value: Node, conv: None, fmt: Literal[""], attr: object):
        if value.tag:
            yield ("lit", f"<{value.tag}")
            for k, v in value.attrs:
                if v is None:
                    yield ("lit", f" {k}")
                    continue
                yield ("lit", f' {k}="')
                yield from recurse(v, None, "", k)
                yield ("lit", '"')
            if value.self_closing:
                assert not value.children
                yield ("lit", "/>")
                return
            yield ("lit", ">")
        for child in value.children:
            match child:
                case str():
                    yield ("lit", child)
                case _:
                    yield from recurse(child, None, "", None)
        if value.tag:
            yield ("lit", f"</{value.tag}>")

    def gen(self, value: Any):
        return recurse(value, None, "", None)

    def string_parts(self, root):
        for part in self.gen(root):
            match part:
                case ("lit", s):
                    yield s
                case ("res" | "extra", _):
                    pass
                case _:  # pragma: no cover
                    raise Exception(f"Unrecognized part: {part}")

    def compose(self, root, filter):
        body = []
        resources = deque()
        for part in filter(self.gen(root)):
            match part:
                case ("lit", s):
                    body.append(s)
                case ("res", res):
                    resources.append(res)
                case _:  # pragma: no cover
                    raise Exception(f"Unrecognized part: {part}")
        return "".join(body), resources

    def page(self, root, template=default_template):
        filt = ResourceFilter()
        body, resources = self.compose(root, filt)
        head = []
        while resources:
            res = resources.popleft()
            rnode = html(res)
            content, more_resources = self.compose(rnode, filt)
            head.append(content)
            resources.extend(more_resources)
        return template.format(resources="".join(head), body=body)
