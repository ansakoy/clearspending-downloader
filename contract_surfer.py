# -*- coding: utf-8 -*-
'''
Скрипт выгружает контрактные данные через API Госзатрат (http://clearspending.ru/) в виде таблицы в формате CSV.
Возможны два варианта выгрузки:
1. по продуктам (одна строка - один продукт контракта), метод .get_products()
2. по контрактам (одна строка - один контракт, без детализации по продуктам), метод .get_contracts()
Также можно получить информацию о том, сколько контрактов доступно по запросу.
Возможно формирование выборок со следующими параметрами:
- ФЗ (федеральный закон, по которому заключен контракт) (по умолчанию отсутствует)
- ИНН заказчика (по умолчанию отсутствует)
- КПП заказчика (по умолчанию отсутствует)
- Начало периода (по умолчанию - начало текущего года)
- Конец периода (по умолчанию - настоящий момент
- Диапазон цен (по умолчанию отсутствует)
- Код региона заказчика (по умолчанию отсутствует)
Можно указать название файла, в который будут выгружены данные.
По умолчанию название файла 'no_name'
'''

from __future__ import unicode_literals
import json
import csv
import argparse
import urllib
import datetime

# Поля выгружаемых таблиц
CLEARSPENDING_URL = 'clearspending_url' # ссылка на карточку контракта на clearspending.ru
SIGN_DATE = 'sign_date' # дата подписания контракта
PRODUCT_DESCR = 'product_description' # описание закупленного продукта
FST_PROD_DESCR = '1st_product_description' # описание первого продукта (при выгрузке по контрактам)
NUM_PRODUCTS = 'num_products' # число продуктов в контракте (при выгрузке по контрактам)
OKPD2 = 'okpd2' # код ОКПД2 (если имеется)
OKPD2_NAME = 'okpd2_name' # расшифровка кода ОКПД2 (если имеется)
OKPD = 'okpd' # код ОКПД (если имеется)
OKPD_NAME = 'okpd_name' # расшифровка кода ОКПД (если имеется)
OKDP = 'okdp' # код ОКДП (если имеется), актуально до 2014 г.
OKDP_NAME = 'okdp_name' # расшифровка кода (если имеется), актуально до 2014 г.
SINGLE_PRICE = 'single_price' # цена за единицу продукта
OKEI = 'okei' # единица измерения
PRODUCT_SUM = 'product_sum' # сумма по продукту
QUANTITY = 'quantity' # количество закупленных единиц
CONTRACT_PRICE = 'contract_price' # сумма всего контракта
CURRENCY = 'currency' # валюта
REGION_NAME = 'region_name' # наименование региона
REGNUM = 'regnum' # реестровый номер контракта
CUSTOMER_NAME = 'customer_name' # наименование заказчика
CUSTOMER_INN = 'customer_inn' # ИНН заказчика
CUSTOMER_KPP = 'customer_kpp' # КПП заказчика
FST_SUPP_NAME = '1st_supp_name' # наименование первого поставщика
FST_SUPP_INN = '1st_supp_inn' # ИНН первого поставщика
FST_SUPP_KPP = '1st_supp_kpp' # КПП первого поставщика
NUM_SUPPS = 'num_suppliers' # всего поставщиков
CONTRACT_STAGE = 'contract_stage' # стадия исполнения контракта (актуально только для 44-ФЗ)
FZ = 'fz' # федеральный закон - 44-ФЗ, 223-ФЗ, до 2014 г. 94-ФЗ





