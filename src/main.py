import requests
import sa_alt_parser
import sa_msk_parser
import csv
import time
from datetime import datetime

def save_result(data, site):
    csv_header = ['Категория', 'Наименование товара', 'Стоимость, руб']
    curr_dt = datetime.now()
    curr_dt_str = curr_dt.strftime('%Y-%m-%d_%H%M%S')
    with open(f'collected_data_csv\\{site}_product_list_{curr_dt_str}.csv', 'a', encoding='utf-8-sig', newline='') as ouf:
        writer = csv.writer(ouf, delimiter=';')
        writer.writerow(csv_header)
        for category in data:
            cat_name, prods = [a for a in category.items()][0]
            for prod in prods:
                writer.writerow([cat_name, prod['name'], prod['price']])
    print(f'Результат сохранен в файл {site}_product_list_{curr_dt_str}.csv')

def parsing(site, url):
    print(f'Выполняется парсинг данных с сайта {site}...')
    t_start = time.time()
    with requests.Session() as rs:
        data = sa_msk_parser.get_data(url, rs) if site == 'SA_MSK' else sa_alt_parser.get_data(url,rs)
    t_stop = time.time()
    tm = t_stop - t_start
    print(f'Готово! Время выполнения {tm} секунд.')
    print('Сохранение результатов в файл csv...')
    save_result(data, site)

url_msk = 'https://alsemya.ru/all-categories'
url_alt = 'https://altsemena.org/catalog/'
app_on = True
while app_on:
    print('Выберите действие в меню нажав 1 - 3 или 0 для выхода, нажмите enter:')
    print('1. Получить данные с обоих сайтов SEMALT ALT и SEMALT MSK.')
    print('2. Получить данные с сайта SEMALT MSK.')
    print('3. Получить данные с сайта SEMALT ALT.')
    print('0. Выход.')
    menu = input()
    match menu:
        case '1':
            parsing('SA_MSK', url_msk)
            parsing('SA_ALT', url_alt)
        case '2':
            parsing('SA_MSK', url_msk)
        case '3':
            parsing('SA_ALT', url_alt)
        case '0':
            print('Завершаем работу приложения.')
            app_on = False
        case _:
            print('Некорректный ввод, попробуйте еще раз')