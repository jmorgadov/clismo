import pytest
from clismo.automata import Automata
from clismo import csre


def test_simple_check():
    assert csre.check("a", "a")
    assert csre.check("a", "b") == False
    assert csre.check("a", "aa") == False
    assert csre.check("ab", "ab")
    assert csre.check("ab", "aab") == False


def test_star_op():
    assert csre.check("a*", "")
    assert csre.check("a*", "a")
    assert csre.check("a*", "aa")
    assert csre.check("a*b", "aaab")
    assert csre.check("a*b", "aaa") == False


def test_or_op():
    assert csre.check("a|b", "a")
    assert csre.check("a|b", "b")
    assert csre.check("a|b", "c") == False
    assert csre.check("a|b|c", "c")


def test_escape_char():
    assert csre.check(r"\(a", "a") == False
    assert csre.check(r"\(a", "(a")
    assert csre.check(r"a\*", "a*")
    assert csre.check(r"a\*", "a") == False
    assert csre.check(r"a\**", "a***")
    assert csre.check(r"a\**", "a")
    assert csre.check(r"a\\*", "a\\\\")


def test_special_chars():
    assert csre.check(r"a..*b", "afoob")
    assert csre.check(r"a.*b", "ab")
    assert csre.check(r"a.*b", "afoob")
    assert csre.check(r"a\sb", "a b")
    assert csre.check(r"a\nb", "a\nb")
    assert csre.check(r"a\tb", "a\tb")
    assert csre.check(r"a\rb", "a\rb")
    assert csre.check(r"a\a*b", "afoob")
    assert csre.check(r"a\a*b", "aFoob") == False
    assert csre.check(r"a\A*b", "aFOOb")
    assert csre.check(r"a\A*b", "aFoob") == False
    assert csre.check(r"a(\A|\a)*b", "aFoob")
    assert csre.check(r"a\db", "a5b")
    assert csre.check(r"a\d*b", "a5x4b") == False
    assert csre.check(r"a\d*.\db", "a5x4b")


def test_combined_op():
    assert csre.check("aa*|b*", "a")
    assert csre.check("aa*|b*", "b")
    assert csre.check("aa*|b*", "")
    assert csre.check("aa*b*", "a")
    assert csre.check("aa*b*", "b") == False
    assert csre.check("aa*b*", "ab")
    assert csre.check("aa*b*", "aab")
    assert csre.check("(a|b)*", "aabbababa")


def test_negation():
    assert csre.check(r"(^a)", "b")
    assert csre.check(r"(^a)", "a") == False
    assert csre.check(r"(^a)(^a)*", "bcdef")
    assert csre.check(r"'((^')|(\\'))*(^\\)'", "'asfew'")
    assert csre.check(r"'((^')|(\\'))*(^\\)'", "'ab\\'") == False
    assert csre.check(r"'((^')|(\\'))*(^\\)'", "'asfew\\'a") == False
    assert csre.check(r"'((^')|(\\'))*(^\\)'", "'asfew\\'a'")
    assert csre.check(r"'((^')|(\\'))*(^\\)'", "'asfew' foo 'bar'") == False
    assert csre.check(r"'((^')|(\\'))*(^\\)'", "'asfew\\' foo \\'bar'")


def test_match():
    assert csre.match("a", "a")
    assert csre.match("a", "b") is None

    re_match = csre.match("a", "aaaa")
    assert re_match
    assert re_match.end == 1

    re_match = csre.match(r"'((^')|(\\'))*(^\\)'", "'aaa'")
    assert re_match
    assert re_match.end == 5

    re_match = csre.match(r"'((^')|(\\'))*(^\\)'", "'aaa' foo")
    assert re_match
    assert re_match.end == 5

    re_match = csre.match(r"'((^')|(\\'))*(^\\)'", "'aaa' foo 'bar'")
    assert re_match
    assert re_match.end == 5

    re_match = csre.match(r"'((^')|(\\'))*(^\\)'", "'aaa\\' foo \\'bar'")
    assert re_match
    assert re_match.end == 17
