import requests
import json
import csv
import time
from bs4 import BeautifulSoup as bs

def get_soup(url, parser='lxml'):
    try:
        html = requests.get(url)
        html.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("HTTP error occurred:", e)
    except requests.exceptions.RequestException as e:
        print("A request error occurred:", e)
    except Exception as e:
        print('Что-то пошло не так (...', e)
    
    html.encoding = 'utf-8'
    return bs(html.text, parser)

def get_data(url):
    soup = get_soup(url)
    prod_data = []
    category_cont = soup.select_one('div.category__grid')
    category_name = soup.select_one('h1.catalog__heading,h1.page__heading').text
    if category_cont:
        cat_links = [a['href'] for a in category_cont.select('a.category__item')]
        for link in cat_links:
            prod_data = prod_data + get_data(link)
        return prod_data
    else:
        pagination = soup.select_one('ul.pagination')
        max_page = 1 if not pagination else len(pagination.select('li')) - 2
        page = 1
        while page <= max_page:
            product_cont = soup.select_one('div.products__grid')
            products = [] if not product_cont else [product_tag for product_tag in product_cont.select('div.products__item-desc')]
            for product in products:
                p_name = product.select_one('a.products__item-title').text
                p_price = product.select_one('span.products__item-price').text.strip(' ₽\n\t')
                try:
                    p_price = int(p_price)
                except Exception as e:
                    print(f'Категория: {category_name}, товар: {p_name}. Некорректное значение стоимости - {p_price}')
                prod_data.append({'name': p_name, 'price': p_price})
            page += 1
            if page <= max_page:
                next_link = url + f'?page={page}'
                soup = get_soup(next_link)
        return [{category_name: prod_data}]


start = time.time()
scheme = 'https://alsemya.ru/all-categories'

products = get_data(scheme)

csv_header = ['Категория', 'Наименование товара', 'Стоимость, руб']
with open('SA_MSK_product_list.csv', 'w', encoding='utf-8-sig', newline='') as ouf:
    writer = csv.writer(ouf, delimiter=';')
    writer.writerow(csv_header)

with open('product_list.json', 'w', encoding='utf-8') as ouf:
    json.dump(products, ouf, indent=4, ensure_ascii=False)

with open('SA_MSK_product_list.csv', 'a', encoding='utf-8-sig', newline='') as ouf:
    writer = csv.writer(ouf, delimiter=';')
    for category in products:
        cat_name, prods = [a for a in category.items()][0]
        for prod in prods:
            writer.writerow([cat_name, prod['name'], prod['price']])

stop = time.time()
t = stop - start
print(f'Время выполнения = {t}')
