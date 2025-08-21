# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: 计算器
import re


def cal(calc_formula: str) -> str:
    """
    公式计算，保持原有格式计算数值的项
    :param calc_formula:
    :return:
    "64.7*2+(70.6+332.9)/2*2+13*2+L"  ->  "558.9+L"
    "2*L+64.7-8"  ->  "2*L+56.7"
    "(63~64)*2+10*2"  ->  "(63~64)*2+20"
    """
    calc_formula = calc_formula.replace("（", "(").replace("）", ")").replace(" ", "")
    target_list = re.split(r"(?=[-+])", calc_formula)
    number_list = []
    not_number_list = []
    number_is_first = False
    # 过滤
    for i in range(len(target_list) - 1, -1, -1):
        target = target_list[i]
        # 过滤空字符串
        if not str(target).strip():
            target_list.pop(i)
        # 过滤非有效值
        if target in ["+", "-", "*", "/"]:
            target_list.pop(i)
    # 获取数值列表和非数值列表
    for i in range(0, len(target_list)):
        target = target_list[i]
        if len(str(target).split("|")) > 1:
            not_number_list.append(target)
            continue
        try:
            eval(target)
            number_list.append(target)
            if i == 0:
                number_is_first = True
        except Exception as e:
            not_number_list.append(target)
    number_str = ["{0}".format(number) for number in number_list]
    number_str = "".join(number_str)
    union_symbol = ""
    if len(number_str) > 0:
        if number_str[0] in ["*", "/"]:
            union_symbol = number_str[0]
            number_str = number_str[1:]
    try:
        num = eval("".join(number_str))
    except Exception as e:
        num = number_str
    if isinstance(num, int) or isinstance(num, float):
        number_str_cal_result = round(num, 8) if len(number_str) > 0 else ""
    else:
        number_str_cal_result = num if len(number_str) > 0 else ""
    not_number_str = ["{0}".format(not_number) for not_number in not_number_list]
    if number_is_first:
        result_union = str(number_str_cal_result) + union_symbol + "".join(not_number_str)
    else:
        if not number_str_cal_result and not union_symbol and len(str(number_str_cal_result)) > 0:
            # print(number_str_cal_result, type(number_str_cal_result), len(str(number_str_cal_result)))
            if number_str_cal_result > 0:
                union_symbol = "+"
        result_union = "".join(not_number_str) + union_symbol + str(number_str_cal_result)
    return result_union


if __name__ == "__main__":
    # print(cal("64.7*2+(70.6+332.9)/2*2+13*2+L"))
    # print(cal("2*L+64.7-8"))
    # print(cal("(63~64)*2+10*2"))
    # print(cal("64.7*2+339.7*2+13*2"))
    print(cal("2+/2+1000"))
    # print(cal(".+250+320+200+200+200"))
    print(cal("*250+200"))
    print(cal("+752+2+"))
    # print(cal("+05+120"))
    # print(cal("100*2/4"))
    # print(cal("60.3+733.9"))
    # print(cal("1811-(137+350)"))
    print(cal("10+20+均353.5"))
    # print(round(eval("均353.5"), 8))
    print(cal("811-846.6"))
    print(cal("846.6-811"))
    pass

