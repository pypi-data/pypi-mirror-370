from builtins import bool as bool21, str as str20, Exception as Exception37, int as int24, list as list17, tuple as tuple18, len as len14
from typing import MutableSequence as MutableSequence32, Callable as Callable22, Sequence as Sequence23, Union as Union25
from temper_core import Pair as Pair0, list_join as list_join33, list_map as list_map34, int_to_string as int_to_string15, listed_reduce_from as listed_reduce_from35, str_cat as str_cat16, string_split as string_split36, list_get as list_get9
tuple_2443 = tuple18
list_join_2445 = list_join33
list_2446 = list17
pair_2447 = Pair0
list_map_2448 = list_map34
len_2449 = len14
int_to_string_2450 = int_to_string15
listed_reduce_from_2451 = listed_reduce_from35
str_cat_2452 = str_cat16
string_split_2453 = string_split36
list_get_2454 = list_get9
class Test:
    failed_on_assert_60: 'bool21'
    passing_61: 'bool21'
    messages_62: 'MutableSequence32[str20]'
    __slots__ = ('failed_on_assert_60', 'passing_61', 'messages_62')
    def assert_(this_9, success_38: 'bool21', message_39: 'Callable22[[], str20]') -> 'None':
        t_353: 'str20'
        if not success_38:
            this_9.passing_61 = False
            t_353 = message_39()
            this_9.messages_62.append(t_353)
    def assert_hard(this_10, success_42: 'bool21', message_43: 'Callable22[[], str20]') -> 'None':
        this_10.assert_(success_42, message_43)
        if not success_42:
            this_10.failed_on_assert_60 = True
            assert False, str20(this_10.messages_combined())
    def soft_fail_to_hard(this_11) -> 'None':
        if this_11.has_unhandled_fail:
            this_11.failed_on_assert_60 = True
            assert False, str20(this_11.messages_combined())
    @property
    def passing(this_13) -> 'bool21':
        return this_13.passing_61
    def messages(this_14) -> 'Sequence23[str20]':
        "Messages access is presented as a function because it likely allocates. Also,\nmessages might be automatically constructed in some cases, so it's possibly\nunwise to depend on their exact formatting.\n\nthis__14: Test\n"
        return tuple_2443(this_14.messages_62)
    @property
    def failed_on_assert(this_15) -> 'bool21':
        return this_15.failed_on_assert_60
    @property
    def has_unhandled_fail(this_16) -> 'bool21':
        t_224: 'bool21'
        if this_16.failed_on_assert_60:
            t_224 = True
        else:
            t_224 = this_16.passing_61
        return not t_224
    def messages_combined(this_17) -> 'Union25[str20, None]':
        return_31: 'Union25[str20, None]'
        if not this_17.messages_62:
            return_31 = None
        else:
            def fn_346(it_59: 'str20') -> 'str20':
                return it_59
            return_31 = list_join_2445(this_17.messages_62, ', ', fn_346)
        return return_31
    def __init__(this_21) -> None:
        this_21.failed_on_assert_60 = False
        this_21.passing_61 = True
        t_345: 'MutableSequence32[str20]' = list_2446()
        this_21.messages_62 = t_345
def process_test_cases(test_cases_64: 'Sequence23[(Pair0[str20, (Callable22[[Test], None])])]') -> 'Sequence23[(Pair0[str20, (Sequence23[str20])])]':
    def fn_342(test_case_66: 'Pair0[str20, (Callable22[[Test], None])]') -> 'Pair0[str20, (Sequence23[str20])]':
        t_337: 'bool21'
        t_340: 'Sequence23[str20]'
        t_206: 'bool21'
        t_208: 'bool21'
        key_68: 'str20' = test_case_66.key
        fun_69: 'Callable22[[Test], None]' = test_case_66.value
        test_70: 'Test' = Test()
        had_bubble_71: 'bool21' = False
        try:
            fun_69(test_70)
        except Exception37:
            had_bubble_71 = True
        messages_72: 'Sequence23[str20]' = test_70.messages()
        failures_73: 'Sequence23[str20]'
        if test_70.passing:
            t_206 = not had_bubble_71
        else:
            t_206 = False
        if t_206:
            failures_73 = ()
        else:
            if had_bubble_71:
                t_337 = test_70.failed_on_assert
                t_208 = not t_337
            else:
                t_208 = False
            if t_208:
                all_messages_74: 'MutableSequence32[str20]' = list_2446(messages_72)
                all_messages_74.append('Bubble')
                t_340 = tuple_2443(all_messages_74)
                failures_73 = t_340
            else:
                failures_73 = messages_72
        return pair_2447(key_68, failures_73)
    return list_map_2448(test_cases_64, fn_342)
