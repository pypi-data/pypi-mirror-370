from abc import ABCMeta as ABCMeta19, abstractmethod as abstractmethod53
from builtins import str as str20, RuntimeError as RuntimeError52, bool as bool21, int as int24, float as float54, Exception as Exception37, list as list17, isinstance as isinstance28, len as len14, tuple as tuple18
from typing import Union as Union25, ClassVar as ClassVar31, Sequence as Sequence23, MutableSequence as MutableSequence32, Dict as Dict55, Any as Any27, TypeVar as TypeVar56, Generic as Generic57
from types import MappingProxyType as MappingProxyType26
from temper_core import Label as Label30, cast_by_type as cast_by_type29, string_from_code_point as string_from_code_point10, require_string_index as require_string_index58, list_get as list_get9, list_for_each as list_for_each38, mapped_for_each as mapped_for_each39, int_to_string as int_to_string15, int_to_float64 as int_to_float6440, float64_to_string as float64_to_string41, float64_to_int as float64_to_int42, string_to_float64 as string_to_float6443, list_get_or as list_get_or44, list_builder_set as list_builder_set45, mapped_has as mapped_has46, map_builder_set as map_builder_set47, mapped_to_map as mapped_to_map48, string_get as string_get12, string_next as string_next13, str_cat as str_cat16, string_has_at_least as string_has_at_least49, float_lt_eq as float_lt_eq50, float_not_eq as float_not_eq51
from math import nan as nan59, inf as inf60
len_2461 = len14
list_get_2462 = list_get9
list_for_each_2463 = list_for_each38
mapped_for_each_2464 = mapped_for_each39
int_to_string_2465 = int_to_string15
int_to_float64_2466 = int_to_float6440
float64_to_string_2467 = float64_to_string41
float64_to_int_2468 = float64_to_int42
string_to_float64_2470 = string_to_float6443
list_2472 = list17
list_get_or_2474 = list_get_or44
list_builder_set_2475 = list_builder_set45
mapped_has_2482 = mapped_has46
map_builder_set_2484 = map_builder_set47
tuple_2485 = tuple18
mapped_to_map_2486 = mapped_to_map48
string_get_2488 = string_get12
string_next_2489 = string_next13
str_cat_2492 = str_cat16
string_has_at_least_2494 = string_has_at_least49
float_lt_eq_2496 = float_lt_eq50
float_not_eq_2497 = float_not_eq51
class InterchangeContext(metaclass = ABCMeta19):
    def get_header(this_74, header_name_337: 'str20') -> 'Union25[str20, None]':
        raise RuntimeError52()
class NullInterchangeContext(InterchangeContext):
    instance: ClassVar31['NullInterchangeContext']
    __slots__ = ()
    def get_header(this_75, header_name_340: 'str20') -> 'Union25[str20, None]':
        return None
    def __init__(this_169) -> None:
        pass
NullInterchangeContext.instance = NullInterchangeContext()
class JsonProducer(metaclass = ABCMeta19):
    @property
    @abstractmethod53
    def interchange_context(self) -> 'InterchangeContext':
        pass
    def start_object(this_76) -> 'None':
        raise RuntimeError52()
    def end_object(this_77) -> 'None':
        raise RuntimeError52()
    def object_key(this_78, key_350: 'str20') -> 'None':
        raise RuntimeError52()
    def start_array(this_79) -> 'None':
        raise RuntimeError52()
    def end_array(this_80) -> 'None':
        raise RuntimeError52()
    def null_value(this_81) -> 'None':
        raise RuntimeError52()
    def boolean_value(this_82, x_359: 'bool21') -> 'None':
        raise RuntimeError52()
    def int_value(this_83, x_362: 'int24') -> 'None':
        raise RuntimeError52()
    def float64_value(this_84, x_365: 'float54') -> 'None':
        raise RuntimeError52()
    def numeric_token_value(this_85, x_368: 'str20') -> 'None':
        'A number that fits the JSON number grammar to allow\ninterchange of numbers that are not easily represntible\nusing numeric types that Temper connects to.\n\nthis__85: JsonProducer\n\nx__368: String\n'
        raise RuntimeError52()
    def string_value(this_86, x_371: 'str20') -> 'None':
        raise RuntimeError52()
    @property
    def parse_error_receiver(this_87) -> 'Union25[JsonParseErrorReceiver, None]':
        return None
class JsonSyntaxTree(metaclass = ABCMeta19):
    def produce(this_88, p_376: 'JsonProducer') -> 'None':
        raise RuntimeError52()
class JsonObject(JsonSyntaxTree):
    properties_378: 'MappingProxyType26[str20, (Sequence23[JsonSyntaxTree])]'
    __slots__ = ('properties_378',)
    def property_value_or_null(this_89, property_key_380: 'str20') -> 'Union25[JsonSyntaxTree, None]':
        "The JSON value tree associated with the given property key or null\nif there is no such value.\n\nThe properties map contains a list of sub-trees because JSON\nallows duplicate properties.  ECMA-404 \xa76 notes (emphasis added):\n\n> The JSON syntax does not impose any restrictions on the strings\n> used as names, **does not require that name strings be unique**,\n> and does not assign any significance to the ordering of\n> name/value pairs.\n\nWhen widely used JSON parsers need to relate a property key\nto a single value, they tend to prefer the last key/value pair\nfrom a JSON object.  For example:\n\nJS:\n\n    JSON.parse('{\"x\":\"first\",\"x\":\"last\"}').x === 'last'\n\nPython:\n\n    import json\n    json.loads('{\"x\":\"first\",\"x\":\"last\"}')['x'] == 'last'\n\nC#:\n\n   using System.Text.Json;\n\t\tJsonDocument d = JsonDocument.Parse(\n\t\t\t\"\"\"\n\t\t\t{\"x\":\"first\",\"x\":\"last\"}\n\t\t\t\"\"\"\n\t\t);\n\t\td.RootElement.GetProperty(\"x\").GetString() == \"last\"\n\nthis__89: JsonObject\n\npropertyKey__380: String\n"
        return_189: 'Union25[JsonSyntaxTree, None]'
        tree_list_382: 'Sequence23[JsonSyntaxTree]' = this_89.properties_378.get(property_key_380, ())
        last_index_383: 'int24' = len_2461(tree_list_382) - 1
        if last_index_383 >= 0:
            return_189 = list_get_2462(tree_list_382, last_index_383)
        else:
            return_189 = None
        return return_189
    def property_value_or_bubble(this_90, property_key_385: 'str20') -> 'JsonSyntaxTree':
        return_190: 'JsonSyntaxTree'
        t_2410: 'Union25[JsonSyntaxTree, None]' = this_90.property_value_or_null(property_key_385)
        if t_2410 is None:
            raise RuntimeError52()
        else:
            return_190 = t_2410
        return return_190
    def produce(this_91, p_388: 'JsonProducer') -> 'None':
        p_388.start_object()
        def fn_2405(k_390: 'str20', vs_391: 'Sequence23[JsonSyntaxTree]') -> 'None':
            def fn_2402(v_392: 'JsonSyntaxTree') -> 'None':
                p_388.object_key(k_390)
                v_392.produce(p_388)
            list_for_each_2463(vs_391, fn_2402)
        mapped_for_each_2464(this_91.properties_378, fn_2405)
        p_388.end_object()
    def __init__(this_186, properties_394: 'MappingProxyType26[str20, (Sequence23[JsonSyntaxTree])]') -> None:
        this_186.properties_378 = properties_394
    @property
    def properties(this_790) -> 'MappingProxyType26[str20, (Sequence23[JsonSyntaxTree])]':
        return this_790.properties_378
