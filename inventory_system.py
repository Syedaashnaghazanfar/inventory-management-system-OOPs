# inventory management system 

from abc import ABC, abstractmethod
from datetime import datetime
import json


# ---------- Custom Exceptions ----------
class InventoryError(Exception):
    pass

class DuplicateProductIDError(InventoryError):
    pass

class OutOfStockError(InventoryError):
    pass

class InvalidProductDataError(InventoryError):
    pass


# ---------- Abstract Base Class ----------


#we use ABC to define an abstract base class for products here ABC is a module in Python's standard library that provides tools for defining abstract base classes.
class Product(ABC):
    #encapsulated products
    def __init__(self, product_id, name, price, quantity_in_stock):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._quantity_in_stock = quantity_in_stock
    #methods 
    def restock(self, amount):
        self._quantity_in_stock += amount

    def sell(self, quantity):
        if quantity > self._quantity_in_stock:
            raise OutOfStockError(f"Not enough stock for product {self._name}")
        self._quantity_in_stock -= quantity

    def get_total_value(self):
        return self._price * self._quantity_in_stock
    #here @abstractmethod is a decorator that indicates that the method is abstract and must be implemented by any subclass of the abstract base class.
    @abstractmethod
    # __str__ is a special method in Python that is used to define a string representation of an object. It is called when you use the str() function or print() function on an object.
    #it is used to provide a human-readable string representation of the object.
    def __str__(self):
        pass
    #this returns the dictionary representation of the object.
    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "product_id": self._product_id,
            "name": self._name,
            "price": self._price,
            "quantity_in_stock": self._quantity_in_stock,
        }


# ---------- Subclasses ----------


#we inherit the Product class to create specific product types
class Electronics(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, warranty_years, brand):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.warranty_years = warranty_years
        self.brand = brand

    def __str__(self):
        return f"[Electronics] {self._name} (Brand: {self.brand}, Warranty: {self.warranty_years} yrs) - ${self._price}, Qty: {self._quantity_in_stock}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"warranty_years": self.warranty_years, "brand": self.brand})
        return data


class Grocery(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, expiry_date):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.expiry_date = expiry_date  # "YYYY-MM-DD"

    def is_expired(self):
        return datetime.strptime(self.expiry_date, "%Y-%m-%d").date() < datetime.today().date()

    def __str__(self):
        status = "Expired" if self.is_expired() else "Fresh"
        return f"[Grocery] {self._name} (Expires: {self.expiry_date}, Status: {status}) - ${self._price}, Qty: {self._quantity_in_stock}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"expiry_date": self.expiry_date})
        return data


class Clothing(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, size, material):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.size = size
        self.material = material

    def __str__(self):
        return f"[Clothing] {self._name} (Size: {self.size}, Material: {self.material}) - ${self._price}, Qty: {self._quantity_in_stock}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"size": self.size, "material": self.material})
        return data




