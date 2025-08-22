import requests
import csv
import time
from bs4 import BeautifulSoup as bs
from datetime import datetime

def get_soup(url, session = None, parser='lxml'):
    try:
        html = session.get(url) if session else requests.get(url)
        html.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("HTTP error occurred:", e)
    except requests.exceptions.RequestException as e:
        print("A request error occurred:", e)
    except Exception as e:
        print('Что-то пошло не так (...', e)
    
    html.encoding = 'utf-8'
    return bs(html.text, parser)

def get_price(tag, c_name, p_name):
    price = tag.select_one('span.products__item-price').text.strip(' ₽\n\t')
    if price.isdigit():
        return int(price)
    try:
        price_lst = price.split(' ₽')
        price = int(price_lst[-1])
        return price
    except Exception as e:
        print(f'Категория: {c_name}, товар: {p_name}. Некорректное значение стоимости - {price}')
        return price

def get_name(name):
    repls = {'гр.р': 'гр.', 'шт.р': 'шт.'}
    for old, new in repls.items():
        name = name.replace(old, new)
    return name

def get_data(url, session = None):
    soup = get_soup(url, session)
    prod_data = []
    category_cont = soup.select_one('div.category__grid')
    category_name = soup.select_one('h1.catalog__heading,h1.page__heading').text
    if category_cont:
        cat_links = [a['href'] for a in category_cont.select('a.category__item')]
        for link in cat_links:
            prod_data = prod_data + get_data(link, session)
        return prod_data
    else:
        page, next_pagin = 1, True
        while next_pagin:
            product_cont = soup.select_one('div.products__grid')
            products = [] if not product_cont else [product_tag for product_tag in product_cont.select('div.products__item-desc')]
            for product in products:
                p_name = get_name(product.select_one('a.products__item-title').text)
                p_price = get_price(product, category_name, p_name)
                prod_data.append({'name': p_name, 'price': p_price})
            pagination = soup.select_one('ul.pagination')
            if not pagination or pagination.select('li')[-1].select_one('span'):
                next_pagin = False
                continue
            page += 1
            next_link = url + f'&page={page}'
            soup = get_soup(next_link, session)
        return [{category_name: prod_data}]

if __name__ == '__main__':
    start = time.time()
    scheme = 'https://alsemya.ru/all-categories'
    with requests.Session() as rs:

        products = get_data(scheme, rs)

    csv_header = ['Категория', 'Наименование товара', 'Стоимость, руб']
    curr_dt = datetime.now()
    curr_dt_str = curr_dt.strftime('%Y-%m-%d_%H%M%S')
    with open(f'SA_MSK_product_list_{curr_dt_str}.csv', 'a', encoding='utf-8-sig', newline='') as ouf:
        writer = csv.writer(ouf, delimiter=';')
        writer.writerow(csv_header)
        for category in products:
            cat_name, prods = [a for a in category.items()][0]
            for prod in prods:
                writer.writerow([cat_name, prod['name'], prod['price']])

    stop = time.time()
    t = stop - start
    print(f'Время выполнения = {t}')