def report_test_results(test_results_75: 'Sequence23[(Pair0[str20, (Sequence23[str20])])]', write_line_76: 'Callable22[[str20], None]') -> 'None':
    t_317: 'int24'
    write_line_76('<testsuites>')
    total_79: 'str20' = int_to_string_2450(len_2449(test_results_75))
    def fn_309(fails_81: 'int24', test_result_82: 'Pair0[str20, (Sequence23[str20])]') -> 'int24':
        t_180: 'int24'
        if not test_result_82.value:
            t_180 = 0
        else:
            t_180 = 1
        return fails_81 + t_180
    fails_80: 'str20' = int_to_string_2450(listed_reduce_from_2451(test_results_75, 0, fn_309))
    totals_84: 'str20' = str_cat_2452("tests='", total_79, "' failures='", fails_80, "'")
    write_line_76(str_cat_2452("  <testsuite name='suite' ", totals_84, " time='0.0'>"))
    def escape_78(s_85: 'str20') -> 'str20':
        t_303: 'Sequence23[str20]' = string_split_2453(s_85, "'")
        def fn_302(x_87: 'str20') -> 'str20':
            return x_87
        return list_join_2445(t_303, '&apos;', fn_302)
    i_88: 'int24' = 0
    while True:
        t_317 = len_2449(test_results_75)
        if not i_88 < t_317:
            break
        test_result_89: 'Pair0[str20, (Sequence23[str20])]' = list_get_2454(test_results_75, i_88)
        failure_messages_90: 'Sequence23[str20]' = test_result_89.value
        name_91: 'str20' = escape_78(test_result_89.key)
        basics_92: 'str20' = str_cat_2452("name='", name_91, "' classname='", name_91, "' time='0.0'")
        if not failure_messages_90:
            write_line_76(str_cat_2452('    <testcase ', basics_92, ' />'))
        else:
            write_line_76(str_cat_2452('    <testcase ', basics_92, '>'))
            def fn_308(it_94: 'str20') -> 'str20':
                return it_94
            message_93: 'str20' = escape_78(list_join_2445(failure_messages_90, ', ', fn_308))
            write_line_76(str_cat_2452("      <failure message='", message_93, "' />"))
            write_line_76('    </testcase>')
        i_88 = i_88 + 1
    write_line_76('  </testsuite>')
    write_line_76('</testsuites>')
def run_test_cases(test_cases_95: 'Sequence23[(Pair0[str20, (Callable22[[Test], None])])]') -> 'str20':
    report_97: 'list17[str20]' = ['']
    t_298: 'Sequence23[(Pair0[str20, (Sequence23[str20])])]' = process_test_cases(test_cases_95)
    def fn_296(line_98: 'str20') -> 'None':
        report_97.append(line_98)
        report_97.append('\n')
    report_test_results(t_298, fn_296)
    return ''.join(report_97)
def run_test(test_fun_99: 'Callable22[[Test], None]') -> 'None':
    test_101: 'Test' = Test()
    try:
        test_fun_99(test_101)
    except Exception37:
        def fn_290() -> 'str20':
            return 'bubble during test running'
        test_101.assert_(False, fn_290)
    test_101.soft_fail_to_hard()
