import re, os
from bs4 import BeautifulSoup

def search_error_check(handle):
    error_message = "could not extract ResultSet"
    if error_message in handle:
        return 0
    return 1

def strip_non_numeric(input_string):
    return re.sub(r'\D', '', input_string)  # \D matches any non-digit character

def get_year(string_ls):
    for i, string in enumerate(string_ls):
        y = strip_non_numeric(string)
        if y:
            y_int = int(y)
            if 3000>y_int>2000:
                while(3000>y_int>2100):
                    y_int -= 100
            elif y_int>2500:
                while(y_int>2500):
                    y_int //= 10
            y = str(y_int)
            if y_int<21:
                y+='--'
            elif y_int<210:
                y+='-'
            if not y.startswith(('1', '2')): 
                y = '0' + y
            string_ls[i] = y

def parse(txt, sort_order=False):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # Change to the directory of the script
    # print("Current working directory:", os.getcwd())

    if (sort_order == "Descending"):
        sort_order = True
    else:
        sort_order = False

    tituloCompleto = r'\.tituloCompleto=(?:null|"(.*)";)'
    data = r'\.dataBibliografico=(?:null|"(.{0,15})";)'
    idd = r's[\d]+\.id=(\d+);'

    end_of_times = []
    
    handle = txt

    if not search_error_check(handle):
        print("Search Failed! Likely due to a search too large.")
        return [("Search Failed!", 0)]

    handle = handle.replace(" \\/", ".")
    handle = handle.replace("\\/", ".")
    handle = bytes(handle, 'utf-8').decode('unicode_escape')

    match_id = re.findall(idd, handle)
    match_data = re.findall(data, handle)
    get_year(match_data)
    matches = re.findall(tituloCompleto,handle)

    for y, x in enumerate(matches):
        try:
            end_of_times.append([x, match_data[y], match_id[y*2]])
        except:
            end_of_times.append([x, "No_Data_Avaliable!", match_id[y]])
    if len(matches) != len(match_data):
        print(f"match len = {len(matches)}\nmatch_data len = {len(match_data)}\nmatch id len = {len(match_id)}")
    end_of_times.sort(key=lambda x: x[1], reverse=sort_order)

    return end_of_times

def parse_Registro_html(txt):

    soup = BeautifulSoup(txt, 'html.parser')

    # Find all table rows that have the data you care about
    rows = soup.find_all('tr')

    where_great_men_fail = []

    for row in rows:
        tds = row.find_all('td')
        if len(tds) == 7:  # Ensure it's the structure you expect
            data = [td.get_text(strip=True) for td in tds[1:]]
            where_great_men_fail.append(data)

    # Step 1: Find the span with the text "Autor"
    autor_label = soup.find('span', string='Autor')

    acesso_eletronico_label = soup.find('span', string='Acesso eletrônico')

    if autor_label:
        # Step 2: Find the next <div class="width-100"> after that
        author_div = autor_label.find_next('div', class_='width-100')
        if author_div:
            author_name = author_div.get_text(strip=True)
            # print("Author:", author_name)
    
    href_a = ""

    if acesso_eletronico_label:
        elec_div = acesso_eletronico_label.find_next('a')
        href_a = elec_div.get('href')
    
    return where_great_men_fail, author_name, href_a

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # Change to the directory of the script
    with open('html_ufsm.txt', 'r', encoding='utf-8') as file:
        handle = file.read()
        x = parse(handle)
        for w, y in enumerate(x):
            print(y, w)
        # x = parse_Registro_html(handle)