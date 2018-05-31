import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from argparse import ArgumentParser
from requests import get
from typing import List, Set, IO
from tqdm import tqdm

APP_NAME = 'VDS'
__version__ = '20180601'
APP_EMAIL = 'alexeysvetlov92@gmail.com'
HEADERS = {'user-agent': f'{APP_NAME}/{__version__} ({APP_EMAIL})'}
LOGGER_STR_FORMAT = u'%(filename)s[LINE:%(lineno)d] Level:%(levelname)-8s [%(asctime)s]  %(message)s'
area_ids: list = [1]
specializations_ids: list = [1.395, 1.117, 1.221]


def get_areas():
    res = get('https://api.hh.ru/areas', headers=HEADERS)
    with open(f"areas{str(datetime.utcnow()).replace(':', '').replace('-', '').replace('.', '')}.txt",
              mode="w+", encoding="UTF8") as file:
        file.write(res.text)
        file.flush()


def get_specializations():
    res = get('https://api.hh.ru/specializations', headers=HEADERS)
    with open(f"specializations{str(datetime.utcnow()).replace(':', '').replace('-', '').replace('.', '')}"
              f".txt", mode="w+", encoding="UTF8") as file:
        file.write(res.text)
        file.flush()


def get_vacancies_data(vacancies_url_pool: Set[str], logfilename: str, parsing_datetime):
    try:
        datafile = open(file=logfilename, encoding='utf8', mode='x')
        datafile.close()
    except FileExistsError:
        pass
    with open(file=logfilename, encoding='utf8', mode='a') as file:
        progressbar = tqdm(total=len(vacancies_url_pool))
        with ThreadPoolExecutor(max_workers=args.threadpoolsize) as executor:
            for vacancies_url in vacancies_url_pool:
                executor.submit(get_vacancy_data, vacancies_url, progressbar, file, parsing_datetime)
            executor.shutdown()
        progressbar.close()


def get_vacancy_data(vacancy_url: str, progressbar_ref: tqdm, logfile: IO, datetime):
    response = get(vacancy_url, headers=HEADERS)
    text = f'{datetime} Vacancy:{response.text.lower()}\n'
    logfile.write(text)
    logfile.flush()
    progressbar_ref.update(1)


def get_vacancies_list(area_id: int, specialization_number: float) -> List[str]:
    vacancies_list: List[str] = []
    site = 'https://api.hh.ru/vacancies?'
    page_number = 0
    while True:
        parameters = f"area={area_id}&" \
                     f"specialization={specialization_number}&" \
                     f"page={page_number}&" \
                     f"per_page=100&" \
                     f"no_magic=true&" \
                     f"period=1"
        response = get(site + parameters, headers=HEADERS).json()
        for vacancies_data in response['items']:
            vacancies_list.append(vacancies_data['url'])
        if page_number == response['pages'] - 1:
            break
        else:
            page_number += 1
    return vacancies_list


def get_vacancies_url() -> Set[str]:
    all_vacancies: List[str] = []
    for area_number in area_ids:
        for spec_number in specializations_ids:
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


def parse_args():
    parser = ArgumentParser(description='Vacancies data scrapper script.')
    parser.add_argument("-a", "--action", type=str, default='parsing',
                        help='Type of action\n'
                             'Options: parsing|areas|specializations\n'
                             'parsing - this is main action and this set as default.\n'
                             'areas - allows you to get areas info\n'
                             'specializations - allows you to get specializations info')
    parser.add_argument("-i", "--interval", type=int, default=1440,
                        help='Set interval rate for parse data'
                             '(60 minutes as default)')
    parser.add_argument("-tps", "--threadpoolsize", type=int, default=16,
                        help='Set thread pool size. '
                             '(4 threads as default)')
    parser.add_argument("-dfn", "--datafilename", type=str, default='vdsdata.txt',
                        help='Set custom log file name. \n'
                             '(vds.log as default)')
    parser.add_argument("-d", "--debug", type=bool, default=False,
                        help='If True, logging level will be debug. \n'
                             '(False as default)')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    logger_level = None
    if args.debug is True:
        logger_level = logging.DEBUG
    else:
        logger_level = logging.INFO
    logging.basicConfig(format=LOGGER_STR_FORMAT,
                        level=logger_level,
                        filename='vds.log')
    logging.debug(args)
    logging.info('Starting vds...')
    if args.action is 'parsing':
        while True:
            logging.info('Parsing data...')
            print('Parsing data...')
            parsing_data_datetime = datetime.isoformat(datetime.now(), sep='T')
            url_vacancies_pool = get_vacancies_url()
            get_vacancies_data(url_vacancies_pool, args.datafilename, parsing_data_datetime)
            print(f'Parsing data complete.')
            logging.info(f'Parsing data complete.')
            time.sleep(args.interval * 60)

    elif args.action is 'areas':
        logging.info('Getting areas data...')
        get_areas()
        logging.info('Getting areas data complete')
    elif args.action is 'specializations':
        logging.info('Getting specializations data...')
        get_specializations()
        logging.info('Getting specializations data complete')
    logging.info('Stopping vds')
