from abc import ABCMeta as ABCMeta19
from builtins import str as str20, bool as bool21, int as int24, list as list17, isinstance as isinstance28, len as len14, tuple as tuple18
from typing import Callable as Callable22, Sequence as Sequence23, Union as Union25, Any as Any27, ClassVar as ClassVar31, MutableSequence as MutableSequence32
from types import MappingProxyType as MappingProxyType26
from temper_core import cast_by_type as cast_by_type29, Label as Label30, Pair as Pair0, map_constructor as map_constructor1, generic_eq as generic_eq7, list_get as list_get9, string_from_code_point as string_from_code_point10, string_get as string_get12, string_next as string_next13, int_to_string as int_to_string15, str_cat as str_cat16
from temper_core.regex import regex_compile_formatted as regex_compile_formatted2, regex_compiled_found as regex_compiled_found3, regex_compiled_find as regex_compiled_find4, regex_compiled_replace as regex_compiled_replace5, regex_compiled_split as regex_compiled_split6, regex_formatter_push_capture_name as regex_formatter_push_capture_name8, regex_formatter_push_code_to as regex_formatter_push_code_to11
pair_2416 = Pair0
map_constructor_2417 = map_constructor1
regex_compile_formatted_2418 = regex_compile_formatted2
regex_compiled_found_2419 = regex_compiled_found3
regex_compiled_find_2420 = regex_compiled_find4
regex_compiled_replace_2421 = regex_compiled_replace5
regex_compiled_split_2422 = regex_compiled_split6
generic_eq_2424 = generic_eq7
regex_formatter_push_capture_name_2426 = regex_formatter_push_capture_name8
list_get_2427 = list_get9
string_from_code_point_2428 = string_from_code_point10
regex_formatter_push_code_to_2429 = regex_formatter_push_code_to11
string_get_2431 = string_get12
string_next_2432 = string_next13
len_2433 = len14
int_to_string_2435 = int_to_string15
str_cat_2436 = str_cat16
list_2438 = list17
tuple_2440 = tuple18
class RegexNode(metaclass = ABCMeta19):
    def compiled(this_42) -> 'Regex':
        return Regex(this_42)
    def found(this_43, text_170: 'str20') -> 'bool21':
        return this_43.compiled().found(text_170)
    def find(this_44, text_173: 'str20') -> 'Match':
        return this_44.compiled().find(text_173)
    def replace(this_45, text_176: 'str20', format_177: 'Callable22[[Match], str20]') -> 'str20':
        'Replace and split functions are also available. Both apply to all matches in\nthe string, replacing all or splitting at all.\n\nthis__45: RegexNode\n\ntext__176: String\n\nformat__177: fn (Match): String\n'
        return this_45.compiled().replace(text_176, format_177)
    def split(this_46, text_180: 'str20') -> 'Sequence23[str20]':
        return this_46.compiled().split(text_180)
class Capture(RegexNode):
    '`Capture` is a [group](#groups) that remembers the matched text for later\naccess. Temper supports only named matches, with current intended syntax\n`/(?name = ...)/`.'
    name_182: 'str20'
    item_183: 'RegexNode'
    __slots__ = ('name_182', 'item_183')
    def __init__(this_87, name_185: 'str20', item_186: 'RegexNode') -> None:
        this_87.name_182 = name_185
        this_87.item_183 = item_186
    @property
    def name(this_437) -> 'str20':
        return this_437.name_182
    @property
    def item(this_440) -> 'RegexNode':
        return this_440.item_183
class CodePart(RegexNode, metaclass = ABCMeta19):
    pass
class CodePoints(CodePart):
    value_187: 'str20'
    __slots__ = ('value_187',)
    def __init__(this_89, value_189: 'str20') -> None:
        this_89.value_187 = value_189
    @property
    def value(this_443) -> 'str20':
        return this_443.value_187
class Special(RegexNode, metaclass = ABCMeta19):
    pass
class SpecialSet(CodePart, Special, metaclass = ABCMeta19):
    pass