class JsonArray(JsonSyntaxTree):
    elements_395: 'Sequence23[JsonSyntaxTree]'
    __slots__ = ('elements_395',)
    def produce(this_92, p_397: 'JsonProducer') -> 'None':
        p_397.start_array()
        def fn_2395(v_399: 'JsonSyntaxTree') -> 'None':
            v_399.produce(p_397)
        list_for_each_2463(this_92.elements_395, fn_2395)
        p_397.end_array()
    def __init__(this_192, elements_401: 'Sequence23[JsonSyntaxTree]') -> None:
        this_192.elements_395 = elements_401
    @property
    def elements(this_793) -> 'Sequence23[JsonSyntaxTree]':
        return this_793.elements_395
class JsonBoolean(JsonSyntaxTree):
    content_402: 'bool21'
    __slots__ = ('content_402',)
    def produce(this_93, p_404: 'JsonProducer') -> 'None':
        p_404.boolean_value(this_93.content_402)
    def __init__(this_196, content_407: 'bool21') -> None:
        this_196.content_402 = content_407
    @property
    def content(this_796) -> 'bool21':
        return this_796.content_402
class JsonNull(JsonSyntaxTree):
    __slots__ = ()
    def produce(this_94, p_409: 'JsonProducer') -> 'None':
        p_409.null_value()
    def __init__(this_199) -> None:
        pass
class JsonString(JsonSyntaxTree):
    content_412: 'str20'
    __slots__ = ('content_412',)
    def produce(this_95, p_414: 'JsonProducer') -> 'None':
        p_414.string_value(this_95.content_412)
    def __init__(this_202, content_417: 'str20') -> None:
        this_202.content_412 = content_417
    @property
    def content(this_799) -> 'str20':
        return this_799.content_412
class JsonNumeric(JsonSyntaxTree, metaclass = ABCMeta19):
    def as_json_numeric_token(this_96) -> 'str20':
        raise RuntimeError52()
    def as_int(this_97) -> 'int24':
        raise RuntimeError52()
    def as_float64(this_98) -> 'float54':
        raise RuntimeError52()
class JsonInt(JsonNumeric):
    content_424: 'int24'
    __slots__ = ('content_424',)
    def produce(this_99, p_426: 'JsonProducer') -> 'None':
        p_426.int_value(this_99.content_424)
    def as_json_numeric_token(this_100) -> 'str20':
        return int_to_string_2465(this_100.content_424)
    def as_int(this_101) -> 'int24':
        return this_101.content_424
    def as_float64(this_102) -> 'float54':
        return int_to_float64_2466(this_102.content_424)
    def __init__(this_208, content_435: 'int24') -> None:
        this_208.content_424 = content_435
    @property
    def content(this_802) -> 'int24':
        return this_802.content_424
class JsonFloat64(JsonNumeric):
    content_436: 'float54'
    __slots__ = ('content_436',)
    def produce(this_103, p_438: 'JsonProducer') -> 'None':
        p_438.float64_value(this_103.content_436)
    def as_json_numeric_token(this_104) -> 'str20':
        return float64_to_string_2467(this_104.content_436)
    def as_int(this_105) -> 'int24':
        return float64_to_int_2468(this_105.content_436)
    def as_float64(this_106) -> 'float54':
        return this_106.content_436
    def __init__(this_214, content_447: 'float54') -> None:
        this_214.content_436 = content_447
    @property
    def content(this_805) -> 'float54':
        return this_805.content_436
class JsonNumericToken(JsonNumeric):
    content_448: 'str20'
    __slots__ = ('content_448',)
    def produce(this_107, p_450: 'JsonProducer') -> 'None':
        p_450.numeric_token_value(this_107.content_448)
    def as_json_numeric_token(this_108) -> 'str20':
        return this_108.content_448
    def as_int(this_109) -> 'int24':
        return_224: 'int24'
        t_1685: 'int24'
        t_1686: 'float54'
        try:
            t_1685 = int(this_109.content_448)
            return_224 = t_1685
        except Exception37:
            t_1686 = string_to_float64_2470(this_109.content_448)
            return_224 = float64_to_int_2468(t_1686)
        return return_224
    def as_float64(this_110) -> 'float54':
        return string_to_float64_2470(this_110.content_448)
    def __init__(this_220, content_459: 'str20') -> None:
        this_220.content_448 = content_459
    @property
    def content(this_808) -> 'str20':
        return this_808.content_448
class JsonTextProducer(JsonProducer):
    interchange_context_460: 'InterchangeContext'
    buffer_461: 'list17[str20]'
    stack_462: 'MutableSequence32[int24]'
    well_formed_463: 'bool21'
    __slots__ = ('interchange_context_460', 'buffer_461', 'stack_462', 'well_formed_463')
    def __init__(this_111, interchange_context_850: 'Union25[InterchangeContext, None]' = None) -> None:
        _interchange_context_850: 'Union25[InterchangeContext, None]' = interchange_context_850
        interchange_context_465: 'InterchangeContext'
        if _interchange_context_850 is None:
            interchange_context_465 = NullInterchangeContext.instance
        else:
            interchange_context_465 = _interchange_context_850
        this_111.interchange_context_460 = interchange_context_465
        t_2366: 'list17[str20]' = ['']
        this_111.buffer_461 = t_2366
        t_2367: 'MutableSequence32[int24]' = list_2472()
        this_111.stack_462 = t_2367
        this_111.stack_462.append(5)
        this_111.well_formed_463 = True
    def state_467(this_112) -> 'int24':
        t_2364: 'int24' = len_2461(this_112.stack_462)
        return list_get_or_2474(this_112.stack_462, t_2364 - 1, -1)
    def before_value_469(this_113) -> 'None':
        t_2357: 'int24'
        t_2360: 'int24'
        t_2362: 'int24'
        t_1643: 'bool21'
        current_state_471: 'int24' = this_113.state_467()
        if current_state_471 == 3:
            t_2357 = len_2461(this_113.stack_462)
            list_builder_set_2475(this_113.stack_462, t_2357 - 1, 4)
        elif current_state_471 == 4:
            this_113.buffer_461.append(',')
        elif current_state_471 == 1:
            t_2360 = len_2461(this_113.stack_462)
            list_builder_set_2475(this_113.stack_462, t_2360 - 1, 2)
        elif current_state_471 == 5:
            t_2362 = len_2461(this_113.stack_462)
            list_builder_set_2475(this_113.stack_462, t_2362 - 1, 6)
        else:
            if current_state_471 == 6:
                t_1643 = True
            else:
                t_1643 = current_state_471 == 2
            if t_1643:
                this_113.well_formed_463 = False
    def start_object(this_114) -> 'None':
        this_114.before_value_469()
        this_114.buffer_461.append('{')
        this_114.stack_462.append(0)
    def end_object(this_115) -> 'None':
        t_1631: 'bool21'
        this_115.buffer_461.append('}')
        current_state_476: 'int24' = this_115.state_467()
        if 0 == current_state_476:
            t_1631 = True
        else:
            t_1631 = 2 == current_state_476
        if t_1631:
            this_115.stack_462.pop()
        else:
            this_115.well_formed_463 = False
    def object_key(this_116, key_478: 'str20') -> 'None':
        t_2348: 'int24'
        current_state_480: 'int24' = this_116.state_467()
        if not current_state_480 == 0:
            if current_state_480 == 2:
                this_116.buffer_461.append(',')
            else:
                this_116.well_formed_463 = False
        encode_json_string_313(key_478, this_116.buffer_461)
        this_116.buffer_461.append(':')
        if current_state_480 >= 0:
            t_2348 = len_2461(this_116.stack_462)
            list_builder_set_2475(this_116.stack_462, t_2348 - 1, 1)
    def start_array(this_117) -> 'None':
        this_117.before_value_469()
        this_117.buffer_461.append('[')
        this_117.stack_462.append(3)
    def end_array(this_118) -> 'None':
        t_1619: 'bool21'
        this_118.buffer_461.append(']')
        current_state_485: 'int24' = this_118.state_467()
        if 3 == current_state_485:
            t_1619 = True
        else:
            t_1619 = 4 == current_state_485
        if t_1619:
            this_118.stack_462.pop()
        else:
            this_118.well_formed_463 = False
    def null_value(this_119) -> 'None':
        this_119.before_value_469()
        this_119.buffer_461.append('null')
    def boolean_value(this_120, x_489: 'bool21') -> 'None':
        t_1615: 'str20'
        this_120.before_value_469()
        if x_489:
            t_1615 = 'true'
        else:
            t_1615 = 'false'
        this_120.buffer_461.append(t_1615)
    def int_value(this_121, x_492: 'int24') -> 'None':
        this_121.before_value_469()
        t_2332: 'str20' = int_to_string_2465(x_492)
        this_121.buffer_461.append(t_2332)
    def float64_value(this_122, x_495: 'float54') -> 'None':
        this_122.before_value_469()
        t_2329: 'str20' = float64_to_string_2467(x_495)
        this_122.buffer_461.append(t_2329)
    def numeric_token_value(this_123, x_498: 'str20') -> 'None':
        this_123.before_value_469()
        this_123.buffer_461.append(x_498)
    def string_value(this_124, x_501: 'str20') -> 'None':
        this_124.before_value_469()
        encode_json_string_313(x_501, this_124.buffer_461)
    def to_json_string(this_125) -> 'str20':
        return_240: 'str20'
        t_2322: 'int24'
        t_1606: 'bool21'
        t_1607: 'bool21'
        if this_125.well_formed_463:
            if len_2461(this_125.stack_462) == 1:
                t_2322 = this_125.state_467()
                t_1606 = t_2322 == 6
            else:
                t_1606 = False
            t_1607 = t_1606
        else:
            t_1607 = False
        if t_1607:
            return_240 = ''.join(this_125.buffer_461)
        else:
            raise RuntimeError52()
        return return_240
    @property
    def interchange_context(this_818) -> 'InterchangeContext':
        return this_818.interchange_context_460
