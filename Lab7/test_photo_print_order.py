import pytest
from hypothesis import given, strategies as st

from photo_print_order import INCLUDED_PRINTS, dispatch_status, extra_print_charge, order_valid

FINISHES = ["matte", "gloss", "canvas"]
SIZES = sorted(INCLUDED_PRINTS)
NAN = float("nan")

# Anything a caller could pass, including values of the wrong type.
anything = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(),
    st.text(),
    st.binary(),
    st.lists(st.integers()),
)


def mixed(valid):
    """Mostly arbitrary values, with valid ones mixed in to reach deeper code."""
    return st.one_of(valid, anything)


# Example tests
def test_within_included_prints():
    assert extra_print_charge("4x6", 15, "matte", False) == 0


def test_order_valid():
    assert order_valid(10, 100, False) is True


# extra_print_charge
@given(mixed(st.sampled_from(SIZES)), mixed(st.integers(0, 600)), mixed(st.sampled_from(FINISHES)), anything)
def test_extra_print_charge_arbitrary_input(size, copies, finish, is_member):
    try:
        charge = extra_print_charge(size, copies, finish, is_member)
    except ValueError:
        return
    assert type(charge) is int and charge >= 0


@given(st.sampled_from(SIZES), st.integers(0, 10_000), st.sampled_from(FINISHES), st.booleans())
def test_extra_print_charge_zero_within_allowance(size, copies, finish, is_member):
    allowance = INCLUDED_PRINTS[size] + (5 if is_member and size != "8x10" else 0)
    charge = extra_print_charge(size, copies, finish, is_member)
    assert type(charge) is int
    assert (charge == 0) == (copies <= allowance)


@given(
    st.sampled_from(SIZES),
    st.sampled_from(FINISHES),
    st.booleans(),
    st.integers(0, 10_000),
    st.integers(0, 10_000),
)
def test_extra_print_charge_never_drops_with_more_copies(size, finish, is_member, a, b):
    low, high = sorted((a, b))
    assert extra_print_charge(size, low, finish, is_member) <= extra_print_charge(size, high, finish, is_member)


@given(st.one_of(st.floats(), st.booleans(), st.text(), st.none()))
def test_non_integer_copies_rejected(copies):
    with pytest.raises(ValueError):
        extra_print_charge("4x6", copies, "matte", False)


@given(anything.filter(lambda f: f not in FINISHES))
def test_unknown_finish_rejected(finish):
    with pytest.raises(ValueError):
        extra_print_charge("4x6", 30, finish, False)


@given(st.one_of(st.none(), st.integers(), st.text()))
def test_non_bool_membership_rejected(is_member):
    with pytest.raises(ValueError):
        extra_print_charge("4x6", 30, "matte", is_member)


# order_valid
@given(mixed(st.floats(0, 100)), mixed(st.integers(0, 600)), mixed(st.booleans()))
def test_order_valid_arbitrary_input_returns_bool(file_mb, copies, is_rush):
    assert isinstance(order_valid(file_mb, copies, is_rush), bool)


@given(st.floats(0, 1000), st.integers(0, 2000), st.booleans())
def test_order_valid_matches_limits(file_mb, copies, is_rush):
    expected = copies <= 50 if is_rush else (file_mb <= 25 and copies <= 500)
    assert order_valid(file_mb, copies, is_rush) is expected


@given(
    st.one_of(st.integers(max_value=-1), st.floats(max_value=-1e-9), st.just(NAN), st.none(), st.text()),
    st.booleans(),
)
def test_order_valid_rejects_bad_file_size(file_mb, is_rush):
    assert order_valid(file_mb, 10, is_rush) is False


@given(
    st.one_of(st.integers(max_value=-1), st.floats(), st.booleans(), st.none(), st.text()),
    st.booleans(),
)
def test_order_valid_rejects_bad_copies(copies, is_rush):
    assert order_valid(1, copies, is_rush) is False


# dispatch_status
@given(mixed(st.floats(-100, 200)), mixed(st.booleans()), mixed(st.booleans()))
def test_dispatch_status_arbitrary_input(hours, is_framed, is_international):
    try:
        status = dispatch_status(hours, is_framed, is_international)
    except ValueError:
        return
    assert status in {"on_time", "tight", "missed"}


@given(
    st.one_of(st.none(), st.booleans(), st.text(), st.lists(st.integers()), st.sampled_from([NAN, float("inf"), float("-inf")])),
    st.booleans(),
    st.booleans(),
)
def test_dispatch_status_rejects_bad_hours(hours, is_framed, is_international):
    with pytest.raises(ValueError):
        dispatch_status(hours, is_framed, is_international)


@given(
    st.floats(-100, 200),
    st.one_of(st.none(), st.integers(), st.text()),
    st.one_of(st.none(), st.integers(), st.text()),
)
def test_dispatch_status_rejects_non_bool_flags(hours, is_framed, is_international):
    with pytest.raises(ValueError):
        dispatch_status(hours, is_framed, is_international)


@given(st.floats(-100, 200), st.floats(-100, 200), st.booleans(), st.booleans())
def test_dispatch_status_never_worse_with_more_notice(a, b, is_framed, is_international):
    rank = {"missed": 0, "tight": 1, "on_time": 2}
    low, high = sorted((a, b))
    assert rank[dispatch_status(low, is_framed, is_international)] <= rank[dispatch_status(high, is_framed, is_international)]
