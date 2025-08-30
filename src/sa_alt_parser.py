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
    price = tag.select_one('div.product-item-price-current').text.strip(' ₽\n\t\r').replace('\xa0','')
    if not price:
        return ' -'
    try:
        price = float(price)
        return price
    except Exception as e:
        print(f'Категория: {c_name}, товар: {p_name}. Некорректное значение стоимости - {price}')
        return price

def get_name(name):
    repls = {'гр.р': 'гр.', 'шт.р': 'шт.'}
    for old, new in repls.items():
        name = name.replace(old, new)
    return name

def get_data(url, session=None):
    scheme = 'https://altsemena.org'
    soup = get_soup(url, session)
    prod_data = []
    category_cont = soup.select_one('div.bx_catalog_tile')
    category_name = soup.select_one('h1.bx_catalog_tile_category_title').text if soup.select_one('h1.bx_catalog_tile_category_title') else ''
    items_cont = soup.select_one('div.wrapper_product_items')
    if not items_cont:
        if not category_cont:
            url_tags = soup.select('a.catalog-section-list-item-link')
        else:
            url_tags = soup.select('h2.bx_catalog_tile_title a')
        cat_links = [scheme + a['href'] for a in url_tags]
        for link in cat_links:
            prod_data = prod_data + get_data(link, session)
        return prod_data
    else:
        pagination = soup.select_one('div.bx-pagination')
        max_page = 1 if not pagination else int(pagination.select('li')[-2].select_one('span').text)
        page = 1
        while page <= max_page:
            products = items_cont.select('div.product-item') if items_cont.select('div.product-item') else []
            for product in products:
                p_name = get_name(product.select_one('div.product-item-title a').text.strip())
                p_price = get_price(product, category_name, p_name)
                prod_data.append({'name': p_name, 'price': p_price})
            page += 1
            if page <= max_page:
                next_link = url + f'?PAGEN_1={page}'
                soup = get_soup(next_link, session)
                items_cont = soup.select_one('div.wrapper_product_items')
        return [{category_name: prod_data}]

if __name__ == '__main__':
    start = time.time()
    url = 'https://altsemena.org/catalog/'
    with requests.Session() as rs:   
        products = get_data(url, rs)

    csv_header = ['Категория', 'Наименование товара', 'Стоимость, руб']
    curr_dt = datetime.now()
    curr_dt_str = curr_dt.strftime('%Y-%m-%d_%H%M%S')
    with open(f'SA_ALT_product_list_{curr_dt_str}.csv', 'a', encoding='utf-8-sig', newline='') as ouf:
        writer = csv.writer(ouf, delimiter=';')
        writer.writerow(csv_header)
        for category in products:
            cat_name, prods = [a for a in category.items()][0]
            for prod in prods:
                writer.writerow([cat_name, prod['name'], prod['price']])

    stop = time.time()
    t = stop - start
    print(f'Время выполнения = {t}')