class CodeRange(CodePart):
    min_197: 'int24'
    max_198: 'int24'
    __slots__ = ('min_197', 'max_198')
    def __init__(this_105, min_200: 'int24', max_201: 'int24') -> None:
        this_105.min_197 = min_200
        this_105.max_198 = max_201
    @property
    def min(this_446) -> 'int24':
        return this_446.min_197
    @property
    def max(this_449) -> 'int24':
        return this_449.max_198
class CodeSet(RegexNode):
    items_202: 'Sequence23[CodePart]'
    negated_203: 'bool21'
    __slots__ = ('items_202', 'negated_203')
    def __init__(this_107, items_205: 'Sequence23[CodePart]', negated_535: 'Union25[bool21, None]' = None) -> None:
        _negated_535: 'Union25[bool21, None]' = negated_535
        negated_206: 'bool21'
        if _negated_535 is None:
            negated_206 = False
        else:
            negated_206 = _negated_535
        this_107.items_202 = items_205
        this_107.negated_203 = negated_206
    @property
    def items(this_452) -> 'Sequence23[CodePart]':
        return this_452.items_202
    @property
    def negated(this_455) -> 'bool21':
        return this_455.negated_203
class Or(RegexNode):
    '`Or` matches any one of multiple options, such as `/ab|cd|e*/`.'
    items_207: 'Sequence23[RegexNode]'
    __slots__ = ('items_207',)
    def __init__(this_110, items_209: 'Sequence23[RegexNode]') -> None:
        this_110.items_207 = items_209
    @property
    def items(this_458) -> 'Sequence23[RegexNode]':
        return this_458.items_207
class Repeat(RegexNode):
    item_210: 'RegexNode'
    min_211: 'int24'
    max_212: 'Union25[int24, None]'
    reluctant_213: 'bool21'
    __slots__ = ('item_210', 'min_211', 'max_212', 'reluctant_213')
    def __init__(this_113, item_215: 'RegexNode', min_216: 'int24', max_217: 'Union25[int24, None]', reluctant_537: 'Union25[bool21, None]' = None) -> None:
        _reluctant_537: 'Union25[bool21, None]' = reluctant_537
        reluctant_218: 'bool21'
        if _reluctant_537 is None:
            reluctant_218 = False
        else:
            reluctant_218 = _reluctant_537
        this_113.item_210 = item_215
        this_113.min_211 = min_216
        this_113.max_212 = max_217
        this_113.reluctant_213 = reluctant_218
    @property
    def item(this_461) -> 'RegexNode':
        return this_461.item_210
    @property
    def min(this_464) -> 'int24':
        return this_464.min_211
    @property
    def max(this_467) -> 'Union25[int24, None]':
        return this_467.max_212
    @property
    def reluctant(this_470) -> 'bool21':
        return this_470.reluctant_213
class Sequence(RegexNode):
    '`Sequence` strings along multiple other regexes in order.'
    items_227: 'Sequence23[RegexNode]'
    __slots__ = ('items_227',)
    def __init__(this_119, items_229: 'Sequence23[RegexNode]') -> None:
        this_119.items_227 = items_229
    @property
    def items(this_473) -> 'Sequence23[RegexNode]':
        return this_473.items_227
class Match:
    full_230: 'Group'
    groups_231: 'MappingProxyType26[str20, Group]'
    __slots__ = ('full_230', 'groups_231')
    def __init__(this_122, full_233: 'Group', groups_234: 'MappingProxyType26[str20, Group]') -> None:
        this_122.full_230 = full_233
        this_122.groups_231 = groups_234
    @property
    def full(this_488) -> 'Group':
        return this_488.full_230
    @property
    def groups(this_491) -> 'MappingProxyType26[str20, Group]':
        return this_491.groups_231
class Group:
    name_235: 'str20'
    value_236: 'str20'
    begin_237: 'int24'
    end_238: 'int24'
    __slots__ = ('name_235', 'value_236', 'begin_237', 'end_238')
    def __init__(this_125, name_240: 'str20', value_241: 'str20', begin_242: 'int24', end_243: 'int24') -> None:
        this_125.name_235 = name_240
        this_125.value_236 = value_241
        this_125.begin_237 = begin_242
        this_125.end_238 = end_243
    @property
    def name(this_476) -> 'str20':
        return this_476.name_235
    @property
    def value(this_479) -> 'str20':
        return this_479.value_236
    @property
    def begin(this_482) -> 'int24':
        return this_482.begin_237
    @property
    def end(this_485) -> 'int24':
        return this_485.end_238
