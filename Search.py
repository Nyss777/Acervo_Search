import requests, sys, os

# Common headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "text/plain",
    "Origin": "https://portal.ufsm.br",
    "Connection": "keep-alive",
    "Referer": "https://portal.ufsm.br/biblioteca/pesquisa/index.html",}

def search(search_word, number_results, sort_order=2, Headers=HEADERS):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # Change to the directory of the script

    if (sort_order == "Decrescente"):
        sort_order = "desc"
    else:
        sort_order = "asc"

    # Base URL for the DWR service
    BASE_URL = "https://portal.ufsm.br/biblioteca/dwr/call/plaincall"


    # Session object to maintain cookies
    session = requests.Session()

    # Sample session data (replace with actual session ID if necessary)
    session.cookies.set("JSESSIONID", "bf578cdcd8b9559e6bfd7fa25dd3")
    session.cookies.set("BACKENDUSED", "wportal05-s3")

    def post_validate():
        """Send a validate request."""
        url = f"{BASE_URL}/registroBibliograficoAjax.validate.dwr"
        payload = f"""
callCount=1
page=/biblioteca/pesquisa/index.html
httpSessionId=bf578cdcd8b9559e6bfd7fa25dd3
scriptSessionId=FB8B94048CBF4678600C9DF04240BA86457
c0-scriptName=registroBibliograficoAjax
c0-methodName=validate
c0-id=0
c0-e1=string:{search_word}
c0-e2=null:null
c0-e3=null:null
c0-param0=Object_Object:{{geral:reference:c0-e1, orderBy:reference:c0-e2, orderMode:reference:c0-e3}}
batchId=0
"""
        response = session.post(url, headers=Headers, data=payload.strip())

    def post_count():
        """Send a count request."""
        url = f"{BASE_URL}/registroBibliograficoAjax.count.dwr"
        payload = f"""
callCount=1
page=/biblioteca/pesquisa/index.html
httpSessionId=bf578cdcd8b9559e6bfd7fa25dd3
scriptSessionId=FB8B94048CBF4678600C9DF04240BA86457
c0-scriptName=registroBibliograficoAjax
c0-methodName=count
c0-id=0
c0-e1=string:{search_word}
c0-e2=null:null
c0-e3=null:null
c0-param0=Object_Object:{{geral:reference:c0-e1, orderBy:reference:c0-e2, orderMode:reference:c0-e3}}
batchId=1
"""
        response = session.post(url, headers=Headers, data=payload.strip())

    def post_search():
        """Send a search request."""
        url = f"{BASE_URL}/registroBibliograficoAjax.search.dwr"
        payload = f"""
callCount=1
page=/biblioteca/pesquisa/index.html
httpSessionId=bf578cdcd8b9559e6bfd7fa25dd3
scriptSessionId=FB8B94048CBF4678600C9DF04240BA86457
c0-scriptName=registroBibliograficoAjax
c0-methodName=search
c0-id=0
c0-param0=number:0
c0-param1=number:{number_results}
c0-e1=string:{search_word}
c0-e2=string:dataBibliografico
c0-e3=string:{sort_order}
c0-e4=number:1
c0-e5=number:33
c0-e6=number:660
c0-e7=number:20
c0-e8=number:20
c0-e9=number:39
c0-param2=Object_Object:{{geral:reference:c0-e1, orderBy:reference:c0-e2, orderMode:reference:c0-e3, currentPage:reference:c0-e4, totalPages:reference:c0-e5, totalItems:reference:c0-e6, firstResult:reference:c0-e7, maxResults:reference:c0-e8, lastResult:reference:c0-e9}}
batchId=2
"""
        response = session.post(url, headers=Headers, data=payload.strip())
        return response.text

    post_validate()
    post_count()
    return post_search()

def registroSearch(id, HEADERS=HEADERS):
    url = f"https://portal.ufsm.br/biblioteca/pesquisa/registro.html?idRegistro={id}"
    response = requests.get(url, headers=HEADERS)
    response.encoding = 'ISO-8859-1'
    return response.text

if __name__ == '__main__':
    # from Parser import *
    # import time
    search_word = "assis"
    number_results = 100
    txt = search(search_word, number_results)
    with open('html_ufsm.txt', 'w+') as handle:
        handle.write(txt)
    print("Done!")
    # print("Start!")
    # s = time.time()
    # parse(txt)
    # e = time.time()
    # print(e-s, 'segundos')
    # registroSearch(1172)