class ContractSurfer(Extractor):

    def __init__(self, filename=None, span=30):
        Extractor.__init__(filename)
        self.target_url = ''
        self.span = span

    def get_default_daterange(self, begin, end):
        default_year = datetime.datetime.now().year
        if not begin:
            begin = '01.01.{}'.format(default_year)
        if not end:
            end = '31.12.{}'.format(default_year)
        return begin, end

    def get_scenario(self,
                     start_date=None,
                     stop_date=None,
                     prodkeys=None,
                     prodcode=None,
                     **kwargs):
        # Выбрать тип запроса и дальнейший сценарий выгрузки
        daterange = self.get_default_daterange(begin=start_date, end=stop_date)
        begin = daterange[0]
        end = daterange[1]
        print '\nПАРАМЕТРЫ ЗАПРОСА:'
        print 'Период: {}-{}'.format(begin, end)
        if prodkeys or prodcode:
            date_range_chunks = self.get_dateranges_for_search(begin, end)
            self.target_url = 'http://openapi.clearspending.ru/restapi/v3/contracts/search/?daterange={}-{}'
        else:
            date_range_chunks = [(begin, end)]
            self.target_url = 'http://openapi.clearspending.ru/restapi/v3/contracts/select/?daterange={}-{}'
        return date_range_chunks

    def construct_api(self,
                      cust_inn=None,
                      cust_kpp=None,
                      region=None,
                      fz=None,
                      pricerange=None,
                      supp_inn=None,
                      supp_kpp=None,
                      prodcode=None,
                      prodkeys=None):
        # Конструктор API-запроса
        if cust_inn:
            self.target_url += '&customerinn={}'.format(cust_inn)
            print 'ИНН заказчика: {}'.format(cust_inn)
        if cust_kpp:
            self.target_url += '&customerkpp={}'.format(cust_kpp)
            print 'КПП заказчика: {}'.format(cust_kpp)
        if region:
            self.target_url += '&customerregion={}'.format(region)
            print 'Код региона заказчика: {}'.format(region)
        if fz:
            self.target_url += '&fz={}'.format(fz)
            print 'ФЗ: {}'.format(fz)
        if pricerange:
            self.target_url += '&pricerange={}'.format(pricerange)
            print 'Диапазон цен: {}'.format(pricerange)
        if supp_inn:
            self.target_url += '&supplierinn={}'.format(supp_inn)
            print 'ИНН поставщика: {}'.format(supp_inn)
        if supp_kpp:
            self.target_url += '&supplierkpp={}'.format(supp_kpp)
            print 'КПП поставщика: {}'.format(supp_kpp)
        if prodkeys:
            self.target_url += '&productsearchlist={}'.format(prodkeys)
            print 'Ключевые слова: {}'.format(prodkeys)
        if prodcode:
            self.target_url += '&okdp_okpd={}'.format(prodcode)
            print 'Код товара/работы/услуги: {}'.format(prodcode)
        print '\nURL ЗАПРОСА:', self.target_url  # print 'Request URL:', target_url
        return self.target_url

    def get_dateranges_for_search(self, begin, end):
        # Разбить период на отрезки времени, длина которых равна значению span
        span = self.span
        begin = datetime.datetime.strptime(begin, '%d.%m.%Y')
        end = datetime.datetime.strptime(end, '%d.%m.%Y')
        diff = end - begin
        ranges = list()
        if diff > datetime.timedelta(span):
            start = begin
            finish = begin + datetime.timedelta(span-1)
            while start <= end:
                ranges.append((start.strftime('%d.%m.%Y'), finish.strftime('%d.%m.%Y')))
                start += datetime.timedelta(span)
                finish += datetime.timedelta(span)
        else:
            ranges.append((begin.strftime('%d.%m.%Y'), end.strftime('%d.%m.%Y')))
        return ranges

    def get_num_pages(self, url):
        # Установить число страниц, выпадающих по запросу
        response = urllib.urlopen(url)
        try:
            data = json.loads(response.read())
            num_contracts = data['contracts']['total']
            print '\nЧисло подходящих контрактов:', num_contracts
            num_pages = num_contracts / 50 + (num_contracts % 50 != 0)
            return num_pages
        except ValueError:
            print 'Данные, отвечающие параметрам, не найдены'

    def get_current_page(self, url, page):
        # Сформирова URL текущей страницы, отправить запрос, найти в полученном ответе контракты
        target = url + '&page={}'.format(page)
        response = urllib.urlopen(target)
        contracts = json.loads(response.read())['contracts']['data']
        return contracts

    def get_contract_info(self, contract):
        # Собрать данные по контракту
        stages = {'E': 'Исполнение',
                  'EC': 'Исполнение завершено',
                  'ET': 'Исполнение прекращено'}
        regnum = contract.get('regNum', '-')
        base_url = 'https://clearspending.ru/contract/{}'
        contract_info = {CLEARSPENDING_URL: base_url.format(regnum),
                         REGNUM: regnum,
                         SIGN_DATE: contract.get('signDate', '-'),
                         FZ: contract.get('fz', '-'),
                         CUSTOMER_NAME: contract.get('customer', {}).get('fullName', '-'),
                         CUSTOMER_INN: contract.get('customer', {}).get('inn', '-'),
                         CUSTOMER_KPP: contract.get('customer', {}).get('kpp', '-'),
                         NUM_SUPPS: len(contract.get('suppliers', [])),
                         FST_SUPP_NAME: contract.get('suppliers', [{}])[0].get('organizationName', '-'),
                         FST_SUPP_INN: contract.get('suppliers', [{}])[0].get('inn', '-'),
                         FST_SUPP_KPP: contract.get('suppliers', [{}])[0].get('kpp', '-'),
                         CONTRACT_PRICE: contract.get('price', '-'),
                         CURRENCY: contract.get('currency', {}).get('name', '-'),
                         REGION_NAME: self.regions.get(contract.get('regionCode', '-')),
                         CONTRACT_STAGE: stages.get(contract.get('currentContractStage', '-'))}
        return contract_info

    def add_fst_prod_info(self, contract, contr_info):
        # Собрать данные о первом продукте в списке и об общем числе продуктов в контракте
        contr_info[NUM_PRODUCTS] = len(contract.get('products', []))
        contr_info[FST_PROD_DESCR] = contract.get('products', [{}])[0].get('name', '-')
        return contr_info

    def add_products_info(self, product, contr_info):
        # Собрать данные по продукту
        contr_info[PRODUCT_DESCR] = product.get('name', '-')
        contr_info[OKPD2] = product.get('OKPD2', {}).get('code', '-')
        contr_info[OKPD2_NAME] = product.get('OKPD2', {}).get('name', '-')
        contr_info[OKPD] = product.get('OKPD', {}).get('code', '-')
        contr_info[OKPD_NAME] = product.get('OKPD', {}).get('name', '-')
        contr_info[OKDP] = product.get('OKDP', {}).get('code', '-')
        contr_info[OKDP_NAME] = product.get('OKDP', {}).get('name', '-')
        contr_info[SINGLE_PRICE] = product.get('price', '-')
        contr_info[OKEI] = product.get('OKEI', {}).get('name', '-')
        contr_info[QUANTITY] = product.get('quantity', '-')
        contr_info[PRODUCT_SUM] = product.get('sum', '-')
        return contr_info

    def get_products(self, **kwargs):
        # Выгрузить данные по продуктам
        dateranges = self.get_scenario(**kwargs)
        static_url = self.construct_api(**kwargs)
        for daterange in dateranges:
            begin = daterange[0]
            end = daterange[1]
            target_url = static_url.format(begin, end)
            num_pages = self.get_num_pages(target_url)
            if num_pages:
                headers_list = [CLEARSPENDING_URL, REGNUM, SIGN_DATE,
                                PRODUCT_DESCR, OKPD2, OKPD2_NAME, OKPD, OKPD_NAME, OKDP, OKDP_NAME,
                                SINGLE_PRICE, OKEI, PRODUCT_SUM, QUANTITY,
                                CUSTOMER_NAME, CUSTOMER_INN, CUSTOMER_KPP,
                                FST_SUPP_NAME, FST_SUPP_INN, FST_SUPP_KPP, NUM_SUPPS,
                                CURRENCY, REGION_NAME, CONTRACT_STAGE, FZ]  # Поля для таблицы
                self.start_csv(headers_list)  # Начало записи таблицы в файл
                for page in xrange(1, num_pages + 1):
                    contracts = self.get_current_page(target_url, page)
                    for contract in contracts:
                        products = contract.get('products')
                        if products:
                            for product in products:
                                contract_info = self.get_contract_info(contract) # Создаем словарь с общими данными контракта
                                details_by_prod = self.add_products_info(product, contract_info) # Добавляем в этот словарь данные по продукту
                                self.to_csv(headers_list, details_by_prod)
                self.stop_csv()  # Конец записи таблицы в файл
                print 'ГОТОВО'

    def span_for_search_is_ok(self, dateranges, static):
        for daterange in dateranges:
            begin = daterange[0]
            end = daterange[1]
            target_url = static.format(begin, end)
            response = urllib.urlopen(target_url)
            total = json.loads(response.read())['contracts']['total']
            if total >= 500:
                print 'Число результатов превышает лимит. ' \
                      'Попробуйте разбить период на отрезки длиной менее {} дней ' \
                      'или ввести дополнительные параметры фильтрации'.format(self.span)
                break
        return True

    def get_contracts(self, **kwargs):
        # Выгрузить данные по контрактам
        dateranges = self.get_scenario(**kwargs)
        static_url = self.construct_api(**kwargs)
        for daterange in dateranges:
            begin = daterange[0]
            end = daterange[1]
            target_url = static_url.format(begin, end)
            num_pages = self.get_num_pages(target_url)
            if num_pages:
                headers_list = [CLEARSPENDING_URL, REGNUM, SIGN_DATE,
                               FST_PROD_DESCR, NUM_PRODUCTS,
                               CUSTOMER_NAME, CUSTOMER_INN, CUSTOMER_KPP,
                               FST_SUPP_NAME, FST_SUPP_INN, FST_SUPP_KPP, NUM_SUPPS,
                                CONTRACT_PRICE,
                               CURRENCY, REGION_NAME, CONTRACT_STAGE, FZ]  # Поля для таблицы
                self.start_csv(headers_list)  # Начало записи таблицы в файл
                for page in xrange(1, num_pages + 1):
                    contracts = self.get_current_page(target_url, page)
                    for contract in contracts:
                        contract_info = self.get_contract_info(contract)  # Создаем словарь с общими данными контракта
                        fst_prod_details = self.add_fst_prod_info(contract, contract_info)  # Добавляем в этот словарь данные по первому продукту в списке
                        self.to_csv(headers_list, fst_prod_details) # Записываем строку в таблицу
                self.stop_csv()  # Конец записи таблицы в файл
                print 'ГОТОВО'