class RegexRefs_54:
    code_points_244: 'CodePoints'
    group_245: 'Group'
    match_246: 'Match'
    or_object_247: 'Or'
    __slots__ = ('code_points_244', 'group_245', 'match_246', 'or_object_247')
    def __init__(this_127, code_points_539: 'Union25[CodePoints, None]' = None, group_541: 'Union25[Group, None]' = None, match_543: 'Union25[Match, None]' = None, or_object_545: 'Union25[Or, None]' = None) -> None:
        _code_points_539: 'Union25[CodePoints, None]' = code_points_539
        _group_541: 'Union25[Group, None]' = group_541
        _match_543: 'Union25[Match, None]' = match_543
        _or_object_545: 'Union25[Or, None]' = or_object_545
        t_1289: 'CodePoints'
        t_1290: 'Group'
        t_1292: 'MappingProxyType26[str20, Group]'
        t_1293: 'Match'
        t_1294: 'Or'
        code_points_249: 'CodePoints'
        if _code_points_539 is None:
            t_1289 = CodePoints('')
            code_points_249 = t_1289
        else:
            code_points_249 = _code_points_539
        group_250: 'Group'
        if _group_541 is None:
            t_1290 = Group('', '', 0, 0)
            group_250 = t_1290
        else:
            group_250 = _group_541
        match_251: 'Match'
        if _match_543 is None:
            t_1292 = map_constructor_2417((pair_2416('', group_250),))
            t_1293 = Match(group_250, t_1292)
            match_251 = t_1293
        else:
            match_251 = _match_543
        or_object_252: 'Or'
        if _or_object_545 is None:
            t_1294 = Or(())
            or_object_252 = t_1294
        else:
            or_object_252 = _or_object_545
        this_127.code_points_244 = code_points_249
        this_127.group_245 = group_250
        this_127.match_246 = match_251
        this_127.or_object_247 = or_object_252
    @property
    def code_points(this_494) -> 'CodePoints':
        return this_494.code_points_244
    @property
    def group(this_497) -> 'Group':
        return this_497.group_245
    @property
    def match_(this_500) -> 'Match':
        return this_500.match_246
    @property
    def or_object(this_503) -> 'Or':
        return this_503.or_object_247
class Regex:
    data_253: 'RegexNode'
    compiled_272: 'Any27'
    __slots__ = ('data_253', 'compiled_272')
    def __init__(this_55, data_255: 'RegexNode') -> None:
        t_412: 'RegexNode' = data_255
        this_55.data_253 = t_412
        formatted_257: 'str20' = RegexFormatter_64.regex_format(data_255)
        t_1172: 'Any27' = regex_compile_formatted_2418(data_255, formatted_257)
        this_55.compiled_272 = t_1172
    def found(this_56, text_259: 'str20') -> 'bool21':
        return regex_compiled_found_2419(this_56, this_56.compiled_272, text_259)
    def find(this_57, text_262: 'str20', begin_547: 'Union25[int24, None]' = None) -> 'Match':
        _begin_547: 'Union25[int24, None]' = begin_547
        begin_263: 'int24'
        if _begin_547 is None:
            begin_263 = 0
        else:
            begin_263 = _begin_547
        return regex_compiled_find_2420(this_57, this_57.compiled_272, text_262, begin_263, regex_refs_162)
    def replace(this_58, text_266: 'str20', format_267: 'Callable22[[Match], str20]') -> 'str20':
        return regex_compiled_replace_2421(this_58, this_58.compiled_272, text_266, format_267, regex_refs_162)
    def split(this_59, text_270: 'str20') -> 'Sequence23[str20]':
        return regex_compiled_split_2422(this_59, this_59.compiled_272, text_270, regex_refs_162)
    @property
    def data(this_530) -> 'RegexNode':
        return this_530.data_253
