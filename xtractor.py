# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json
import csv

class Extractor(object):
    '''
    Методы сохранения данных в файлах .JSON и .CSV
    '''
    regions_reference = 'region_codes.json'  # Расшифровки кодов регионов

    def __init__(self, filename=None):
        if filename:
            self.filename = filename
        else:
            self.filename = 'no_name'
        self.csv_file = None
        self.regions = self.load_regions_ref()
        self.csv_writer = None
        self.json_file = None
        self.first = True

    def load_regions_ref(self):
        # Загрузить файл-справочник с расшифровками кодов регионов
        with open(self.regions_reference) as regions:
            return json.load(regions)

    def start_csv(self, headers):
        # Начать запись в файл CSV, записать строку заголовков
        filename = self.filename + '.csv'
        print 'Запись в файл:', self.filename
        self.csv_file = open(filename, 'wb')
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=headers)
        self.csv_writer.writeheader()

    def stop_csv(self):
        # Закрыть файл CSV, в который записывались данные
        self.csv_file.close()

    def start_json(self):
        # Начать запись в файл JSON
        filename = self.filename + '.json'
        self.json_file = open(filename, 'w')
        self.json_file.write('[')

    def write_json(self, dictionary):
        # Записать словарь в файл JSON
        if not self.first:
            self.json_file.write(',\n')
        json.dump(dictionary, self.json_file)
        self.filename = False

    def stop_json(self):
        # Закрыть файл JSON, в который записывались данные
        self.json_file.write(']')
        self.json_file.close()

    def to_csv(self, headers, data):
        # Преобразовать данные в пригодный для записи в CSV вид, записать строку
        values = dict()
        for header in headers:
            try:
                values[header] = data[header].encode('utf-8')
            except:
                values[header] = str(data[header])
        self.csv_writer.writerow(values)