"""
@Author: kang.yang
@Date: 2025/8/18 10:27
"""
from kytest.utils.excel_util import Excel


def get_putong_statement(source_file):
    excel = Excel(source_file)
    statement_list = [
        {'type': row[0], "statement": row[1].strip()} for row in excel.read(sheet_name=0)
    ]
    statements = []
    for statment in statement_list:
        _type = statment["type"]
        _state = statment["statement"]
        if '语义' not in _type:
            statements.append(_state)
    return statements


def get_yuyi_statement(source_file):
    excel = Excel(source_file)
    statement_list = [
        {'type': row[0], "statement": row[1].strip()} for row in excel.read(sheet_name=0)
    ]
    statements = []
    for statment in statement_list:
        _type = statment["type"]
        _state = statment["statement"]
        if '语义' in _type:
            statements.append(_state)
    return statements
