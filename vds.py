import json
from typing import List, Set
from requests.auth import HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging
import requests

APP_NAME = 'VDS'
__version__ = '20180601'
APP_EMAIL = 'alexeysvetlov92@gmail.com'
HEADERS = {'User-Agent': f'{APP_NAME}/{__version__} ({APP_EMAIL})',
           'Content-Type': 'application/json'}
LOGGER_STR_FORMAT = u'%(filename)s[LINE:%(lineno)d] Level:%(levelname)-8s [%(asctime)s]  %(message)s'
AREA_IDS: list = [1]
SPECIALIZATIONS_IDS: list = [1.395, 1.117, 1.221, 1.327]
THREAD_POOL_SIZE: int = 16
LOGGER_LEVEL = logging.INFO
LOG_FILENAME = 'vsd.log'

ELASTIC_SEARCH_HOST = 'localhost'
ELASTIC_SEARCH_PORT = 9200
ELASTIC_SEARCH_INDEX_NAME = 'vds'
ELASTIC_SEARCH_INDEX_DOC = 'doc'
ELASTIC_SEARCH_LOGIN = 'admin'
ELASTIC_SEARCH_PASSWORD = 'admin'
ELASTIC_AUTH = HTTPBasicAuth(ELASTIC_SEARCH_LOGIN, ELASTIC_SEARCH_PASSWORD)


def get_areas():
    res = requests.get('https://api.hh.ru/areas', headers=HEADERS)
    with open(f"{str(datetime.utcnow()).replace(':', '').replace('-', '').replace('.', '')}_areas.txt",
              mode="w+", encoding="UTF8") as file:
        file.write(res.text)
        file.flush()


def get_specializations():
    res = requests.get('https://api.hh.ru/specializations', headers=HEADERS)
    with open(f"{str(datetime.utcnow()).replace(':', '').replace('-', '').replace('.', '')}_specializations.txt",
              mode="w+", encoding="UTF8") as file:
        file.write(res.text)
        file.flush()


def load_vacancy_data(vacancie_url: str, elsaticsearch_index_name: str):
    hh_responce = requests.get(vacancie_url)
    data = hh_responce.text.lower().encode('utf-8')
    json_data: dict = json.loads(data)

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
        logging.warning(f'Code:{es_response.status_code} {es_response.url} {es_response.text}')


def load_vacancies_data(vacancies_url_pool: Set[str], es_index_name: str):
    logging.info(f'Loading vacancies data...')
    with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE) as executor:
        for vacancies_url in vacancies_url_pool:
            executor.submit(load_vacancy_data, vacancies_url, es_index_name)
        executor.shutdown()
    logging.info(f'Loading vacancies data complete')


def get_vacancies_list(area_id: int, specialization_number: float) -> List[str]:
    vacancies_list: List[str] = []
    logging.info(f'Get vacancies by area:{area_id} specialization_number:{specialization_number}')
    site = 'https://api.hh.ru/vacancies?'
    page_number = 0
    while True:
        logging.info(f'\tPage number is {page_number}')
        parameters = f"area={area_id}&" \
                     f"specialization={specialization_number}&" \
                     f"page={page_number}&" \
                     f"per_page=100&" \
                     f"no_magic=true&" \
                     f"period=1"
        response = requests.get(site + parameters, headers=HEADERS).json()
        for vacancies_data in response['items']:
            vacancies_list.append(vacancies_data['url'])
        if page_number == response['pages'] - 1:
            break
        else:
            page_number += 1
    return vacancies_list


def get_unique_vacancies_url() -> Set[str]:
    all_vacancies: List[str] = []
    for area_number in AREA_IDS:
        for spec_number in SPECIALIZATIONS_IDS:
            for url in get_vacancies_list(area_id=area_number, specialization_number=spec_number):
                all_vacancies.append(url)
    unique_vacancies = set()

    for url in all_vacancies:
        unique_vacancies.add(url)

    logging.info(f'Statistic: all_vacancies {len(all_vacancies)}, unique_vacancies {len(unique_vacancies)}')
    print(f'Statistic: all_vacancies {len(all_vacancies)}, unique_vacancies {len(unique_vacancies)}')
    logging.debug('all_vacancies' + str(all_vacancies))
    logging.debug('unique_vacancies' + str(unique_vacancies))
    return unique_vacancies


def create_index(indexname: str):
    logging.info(f'Creating index {index_name} ...')
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
    es_response = requests.put(url=f'https://{ELASTIC_SEARCH_HOST}:{ELASTIC_SEARCH_PORT}/{indexname}',
                               headers=HEADERS,
                               auth=ELASTIC_AUTH,
                               json=index_data,
                               verify=False)
    if es_response.status_code is not 201:
        logging.warning(f'Code:{es_response.status_code} {es_response.text}')
    logging.info(f'Creating index {index_name} finished')


if __name__ == '__main__':
    logging.basicConfig(format=LOGGER_STR_FORMAT,
                        level=LOGGER_LEVEL,
                        filename=LOG_FILENAME)
    logging.info('Starting vds...')
    get_areas()
    get_specializations()
    current_datetime = datetime.now()
    index_name = f'{ELASTIC_SEARCH_INDEX_NAME}-' \
                    f'{current_datetime.year}' \
                    f'{str(current_datetime.month).zfill(2)}' \
                    f'{str(current_datetime.day).zfill(2)}'
    create_index(index_name)
    url_vacancies_pool = get_unique_vacancies_url()
    load_vacancies_data(url_vacancies_pool, index_name)
    logging.info('vds finished')
