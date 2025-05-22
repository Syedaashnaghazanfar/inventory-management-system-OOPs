import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# test_inventory.py
import pytest
from datetime import datetime, timedelta
from inventory_system import Inventory, Electronics, Grocery, Clothing
from inventory_system import InventoryError, DuplicateProductIDError, OutOfStockError
@pytest.fixture
def sample_inventory():
    inv = Inventory()
    inv.add_product(Electronics("E001", "Phone", 999.99, 10, 2, "Apple"))
    inv.add_product(Grocery("G001", "Milk", 3.5, 20, (datetime.today() + timedelta(days=5)).strftime("%Y-%m-%d")))
    inv.add_product(Clothing("C001", "Shirt", 29.99, 15, "M", "Cotton"))
    return inv


def test_add_duplicate_product(sample_inventory):
    with pytest.raises(DuplicateProductIDError):
        sample_inventory.add_product(Electronics("E001", "Another Phone", 899.99, 5, 1, "Samsung"))


def test_sell_product(sample_inventory):
    sample_inventory.sell_product("E001", 2)
    assert sample_inventory._products["E001"]._quantity_in_stock == 8


def test_sell_product_out_of_stock(sample_inventory):
    with pytest.raises(OutOfStockError):
        sample_inventory.sell_product("E001", 100)


def test_restock_product(sample_inventory):
    sample_inventory.restock_product("G001", 10)
    assert sample_inventory._products["G001"]._quantity_in_stock == 30


def test_search_by_name(sample_inventory):
    results = sample_inventory.search_by_name("milk")
    assert len(results) == 1
    assert results[0]._name.lower() == "milk"


def test_search_by_type(sample_inventory):
    results = sample_inventory.search_by_type("Electronics")
    assert len(results) == 1
    assert isinstance(results[0], Electronics)


def test_remove_expired_products():
    inv = Inventory()
    expired_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    inv.add_product(Grocery("G002", "Yogurt", 2.5, 10, expired_date))
    inv.remove_expired_products()
    assert "G002" not in inv._products


def test_total_inventory_value(sample_inventory):
    total_value = sample_inventory.total_inventory_value()
    assert isinstance(total_value, float)
    assert total_value > 0


def test_remove_nonexistent_product(sample_inventory):
    sample_inventory.remove_product("INVALID_ID")  # should not raise
    assert "INVALID_ID" not in sample_inventory._products


def test_sell_invalid_product(sample_inventory):
    with pytest.raises(InventoryError):
        sample_inventory.sell_product("INVALID", 1)
