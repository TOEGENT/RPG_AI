import re
import difflib


def safe_input(string="", expect_type=str, filter=lambda x: x):
    is_regex = isinstance(expect_type, re.Pattern)

    # нормализация новых вариантов
    multi_type = expect_type if isinstance(expect_type, (tuple, list)) else (expect_type,)
    multi_filter = (
        filter if isinstance(filter, (tuple, list)) else (filter,)
    )

    while True:
        raw = input(string)

        # режим регулярки остаётся как раньше
        if is_regex:
            if re.fullmatch(expect_type, raw):
                return raw
            print("Неверный ввод!!")
            continue

        # режим expect_type=None → возвращаем сырую строку, но фильтруем
        if expect_type is None:
            val = raw
            if any(f(val) for f in multi_filter):
                return val
            print("Неверный ввод!!")
            continue

        # режим одного или нескольких типов
        converted = None
        success = False

        for t in multi_type:
            try:
                converted = t(raw)
                success = True
                break
            except (ValueError, TypeError):
                continue

        if not success:
            print("Неверный ввод!!")
            continue

        # применяем один или несколько фильтров
        if any(f(converted) for f in multi_filter) or converted is None:
            return converted

        print("Неверный ввод!!")


def closest_match(target, choices):
    matches = difflib.get_close_matches(target, choices, n=1, cutoff=0.51)
    return matches[0] if matches else None