class RegexFormatter_64:
    out_294: 'list17[str20]'
    __slots__ = ('out_294',)
    @staticmethod
    def regex_format(data_300: 'RegexNode') -> 'str20':
        return RegexFormatter_64().format(data_300)
    def format(this_65, regex_303: 'RegexNode') -> 'str20':
        this_65.push_regex_305(regex_303)
        return ''.join(this_65.out_294)
    def push_regex_305(this_66, regex_306: 'RegexNode') -> 'None':
        t_890: 'Capture'
        t_892: 'CodePoints'
        t_894: 'CodeRange'
        t_896: 'CodeSet'
        t_898: 'Or'
        t_900: 'Repeat'
        t_902: 'Sequence'
        if isinstance28(regex_306, Capture):
            t_890 = cast_by_type29(regex_306, Capture)
            this_66.push_capture_308(t_890)
        elif isinstance28(regex_306, CodePoints):
            t_892 = cast_by_type29(regex_306, CodePoints)
            this_66.push_code_points_326(t_892, False)
        elif isinstance28(regex_306, CodeRange):
            t_894 = cast_by_type29(regex_306, CodeRange)
            this_66.push_code_range_332(t_894)
        elif isinstance28(regex_306, CodeSet):
            t_896 = cast_by_type29(regex_306, CodeSet)
            this_66.push_code_set_338(t_896)
        elif isinstance28(regex_306, Or):
            t_898 = cast_by_type29(regex_306, Or)
            this_66.push_or_350(t_898)
        elif isinstance28(regex_306, Repeat):
            t_900 = cast_by_type29(regex_306, Repeat)
            this_66.push_repeat_354(t_900)
        elif isinstance28(regex_306, Sequence):
            t_902 = cast_by_type29(regex_306, Sequence)
            this_66.push_sequence_359(t_902)
        elif generic_eq_2424(regex_306, begin):
            this_66.out_294.append('^')
        elif generic_eq_2424(regex_306, dot):
            this_66.out_294.append('.')
        elif generic_eq_2424(regex_306, end):
            this_66.out_294.append('$')
        elif generic_eq_2424(regex_306, word_boundary):
            this_66.out_294.append('\\b')
        elif generic_eq_2424(regex_306, digit):
            this_66.out_294.append('\\d')
        elif generic_eq_2424(regex_306, space):
            this_66.out_294.append('\\s')
        elif generic_eq_2424(regex_306, word):
            this_66.out_294.append('\\w')
    def push_capture_308(this_67, capture_309: 'Capture') -> 'None':
        this_67.out_294.append('(')
        t_863: 'list17[str20]' = this_67.out_294
        t_1259: 'str20' = capture_309.name
        regex_formatter_push_capture_name_2426(this_67, t_863, t_1259)
        t_1261: 'RegexNode' = capture_309.item
        this_67.push_regex_305(t_1261)
        this_67.out_294.append(')')
    def push_code_315(this_69, code_316: 'int24', inside_code_set_317: 'bool21') -> 'None':
        t_850: 'bool21'
        t_851: 'bool21'
        t_852: 'str20'
        t_854: 'str20'
        t_855: 'bool21'
        t_856: 'bool21'
        t_857: 'bool21'
        t_858: 'bool21'
        t_859: 'str20'
        with Label30() as fn_318:
            special_escape_319: 'str20'
            if code_316 == Codes_81.carriage_return:
                special_escape_319 = 'r'
            elif code_316 == Codes_81.newline:
                special_escape_319 = 'n'
            elif code_316 == Codes_81.tab:
                special_escape_319 = 't'
            else:
                special_escape_319 = ''
            if special_escape_319 != '':
                this_69.out_294.append('\\')
                this_69.out_294.append(special_escape_319)
                fn_318.break_()
            if code_316 <= 127:
                escape_need_320: 'int24' = list_get_2427(escape_needs_163, code_316)
                if escape_need_320 == 2:
                    t_851 = True
                else:
                    if inside_code_set_317:
                        t_850 = code_316 == Codes_81.dash
                    else:
                        t_850 = False
                    t_851 = t_850
                if t_851:
                    this_69.out_294.append('\\')
                    t_852 = string_from_code_point_2428(code_316)
                    this_69.out_294.append(t_852)
                    fn_318.break_()
                elif escape_need_320 == 0:
                    t_854 = string_from_code_point_2428(code_316)
                    this_69.out_294.append(t_854)
                    fn_318.break_()
            if code_316 >= Codes_81.supplemental_min:
                t_858 = True
            else:
                if code_316 > Codes_81.high_control_max:
                    if Codes_81.surrogate_min <= code_316:
                        t_855 = code_316 <= Codes_81.surrogate_max
                    else:
                        t_855 = False
                    if t_855:
                        t_856 = True
                    else:
                        t_856 = code_316 == Codes_81.uint16_max
                    t_857 = not t_856
                else:
                    t_857 = False
                t_858 = t_857
            if t_858:
                t_859 = string_from_code_point_2428(code_316)
                this_69.out_294.append(t_859)
            else:
                regex_formatter_push_code_to_2429(this_69, this_69.out_294, code_316, inside_code_set_317)
    def push_code_points_326(this_71, code_points_327: 'CodePoints', inside_code_set_328: 'bool21') -> 'None':
        t_1245: 'int24'
        t_1247: 'int24'
        value_330: 'str20' = code_points_327.value
        index_331: 'int24' = 0
        while True:
            if not len14(value_330) > index_331:
                break
            t_1245 = string_get_2431(value_330, index_331)
            this_71.push_code_315(t_1245, inside_code_set_328)
            t_1247 = string_next_2432(value_330, index_331)
            index_331 = t_1247
    def push_code_range_332(this_72, code_range_333: 'CodeRange') -> 'None':
        this_72.out_294.append('[')
        this_72.push_code_range_unwrapped_335(code_range_333)
        this_72.out_294.append(']')
    def push_code_range_unwrapped_335(this_73, code_range_336: 'CodeRange') -> 'None':
        t_1235: 'int24' = code_range_336.min
        this_73.push_code_315(t_1235, True)
        this_73.out_294.append('-')
        t_1238: 'int24' = code_range_336.max
        this_73.push_code_315(t_1238, True)
    def push_code_set_338(this_74, code_set_339: 'CodeSet') -> 'None':
        t_1229: 'int24'
        t_1231: 'CodePart'
        t_835: 'CodeSet'
        adjusted_341: 'RegexNode' = this_74.adjust_code_set_343(code_set_339, regex_refs_162)
        if isinstance28(adjusted_341, CodeSet):
            t_835 = cast_by_type29(adjusted_341, CodeSet)
            this_74.out_294.append('[')
            if t_835.negated:
                this_74.out_294.append('^')
            i_342: 'int24' = 0
            while True:
                t_1229 = len_2433(t_835.items)
                if not i_342 < t_1229:
                    break
                t_1231 = list_get_2427(t_835.items, i_342)
                this_74.push_code_set_item_347(t_1231)
                i_342 = i_342 + 1
            this_74.out_294.append(']')
        else:
            this_74.push_regex_305(adjusted_341)
    def adjust_code_set_343(this_75, code_set_344: 'CodeSet', regex_refs_345: 'RegexRefs_54') -> 'RegexNode':
        return code_set_344
    def push_code_set_item_347(this_76, code_part_348: 'CodePart') -> 'None':
        t_820: 'CodePoints'
        t_822: 'CodeRange'
        t_824: 'SpecialSet'
        if isinstance28(code_part_348, CodePoints):
            t_820 = cast_by_type29(code_part_348, CodePoints)
            this_76.push_code_points_326(t_820, True)
        elif isinstance28(code_part_348, CodeRange):
            t_822 = cast_by_type29(code_part_348, CodeRange)
            this_76.push_code_range_unwrapped_335(t_822)
        elif isinstance28(code_part_348, SpecialSet):
            t_824 = cast_by_type29(code_part_348, SpecialSet)
            this_76.push_regex_305(t_824)
    def push_or_350(this_77, or_351: 'Or') -> 'None':
        t_1208: 'RegexNode'
        t_1211: 'int24'
        t_1214: 'RegexNode'
        if not (not or_351.items):
            this_77.out_294.append('(?:')
            t_1208 = list_get_2427(or_351.items, 0)
            this_77.push_regex_305(t_1208)
            i_353: 'int24' = 1
            while True:
                t_1211 = len_2433(or_351.items)
                if not i_353 < t_1211:
                    break
                this_77.out_294.append('|')
                t_1214 = list_get_2427(or_351.items, i_353)
                this_77.push_regex_305(t_1214)
                i_353 = i_353 + 1
            this_77.out_294.append(')')
    def push_repeat_354(this_78, repeat_355: 'Repeat') -> 'None':
        t_1196: 'str20'
        t_1199: 'str20'
        t_796: 'bool21'
        t_797: 'bool21'
        t_798: 'bool21'
        this_78.out_294.append('(?:')
        t_1188: 'RegexNode' = repeat_355.item
        this_78.push_regex_305(t_1188)
        this_78.out_294.append(')')
        min_357: 'int24' = repeat_355.min
        max_358: 'Union25[int24, None]' = repeat_355.max
        if min_357 == 0:
            t_796 = max_358 == 1
        else:
            t_796 = False
        if t_796:
            this_78.out_294.append('?')
        else:
            if min_357 == 0:
                t_797 = max_358 is None
            else:
                t_797 = False
            if t_797:
                this_78.out_294.append('*')
            else:
                if min_357 == 1:
                    t_798 = max_358 is None
                else:
                    t_798 = False
                if t_798:
                    this_78.out_294.append('+')
                else:
                    t_1196 = int_to_string_2435(min_357)
                    this_78.out_294.append(str_cat_2436('{', t_1196))
                    if min_357 != max_358:
                        this_78.out_294.append(',')
                        if not max_358 is None:
                            t_1199 = int_to_string_2435(max_358)
                            this_78.out_294.append(t_1199)
                    this_78.out_294.append('}')
        if repeat_355.reluctant:
            this_78.out_294.append('?')
    def push_sequence_359(this_79, sequence_360: 'Sequence') -> 'None':
        t_1183: 'int24'
        t_1185: 'RegexNode'
        i_362: 'int24' = 0
        while True:
            t_1183 = len_2433(sequence_360.items)
            if not i_362 < t_1183:
                break
            t_1185 = list_get_2427(sequence_360.items, i_362)
            this_79.push_regex_305(t_1185)
            i_362 = i_362 + 1
    def max_code(this_80, code_part_364: 'CodePart') -> 'Union25[int24, None]':
        return_157: 'Union25[int24, None]'
        t_1179: 'int24'
        t_783: 'CodePoints'
        if isinstance28(code_part_364, CodePoints):
            t_783 = cast_by_type29(code_part_364, CodePoints)
            value_366: 'str20' = t_783.value
            if not value_366:
                return_157 = None
            else:
                max_367: 'int24' = 0
                index_368: 'int24' = 0
                while True:
                    if not len14(value_366) > index_368:
                        break
                    next_369: 'int24' = string_get_2431(value_366, index_368)
                    if next_369 > max_367:
                        max_367 = next_369
                    t_1179 = string_next_2432(value_366, index_368)
                    index_368 = t_1179
                return_157 = max_367
        elif isinstance28(code_part_364, CodeRange):
            return_157 = cast_by_type29(code_part_364, CodeRange).max
        elif generic_eq_2424(code_part_364, digit):
            return_157 = Codes_81.digit9
        elif generic_eq_2424(code_part_364, space):
            return_157 = Codes_81.space
        elif generic_eq_2424(code_part_364, word):
            return_157 = Codes_81.lower_z
        else:
            return_157 = None
        return return_157
    def __init__(this_138) -> None:
        t_1173: 'list17[str20]' = ['']
        this_138.out_294 = t_1173
