import math

INCLUDED_PRINTS = {"4x6": 20, "5x7": 15, "8x10": 10}
FINISHES = ("matte", "gloss", "canvas")


def _is_count(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_number(value):
    if isinstance(value, bool):
        return False
    return isinstance(value, int) or (isinstance(value, float) and math.isfinite(value))


def extra_print_charge(print_size, copies, finish, is_member):
    if not isinstance(print_size, str) or print_size not in INCLUDED_PRINTS:
        raise ValueError("unknown print size")
    if not _is_count(copies):
        raise ValueError("invalid copies")
    if finish not in FINISHES:
        raise ValueError("unknown finish")
    if not isinstance(is_member, bool):
        raise ValueError("invalid membership flag")
    included = INCLUDED_PRINTS[print_size]
    if is_member and print_size != "8x10":
        included += 5
    extra = copies - included
    if extra <= 0:
        return 0
    if finish == "matte":
        rate = 4
    else:
        rate = 7
    if extra > 50:
        rate = rate + 2
        if finish == "canvas":
            rate += 5
    return extra * rate


def order_valid(file_mb, copies, is_rush):
    if not isinstance(is_rush, bool):
        return False
    if not _is_number(file_mb) or file_mb < 0 or not _is_count(copies):
        return False
    if is_rush:
        return copies <= 50
    if file_mb > 25:
        return False
    return copies <= 500


def dispatch_status(hours_before_dispatch, is_framed, is_international):
    if not _is_number(hours_before_dispatch):
        raise ValueError("invalid hours")
    if not isinstance(is_framed, bool) or not isinstance(is_international, bool):
        raise ValueError("invalid flag")
    if is_framed:
        cutoff = 24
    else:
        cutoff = 12
    if is_international:
        cutoff += 24
    if hours_before_dispatch >= cutoff:
        return "on_time"
    elif hours_before_dispatch >= cutoff - 6:
        return "tight"
    return "missed"

if __name__ == "__main__":
    nan = float("nan")
    calls = [
        (extra_print_charge, ("4x6", 30, "matte", False)),
        (extra_print_charge, ("4x6", 80, "canvas", True)),
        (extra_print_charge, ("4x6", nan, "matte", False)),
        (extra_print_charge, ("4x6", 25.5, "matte", False)),
        (extra_print_charge, ("4x6", 25, "sepia", False)),
        (extra_print_charge, (["4x6"], 25, "matte", False)),
        (extra_print_charge, ("4x6", None, "matte", False)),
        (order_valid, (10, 100, False)),
        (order_valid, (10, -5, False)),
        (order_valid, (-1, 10, False)),
        (order_valid, (nan, 10, False)),
        (order_valid, (None, 10, False)),
        (dispatch_status, (20, False, False)),
        (dispatch_status, (nan, False, False)),
        (dispatch_status, (None, True, False)),
    ]
    for fn, args in calls:
        try:
            result = repr(fn(*args))
        except Exception as exc:
            result = f"{type(exc).__name__}: {exc}"
        print(f"{fn.__name__}{args} -> {result}")