# class ContractsSurferOlder(object):
#     regions_reference = 'region_codes.json'
#
#     def __init__(self, filename=None):
#         if filename:
#             self.filename = filename
#         else:
#             self.filename = 'no_name'
#         self.file_handler = None
#         self.regions = self.load_regions_ref()
#         self.writer = None
#
#     def load_regions_ref(self):
#         # Загрузить файл-справочник с расшифровками кодов регионов
#         with open(self.regions_reference) as regions:
#             return json.load(regions)
#
#     def construct_api(self,
#                       start_date=None,
#                       stop_date=None,
#                       inn=None,
#                       kpp=None,
#                       region=None,
#                       fz=None,
#                       pricerange=None,
#                       product_search=None):
#         # Конструктор API-запроса
#         # По умолчанию выгружает данные с начала текущего года
#         print '\nПАРАМЕТРЫ ЗАПРОСА:'
#         default_daterange = self.get_default_daterange()
#         default_start = default_daterange[0]
#         default_stop = default_daterange[1]
#         target_url = 'http://openapi.clearspending.ru/restapi/v3/contracts/select/?'
#         if start_date is None and stop_date is None:
#             target_url += '&daterange={}-{}'.format(default_start, default_stop)
#             print 'Период: {}-{}'.format(default_start, default_stop)
#         elif stop_date is None and start_date:
#             target_url += '&daterange={}-{}'.format(start_date, default_stop)
#             print 'Период: {}-{}'.format(start_date, default_stop)
#         elif stop_date and not start_date:
#             target_url += '&daterange={}-{}'.format(default_start, stop_date)
#             print 'Период: {}-{}'.format(default_start, stop_date)
#         else:
#             target_url += '&daterange={}-{}'.format(start_date, stop_date)
#             print 'Период: {}-{}'.format(start_date, stop_date)
#         if inn:
#             target_url += '&customerinn={}'.format(inn)
#             print 'ИНН заказчика: {}'.format(inn)
#         if kpp:
#             target_url += '&customerkpp={}'.format(kpp)
#             print 'КПП заказчика: {}'.format(kpp)
#         if region:
#             target_url += '&customerregion={}'.format(region)
#             print 'Код региона заказчика: {}'.format(region)
#         if fz:
#             target_url += '&fz={}'.format(fz)
#             print 'ФЗ: {}'.format(fz)
#         if pricerange:
#             target_url += '&pricerange={}'.format(pricerange)
#             print 'Диапазон цен: {}'.format(pricerange)
#         if product_search:
#             target_url += '&productsearchlist={}'.format(product_search)
#             print 'Ключевые слова: {}'.format(product_search)
#         print '\nURL ЗАПРОСА:', target_url  # print 'Request URL:', target_url
#         return target_url
#
#     def get_default_daterange(self, begin=None, end=None):
#         default_year = datetime.datetime.now().year
#         if not begin:
#             begin = '01.01.{}'.format(default_year)
#         if not end:
#             end = '31.12.{}'.format(default_year)
#         return begin, end
#
#     def get_dateranges(self, begin, end, span=30):
#         # Разбить период на отрезки времени, длина которых равна значению span
#         begin = datetime.datetime.strptime(begin, '%d.%m.%Y')
#         end = datetime.datetime.strptime(end, '%d.%m.%Y')
#         diff = end - begin
#         ranges = list()
#         if diff > datetime.timedelta(span):
#             start = begin
#             finish = begin + datetime.timedelta(span-1)
#             while start <= end:
#                 ranges.append((start.strftime('%d.%m.%Y'), finish.strftime('%d.%m.%Y')))
#                 start += datetime.timedelta(span)
#                 finish += datetime.timedelta(span)
#         else:
#             ranges.append((begin.strftime('%d.%m.%Y'), end.strftime('%d.%m.%Y')))
#         return ranges
#
#     def get_num_pages(self, url):
#         # Установить число страниц, выпадающих по запросу
#         response = urllib.urlopen(url)
#         try:
#             data = json.loads(response.read())
#             num_contracts = data['contracts']['total']
#             print '\nЧисло подходящих контрактов:', num_contracts
#             num_pages = num_contracts / 50 + (num_contracts % 50 != 0)
#             return num_pages
#         except ValueError:
#             print 'Данные, отвечающие параметрам, не найдены'
#
#     def get_request_info(self, **kwargs):
#         # Вывести на печать параметры запроса и цифру, показывающую, сколько контрактов найдено по запросу
#         target_url = self.construct_api(**kwargs)
#         self.get_num_pages(target_url)
#
#     def get_current_page(self, url, page):
#         # Сформирова URL текущей страницы, отправить запрос, найти в полученном ответе контракты
#         target = url + '&page={}'.format(page)
#         response = urllib.urlopen(target)
#         contracts = json.loads(response.read())['contracts']['data']
#         return contracts
#
#     def get_contract_info(self, contract):
#         # Собрать данные по контракту
#         stages = {'E': 'Исполнение',
#                   'EC': 'Исполнение завершено',
#                   'ET': 'Исполнение прекращено'}
#         regnum = contract.get('regNum', '-')
#         base_url = 'https://clearspending.ru/contract/{}'
#         contract_info = {CLEARSPENDING_URL: base_url.format(regnum),
#                          REGNUM: regnum,
#                          SIGN_DATE: contract.get('signDate', '-'),
#                          FZ: contract.get('fz', '-'),
#                          CUSTOMER_NAME: contract.get('customer', {}).get('fullName', '-'),
#                          CUSTOMER_INN: contract.get('customer', {}).get('inn', '-'),
#                          CUSTOMER_KPP: contract.get('customer', {}).get('kpp', '-'),
#                          NUM_SUPPS: len(contract.get('suppliers', [])),
#                          FST_SUPP_NAME: contract.get('suppliers', [{}])[0].get('organizationName', '-'),
#                          FST_SUPP_INN: contract.get('suppliers', [{}])[0].get('inn', '-'),
#                          FST_SUPP_KPP: contract.get('suppliers', [{}])[0].get('kpp', '-'),
#                          CONTRACT_PRICE: contract.get('price', '-'),
#                          CURRENCY: contract.get('currency', {}).get('name', '-'),
#                          REGION_NAME: self.regions_reference.get(contract.get('regionCode', '-')),
#                          CONTRACT_STAGE: stages.get(contract.get('currentContractStage', '-'))}
#         return contract_info
#
#     def add_fst_prod_info(self, contract, contr_info):
#         # Собрать данные о первом продукте в списке и об общем числе продуктов в контракте
#         contr_info[NUM_PRODUCTS] = len(contract.get('products', []))
#         contr_info[FST_PROD_DESCR] = contract.get('products', [{}])[0].get('name', '-')
#         return contr_info
#
#     def add_products_info(self, product, contr_info):
#         # Собрать данные по продукту
#         contr_info[PRODUCT_DESCR] = product.get('name', '-')
#         contr_info[OKPD2] = product.get('OKPD2', {}).get('code', '-')
#         contr_info[OKPD2_NAME] = product.get('OKPD2', {}).get('name', '-')
#         contr_info[OKPD] = product.get('OKPD', {}).get('code', '-')
#         contr_info[OKPD_NAME] = product.get('OKPD', {}).get('name', '-')
#         contr_info[OKDP] = product.get('OKDP', {}).get('code', '-')
#         contr_info[OKDP_NAME] = product.get('OKDP', {}).get('name', '-')
#         contr_info[SINGLE_PRICE] = product.get('price', '-')
#         contr_info[OKEI] = product.get('OKEI', {}).get('name', '-')
#         contr_info[QUANTITY] = product.get('quantity', '-')
#         contr_info[PRODUCT_SUM] = product.get('sum', '-')
#         return contr_info
#
#     def get_products(self, **kwargs):
#         # Выгрузить данные по продуктам
#         target_url = self.construct_api(**kwargs)
#         num_pages = self.get_num_pages(target_url)
#         if num_pages:
#             headers_list = [CLEARSPENDING_URL, REGNUM, SIGN_DATE,
#                             PRODUCT_DESCR, OKPD2, OKPD2_NAME, OKPD, OKPD_NAME, OKDP, OKDP_NAME,
#                             SINGLE_PRICE, OKEI, PRODUCT_SUM, QUANTITY,
#                             CUSTOMER_NAME, CUSTOMER_INN, CUSTOMER_KPP,
#                             FST_SUPP_NAME, FST_SUPP_INN, FST_SUPP_KPP, NUM_SUPPS,
#                             CURRENCY, REGION_NAME, CONTRACT_STAGE, FZ]  # Поля для таблицы
#             self.start_csv(headers_list)  # Начало записи таблицы в файл
#             for page in xrange(1, num_pages + 1):
#                 contracts = self.get_current_page(target_url, page)
#                 for contract in contracts:
#                     products = contract.get('products')
#                     if products:
#                         for product in products:
#                             contract_info = self.get_contract_info(contract) # Создаем словарь с общими данными контракта
#                             details_by_prod = self.add_products_info(product, contract_info) # Добавляем в этот словарь данные по продукту
#                             self.to_csv(headers_list, details_by_prod)
#             self.stop_csv()  # Конец записи таблицы в файл
#             print 'ГОТОВО'
#
#     def get_contracts(self, **kwargs):
#         # Выгрузить данные по контрактам
#         target_url = self.construct_api(**kwargs)
#         num_pages = self.get_num_pages(target_url)
#         if num_pages:
#             headers_list = [CLEARSPENDING_URL, REGNUM, SIGN_DATE,
#                            FST_PROD_DESCR, NUM_PRODUCTS,
#                            CUSTOMER_NAME, CUSTOMER_INN, CUSTOMER_KPP,
#                            FST_SUPP_NAME, FST_SUPP_INN, FST_SUPP_KPP, NUM_SUPPS,
#                             CONTRACT_PRICE,
#                            CURRENCY, REGION_NAME, CONTRACT_STAGE, FZ]  # Поля для таблицы
#             self.start_csv(headers_list)  # Начало записи таблицы в файл
#             for page in xrange(1, num_pages + 1):
#                 contracts = self.get_current_page(target_url, page)
#                 for contract in contracts:
#                     contract_info = self.get_contract_info(contract)  # Создаем словарь с общими данными контракта
#                     fst_prod_details = self.add_fst_prod_info(contract, contract_info)  # Добавляем в этот словарь данные по первому продукту в списке
#                     self.to_csv(headers_list, fst_prod_details) # Записываем строку в таблицу
#             self.stop_csv()  # Конец записи таблицы в файл
#             print 'ГОТОВО'
#
#
#     def to_csv(self, headers, data):
#         # Преобразовать данные в пригодный для записи в CSV вид, записать строку
#         values = dict()
#         for header in headers:
#             try:
#                 values[header] = data[header].encode('utf-8')
#             except:
#                 values[header] = str(data[header])
#         self.writer.writerow(values)
#
#     def start_csv(self, headers):
#         # Начать запись в файл CSV, записать строку заголовков
#         self.filename += '.csv'
#         print 'Запись в файл:', self.filename
#         self.file_handler = open(self.filename, 'wb')
#         self.writer = csv.DictWriter(self.file_handler, fieldnames=headers)
#         self.writer.writeheader()
#
#     def stop_csv(self):
#         # Закрыть файл, в который записывались данные
#         self.file_handler.close()

