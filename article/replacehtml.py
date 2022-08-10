import re

def replace_html(value):
    value = re.sub('<[^>]*>', '', value)
    return value