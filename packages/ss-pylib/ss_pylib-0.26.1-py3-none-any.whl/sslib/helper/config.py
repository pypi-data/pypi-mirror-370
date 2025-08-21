import re
from configparser import ConfigParser


class Config:
  def __init__(self, path:str):
    self.config_parser = ConfigParser()
    self.config_parser.read(path)
    
  def get(self, key:str) -> str:
    group = re.match(r'\w+(?=\.)', key)
    group = '' if group is None else group.group()
    key = re.sub(r'\w+(?=\.).', '', key)
    return self.config_parser[group][key]
  
  def get_group(self, group:str) -> dict:
    return dict(self.config_parser.items(group))