# Парсер аргументов командной строки
parser = argparse.ArgumentParser(description='Выгрузить данные через API Clearspending.ru')
parser.add_argument('-o', '--output',
                    type=str,
                    metavar='',
                    help='Название итогового файла CSV')
parser.add_argument('-b', '--begin',
                    type=str,
                    metavar='',
                    help='Начало периода в форме дд.мм.гггг')
parser.add_argument('-e', '--end',
                    type=str,
                    metavar='',
                    help='Конец периода в форме дд.мм.гггг')
parser.add_argument('-i', '--inn',
                    type=str,
                    metavar='',
                    help='ИНН заказчика')
parser.add_argument('-k', '--kpp',
                    type=str,
                    metavar='',
                    help='КПП заказчика')
parser.add_argument('-r', '--region',
                    type=str,
                    metavar='',
                    help='Код региона заказчика')
parser.add_argument('-p', '--pricerange',
                    type=str,
                    metavar='',
                    help='Диапазон цен контрактов, например: 10000-50000')
parser.add_argument('-f', '--fz',
                    type=str,
                    metavar='',
                    help='ФЗ, варианты: 94, 44, 223')
group = parser.add_mutually_exclusive_group()
group.add_argument('-C', '--contracts',
                   action='store_true',
                   help='Выгрузить данные в формате 1 строка = 1 контракт')