class JsonParseErrorReceiver(metaclass = ABCMeta19):
    def explain_json_error(this_126, explanation_521: 'str20') -> 'None':
        raise RuntimeError52()
class JsonSyntaxTreeProducer(JsonProducer, JsonParseErrorReceiver):
    stack_523: 'MutableSequence32[(MutableSequence32[JsonSyntaxTree])]'
    error_524: 'Union25[str20, None]'
    __slots__ = ('stack_523', 'error_524')
    @property
    def interchange_context(this_127) -> 'InterchangeContext':
        return NullInterchangeContext.instance
    def __init__(this_128) -> None:
        t_2318: 'MutableSequence32[(MutableSequence32[JsonSyntaxTree])]' = list_2472()
        this_128.stack_523 = t_2318
        t_2319: 'MutableSequence32[JsonSyntaxTree]' = list_2472()
        this_128.stack_523.append(t_2319)
        this_128.error_524 = None
    def store_value_529(this_129, v_530: 'JsonSyntaxTree') -> 'None':
        t_2315: 'int24'
        if not (not this_129.stack_523):
            t_2315 = len_2461(this_129.stack_523)
            list_get_2462(this_129.stack_523, t_2315 - 1).append(v_530)
    def start_object(this_130) -> 'None':
        t_2312: 'MutableSequence32[JsonSyntaxTree]' = list_2472()
        this_130.stack_523.append(t_2312)
    def end_object(this_131) -> 'None':
        t_2298: 'Union25[(Dict55[str20, (MutableSequence32[JsonSyntaxTree])]), None]'
        t_2310: 'JsonObject'
        t_1569: 'JsonString'
        t_1572: 'JsonString'
        t_1578: 'Dict55[str20, (MutableSequence32[JsonSyntaxTree])]'
        t_1581: 'Dict55[str20, (MutableSequence32[JsonSyntaxTree])]'
        t_1583: 'Sequence23[JsonSyntaxTree]'
        t_1585: 'Sequence23[JsonSyntaxTree]'
        t_1587: 'MutableSequence32[JsonSyntaxTree]'
        t_1589: 'MutableSequence32[JsonSyntaxTree]'
        with Label30() as fn_535:
            if not this_131.stack_523:
                fn_535.break_()
            ls_536: 'MutableSequence32[JsonSyntaxTree]' = this_131.stack_523.pop()
            m_537: 'Dict55[str20, (Sequence23[JsonSyntaxTree])]' = {}
            multis_538: 'Union25[(Dict55[str20, (MutableSequence32[JsonSyntaxTree])]), None]' = None
            i_539: 'int24' = 0
            n_540: 'int24' = len_2461(ls_536) & -2
            while i_539 < n_540:
                postfix_return_38: 'int24' = i_539
                i_539 = i_539 + 1
                key_tree_541: 'JsonSyntaxTree' = list_get_2462(ls_536, postfix_return_38)
                if not isinstance28(key_tree_541, JsonString):
                    break
                t_1569 = cast_by_type29(key_tree_541, JsonString)
                t_1572 = t_1569
                key_542: 'str20' = t_1572.content
                postfix_return_39: 'int24' = i_539
                i_539 = i_539 + 1
                value_543: 'JsonSyntaxTree' = list_get_2462(ls_536, postfix_return_39)
                if mapped_has_2482(m_537, key_542):
                    if multis_538 is None:
                        t_2298 = {}
                        multis_538 = t_2298
                    if multis_538 is None:
                        raise RuntimeError52()
                    else:
                        t_1578 = multis_538
                    t_1581 = t_1578
                    mb_544: 'Dict55[str20, (MutableSequence32[JsonSyntaxTree])]' = t_1581
                    if not mapped_has_2482(mb_544, key_542):
                        t_1583 = m_537[key_542]
                        t_1585 = t_1583
                        map_builder_set_2484(mb_544, key_542, list_2472(t_1585))
                    t_1587 = mb_544[key_542]
                    t_1589 = t_1587
                    t_1589.append(value_543)
                else:
                    map_builder_set_2484(m_537, key_542, (value_543,))
            multis_545: 'Union25[(Dict55[str20, (MutableSequence32[JsonSyntaxTree])]), None]' = multis_538
            if not multis_545 is None:
                def fn_2287(k_546: 'str20', vs_547: 'MutableSequence32[JsonSyntaxTree]') -> 'None':
                    t_2285: 'Sequence23[JsonSyntaxTree]' = tuple_2485(vs_547)
                    map_builder_set_2484(m_537, k_546, t_2285)
                mapped_for_each_2464(multis_545, fn_2287)
            t_2310 = JsonObject(mapped_to_map_2486(m_537))
            this_131.store_value_529(t_2310)
    def object_key(this_132, key_549: 'str20') -> 'None':
        t_2283: 'JsonString' = JsonString(key_549)
        this_132.store_value_529(t_2283)
    def start_array(this_133) -> 'None':
        t_2281: 'MutableSequence32[JsonSyntaxTree]' = list_2472()
        this_133.stack_523.append(t_2281)
    def end_array(this_134) -> 'None':
        t_2279: 'JsonArray'
        with Label30() as fn_554:
            if not this_134.stack_523:
                fn_554.break_()
            ls_555: 'MutableSequence32[JsonSyntaxTree]' = this_134.stack_523.pop()
            t_2279 = JsonArray(tuple_2485(ls_555))
            this_134.store_value_529(t_2279)
    def null_value(this_135) -> 'None':
        t_2274: 'JsonNull' = JsonNull()
        this_135.store_value_529(t_2274)
    def boolean_value(this_136, x_559: 'bool21') -> 'None':
        t_2272: 'JsonBoolean' = JsonBoolean(x_559)
        this_136.store_value_529(t_2272)
    def int_value(this_137, x_562: 'int24') -> 'None':
        t_2270: 'JsonInt' = JsonInt(x_562)
        this_137.store_value_529(t_2270)
    def float64_value(this_138, x_565: 'float54') -> 'None':
        t_2268: 'JsonFloat64' = JsonFloat64(x_565)
        this_138.store_value_529(t_2268)
    def numeric_token_value(this_139, x_568: 'str20') -> 'None':
        t_2266: 'JsonNumericToken' = JsonNumericToken(x_568)
        this_139.store_value_529(t_2266)
    def string_value(this_140, x_571: 'str20') -> 'None':
        t_2264: 'JsonString' = JsonString(x_571)
        this_140.store_value_529(t_2264)
    def to_json_syntax_tree(this_141) -> 'JsonSyntaxTree':
        t_1543: 'bool21'
        if len_2461(this_141.stack_523) != 1:
            t_1543 = True
        else:
            t_1543 = not this_141.error_524 is None
        if t_1543:
            raise RuntimeError52()
        ls_575: 'MutableSequence32[JsonSyntaxTree]' = list_get_2462(this_141.stack_523, 0)
        if len_2461(ls_575) != 1:
            raise RuntimeError52()
        return list_get_2462(ls_575, 0)
    @property
    def json_error(this_142) -> 'Union25[str20, None]':
        return this_142.error_524
    @property
    def parse_error_receiver(this_143) -> 'JsonParseErrorReceiver':
        return this_143
    def explain_json_error(this_144, error_581: 'str20') -> 'None':
        this_144.error_524 = error_581