class Codes_81:
    ampersand: ClassVar31['int24']
    backslash: ClassVar31['int24']
    caret: ClassVar31['int24']
    carriage_return: ClassVar31['int24']
    curly_left: ClassVar31['int24']
    curly_right: ClassVar31['int24']
    dash: ClassVar31['int24']
    dot: ClassVar31['int24']
    high_control_min: ClassVar31['int24']
    high_control_max: ClassVar31['int24']
    digit0: ClassVar31['int24']
    digit9: ClassVar31['int24']
    lower_a: ClassVar31['int24']
    lower_z: ClassVar31['int24']
    newline: ClassVar31['int24']
    peso: ClassVar31['int24']
    pipe: ClassVar31['int24']
    plus: ClassVar31['int24']
    question: ClassVar31['int24']
    round_left: ClassVar31['int24']
    round_right: ClassVar31['int24']
    slash: ClassVar31['int24']
    square_left: ClassVar31['int24']
    square_right: ClassVar31['int24']
    star: ClassVar31['int24']
    tab: ClassVar31['int24']
    tilde: ClassVar31['int24']
    upper_a: ClassVar31['int24']
    upper_z: ClassVar31['int24']
    space: ClassVar31['int24']
    surrogate_min: ClassVar31['int24']
    surrogate_max: ClassVar31['int24']
    supplemental_min: ClassVar31['int24']
    uint16_max: ClassVar31['int24']
    underscore: ClassVar31['int24']
    __slots__ = ()
    def __init__(this_159) -> None:
        pass
