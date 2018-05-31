from concurrent.futures import ThreadPoolExecutor
from argparse import ArgumentParser
from requests import get
from typing import List
import logging
import datetime

from tqdm import tqdm

APP_NAME = 'VDS'
__version__ = '0.0.1'
APP_EMAIL = 'alexeysvetlov92@gmail.com'
HEADERS = {'user-agent': f'{APP_NAME}/{__version__} ({APP_EMAIL})'}
LOGGER_STR_FORMAT = u'%(filename)s[LINE:%(lineno)d] Level:%(levelname)-8s [%(asctime)s]  %(message)s'
area_ids: list = [1]
specializations_ids: list = [1.395, 1.117, 1.221]


def get_vacancy_data(vacancy_url: str, progressbar_ref: tqdm):
    bad_chars = ['\u2212', '\u2015', '\u200b', '\xe9', '\u2219', '\u25aa', '\u3000', '\ufeff', '\u2011', '\u200e',
                 '\ufb01', '\u0306', '\uff0c', '\u2713']
    response = get(vacancy_url, headers=HEADERS)
    text = response.text.lower()
    for char in bad_chars:
        text = text.replace(char, '')
    logging.info(text)
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


def get_areas():
    res = get('https://api.hh.ru/areas', headers=HEADERS)
    with open(f"areas{str(datetime.datetime.utcnow()).replace(':', '').replace('-', '').replace('.', '')}.txt",
              mode="w+", encoding="UTF8") as file:
        file.write(res.text)
        file.flush()


def get_specializations():
    res = get('https://api.hh.ru/specializations', headers=HEADERS)
    with open(f"specializations{str(datetime.datetime.utcnow()).replace(':', '').replace('-', '').replace('.', '')}"
              f".txt", mode="w+", encoding="UTF8") as file:
        file.write(res.text)
        file.flush()


def parse_args():
    parser = ArgumentParser(description='Vacancies data scrapper script.')
    parser.add_argument("-a", "--action", type=str, default='parsing',
                        help='Type of action\n'
                             'Options: parsing|areas|specializations\n'
                             'parsing - this is main action and this set as default.\n'
                             'areas - allows you to get areas info\n'
                             'specializations - allows you to get specializations info')
    parser.add_argument("-i", "--interval", type=int, default=60,
                        help='Set interval rate for parse data'
                             '(60 minutes as default)')
    parser.add_argument("-tps", "--threadpoolsize", type=int, default=4,
                        help='Set thread pool size. '
                             '(4 threads as default)')
    parser.add_argument("-lfn", "--logfilename", type=str, default='vds.log',
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
                        filename=args.logfilename)
    logging.debug(args)
    logging.info('Starting vds...')
    if args.action is 'parsing':
        logging.info('Parsing data...')
        print('Parsing data...')
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
        logging.info(f'Parsing data complete.')
        print(f'Parsing data complete.')

        progressbar = tqdm(total=len(unique_vacancies))
        with ThreadPoolExecutor(max_workers=args.threadpoolsize) as executor:
            for url in unique_vacancies:
                executor.submit(get_vacancy_data, url, progressbar)
            executor.shutdown()
        progressbar.close()
    elif args.action is 'areas':
        logging.info('Getting areas data...')
        get_areas()
        logging.info('Getting areas data complete')
    elif args.action is 'specializations':
        logging.info('Getting specializations data...')
        get_specializations()
        logging.info('Getting specializations data complete')
    logging.info('Stopping vds')