def parse_json_value_318(source_text_600: 'str20', i_601: 'int24', out_602: 'JsonProducer') -> 'int24':
    return_269: 'int24'
    t_2098: 'int24'
    t_2101: 'int24'
    t_1318: 'bool21'
    with Label30() as fn_603:
        t_2098 = skip_json_spaces_317(source_text_600, i_601)
        i_601 = t_2098
        if not len14(source_text_600) > i_601:
            expected_token_error_315(source_text_600, i_601, out_602, 'JSON value')
            return_269 = -1
            fn_603.break_()
        t_2101 = string_get_2488(source_text_600, i_601)
        if t_2101 == 123:
            return_269 = parse_json_object_319(source_text_600, i_601, out_602)
        elif t_2101 == 91:
            return_269 = parse_json_array_320(source_text_600, i_601, out_602)
        elif t_2101 == 34:
            return_269 = parse_json_string_321(source_text_600, i_601, out_602)
        else:
            if t_2101 == 116:
                t_1318 = True
            else:
                t_1318 = t_2101 == 102
            if t_1318:
                return_269 = parse_json_boolean_324(source_text_600, i_601, out_602)
            elif t_2101 == 110:
                return_269 = parse_json_null_325(source_text_600, i_601, out_602)
            else:
                return_269 = parse_json_number_327(source_text_600, i_601, out_602)
    return return_269
T_145 = TypeVar56('T_145', bound = Any27, covariant = True)
class JsonAdapter(Generic57[T_145], metaclass = ABCMeta19):
    def encode_to_json(this_146, x_691: 'T_145', p_692: 'JsonProducer') -> 'None':
        raise RuntimeError52()
    def decode_from_json(this_147, t_695: 'JsonSyntaxTree', ic_696: 'InterchangeContext') -> 'T_145':
        raise RuntimeError52()
class BooleanJsonAdapter_148(JsonAdapter['bool21']):
    __slots__ = ()
    def encode_to_json(this_149, x_699: 'bool21', p_700: 'JsonProducer') -> 'None':
        p_700.boolean_value(x_699)
    def decode_from_json(this_150, t_703: 'JsonSyntaxTree', ic_704: 'InterchangeContext') -> 'bool21':
        t_1296: 'JsonBoolean'
        t_1296 = cast_by_type29(t_703, JsonBoolean)
        return t_1296.content
    def __init__(this_282) -> None:
        pass
class Float64JsonAdapter_151(JsonAdapter['float54']):
    __slots__ = ()
    def encode_to_json(this_152, x_709: 'float54', p_710: 'JsonProducer') -> 'None':
        p_710.float64_value(x_709)
    def decode_from_json(this_153, t_713: 'JsonSyntaxTree', ic_714: 'InterchangeContext') -> 'float54':
        t_1292: 'JsonNumeric'
        t_1292 = cast_by_type29(t_713, JsonNumeric)
        return t_1292.as_float64()
    def __init__(this_287) -> None:
        pass
class IntJsonAdapter_154(JsonAdapter['int24']):
    __slots__ = ()
    def encode_to_json(this_155, x_719: 'int24', p_720: 'JsonProducer') -> 'None':
        p_720.int_value(x_719)
    def decode_from_json(this_156, t_723: 'JsonSyntaxTree', ic_724: 'InterchangeContext') -> 'int24':
        t_1288: 'JsonNumeric'
        t_1288 = cast_by_type29(t_723, JsonNumeric)
        return t_1288.as_int()
    def __init__(this_292) -> None:
        pass
class StringJsonAdapter_157(JsonAdapter['str20']):
    __slots__ = ()
    def encode_to_json(this_158, x_729: 'str20', p_730: 'JsonProducer') -> 'None':
        p_730.string_value(x_729)
    def decode_from_json(this_159, t_733: 'JsonSyntaxTree', ic_734: 'InterchangeContext') -> 'str20':
        t_1284: 'JsonString'
        t_1284 = cast_by_type29(t_733, JsonString)
        return t_1284.content
    def __init__(this_297) -> None:
        pass
T_161 = TypeVar56('T_161', bound = Any27)
class ListJsonAdapter_160(JsonAdapter['Sequence23[T_161]']):
    adapter_for_t_738: 'JsonAdapter[T_161]'
    __slots__ = ('adapter_for_t_738',)
    def encode_to_json(this_162, x_740: 'Sequence23[T_161]', p_741: 'JsonProducer') -> 'None':
        p_741.start_array()
        def fn_2073(el_743: 'T_161') -> 'None':
            this_162.adapter_for_t_738.encode_to_json(el_743, p_741)
        list_for_each_2463(x_740, fn_2073)
        p_741.end_array()
    def decode_from_json(this_163, t_745: 'JsonSyntaxTree', ic_746: 'InterchangeContext') -> 'Sequence23[T_161]':
        t_1278: 'T_161'
        b_748: 'MutableSequence32[T_161]' = list_2472()
        t_1273: 'JsonArray'
        t_1273 = cast_by_type29(t_745, JsonArray)
        elements_749: 'Sequence23[JsonSyntaxTree]' = t_1273.elements
        n_750: 'int24' = len_2461(elements_749)
        i_751: 'int24' = 0
        while i_751 < n_750:
            el_752: 'JsonSyntaxTree' = list_get_2462(elements_749, i_751)
            i_751 = i_751 + 1
            t_1278 = this_163.adapter_for_t_738.decode_from_json(el_752, ic_746)
            b_748.append(t_1278)
        return tuple_2485(b_748)
    def __init__(this_302, adapter_for_t_754: 'JsonAdapter[T_161]') -> None:
        this_302.adapter_for_t_738 = adapter_for_t_754
T_165 = TypeVar56('T_165', bound = Any27)
class OrNullJsonAdapter(JsonAdapter['Union25[T_165, None]']):
    adapter_for_t_757: 'JsonAdapter[T_165]'
    __slots__ = ('adapter_for_t_757',)
    def encode_to_json(this_166, x_759: 'Union25[T_165, None]', p_760: 'JsonProducer') -> 'None':
        if x_759 is None:
            p_760.null_value()
        else:
            x_875: 'T_165' = x_759
            this_166.adapter_for_t_757.encode_to_json(x_875, p_760)
    def decode_from_json(this_167, t_763: 'JsonSyntaxTree', ic_764: 'InterchangeContext') -> 'Union25[T_165, None]':
        return_312: 'Union25[T_165, None]'
        if isinstance28(t_763, JsonNull):
            return_312 = None
        else:
            return_312 = this_167.adapter_for_t_757.decode_from_json(t_763, ic_764)
        return return_312
    def __init__(this_308, adapter_for_t_767: 'JsonAdapter[T_165]') -> None:
        this_308.adapter_for_t_757 = adapter_for_t_767
