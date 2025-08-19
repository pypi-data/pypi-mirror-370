from temper_std.json import JsonAdapter, JsonProducer, JsonSyntaxTree, InterchangeContext, JsonString
from datetime import date as date66
from builtins import str as str20, int as int24, bool as bool21, list as list17, len as len14
from temper_core import cast_by_type as cast_by_type29, date_to_string as date_to_string63, date_from_iso_string as date_from_iso_string64, int_to_string as int_to_string15, string_get as string_get12, string_next as string_next13, string_count_between as string_count_between65
from typing import Sequence as Sequence23
from temper_std.json import JsonAdapter, JsonString
date_to_string_2499 = date_to_string63
date_from_iso_string_2500 = date_from_iso_string64
int_to_string_2501 = int_to_string15
len_2502 = len14
string_get_2503 = string_get12
string_next_2505 = string_next13
string_count_between_2506 = string_count_between65
class DateJsonAdapter_109(JsonAdapter['date66']):
    __slots__ = ()
    def encode_to_json(this_119, x_115: 'date66', p_116: 'JsonProducer') -> 'None':
        encode_to_json_90(x_115, p_116)
    def decode_from_json(this_120, t_117: 'JsonSyntaxTree', ic_118: 'InterchangeContext') -> 'date66':
        return decode_from_json_93(t_117, ic_118)
    def __init__(this_121) -> None:
        pass
# Type `std/temporal/`.Date connected to datetime.date
def encode_to_json_90(this_20: 'date66', p_91: 'JsonProducer') -> 'None':
    t_312: 'str20' = date_to_string_2499(this_20)
    p_91.string_value(t_312)
def decode_from_json_93(t_94: 'JsonSyntaxTree', ic_95: 'InterchangeContext') -> 'date66':
    t_189: 'JsonString'
    t_189 = cast_by_type29(t_94, JsonString)
    return date_from_iso_string_2500(t_189.content)
def json_adapter_123() -> 'JsonAdapter[date66]':
    return DateJsonAdapter_109()
days_in_month_34: 'Sequence23[int24]' = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
def is_leap_year_32(year_41: 'int24') -> 'bool21':
    return_21: 'bool21'
    t_262: 'int24'
    if year_41 % 4 == 0:
        if year_41 % 100 != 0:
            return_21 = True
        else:
            t_262 = year_41 % 400
            return_21 = t_262 == 0
    else:
        return_21 = False
    return return_21
def pad_to_33(min_width_43: 'int24', num_44: 'int24', sb_45: 'list17[str20]') -> 'None':
    "If the decimal representation of \\|num\\| is longer than [minWidth],\nthen appends that representation.\nOtherwise any sign for [num] followed by enough zeroes to bring the\nwhole length up to [minWidth].\n\n```temper\n// When the width is greater than the decimal's length,\n// we pad to that width.\n\"0123\" == do {\n  let sb = new StringBuilder();\n  padTo(4, 123, sb);\n  sb.toString()\n}\n\n// When the width is the same or lesser, we just use the string form.\n\"123\" == do {\n  let sb = new StringBuilder();\n  padTo(2, 123, sb);\n  sb.toString()\n}\n\n// The sign is always on the left.\n\"-01\" == do {\n  let sb = new StringBuilder();\n  padTo(3, -1, sb);\n  sb.toString()\n}\n```\n\nminWidth__43: Int\n\nnum__44: Int\n\nsb__45: builtins.list<String>\n"
    t_345: 'int24'
    t_347: 'int24'
    t_256: 'bool21'
    decimal_47: 'str20' = int_to_string_2501(num_44, 10)
    decimal_index_48: 'int24' = 0
    decimal_end_49: 'int24' = len_2502(decimal_47)
    if decimal_index_48 < decimal_end_49:
        t_345 = string_get_2503(decimal_47, decimal_index_48)
        t_256 = t_345 == 45
    else:
        t_256 = False
    if t_256:
        sb_45.append('-')
        t_347 = string_next_2505(decimal_47, decimal_index_48)
        decimal_index_48 = t_347
    t_348: 'int24' = string_count_between_2506(decimal_47, decimal_index_48, decimal_end_49)
    n_needed_50: 'int24' = min_width_43 - t_348
    while n_needed_50 > 0:
        sb_45.append('0')
        n_needed_50 = n_needed_50 - 1
    sb_45.append(decimal_47[decimal_index_48 : decimal_end_49])
day_of_week_lookup_table_leapy_35: 'Sequence23[int24]' = (0, 0, 3, 4, 0, 2, 5, 0, 3, 6, 1, 4, 6)
day_of_week_lookup_table_not_leapy_36: 'Sequence23[int24]' = (0, 0, 3, 3, 6, 1, 4, 6, 2, 5, 0, 3, 5)
