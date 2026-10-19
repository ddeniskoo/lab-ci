from unittest.mock import Mock

import pytest

from shop.cart import Cart


def test_empty_cart_items_count() -> None:
    cart = Cart()
    assert cart.items_count() == 0


def test_add_item_increases_count() -> None:
    cart = Cart()
    cart.add("book", price=200.0, qty=2)
    assert cart.items_count() == 2


def test_items_count_with_fixture(cart_with_items: Cart) -> None:
    assert cart_with_items.items_count() == 6


def test_remove_item() -> None:
    cart = Cart()
    cart.add("book", price=200.0)
    cart.remove("book")
    assert cart.items_count() == 0


def test_add_same_item_increases_quantity() -> None:
    cart = Cart()
    cart.add("book", price=200.0, qty=1)
    cart.add("book", price=250.0, qty=2)
    assert cart.items_count() == 3


def test_total_without_discount() -> None:
    cart = Cart()
    cart.add("book", price=200.0, qty=2)
    assert cart.total() == 400.0


@pytest.mark.parametrize(
    ("discount", "expected"),
    [
        (0, 400.0),
        (10, 360.0),
        (25, 300.0),
        (50, 200.0),
        (100, 0.0),
    ],
)
def test_discounts(discount: int, expected: float) -> None:
    cart = Cart()
    cart.add("book", price=200.0, qty=2)
    assert cart.total(discount_percent=discount) == expected


def test_add_negative_price_raises() -> None:
    cart = Cart()

    with pytest.raises(ValueError, match="price"):
        cart.add("book", price=-1.0)


def test_add_zero_quantity_raises() -> None:
    cart = Cart()

    with pytest.raises(ValueError, match="qty"):
        cart.add("book", price=100.0, qty=0)


def test_remove_missing_item_raises() -> None:
    cart = Cart()

    with pytest.raises(KeyError):
        cart.remove("book")


@pytest.mark.parametrize("discount", [-1, 101])
def test_invalid_discount_raises(discount: int) -> None:
    cart = Cart()

    with pytest.raises(ValueError, match="discount_percent"):
        cart.total(discount_percent=discount)


def test_total_in_usd() -> None:
    rates = Mock()
    rates.get_rate.return_value = 40.0

    cart = Cart()
    cart.add("book", price=400.0)

    assert cart.total_in("USD", rates) == 10.0
    rates.get_rate.assert_called_once_with("USD")


def test_invalid_rate_raises() -> None:
    rates = Mock()
    rates.get_rate.return_value = 0.0

    cart = Cart()
    cart.add("book", price=400.0)

    with pytest.raises(ValueError, match="rate"):
        cart.total_in("USD", rates)


def test_most_expensive_empty_cart() -> None:
    cart = Cart()

    assert cart.most_expensive() is None


def test_most_expensive_returns_item() -> None:
    cart = Cart()
    cart.add("book", price=200.0, qty=1)
    cart.add("pen", price=15.0, qty=4)

    result = cart.most_expensive()

    assert result is not None
    assert result.name == "book"
    assert result.price == 200.0