hex_digits_335: 'Sequence23[str20]' = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f')
def encode_hex4_314(cp_513: 'int24', buffer_514: 'list17[str20]') -> 'None':
    b0_516: 'int24' = cp_513 // 4096 & 15
    b1_517: 'int24' = cp_513 // 256 & 15
    b2_518: 'int24' = cp_513 // 16 & 15
    b3_519: 'int24' = cp_513 & 15
    t_2378: 'str20' = list_get_2462(hex_digits_335, b0_516)
    buffer_514.append(t_2378)
    t_2380: 'str20' = list_get_2462(hex_digits_335, b1_517)
    buffer_514.append(t_2380)
    t_2382: 'str20' = list_get_2462(hex_digits_335, b2_518)
    buffer_514.append(t_2382)
    t_2384: 'str20' = list_get_2462(hex_digits_335, b3_519)
    buffer_514.append(t_2384)
def encode_json_string_313(x_505: 'str20', buffer_506: 'list17[str20]') -> 'None':
    t_1660: 'bool21'
    t_1661: 'bool21'
    t_1662: 'str20'
    t_1663: 'str20'
    buffer_506.append('"')
    i_508: 'int24' = 0
    emitted_509: 'int24' = i_508
    while True:
        if not len14(x_505) > i_508:
            break
        cp_510: 'int24' = string_get_2488(x_505, i_508)
        if cp_510 == 8:
            t_1663 = '\\b'
        elif cp_510 == 9:
            t_1663 = '\\t'
        elif cp_510 == 10:
            t_1663 = '\\n'
        elif cp_510 == 12:
            t_1663 = '\\f'
        elif cp_510 == 13:
            t_1663 = '\\r'
        elif cp_510 == 34:
            t_1663 = '\\"'
        elif cp_510 == 92:
            t_1663 = '\\\\'
        else:
            if cp_510 < 32:
                t_1661 = True
            else:
                if 55296 <= cp_510:
                    t_1660 = cp_510 <= 57343
                else:
                    t_1660 = False
                t_1661 = t_1660
            if t_1661:
                t_1662 = '\\u'
            else:
                t_1662 = ''
            t_1663 = t_1662
        replacement_511: 'str20' = t_1663
        next_i_512: 'int24' = string_next_2489(x_505, i_508)
        if replacement_511 != '':
            buffer_506.append(x_505[emitted_509 : i_508])
            buffer_506.append(replacement_511)
            if replacement_511 == '\\u':
                encode_hex4_314(cp_510, buffer_506)
            emitted_509 = next_i_512
        i_508 = next_i_512
    buffer_506.append(x_505[emitted_509 : i_508])
    buffer_506.append('"')
def store_json_error_316(out_589: 'JsonProducer', explanation_590: 'str20') -> 'None':
    t_2258: 'Union25[JsonParseErrorReceiver, None]' = out_589.parse_error_receiver
    if not t_2258 is None:
        t_2258.explain_json_error(explanation_590)
def expected_token_error_315(source_text_583: 'str20', i_584: 'int24', out_585: 'JsonProducer', short_explanation_586: 'str20') -> 'None':
    t_2255: 'int24'
    t_2256: 'str20'
    gotten_588: 'str20'
    if len14(source_text_583) > i_584:
        t_2255 = len_2461(source_text_583)
        t_2256 = source_text_583[i_584 : t_2255]
        gotten_588 = str_cat_2492('`', t_2256, '`')
    else:
        gotten_588 = 'end-of-file'
    store_json_error_316(out_585, str_cat_2492('Expected ', short_explanation_586, ', but got ', gotten_588))
def skip_json_spaces_317(source_text_597: 'str20', i_598: 'int24') -> 'int24':
    t_2252: 'int24'
    t_2253: 'int24'
    t_1530: 'bool21'
    t_1531: 'bool21'
    t_1532: 'bool21'
    while True:
        if not len14(source_text_597) > i_598:
            break
        t_2252 = string_get_2488(source_text_597, i_598)
        if t_2252 == 9:
            t_1532 = True
        else:
            if t_2252 == 10:
                t_1531 = True
            else:
                if t_2252 == 13:
                    t_1530 = True
                else:
                    t_1530 = t_2252 == 32
                t_1531 = t_1530
            t_1532 = t_1531
        if not t_1532:
            break
        t_2253 = string_next_2489(source_text_597, i_598)
        i_598 = t_2253
    return i_598
def decode_hex_unsigned_323(source_text_638: 'str20', start_639: 'int24', limit_640: 'int24') -> 'int24':
    return_274: 'int24'
    t_2250: 'int24'
    t_1523: 'bool21'
    t_1524: 'bool21'
    t_1525: 'bool21'
    t_1526: 'int24'
    with Label30() as fn_641:
        n_642: 'int24' = 0
        i_643: 'int24' = start_639
        while True:
            if not i_643 - limit_640 < 0:
                break
            cp_644: 'int24' = string_get_2488(source_text_638, i_643)
            if 48 <= cp_644:
                t_1523 = cp_644 <= 48
            else:
                t_1523 = False
            if t_1523:
                t_1526 = cp_644 - 48
            else:
                if 65 <= cp_644:
                    t_1524 = cp_644 <= 70
                else:
                    t_1524 = False
                if t_1524:
                    t_1526 = cp_644 - 65 + 10
                else:
                    if 97 <= cp_644:
                        t_1525 = cp_644 <= 102
                    else:
                        t_1525 = False
                    if t_1525:
                        t_1526 = cp_644 - 97 + 10
                    else:
                        return_274 = -1
                        fn_641.break_()
            digit_645: 'int24' = t_1526
            n_642 = n_642 * 16 + digit_645
            t_2250 = string_next_2489(source_text_638, i_643)
            i_643 = t_2250
        return_274 = n_642
    return return_274
