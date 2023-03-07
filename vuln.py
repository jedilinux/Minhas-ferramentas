import os
import re
from urllib.parse import urlparse

def detect_xss(payload):
    # Verifica se o payload contém caracteres de script malicioso
    if re.search(r'<script>', payload):
        return True
    elif re.search(r'onload=', payload):
        return True
    elif re.search(r'<iframe>', payload):
        return True
    else:
        return False

def detect_vulnerabilities(url):
    # Verifica se a URL contém um possível Open Redirect
    parsed_url = urlparse(url)
    if parsed_url.netloc != "www.exemplo.com" and parsed_url.scheme != "https":
        return "Open Redirect detectado!"
    
    # Verifica se a URL contém um possível File Inclusion/Path Traversal
    path = parsed_url.path
    if path.startswith("/../") or path.endswith("/.."):
        return "File Inclusion/Path Traversal detectado!"

    # Verifica se a URL contém um possível XSS
    query = parsed_url.query
    if detect_xss(query):
        return "Vulnerabilidade de XSS detectada!"

    # Nenhuma vulnerabilidade encontrada
    return "Nenhuma vulnerabilidade encontrada."

# Exemplo de uso
url1 = "https://www.exemplo.com/path/to/page.html"
url2 = "https://www.exemplo.com/path/to/page.html?param1=<script>alert('XSS!');</script>&param2=value2"
url3 = "https://www.exemplo.com/path/../../../../etc/passwd"

print(detect_vulnerabilities(url1))
print(detect_vulnerabilities(url2))
print(detect_vulnerabilities(url3))