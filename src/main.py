import sa_alt_parser
import sa_msk_parser

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
            print('Выполняем парсинг данных с сайтов SEMALT ALT и SEMALT MSK...')
            print('Готово!')
        case '2':
            print('Выполняем парсинг данных с сайта SEMALT MSK...')
            print('Готово!')
        case '3':
            print('Выполняем парсинг данных с сайта SEMALT ALT...')
            print('Готово!')
        case '0':
            print('Завершаем работу приложения. Досвиданья.')
            app_on = False
            continue
        case _:
            print('Некорректный ввод, попробуйте еще раз')