def parse_json_string_to_322(source_text_622: 'str20', i_623: 'int24', sb_624: 'list17[str20]', err_out_625: 'JsonProducer') -> 'int24':
    return_273: 'int24'
    t_2220: 'int24'
    t_2222: 'int24'
    t_2225: 'int24'
    t_2230: 'int24'
    t_2232: 'int24'
    t_2233: 'int24'
    t_2234: 'int24'
    t_2235: 'int24'
    t_2236: 'int24'
    t_2243: 'int24'
    t_2247: 'int24'
    t_1480: 'bool21'
    t_1489: 'bool21'
    t_1490: 'bool21'
    t_1498: 'int24'
    t_1499: 'int24'
    t_1501: 'int24'
    t_1503: 'int24'
    t_1504: 'bool21'
    t_1505: 'int24'
    t_1506: 'bool21'
    t_1509: 'bool21'
    t_1514: 'bool21'
    with Label30() as fn_626:
        if not len14(source_text_622) > i_623:
            t_1480 = True
        else:
            t_2220 = string_get_2488(source_text_622, i_623)
            t_1480 = t_2220 != 34
        if t_1480:
            expected_token_error_315(source_text_622, i_623, err_out_625, '"')
            return_273 = -1
            fn_626.break_()
        t_2222 = string_next_2489(source_text_622, i_623)
        i_623 = t_2222
        lead_surrogate_627: 'int24' = -1
        consumed_628: 'int24' = i_623
        while True:
            if not len14(source_text_622) > i_623:
                break
            cp_629: 'int24' = string_get_2488(source_text_622, i_623)
            if cp_629 == 34:
                break
            t_2225 = string_next_2489(source_text_622, i_623)
            i_next_630: 'int24' = t_2225
            end_631: 'int24' = len_2461(source_text_622)
            need_to_flush_632: 'bool21' = False
            if cp_629 != 92:
                t_1503 = cp_629
            else:
                need_to_flush_632 = True
                if not len14(source_text_622) > i_next_630:
                    expected_token_error_315(source_text_622, i_next_630, err_out_625, 'escape sequence')
                    return_273 = -1
                    fn_626.break_()
                esc0_634: 'int24' = string_get_2488(source_text_622, i_next_630)
                t_2230 = string_next_2489(source_text_622, i_next_630)
                i_next_630 = t_2230
                if esc0_634 == 34:
                    t_1490 = True
                else:
                    if esc0_634 == 92:
                        t_1489 = True
                    else:
                        t_1489 = esc0_634 == 47
                    t_1490 = t_1489
                if t_1490:
                    t_1501 = esc0_634
                elif esc0_634 == 98:
                    t_1501 = 8
                elif esc0_634 == 102:
                    t_1501 = 12
                elif esc0_634 == 110:
                    t_1501 = 10
                elif esc0_634 == 114:
                    t_1501 = 13
                elif esc0_634 == 116:
                    t_1501 = 9
                elif esc0_634 == 117:
                    if string_has_at_least_2494(source_text_622, i_next_630, end_631, 4):
                        start_hex_636: 'int24' = i_next_630
                        t_2232 = string_next_2489(source_text_622, i_next_630)
                        i_next_630 = t_2232
                        t_2233 = string_next_2489(source_text_622, i_next_630)
                        i_next_630 = t_2233
                        t_2234 = string_next_2489(source_text_622, i_next_630)
                        i_next_630 = t_2234
                        t_2235 = string_next_2489(source_text_622, i_next_630)
                        i_next_630 = t_2235
                        t_2236 = decode_hex_unsigned_323(source_text_622, start_hex_636, i_next_630)
                        t_1498 = t_2236
                    else:
                        t_1498 = -1
                    hex_635: 'int24' = t_1498
                    if hex_635 < 0:
                        expected_token_error_315(source_text_622, i_next_630, err_out_625, 'four hex digits')
                        return_273 = -1
                        fn_626.break_()
                    t_1499 = hex_635
                    t_1501 = t_1499
                else:
                    expected_token_error_315(source_text_622, i_next_630, err_out_625, 'escape sequence')
                    return_273 = -1
                    fn_626.break_()
                t_1503 = t_1501
            decoded_cp_633: 'int24' = t_1503
            if lead_surrogate_627 >= 0:
                need_to_flush_632 = True
                lead_637: 'int24' = lead_surrogate_627
                if 56320 <= decoded_cp_633:
                    t_1504 = decoded_cp_633 <= 57343
                else:
                    t_1504 = False
                if t_1504:
                    lead_surrogate_627 = -1
                    t_1505 = (lead_637 - 55296) * 1024 | decoded_cp_633 - 56320
                    decoded_cp_633 = 65536 + t_1505
            else:
                if 55296 <= decoded_cp_633:
                    t_1506 = decoded_cp_633 <= 56319
                else:
                    t_1506 = False
                if t_1506:
                    need_to_flush_632 = True
            if need_to_flush_632:
                sb_624.append(source_text_622[consumed_628 : i_623])
                if lead_surrogate_627 >= 0:
                    sb_624.append(string_from_code_point10(lead_surrogate_627))
                if 55296 <= decoded_cp_633:
                    t_1509 = decoded_cp_633 <= 56319
                else:
                    t_1509 = False
                if t_1509:
                    lead_surrogate_627 = decoded_cp_633
                else:
                    lead_surrogate_627 = -1
                    sb_624.append(string_from_code_point10(decoded_cp_633))
                consumed_628 = i_next_630
            i_623 = i_next_630
        if not len14(source_text_622) > i_623:
            t_1514 = True
        else:
            t_2243 = string_get_2488(source_text_622, i_623)
            t_1514 = t_2243 != 34
        if t_1514:
            expected_token_error_315(source_text_622, i_623, err_out_625, '"')
            return_273 = -1
        else:
            if lead_surrogate_627 >= 0:
                sb_624.append(string_from_code_point10(lead_surrogate_627))
            else:
                sb_624.append(source_text_622[consumed_628 : i_623])
            t_2247 = string_next_2489(source_text_622, i_623)
            i_623 = t_2247
            return_273 = i_623
    return return_273
def parse_json_object_319(source_text_604: 'str20', i_605: 'int24', out_606: 'JsonProducer') -> 'int24':
    return_270: 'int24'
    t_2188: 'int24'
    t_2191: 'int24'
    t_2192: 'int24'
    t_2194: 'int24'
    t_2198: 'str20'
    t_2201: 'int24'
    t_2203: 'int24'
    t_2204: 'int24'
    t_2208: 'int24'
    t_2210: 'int24'
    t_2211: 'int24'
    t_2212: 'int24'
    t_2214: 'int24'
    t_1441: 'bool21'
    t_1447: 'bool21'
    t_1453: 'int24'
    t_1456: 'int24'
    t_1460: 'bool21'
    t_1464: 'int24'
    t_1469: 'bool21'
    t_1474: 'bool21'
    with Label30() as fn_607:
        if not len14(source_text_604) > i_605:
            t_1441 = True
        else:
            t_2188 = string_get_2488(source_text_604, i_605)
            t_1441 = t_2188 != 123
        if t_1441:
            expected_token_error_315(source_text_604, i_605, out_606, "'{'")
            return_270 = -1
            fn_607.break_()
        out_606.start_object()
        t_2191 = string_next_2489(source_text_604, i_605)
        t_2192 = skip_json_spaces_317(source_text_604, t_2191)
        i_605 = t_2192
        if len14(source_text_604) > i_605:
            t_2194 = string_get_2488(source_text_604, i_605)
            t_1447 = t_2194 != 125
        else:
            t_1447 = False
        if t_1447:
            while True:
                key_buffer_608: 'list17[str20]' = ['']
                after_key_609: 'int24' = parse_json_string_to_322(source_text_604, i_605, key_buffer_608, out_606)
                if not after_key_609 >= 0:
                    return_270 = -1
                    fn_607.break_()
                t_2198 = ''.join(key_buffer_608)
                out_606.object_key(t_2198)
                t_1453 = require_string_index58(after_key_609)
                t_1456 = t_1453
                t_2201 = skip_json_spaces_317(source_text_604, t_1456)
                i_605 = t_2201
                if len14(source_text_604) > i_605:
                    t_2203 = string_get_2488(source_text_604, i_605)
                    t_1460 = t_2203 == 58
                else:
                    t_1460 = False
                if t_1460:
                    t_2204 = string_next_2489(source_text_604, i_605)
                    i_605 = t_2204
                    after_property_value_610: 'int24' = parse_json_value_318(source_text_604, i_605, out_606)
                    if not after_property_value_610 >= 0:
                        return_270 = -1
                        fn_607.break_()
                    t_1464 = require_string_index58(after_property_value_610)
                    i_605 = t_1464
                else:
                    expected_token_error_315(source_text_604, i_605, out_606, "':'")
                    return_270 = -1
                    fn_607.break_()
                t_2208 = skip_json_spaces_317(source_text_604, i_605)
                i_605 = t_2208
                if len14(source_text_604) > i_605:
                    t_2210 = string_get_2488(source_text_604, i_605)
                    t_1469 = t_2210 == 44
                else:
                    t_1469 = False
                if t_1469:
                    t_2211 = string_next_2489(source_text_604, i_605)
                    t_2212 = skip_json_spaces_317(source_text_604, t_2211)
                    i_605 = t_2212
                else:
                    break
        if len14(source_text_604) > i_605:
            t_2214 = string_get_2488(source_text_604, i_605)
            t_1474 = t_2214 == 125
        else:
            t_1474 = False
        if t_1474:
            out_606.end_object()
            return_270 = string_next_2489(source_text_604, i_605)
        else:
            expected_token_error_315(source_text_604, i_605, out_606, "'}'")
            return_270 = -1
    return return_270
