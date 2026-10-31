import pytest

from photo_print_order import dispatch_status, extra_print_charge, order_valid


def test_within_included_prints():
    assert extra_print_charge("4x6", 15, "matte", False) == 0


def test_unknown_print_size():
    with pytest.raises(ValueError, match="unknown print size"):
        extra_print_charge("poster", 1, "matte", False)


def test_negative_copies():
    with pytest.raises(ValueError, match="invalid copies"):
        extra_print_charge("4x6", -1, "matte", False)


def test_member_within_bonus_allowance():
    # 4x6 includes 20, members get 5 more on sizes other than 8x10.
    assert extra_print_charge("4x6", 10, "matte", True) == 0


def test_member_matte_extra_within_standard_rate():
    # 25 included, 5 extra at the matte rate of 4.
    assert extra_print_charge("4x6", 30, "matte", True) == 20


def test_member_gloss_extra_within_standard_rate():
    # 5x7 member allowance is 20; 5 extra at the non-matte rate of 7.
    assert extra_print_charge("5x7", 25, "gloss", True) == 35


def test_member_canvas_bulk_surcharge():
    # 55 extra: base 7, bulk +2, canvas +5.
    assert extra_print_charge("4x6", 80, "canvas", True) == 770


def test_order_valid():
    assert order_valid(10, 100, False) is True


def test_rush_order_within_limit():
    assert order_valid(10, 40, True) is True


def test_oversized_file_rejected_when_not_rush():
    assert order_valid(30, 10, False) is False


def test_framed_international_missed():
    # Framed cutoff 24, plus 24 for international. 30 hours is below 42.
    assert dispatch_status(30, True, True) == "missed"


def test_unframed_domestic_on_time():
    assert dispatch_status(20, False, False) == "on_time"


def test_unframed_domestic_tight():
    # Domestic unframed cutoff is 12; 8 hours is inside the 6-hour window.
    assert dispatch_status(8, False, False) == "tight"
