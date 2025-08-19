# -*- coding: utf-8 -*-
"""
ADQL processor. Its task is to check if a query has any syntax errors and
to extract all accessed columns as well as keywords and functions being
used in a query.

"""

from __future__ import absolute_import, print_function

__all__ = ["ADQLQueryProcessor"]

from ..common import SQLQueryProcessor
from .ADQLLexer import ADQLLexer
from .ADQLParser import ADQLParser
from .ADQLParserListener import ADQLParserListener


class ADQLQueryProcessor(SQLQueryProcessor):
    def __init__(self, query=None):
        super().__init__(
            ADQLLexer, ADQLParser, ADQLParserListener, '"', query
        )