def parse_json_array_320(source_text_611: 'str20', i_612: 'int24', out_613: 'JsonProducer') -> 'int24':
    return_271: 'int24'
    t_2167: 'int24'
    t_2170: 'int24'
    t_2171: 'int24'
    t_2173: 'int24'
    t_2176: 'int24'
    t_2178: 'int24'
    t_2179: 'int24'
    t_2180: 'int24'
    t_2182: 'int24'
    t_1416: 'bool21'
    t_1422: 'bool21'
    t_1425: 'int24'
    t_1430: 'bool21'
    t_1435: 'bool21'
    with Label30() as fn_614:
        if not len14(source_text_611) > i_612:
            t_1416 = True
        else:
            t_2167 = string_get_2488(source_text_611, i_612)
            t_1416 = t_2167 != 91
        if t_1416:
            expected_token_error_315(source_text_611, i_612, out_613, "'['")
            return_271 = -1
            fn_614.break_()
        out_613.start_array()
        t_2170 = string_next_2489(source_text_611, i_612)
        t_2171 = skip_json_spaces_317(source_text_611, t_2170)
        i_612 = t_2171
        if len14(source_text_611) > i_612:
            t_2173 = string_get_2488(source_text_611, i_612)
            t_1422 = t_2173 != 93
        else:
            t_1422 = False
        if t_1422:
            while True:
                after_element_value_615: 'int24' = parse_json_value_318(source_text_611, i_612, out_613)
                if not after_element_value_615 >= 0:
                    return_271 = -1
                    fn_614.break_()
                t_1425 = require_string_index58(after_element_value_615)
                i_612 = t_1425
                t_2176 = skip_json_spaces_317(source_text_611, i_612)
                i_612 = t_2176
                if len14(source_text_611) > i_612:
                    t_2178 = string_get_2488(source_text_611, i_612)
                    t_1430 = t_2178 == 44
                else:
                    t_1430 = False
                if t_1430:
                    t_2179 = string_next_2489(source_text_611, i_612)
                    t_2180 = skip_json_spaces_317(source_text_611, t_2179)
                    i_612 = t_2180
                else:
                    break
        if len14(source_text_611) > i_612:
            t_2182 = string_get_2488(source_text_611, i_612)
            t_1435 = t_2182 == 93
        else:
            t_1435 = False
        if t_1435:
            out_613.end_array()
            return_271 = string_next_2489(source_text_611, i_612)
        else:
            expected_token_error_315(source_text_611, i_612, out_613, "']'")
            return_271 = -1
    return return_271
def parse_json_string_321(source_text_616: 'str20', i_617: 'int24', out_618: 'JsonProducer') -> 'int24':
    t_2164: 'str20'
    sb_620: 'list17[str20]' = ['']
    after_621: 'int24' = parse_json_string_to_322(source_text_616, i_617, sb_620, out_618)
    if after_621 >= 0:
        t_2164 = ''.join(sb_620)
        out_618.string_value(t_2164)
    return after_621
def after_substring_326(string_660: 'str20', in_string_661: 'int24', substring_662: 'str20') -> 'int24':
    return_277: 'int24'
    t_2159: 'int24'
    t_2160: 'int24'
    with Label30() as fn_663:
        i_664: 'int24' = in_string_661
        j_665: 'int24' = 0
        while True:
            if not len14(substring_662) > j_665:
                break
            if not len14(string_660) > i_664:
                return_277 = -1
                fn_663.break_()
            if string_get_2488(string_660, i_664) != string_get_2488(substring_662, j_665):
                return_277 = -1
                fn_663.break_()
            t_2159 = string_next_2489(string_660, i_664)
            i_664 = t_2159
            t_2160 = string_next_2489(substring_662, j_665)
            j_665 = t_2160
        return_277 = i_664
    return return_277
def parse_json_boolean_324(source_text_646: 'str20', i_647: 'int24', out_648: 'JsonProducer') -> 'int24':
    return_275: 'int24'
    t_2148: 'int24'
    with Label30() as fn_649:
        ch0_650: 'int24'
        if len14(source_text_646) > i_647:
            t_2148 = string_get_2488(source_text_646, i_647)
            ch0_650 = t_2148
        else:
            ch0_650 = 0
        end_651: 'int24' = len_2461(source_text_646)
        keyword_652: 'Union25[str20, None]'
        n_653: 'int24'
        if ch0_650 == 102:
            keyword_652 = 'false'
            n_653 = 5
        elif ch0_650 == 116:
            keyword_652 = 'true'
            n_653 = 4
        else:
            keyword_652 = None
            n_653 = 0
        if not keyword_652 is None:
            keyword_871: 'str20' = keyword_652
            if string_has_at_least_2494(source_text_646, i_647, end_651, n_653):
                after_654: 'int24' = after_substring_326(source_text_646, i_647, keyword_871)
                if after_654 >= 0:
                    return_275 = require_string_index58(after_654)
                    out_648.boolean_value(n_653 == 4)
                    fn_649.break_()
        expected_token_error_315(source_text_646, i_647, out_648, '`false` or `true`')
        return_275 = -1
    return return_275
def parse_json_null_325(source_text_655: 'str20', i_656: 'int24', out_657: 'JsonProducer') -> 'int24':
    return_276: 'int24'
    with Label30() as fn_658:
        after_659: 'int24' = after_substring_326(source_text_655, i_656, 'null')
        if after_659 >= 0:
            return_276 = require_string_index58(after_659)
            out_657.null_value()
            fn_658.break_()
        expected_token_error_315(source_text_655, i_656, out_657, '`null`')
        return_276 = -1
    return return_276
