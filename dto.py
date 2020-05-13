from dataclasses import dataclass
from typing import List

@dataclass
class Product:
  sku: str
  product: str
  skuName: str
  productBasePrice: int
  skuPricePerUnit: float
  categories: List[str]
  quantity: int

@dataclass
class InventoryDetail:
  basePrice: float
  Name: str
  Active: int
  SetDefault: int
  Available: int
  SKU: str
  Price: float
  ReadonlyPrice: float
  btnSubmit: str
