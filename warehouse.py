import uuid
import pickle
import json
import csv
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class StorageZone(Enum):
    COLD = "Холодильна камера"
    DRY = "Сухий склад"
    SECURE = "Зона з охороною"

@dataclass
class ExpiryDate:
    expiration_date: datetime
    production_date: datetime

class Item:    
    def __init__(self, name: str, price: float, zone: StorageZone):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.price = price
        self.zone = zone
        self.audit_status = "Очікує аудиту"

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float):
        if value < 0: raise ValueError("Ціна не може бути від'ємною!")
        self._price = value

    def calculate_storage_cost(self, days: int) -> float:
        return self.price * 0.01 * days

    def __str__(self) -> str:
        return f"Товар: {self.name} | Ціна: {self.price} грн | Зона: {self.zone.value}"

class PerishableItem(Item):
    def __init__(self, name: str, price: float, zone: StorageZone, expiry: ExpiryDate):
        super().__init__(name, price, zone)
        self.expiry = expiry

    def calculate_storage_cost(self, days: int) -> float:
        return super().calculate_storage_cost(days) + (25.0 * days)

class Electronics(Item):
    def __init__(self, name: str, price: float, zone: StorageZone, warranty_months: int):
        super().__init__(name, price, zone)
        self.warranty_months = warranty_months

    def calculate_storage_cost(self, days: int) -> float:
        return super().calculate_storage_cost(days) + (self.price * 0.05)

class CostEstimatorFunctor:
    def __init__(self, margin_multiplier: float):
        self.margin_multiplier = margin_multiplier
        self.total_estimated_income = 0.0
        self.calculations_made = 0

    def __call__(self, item: Item, days: int) -> float:
        self.calculations_made += 1
        cost = item.calculate_storage_cost(days) * self.margin_multiplier
        self.total_estimated_income += cost
        return cost

class ColdZoneIterator:
    def __init__(self, items):
        self.items = items
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        while self.index < len(self.items):
            item = self.items[self.index]
            self.index += 1
            if item.zone == StorageZone.COLD:
                return item
        raise StopIteration

class Warehouse:
    def __init__(self):
        self._items = []
        self.config = {}
        self.estimator = None

    def load_config(self, filepath="config.json"):
        if not os.path.exists(filepath):
            default_config = {
                "warehouse_name": "Головний склад №1",
                "margin_multiplier": 1.5,
                "default_page_size": 3
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)

        with open(filepath, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        margin = self.config.get("margin_multiplier", 1.2)
        self.estimator = CostEstimatorFunctor(margin_multiplier=margin)

    def save_system_state(self, filepath="system.pkl"):
        with open(filepath, 'wb') as f:
            pickle.dump(self._items, f)
        print(f"[System] Стан системи успішно збережено у файл '{filepath}'.")

    def load_system_state(self, filepath="system.pkl"):
        try:
            with open(filepath, 'rb') as f:
                self._items = pickle.load(f)
        except FileNotFoundError:
            pass 

    def export_inventory_report(self, filepath="inventory_report.csv"):
        with open(filepath, 'w', newline="", encoding="utf-16") as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(['ID', 'Назва товару', 'Категорія', 'Ціна (грн)', 'Зона зберігання'])
            for item in self._items:
                item_category = type(item).__name__
                writer.writerow([item.id, item.name, item_category, item.price, item.zone.value])
        print(f"[System] Звіт успішно експортовано у файл '{filepath}'.")

    def add_item(self, item: Item):
        self._items.append(item)
        print(f"[Success] Товар '{item.name}' успішно додано на склад!")

    def display_all(self):
        if not self._items:
            print("[Info] Склад наразі порожній.")
            return
        print("\n--- ПОТОЧНИЙ ІНВЕНТАР ---")
        for item in self._items:
            print(item)
        print("-------------------------")