Codes_81.ampersand = 38
Codes_81.backslash = 92
Codes_81.caret = 94
Codes_81.carriage_return = 13
Codes_81.curly_left = 123
Codes_81.curly_right = 125
Codes_81.dash = 45
Codes_81.dot = 46
Codes_81.high_control_min = 127
Codes_81.high_control_max = 159
Codes_81.digit0 = 48
Codes_81.digit9 = 57
Codes_81.lower_a = 97
Codes_81.lower_z = 122
Codes_81.newline = 10
Codes_81.peso = 36
Codes_81.pipe = 124
Codes_81.plus = 43
Codes_81.question = 63
Codes_81.round_left = 40
Codes_81.round_right = 41
Codes_81.slash = 47
Codes_81.square_left = 91
Codes_81.square_right = 93
Codes_81.star = 42
Codes_81.tab = 9
Codes_81.tilde = 42
Codes_81.upper_a = 65
Codes_81.upper_z = 90
Codes_81.space = 32
Codes_81.surrogate_min = 55296
Codes_81.surrogate_max = 57343
Codes_81.supplemental_min = 65536
Codes_81.uint16_max = 65535
Codes_81.underscore = 95
class Begin_47(Special):
    __slots__ = ()
    def __init__(this_91) -> None:
        pass
begin: 'Special' = Begin_47()
class Dot_48(Special):
    __slots__ = ()
    def __init__(this_93) -> None:
        pass