# ---------- Inventory Class ----------
class Inventory:
    #made a empty dictionary to store products
    #this is a constructor method that initializes the instance of the class when it is created.

    def __init__(self):
        self._products = {}

    #this method is used to add a product to the inventory.
    #it takes a product object as an argument and adds it to the _products dictionary.

    def add_product(self, product: Product):
        # Check if the product ID already exists in the inventory
        #if the product ID already exists in the inventory, it raises a DuplicateProductIDError.
        if product._product_id in self._products:
            raise DuplicateProductIDError("Product ID already exists.")
        self._products[product._product_id] = product

    #this method is used to remove a product from the inventory.
    #it takes a product ID as an argument and removes the corresponding product from the _products dictionary.

    def remove_product(self, product_id):
        self._products.pop(product_id, None)


    #this method is used to search for a product by its name.
    #it takes a name as an argument and returns a list of products that match the name.

    def search_by_name(self, name):
        return [p for p in self._products.values() if name.lower() in p._name.lower()]
    
    #this method is used to search for a product by its type.
    #it takes a product type as an argument and returns a list of products that match the type.

    def search_by_type(self, product_type):
        return [p for p in self._products.values() if p.__class__.__name__.lower() == product_type.lower()]
    
    #this method is used to list all products in the inventory.
    #it returns a list of all products in the _products dictionary.

    def list_all_products(self):
        return list(self._products.values())
    
    #this method is used to sell a product.
    #it takes a product ID and a quantity as arguments and sells the specified quantity of the product.

    def sell_product(self, product_id, quantity):
        if product_id not in self._products:
            raise InventoryError("Product not found.")
        self._products[product_id].sell(quantity)

    #this method is used to restock a product.
    #it takes a product ID and a quantity as arguments and restocks the specified quantity of the product.

    def restock_product(self, product_id, quantity):
        if product_id not in self._products:
            raise InventoryError("Product not found.")
        self._products[product_id].restock(quantity)

    #this method is used to get the total value of the inventory.
    #it returns the sum of the total value of all products in the _products dictionary.

    def total_inventory_value(self):
        return sum(p.get_total_value() for p in self._products.values())
    
    #this method is used to remove expired products from the inventory.
    #it checks each product in the _products dictionary and removes it if it is a Grocery product and is expired.

    def remove_expired_products(self):
        to_remove = [pid for pid, p in self._products.items()
                     if isinstance(p, Grocery) and p.is_expired()]
        for pid in to_remove:
            del self._products[pid]

    #this method is used to save the inventory to a file.
    
    def save_to_file(self, filename):
        with open(filename, "w") as f:
            data = [p.to_dict() for p in self._products.values()]
            json.dump(data, f)

    def load_from_file(self, filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            for item in data:
                cls_name = item.pop("type")
                product = self._create_product_from_dict(cls_name, item)
                self._products[product._product_id] = product
        except Exception as e:
            raise InvalidProductDataError(f"Error loading data: {e}")

    def _create_product_from_dict(self, cls_name, data):
        if cls_name == "Electronics":
            return Electronics(**data)
        elif cls_name == "Grocery":
            return Grocery(**data)
        elif cls_name == "Clothing":
            return Clothing(**data)
        else:
            raise InvalidProductDataError(f"Unknown product type: {cls_name}")


# ---------- CLI Menu ----------
def run_cli():
    inventory = Inventory()
    while True:
        print("\n📦 Inventory Management System Menu:")
        print("1. Add Product")
        print("2. Sell Product")
        print("3. Search Product")
        print("4. View All Products")
        print("5. Restock Product")
        print("6. Remove Expired Products")
        print("7. Save Inventory to File")
        print("8. Load Inventory from File")
        print("9. View Total Inventory Value")
        print("0. Exit")
        choice = input("Enter choice: ")

        try:
            if choice == "1":
                ptype = input("Product Type (Electronics/Grocery/Clothing): ").strip().lower()
                pid = input("Product ID: ")
                name = input("Name: ")
                price = float(input("Price: "))
                qty = int(input("Quantity: "))

                if ptype == "electronics":
                    warranty = int(input("Warranty Years: "))
                    brand = input("Brand: ")
                    product = Electronics(pid, name, price, qty, warranty, brand)
                elif ptype == "grocery":
                    expiry = input("Expiry Date (YYYY-MM-DD): ")
                    product = Grocery(pid, name, price, qty, expiry)
                elif ptype == "clothing":
                    size = input("Size: ")
                    material = input("Material: ")
                    product = Clothing(pid, name, price, qty, size, material)
                else:
                    print("Invalid product type.")
                    continue

                inventory.add_product(product)
                print("✅ Product added successfully.")

            elif choice == "2":
                pid = input("Product ID: ")
                qty = int(input("Quantity to sell: "))
                inventory.sell_product(pid, qty)
                print("🛒 Product sold.")

            elif choice == "3":
                name = input("Enter product name to search: ")
                results = inventory.search_by_name(name)
                if results:
                    for p in results:
                        print(p)
                else:
                    print("No products found.")

            elif choice == "4":
                for p in inventory.list_all_products():
                    print(p)

            elif choice == "5":
                pid = input("Product ID: ")
                qty = int(input("Restock quantity: "))
                inventory.restock_product(pid, qty)
                print("🔄 Product restocked.")

            elif choice == "6":
                inventory.remove_expired_products()
                print("🧹 Expired products removed.")

            elif choice == "7":
                fname = input("Enter filename to save (e.g. inventory.json): ")
                inventory.save_to_file(fname)
                print("💾 Inventory saved.")

            elif choice == "8":
                fname = input("Enter filename to load: ")
                inventory.load_from_file(fname)
                print("📂 Inventory loaded.")

            elif choice == "9":
                print(f"💰 Total Inventory Value: ${inventory.total_inventory_value():.2f}")

            elif choice == "0":
                print("🚪 Exiting system. Bye!")
                break

            else:
                print("Invalid choice.")

        except Exception as e:
            print(f"⚠️ Error: {e}")

