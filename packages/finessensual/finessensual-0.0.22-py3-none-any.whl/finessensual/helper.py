import re

def parse_day( ofpdate: str ) -> str:
    match = re.search( r"^(\d{2})[-/](\d{2})[-/](\d{4})$", ofpdate )
    return match.group(3) + '-' + match.group(2) + '-' + match.group(1)
    
def parse_month( ofpdate: str ) -> str:
    match = re.search( r"^(\d{2})[-/](\d{2})[-/](\d{4})$", ofpdate )
    return match.group(3) + '-' + match.group(2)

def parse_noyear( ofpdate: str ) -> str:
    match = re.search( r"^(\d{2})[-/](\d{2})[-/](\d{4})$", ofpdate )
    return match.group(2) + '-' + match.group(1)
    
