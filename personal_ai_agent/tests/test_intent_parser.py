import builtins
import os

from intent_parser import parse_intent

def test_parse_intent_search_notes():
    assert parse_intent("search my notes for meeting") == "search_notes"


def test_parse_intent_help():
    assert parse_intent("help me") == "help"
