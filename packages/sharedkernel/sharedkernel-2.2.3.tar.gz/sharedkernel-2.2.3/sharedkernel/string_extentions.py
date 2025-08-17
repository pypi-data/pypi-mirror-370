import re

def camel_to_snake(value:str):
   return re.sub('(?!^)([A-Z]+)', r'_\1',value).lower()
