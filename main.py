import re
from bs4 import BeautifulSoup
import requests

url = None
page = requests.get(url)
soup = BeautifulSoup(page.text, "lxml")

