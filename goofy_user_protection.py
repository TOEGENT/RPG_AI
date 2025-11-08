import re
import difflib


def safe_input(string="", expect_type=str, filter=lambda x: x):
    while True:
        if not (isinstance(expect_type, re.Pattern)):  # если не регулярное выражение
            try:
                temp = expect_type(
                    input(string)
                )  # Если expect_type — скомпилированное регулярное выражение, то проверяем ввод через полное совпадение (re.fullmatch)

                if filter(temp) or temp == None:  # если подходит по условию
                    return temp
                else:
                    print("Неверный ввод!")
            except (ValueError, TypeError):
                print("Неверный ввод!!")
        else:  # если регулярка, то смотрим на соответствие

            user_input = input(string)
            if re.fullmatch(expect_type, user_input):
                return user_input
            print("Неверный ввод!!")


def closest_match(target, choices):
    matches = difflib.get_close_matches(
        target, choices, n=1, cutoff=0.51
    )  # cutoff=0 гарантирует, что всегда вернётся хотя бы один "наиболее близкий" вариант,
    return matches[0] if matches else None
