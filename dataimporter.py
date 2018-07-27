import datetime
import json

from requests.auth import HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor
from tkinter import filedialog

import logging
import tkinter as tk
import requests

APP_NAME = 'VDS'
__version__ = '20180601'
APP_EMAIL = 'alexeysvetlov92@gmail.com'
HEADERS = {'User-Agent': f'{APP_NAME}/{__version__} ({APP_EMAIL})',
           'Content-Type': 'application/json'}
LOGGER_STR_FORMAT = u'%(filename)s[LINE:%(lineno)d] Level:%(levelname)-8s [%(asctime)s]  %(message)s'
THREAD_POOL_SIZE: int = 16
LOGGER_LEVEL = logging.INFO
LOG_FILENAME = 'dataimporter.log'

ELASTIC_SEARCH_HOST = 'localhost'
ELASTIC_SEARCH_PORT = 9200
ELASTIC_SEARCH_INDEX_NAME = 'vds_old'
ELASTIC_SEARCH_INDEX_DOC = 'doc'
ELASTIC_SEARCH_LOGIN = 'admin'
ELASTIC_SEARCH_PASSWORD = 'admin'
ELASTIC_AUTH = HTTPBasicAuth(ELASTIC_SEARCH_LOGIN, ELASTIC_SEARCH_PASSWORD)


def get_filepath() -> str:
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename()


def create_index(index_name: str):
    index_data = {
        "mappings": {
            "doc": {
                "properties": {
                    "address_geodata": {
                        "type": "geo_point"
                    },
                    "address_metro_geodata": {
                        "type": "geo_point"
                    }
                }
            }
        }
    }
    es_response = requests.put(url=f'https://{ELASTIC_SEARCH_HOST}:{ELASTIC_SEARCH_PORT}/{index_name}',
                               headers=HEADERS,
                               auth=ELASTIC_AUTH,
                               json=index_data,
                               verify=False)
    if es_response.status_code is not 201:
        logging.warning(f'Code:{es_response.status_code} {es_response.text}')


def load_vacancy_data_in_es(data: str, elsaticsearch_index_name: str):
    json_data: dict = json.loads(data.encode('utf-8'))
    try:
        address_lat = json_data['address']['lat']
        address_lng = json_data['address']['lng']
        json_data['address_geodata'] = f"{address_lat},{address_lng}"

    except TypeError:
        logging.warning('No address geodata')

    try:
        address_metro_lat = json_data['address']['metro']['lat']
        address_metro_lng = json_data['address']['metro']['lng']
        json_data['address_metro_geodata'] = f"{address_metro_lat},{address_metro_lng}"
    except TypeError:
        logging.warning('No metro address geodata')

    es_response = requests.post(url=f'https://{ELASTIC_SEARCH_HOST}:{ELASTIC_SEARCH_PORT}/'
                                    f'{elsaticsearch_index_name}/{ELASTIC_SEARCH_INDEX_DOC}',
                                headers=HEADERS,
                                auth=ELASTIC_AUTH,
                                json=json_data,
                                verify=False)
    if es_response.status_code is not 201:
        logging.warning(f'Code:{es_response.status_code} {es_response.text}')


if __name__ == '__main__':
    logging.basicConfig(format=LOGGER_STR_FORMAT,
                        level=LOGGER_LEVEL,
                        filename=LOG_FILENAME)
    logging.info('Starting vds...')
    logging.info(f'Loading vacancies data...')
    current_datetime = datetime.datetime.now()
    es_index_name = f'{ELASTIC_SEARCH_INDEX_NAME}-' \
                    f'{current_datetime.year}' \
                    f'{str(current_datetime.month).zfill(2)}' \
                    f'{str(current_datetime.day).zfill(2)}'
    logging.info(f'Creating index {es_index_name}')
    create_index(es_index_name)

    with open(file=get_filepath(), encoding='utf-8') as file:
        with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE) as executor:
            for line in file.readlines():
                executor.submit(load_vacancy_data_in_es, line, es_index_name)
            executor.shutdown()
    logging.info(f'Loading vacancies data complete')
