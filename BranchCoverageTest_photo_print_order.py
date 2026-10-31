import pytest

from photo_print_order import dispatch_status, extra_print_charge, order_valid


def test_unknown_print_size():
    with pytest.raises(ValueError, match="unknown print size"):
        extra_print_charge("poster", 1, "matte", False)


def test_known_print_size_continues():
    assert extra_print_charge("4x6", 15, "matte", False) == 0


def test_negative_copies():
    with pytest.raises(ValueError, match="invalid copies"):
        extra_print_charge("4x6", -1, "gloss", True)


def test_non_negative_copies_continue():
    assert extra_print_charge("5x7", 15, "matte", False) == 0


def test_member_bonus_on_smaller_sizes():
    # 4x6 includes 20, and a member receives 5 more.
    assert extra_print_charge("4x6", 25, "matte", True) == 0


def test_non_member_does_not_receive_bonus():
    # 21 copies is one past the standard 20, so the matte extra rate applies.
    assert extra_print_charge("4x6", 21, "matte", False) == 4


def test_member_8x10_does_not_receive_bonus():
    # The member bonus is skipped for 8x10, so 11 copies is one extra.
    assert extra_print_charge("8x10", 11, "gloss", True) == 7


def test_no_charge_when_copies_are_within_allowance():
    assert extra_print_charge("5x7", 10, "canvas", True) == 0


def test_matte_rate_for_a_small_extra():
    assert extra_print_charge("4x6", 30, "matte", True) == 20


def test_non_matte_rate_for_a_small_extra():
    assert extra_print_charge("5x7", 25, "gloss", True) == 35


def test_bulk_canvas_adds_both_surcharges():
    # 55 extra: non-matte 7, bulk +2, canvas +5.
    assert extra_print_charge("4x6", 80, "canvas", True) == 770


def test_bulk_matte_skips_canvas_surcharge():
    # 51 extra at matte 4 plus the bulk +2, with no canvas surcharge.
    assert extra_print_charge("4x6", 76, "matte", True) == 306


def test_small_extra_skips_bulk_surcharge():
    assert extra_print_charge("8x10", 12, "gloss", False) == 14


def test_rush_order_accepted_at_copy_limit():
    assert order_valid(40, 50, True) is True


def test_rush_order_rejected_over_copy_limit():
    assert order_valid(1, 51, True) is False


def test_standard_order_rejects_oversized_file():
    assert order_valid(26, 10, False) is False


def test_standard_order_accepts_file_at_size_limit():
    assert order_valid(25, 500, False) is True


def test_standard_order_rejects_too_many_copies():
    assert order_valid(25, 501, False) is False


def test_framed_domestic_on_time():
    assert dispatch_status(24, True, False) == "on_time"


def test_unframed_domestic_on_time():
    assert dispatch_status(12, False, False) == "on_time"


def test_international_extends_the_cutoff():
    assert dispatch_status(36, False, True) == "on_time"


def test_framed_international_on_time():
    assert dispatch_status(48, True, True) == "on_time"


def test_tight_when_inside_the_six_hour_window():
    assert dispatch_status(18, True, False) == "tight"


def test_missed_when_outside_the_window():
    assert dispatch_status(17, True, False) == "missed"


def test_unframed_international_missed():
    assert dispatch_status(10, False, True) == "missed"
