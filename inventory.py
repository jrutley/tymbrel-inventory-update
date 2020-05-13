from requests import Session
from bs4 import BeautifulSoup
from dto import InventoryDetail
from dataclasses import asdict

class FailedToLoadDetailPage(Exception):
  def __init__(self, url):
    self.url = url

class FailedToUpdateForm(Exception):
  def __init__(self, url):
    self.url = url

def get_all_form_elements(html) -> InventoryDetail:
  parser = BeautifulSoup(html, 'html5lib')
  form_elements = parser.find_all('input')
  d = {}
  for a in form_elements:
    if 'value' in a.attrs:
      d[a.attrs['name']] = a.attrs['value']
  readonly_price = float(d["basePrice"])+float(d["Price"])
  detail = InventoryDetail(
    basePrice = d["basePrice"],
    Name = d["Name"],
    Active = d["Active"],
    SetDefault = d["SetDefault"],
    Available = d["Available"],
    SKU = d["SKU"],
    Price = d["Price"],
    ReadonlyPrice = readonly_price,
    btnSubmit = d["btnSubmit"]
  )
  return detail

def submit_inventory_detail_form(session: Session, detail_url: str, elements: InventoryDetail):
  d = asdict(elements)
  result = session.post(detail_url, d)
  if result.ok:
    return None
  return FailedToUpdateForm(detail_url)

def update_inventory_on_detail_page(session: Session, detail_url, new_inventory_count):
  response = session.get(detail_url)
  if not response.ok:
    return FailedToLoadDetailPage(detail_url)
  elements = get_all_form_elements(response.text)
  if elements is Exception:
    return elements
  elements.Available = str(new_inventory_count)
  return submit_inventory_detail_form(session, detail_url, elements)