dot: 'Special' = Dot_48()
class End_49(Special):
    __slots__ = ()
    def __init__(this_95) -> None:
        pass
end: 'Special' = End_49()
class WordBoundary_50(Special):
    __slots__ = ()
    def __init__(this_97) -> None:
        pass
word_boundary: 'Special' = WordBoundary_50()
class Digit_51(SpecialSet):
    __slots__ = ()
    def __init__(this_99) -> None:
        pass
digit: 'SpecialSet' = Digit_51()
class Space_52(SpecialSet):
    __slots__ = ()
    def __init__(this_101) -> None:
        pass
space: 'SpecialSet' = Space_52()
class Word_53(SpecialSet):
    __slots__ = ()
    def __init__(this_103) -> None:
        pass
word: 'SpecialSet' = Word_53()
def build_escape_needs_161() -> 'Sequence23[int24]':
    t_935: 'bool21'
    t_936: 'bool21'
    t_937: 'bool21'
    t_938: 'bool21'
    t_939: 'bool21'
    t_940: 'bool21'
    t_941: 'bool21'
    t_942: 'bool21'
    t_943: 'bool21'
    t_944: 'bool21'
    t_945: 'bool21'
    t_946: 'bool21'
    t_947: 'bool21'
    t_948: 'bool21'
    t_949: 'bool21'
    t_950: 'bool21'
    t_951: 'bool21'
    t_952: 'bool21'
    t_953: 'bool21'
    t_954: 'bool21'
    t_955: 'bool21'
    t_956: 'bool21'
    t_957: 'bool21'
    t_958: 'bool21'
    t_959: 'int24'
    escape_needs_372: 'MutableSequence32[int24]' = list_2438()
    code_373: 'int24' = 0
    while code_373 < 127:
        if code_373 == Codes_81.dash:
            t_942 = True
        else:
            if code_373 == Codes_81.space:
                t_941 = True
            else:
                if code_373 == Codes_81.underscore:
                    t_940 = True
                else:
                    if Codes_81.digit0 <= code_373:
                        t_935 = code_373 <= Codes_81.digit9
                    else:
                        t_935 = False
                    if t_935:
                        t_939 = True
                    else:
                        if Codes_81.upper_a <= code_373:
                            t_936 = code_373 <= Codes_81.upper_z
                        else:
                            t_936 = False
                        if t_936:
                            t_938 = True
                        else:
                            if Codes_81.lower_a <= code_373:
                                t_937 = code_373 <= Codes_81.lower_z
                            else:
                                t_937 = False
                            t_938 = t_937
                        t_939 = t_938
                    t_940 = t_939
                t_941 = t_940
            t_942 = t_941
        if t_942:
            t_959 = 0
        else:
            if code_373 == Codes_81.ampersand:
                t_958 = True
            else:
                if code_373 == Codes_81.backslash:
                    t_957 = True
                else:
                    if code_373 == Codes_81.caret:
                        t_956 = True
                    else:
                        if code_373 == Codes_81.curly_left:
                            t_955 = True
                        else:
                            if code_373 == Codes_81.curly_right:
                                t_954 = True
                            else:
                                if code_373 == Codes_81.dot:
                                    t_953 = True
                                else:
                                    if code_373 == Codes_81.peso:
                                        t_952 = True
                                    else:
                                        if code_373 == Codes_81.pipe:
                                            t_951 = True
                                        else:
                                            if code_373 == Codes_81.plus:
                                                t_950 = True
                                            else:
                                                if code_373 == Codes_81.question:
                                                    t_949 = True
                                                else:
                                                    if code_373 == Codes_81.round_left:
                                                        t_948 = True
                                                    else:
                                                        if code_373 == Codes_81.round_right:
                                                            t_947 = True
                                                        else:
                                                            if code_373 == Codes_81.slash:
                                                                t_946 = True
                                                            else:
                                                                if code_373 == Codes_81.square_left:
                                                                    t_945 = True
                                                                else:
                                                                    if code_373 == Codes_81.square_right:
                                                                        t_944 = True
                                                                    else:
                                                                        if code_373 == Codes_81.star:
                                                                            t_943 = True
                                                                        else:
                                                                            t_943 = code_373 == Codes_81.tilde
                                                                        t_944 = t_943
                                                                    t_945 = t_944
                                                                t_946 = t_945
                                                            t_947 = t_946
                                                        t_948 = t_947
                                                    t_949 = t_948
                                                t_950 = t_949
                                            t_951 = t_950
                                        t_952 = t_951
                                    t_953 = t_952
                                t_954 = t_953
                            t_955 = t_954
                        t_956 = t_955
                    t_957 = t_956
                t_958 = t_957
            if t_958:
                t_959 = 2
            else:
                t_959 = 1
        escape_needs_372.append(t_959)
        code_373 = code_373 + 1
    return tuple_2440(escape_needs_372)
escape_needs_163: 'Sequence23[int24]' = build_escape_needs_161()
regex_refs_162: 'RegexRefs_54' = RegexRefs_54()
def entire(item_219: 'RegexNode') -> 'RegexNode':
    return Sequence((begin, item_219, end))
def one_or_more(item_221: 'RegexNode', reluctant_549: 'Union25[bool21, None]' = None) -> 'Repeat':
    _reluctant_549: 'Union25[bool21, None]' = reluctant_549
    reluctant_222: 'bool21'
    if _reluctant_549 is None:
        reluctant_222 = False
    else:
        reluctant_222 = _reluctant_549
    return Repeat(item_221, 1, None, reluctant_222)
def optional(item_224: 'RegexNode', reluctant_551: 'Union25[bool21, None]' = None) -> 'Repeat':
    _reluctant_551: 'Union25[bool21, None]' = reluctant_551
    reluctant_225: 'bool21'
    if _reluctant_551 is None:
        reluctant_225 = False
    else:
        reluctant_225 = _reluctant_551
    return Repeat(item_224, 0, 1, reluctant_225)
