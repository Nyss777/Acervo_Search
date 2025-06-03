import re, os

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

    end_of_times = []
    
    handle = txt

    if not search_error_check(handle):
        print("Search Failed! Likely due to a search too large.")
        return [("Search Failed!", 0)]

    handle = handle.replace(" \\/", ".")
    handle = handle.replace("\\/", ".")
    handle = bytes(handle, 'utf-8').decode('unicode_escape')

    match_data = re.findall(data, handle)
    get_year(match_data)
    matches = re.findall(tituloCompleto,handle)

    for y, x in enumerate(matches):
        try:
            end_of_times.append([x, match_data[y]])
        except:
            end_of_times.append([x, "No_Data_Avaliable!"])
    if len(matches) != len(match_data):
        print(f"match len = {len(matches)}\nmatch_data len = {len(match_data)}")
    end_of_times.sort(key=lambda x: x[1], reverse=sort_order)

    return end_of_times

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # Change to the directory of the script
    with open('output.txt', 'r') as file:
        handle = file.read()
        x = parse(handle)
        for w, y in enumerate(x):
            print(y, w)