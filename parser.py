import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json


headers = {
    "Accept": 'text/html',
    "User-Agent": 'Mozila/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebkit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'
}


url = 'https://online.metro-cc.ru/category/sladosti-chipsy-sneki/konfety-podarochnye-nabory'


filename_text = 'requirements.txt'
main_dict = {}
main_dict['products'] = []


def find_info(obj_soup):
    obj_soup = obj_soup.select_one('#products-inner.subcategory-or-type__products')

    def conver_prise(prise):
        titog = ''
        for i in prise:
            if i == '.':
                titog += i
            try:
                titog += str(int(i))
            except:
                pass
        return float(titog)

    def extract_info_product(product_info):
        product_info = product_info.split('\n')

        id = None
        href = None
        title = None
        prise_1 = None
        prise_2 = None
        category = None

        for i in product_info[0].split(' '):
            if 'id=' in i:
                id = i.split('id="')[1].split('"><div')[0]

        for i in  str(obj_soup.find(attrs={"id": id}).select_one('.catalog-2-level-product-card__middle').find('a')).split(' '):  # => Название товара
            if 'href=' in i:
                href = urljoin("https://online.metro-cc.ru", i.split('href=')[1][1:])

        title = obj_soup.find(attrs={"id":id}).select_one('.catalog-2-level-product-card__middle').find('span').text #=> Название товара
        title = title.split('\n')[1].split('    ')[1]

        try:
            category = [c for c in category_list if c.upper() in title.upper()][0]
        except Exception as e:
            category = 'None category'

        prise_1 = obj_soup.find(attrs={"id":id}).select_one('.product-unit-prices__actual-wrapper').find('span').text #=> Актуальная цена
        prise_1 = conver_prise(prise_1.split(' ')[0])

        prise_2 = obj_soup.find(attrs={"id": id}).select_one('.product-unit-prices__old-wrapper').find('span').text  # => Промо цена
        prise_2 = conver_prise(prise_2.split(' ')[0]) if prise_2.split(' ')[0] else prise_1


        if all((id, title, href, prise_1, prise_2)):
                main_dict['products'].append({'id': id, 'title': title, 'href': href, 'category': category, 'prise_1': prise_1, 'prise_2': prise_2})

    for i in str(obj_soup).split('\n\n')[:-1]:
        try:
            extract_info_product(i)
        except Exception as e:
            pass

def get_full_info():

    my_req = requests.get(url)

    obj_soup = BeautifulSoup(my_req.text, 'lxml')

    def create_category(lis):
        itog_lis = []
        for i1 in lis:
            word = ''
            for i2 in i1:
                if i2 != ' ' or word != '':
                    word += i2
            if word != '':
                itog_lis.append(word)
        return itog_lis

    global category_list
    category_list = create_category(obj_soup.select_one('.v-scrollbox__content').text.split('\n'))

    tuple_paginator = (2, int(obj_soup.select_one('.catalog-paginate.v-pagination').find_all('li')[-2].text)+1)

    find_info(obj_soup)

    for page in range(*tuple_paginator):

        with requests.Session() as session:
            my_req = session.get(url, params={'page':page})

        obj_soup = BeautifulSoup(my_req.text, 'lxml')
        find_info(obj_soup)

    with open(filename_text, 'w') as File:
        json.dump(main_dict, File, ensure_ascii=False)

print('===============================================================================')

get_full_info()
print(main_dict)


