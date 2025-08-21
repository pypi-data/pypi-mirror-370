from dataclasses import dataclass

import pytest

from hypetext.h import Constructor, html


class TodoList:
    def __init__(self, *todos):
        self.todos = list(todos)

    def __h__(self):
        return t"<ol>{self.todos:<li>}</ol>"

    __hresources__ = t"""<style>ol {{ color: "blue" }}</style>"""


@dataclass
class Bold:
    message: object

    def __h__(self):
        return t"<b>{self.message}</b>"


@dataclass
class Italic:
    message: object

    def __h__(self):
        return t"<i>{self.message}</i>"


def tostr(t):
    return str(html(t))


def topage(t):
    return html(t).page()


def test_no_interpolation():
    assert tostr("<b>hello</b>") == "<b>hello</b>"


def test_alt_closing():
    assert tostr("<b>hello</>") == "<b>hello</b>"


def test_auto_closing():
    assert tostr("<b><i>hello") == "<b><i>hello</i></b>"


def test_tag_mismatch():
    with pytest.raises(Exception, match="End tag 'i' does not match"):
        tostr("<b>hello</i>")


def test_h():
    assert tostr(Bold("HELLO")) == "<b>HELLO</b>"
    assert tostr(t"<div>{Bold('HELLO')}</div>") == "<div><b>HELLO</b></div>"
    assert tostr(Bold("<hello>")) == "<b>&lt;hello&gt;</b>"
    assert tostr(Bold(Italic("HELLO"))) == "<b><i>HELLO</i></b>"
    assert tostr(t"{Bold('HELLO')!s}") == "Bold(message=&#x27;HELLO&#x27;)"


def test_raw():
    x = "1<2"
    assert tostr(t"<b>{x}</b>") == "<b>1&lt;2</b>"
    assert tostr(t"<b>{x:raw}</b>") == "<b>1<2</b>"


def test_list_wrap():
    xs = [1, 2, 3, 4]
    assert tostr(xs) == "1234"
    assert tostr(t"{xs:<li>}") == "<li>1</li><li>2</li><li>3</li><li>4</li>"
    assert tostr(t"{xs:<li.z>}").startswith('<li class="z">1</li><li class="z">2</li>')
    assert tostr(t"{xs:<.xx>}").startswith('<div class="xx">1</div><div class="xx">2</div>')


def test_list_join():
    xs = [1, 2, 3, 4]
    assert tostr(xs) == "1234"
    assert tostr(t"{xs:j }") == "1 2 3 4"
    assert tostr(t"{xs:j,}") == "1,2,3,4"
    assert tostr(t"{xs:j<br>}") == "1<br>2<br>3<br>4"


def test_none():
    a = 1
    b = None
    c = 2
    assert tostr(t"{a}{b}{c}") == "12"


def test_none_in_list():
    xs = [1, None, 2]
    assert tostr(t"{xs:<b>}") == "<b>1</b><b>2</b>"


def test_autoquote_in_attributes():
    c = "klass"
    assert tostr(t"<div class={c}>hello</div>") == '<div class="klass">hello</div>'
    assert tostr(t"<div class={c} xx>hello</div>") == '<div class="klass" xx>hello</div>'
    assert tostr(t"<div class={c}_x>hello</div>") == '<div class="klass_x">hello</div>'
    assert tostr(t"<div>class={c}</div>") == "<div>class=klass</div>"


def test_attr_list():
    cs = ["alice", "bob", "charlie"]
    assert tostr(t"<div class={cs}></div>") == '<div class="alice bob charlie"></div>'


class Repeat(Constructor):
    def __init__(self, *children, n):
        self.n = int(n)
        self.children = list(children)

    def gen(self, interp):
        for _ in range(self.n):
            yield from interp.gen(self.children, None, "", None)


def test_bad_tag():
    with pytest.raises(ValueError, match="Invalid interpolation"):
        tostr(t"<{1}>xxx</{1}>")


def test_custom_element():
    a = tostr(t"<{Repeat} n=3><b>hello</b></{Repeat}>")
    assert a == "<b>hello</b>" * 3


def test_resources_explicit(file_regression):
    sty = t'<style>div {{ color: "blue"; }}</style>'
    h = html(t"<div>cool{sty:res}</div>")
    file_regression.check(h.page())


def test_resources(file_regression):
    file_regression.check(topage(TodoList("do this", "do that")))


def test_resources_norepeat(file_regression):
    td1 = TodoList("do this", "do that")
    td2 = TodoList("cool", "beans")
    body = t"{td1}<br/>{td2}"
    file_regression.check(topage(body))
