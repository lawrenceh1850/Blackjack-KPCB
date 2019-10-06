def is_num(input):
    try:
        x = int(input)
        return True
    except BaseException:
        return False


def y_or_n(input):
    input = input.lower()
    return input == "y" or input == "n"


def is_num_within_bounds(min, max, inclusive=True):
    min_closure = min
    max_closure = max

    def func(x):
        if inclusive:
            return is_num(x) and float(x) >= min and float(x) <= max
        else:
            return is_num(x) and float(x) > min and float(x) < max
    return func


def unique_strs(picked_strs):
    picked_strs_closure = picked_strs

    def func(x):
        valid = len(x) > 0 and x not in picked_strs_closure
        picked_strs_closure.add(x)
        return valid
    return func