group.add_argument('-P', '--products',
                   action='store_true',
                   help='Выгрузить данные в формате 1 строка = 1 продукт')


def get_data(output, begin, end, inn, kpp, region, pricerange, fz):
    # Функция, формирующая объект и метод класса в соответствии с аргументами
    surfer = ContractsSurfer(output)
    if a.contracts:
        # При вызове параметра -C выгрузить данные по контрактам
        surfer.get_contracts(start_date=begin,
                             stop_date=end,
                             inn=inn,
                             kpp=kpp,
                             region=region,
                             pricerange=pricerange,
                             fz=fz)

    elif a.products:
        # При вызове параметра -P выгрузить данные по продуктам
        surfer.get_products(start_date=begin,
                             stop_date=end,
                             inn=inn,
                             kpp=kpp,
                             region=region,
                             pricerange=pricerange,
                             fz=fz)
    else:
        # Без указания -C или -P вывести на печать параметры запроса и сколько по ним доступно контрактов
        surfer.get_request_info(start_date=begin,
                                stop_date=end,
                                inn=inn,
                                kpp=kpp,
                                region=region,
                                pricerange=pricerange,
                                fz=fz)


if __name__ == '__main__':
    a = parser.parse_args()
    get_data(a.output, a.begin, a.end, a.inn, a.kpp, a.region, a.pricerange, a.fz)
    # surfer = ContractsSurfer()
    # surfer.get_dateranges('01.01.2016', '31.12.2017', 1)