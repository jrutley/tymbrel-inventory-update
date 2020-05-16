import os
from typing import List
from dto import Product
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
import json
from inventory import update_inventory_on_detail_page

def setup():
  session = requests.Session()
  session.headers['user-agent']="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
  url = "https://www.tymbrel.com/manage/login/"
  session.get(url)
  payload = {'username': os.getenv("USER_EMAIL"), 'password': os.getenv("PASSWORD"), 'Login': 'Login'}
  session.post(url, payload)
  website_code = os.getenv("WEBSITECODE")
  url = f"https://www.tymbrel.com/manage/jump/?Target={website_code}"
  session.get(url)
  return session

def scrape_inventory_master_page(p: Product, session):
    error, content_id = get_content_id(p.sku, p.product, p.skuName, True, session)
    if error is not None:
      error, content_id = get_content_id(p.sku, p.product, p.skuName, False, session)
      if error is not None:
        return error

    content_url = f"https://www.tymbrel.com/manage/site/simplecart2/product/{content_id}/inventory/"
    res = session.get(content_url)
    inventory_id = find_inventory_item(res.content, p.sku, p.skuName)
    if isinstance(inventory_id, Exception):
      return inventory_id
    return content_url+inventory_id

def insert_products(products: List[Product], session):
  for p in products:
    print(f"Updating \"{p.product}\" \"{p.skuName}\"")
    detail_url_or_error = scrape_inventory_master_page(p, session)
    if isinstance(detail_url_or_error, Exception):
      yield (detail_url_or_error)
      continue
    yield update_inventory_on_detail_page(session, detail_url_or_error, p.quantity)

class InventoryNotFoundError(Exception):
  def __init__(self, sku, skuName):
    self.sku = sku
    self.skuName = skuName

class SkuNotFoundError(Exception):
  def __init__(self, sku, name, skuName):
    self.sku = sku
    self.name = name
    self.skuName = skuName

def extract_product_id_from_products(productList: list, name: str, sku: str, skuName: str) -> (Exception, int):
  for p in productList:
    if name == p['text']:
      return (None, int(p['value']))
  return (SkuNotFoundError(sku, name, skuName), 0)

def get_content_id(sku: str, name: str, skuName: str, useSku: bool, session) -> (Exception, int):
  if useSku == True:
    searchCriteria = sku
  else:
    searchCriteria = name
  searchPath = f"https://www.tymbrel.com/cmsi-data/searchapp?simplecartproductsearch={searchCriteria}"
  response = session.get(searchPath)

  # If we see a login/password field here, it failed to log in

  products = json.loads(response.text)
  return extract_product_id_from_products(products, name, sku, skuName)

def find_inventory_item(content, sku, skuName: str):
  parser = BeautifulSoup(content, 'html5lib')
  anchors = parser.find_all('a')
  for a in anchors:
    if skuName == a.text:
      return a.attrs['href']
  return InventoryNotFoundError(sku, skuName)