def parse_json_number_327(source_text_666: 'str20', i_667: 'int24', out_668: 'JsonProducer') -> 'int24':
    return_278: 'int24'
    t_2109: 'int24'
    t_2110: 'int24'
    t_2112: 'int24'
    t_2114: 'int24'
    t_2118: 'int24'
    t_2120: 'int24'
    t_2121: 'int24'
    t_2124: 'int24'
    t_2128: 'int24'
    t_2132: 'int24'
    t_2135: 'int24'
    t_1326: 'bool21'
    t_1331: 'bool21'
    t_1332: 'bool21'
    t_1336: 'float54'
    t_1338: 'float54'
    t_1341: 'bool21'
    t_1343: 'float54'
    t_1344: 'float54'
    t_1347: 'bool21'
    t_1351: 'bool21'
    t_1353: 'float54'
    t_1354: 'float54'
    t_1357: 'int24'
    t_1358: 'bool21'
    t_1362: 'bool21'
    t_1366: 'bool21'
    t_1368: 'bool21'
    t_1370: 'bool21'
    t_1371: 'bool21'
    t_1372: 'int24'
    t_1374: 'int24'
    t_1376: 'bool21'
    t_1377: 'float54'
    t_1378: 'bool21'
    t_1379: 'bool21'
    with Label30() as fn_669:
        is_negative_670: 'bool21' = False
        start_of_number_671: 'int24' = i_667
        if len14(source_text_666) > i_667:
            t_2109 = string_get_2488(source_text_666, i_667)
            t_1326 = t_2109 == 45
        else:
            t_1326 = False
        if t_1326:
            is_negative_670 = True
            t_2110 = string_next_2489(source_text_666, i_667)
            i_667 = t_2110
        digit0_672: 'int24'
        if len14(source_text_666) > i_667:
            t_2112 = string_get_2488(source_text_666, i_667)
            digit0_672 = t_2112
        else:
            digit0_672 = -1
        if digit0_672 < 48:
            t_1331 = True
        else:
            t_1331 = 57 < digit0_672
        if t_1331:
            error_673: 'str20'
            if not is_negative_670:
                t_1332 = digit0_672 != 46
            else:
                t_1332 = False
            if t_1332:
                error_673 = 'JSON value'
            else:
                error_673 = 'digit'
            expected_token_error_315(source_text_666, i_667, out_668, error_673)
            return_278 = -1
            fn_669.break_()
        t_2114 = string_next_2489(source_text_666, i_667)
        i_667 = t_2114
        n_digits_674: 'int24' = 1
        t_1336 = int_to_float64_2466(digit0_672 - 48)
        t_1338 = t_1336
        tentative_value_675: 'float54' = t_1338
        if 48 != digit0_672:
            while True:
                if not len14(source_text_666) > i_667:
                    break
                possible_digit_676: 'int24' = string_get_2488(source_text_666, i_667)
                if 48 <= possible_digit_676:
                    t_1341 = possible_digit_676 <= 57
                else:
                    t_1341 = False
                if t_1341:
                    t_2118 = string_next_2489(source_text_666, i_667)
                    i_667 = t_2118
                    n_digits_674 = n_digits_674 + 1
                    t_1344 = tentative_value_675 * 10.0
                    t_1343 = int_to_float64_2466(possible_digit_676 - 48)
                    tentative_value_675 = t_1344 + t_1343
                else:
                    break
        n_digits_after_point_677: 'int24' = 0
        if len14(source_text_666) > i_667:
            t_2120 = string_get_2488(source_text_666, i_667)
            t_1347 = 46 == t_2120
        else:
            t_1347 = False
        if t_1347:
            t_2121 = string_next_2489(source_text_666, i_667)
            i_667 = t_2121
            after_point_678: 'int24' = i_667
            while True:
                if not len14(source_text_666) > i_667:
                    break
                possible_digit_679: 'int24' = string_get_2488(source_text_666, i_667)
                if 48 <= possible_digit_679:
                    t_1351 = possible_digit_679 <= 57
                else:
                    t_1351 = False
                if t_1351:
                    t_2124 = string_next_2489(source_text_666, i_667)
                    i_667 = t_2124
                    n_digits_674 = n_digits_674 + 1
                    n_digits_after_point_677 = n_digits_after_point_677 + 1
                    t_1354 = tentative_value_675 * 10.0
                    t_1353 = int_to_float64_2466(possible_digit_679 - 48)
                    tentative_value_675 = t_1354 + t_1353
                else:
                    break
            if i_667 == after_point_678:
                expected_token_error_315(source_text_666, i_667, out_668, 'digit')
                return_278 = -1
                fn_669.break_()
        n_exponent_digits_680: 'int24' = 0
        if len14(source_text_666) > i_667:
            t_1357 = string_get_2488(source_text_666, i_667) | 32
            t_1358 = 101 == t_1357
        else:
            t_1358 = False
        if t_1358:
            t_2128 = string_next_2489(source_text_666, i_667)
            i_667 = t_2128
            if not len14(source_text_666) > i_667:
                expected_token_error_315(source_text_666, i_667, out_668, 'sign or digit')
                return_278 = -1
                fn_669.break_()
            after_e_681: 'int24' = string_get_2488(source_text_666, i_667)
            if after_e_681 == 43:
                t_1362 = True
            else:
                t_1362 = after_e_681 == 45
            if t_1362:
                t_2132 = string_next_2489(source_text_666, i_667)
                i_667 = t_2132
            while True:
                if not len14(source_text_666) > i_667:
                    break
                possible_digit_682: 'int24' = string_get_2488(source_text_666, i_667)
                if 48 <= possible_digit_682:
                    t_1366 = possible_digit_682 <= 57
                else:
                    t_1366 = False
                if t_1366:
                    t_2135 = string_next_2489(source_text_666, i_667)
                    i_667 = t_2135
                    n_exponent_digits_680 = n_exponent_digits_680 + 1
                else:
                    break
            if n_exponent_digits_680 == 0:
                expected_token_error_315(source_text_666, i_667, out_668, 'exponent digit')
                return_278 = -1
                fn_669.break_()
        after_exponent_683: 'int24' = i_667
        if n_exponent_digits_680 == 0:
            t_1368 = n_digits_after_point_677 == 0
        else:
            t_1368 = False
        if t_1368:
            value_684: 'float54'
            if is_negative_670:
                value_684 = -tentative_value_675
            else:
                value_684 = tentative_value_675
            if n_digits_674 <= 10:
                if float_lt_eq_2496(-2.147483648E9, value_684):
                    t_1370 = float_lt_eq_2496(value_684, 2.147483647E9)
                else:
                    t_1370 = False
                t_1371 = t_1370
            else:
                t_1371 = False
            if t_1371:
                t_1372 = float64_to_int_2468(value_684)
                t_1374 = t_1372
                out_668.int_value(t_1374)
                return_278 = i_667
                fn_669.break_()
        numeric_token_string_685: 'str20' = source_text_666[start_of_number_671 : i_667]
        double_value_686: 'float54' = nan59
        if n_exponent_digits_680 != 0:
            t_1376 = True
        else:
            t_1376 = n_digits_after_point_677 != 0
        if t_1376:
            try:
                t_1377 = string_to_float64_2470(numeric_token_string_685)
                double_value_686 = t_1377
            except Exception37:
                pass
        if float_not_eq_2497(double_value_686, -inf60):
            if float_not_eq_2497(double_value_686, inf60):
                t_1378 = float_not_eq_2497(double_value_686, nan59)
            else:
                t_1378 = False
            t_1379 = t_1378
        else:
            t_1379 = False
        if t_1379:
            out_668.float64_value(double_value_686)
        else:
            out_668.numeric_token_value(numeric_token_string_685)
        return_278 = i_667
    return return_278
def parse_json_to_producer(source_text_592: 'str20', out_593: 'JsonProducer') -> 'None':
    t_2092: 'int24'
    t_2094: 'Union25[JsonParseErrorReceiver, None]'
    t_2095: 'int24'
    t_2096: 'str20'
    t_1307: 'bool21'
    t_1311: 'int24'
    i_595: 'int24' = 0
    after_value_596: 'int24' = parse_json_value_318(source_text_592, i_595, out_593)
    if after_value_596 >= 0:
        t_1311 = require_string_index58(after_value_596)
        t_2092 = skip_json_spaces_317(source_text_592, t_1311)
        i_595 = t_2092
        if len14(source_text_592) > i_595:
            t_2094 = out_593.parse_error_receiver
            t_1307 = not t_2094 is None
        else:
            t_1307 = False
        if t_1307:
            t_2095 = len_2461(source_text_592)
            t_2096 = source_text_592[i_595 : t_2095]
            store_json_error_316(out_593, str_cat_2492('Extraneous JSON `', t_2096, '`'))
def parse_json(source_text_687: 'str20') -> 'JsonSyntaxTree':
    p_689: 'JsonSyntaxTreeProducer' = JsonSyntaxTreeProducer()
    parse_json_to_producer(source_text_687, p_689)
    return p_689.to_json_syntax_tree()
def boolean_json_adapter() -> 'JsonAdapter[bool21]':
    return BooleanJsonAdapter_148()
def float64_json_adapter() -> 'JsonAdapter[float54]':
    return Float64JsonAdapter_151()
def int_json_adapter() -> 'JsonAdapter[int24]':
    return IntJsonAdapter_154()
def string_json_adapter() -> 'JsonAdapter[str20]':
    return StringJsonAdapter_157()
t = TypeVar56('t', bound = Any27)
def list_json_adapter(adapter_for_t_755: 'JsonAdapter[t]') -> 'JsonAdapter[(Sequence23[t])]':
    return ListJsonAdapter_160(adapter_for_t_755)
