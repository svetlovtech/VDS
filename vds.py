from requests import get
from argparse import ArgumentParser
import logging
import datetime


class SetVacancyDataException(ValueError):
    pass


class Specialization:
    def __init__(self, name: str, value: float) -> None:
        self.__name = name
        self.__number = value

    def __str__(self) -> str:
        return f'(Specialization-name:{self.name}; value:{self.number})'

    @property
    def name(self):
        return self.__name

    @property
    def number(self):
        return self.__number


class Area:
    def __init__(self, name: str, value: int) -> None:
        self.__name = name
        self.__number = value

    def __str__(self) -> str:
        return f'(Area-name:{self.name}; value:{self.number})'

    @property
    def name(self):
        return self.__name

    @property
    def number(self):
        return self.__number


class Vacancy:
    def __init__(self, id_number: int, area: Area, specialization: Specialization) -> None:
        self._id_number: int = id_number
        self._area: Area = area
        self._specialization: Specialization = specialization
        self._data: str = None
        self._url = f"https://api.hh.ru/vacancies/{self.id}"
        logging.debug(str(self))

    def __str__(self) -> str:
        return f'(Vacancy-' \
               f'id_number:{self._id_number}; ' \
               f'area:{self._area}; ' \
               f'specialization:{self._specialization}; ' \
               f'data:{self._data}; ' \
               f'url:{self._url})'

    @property
    def url(self):
        return self._url

    @property
    def id(self):
        return self._id_number

    @id.setter
    def id(self, value):
        self._id_number = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value: dict):
        if type(value) is not dict:
            raise SetVacancyDataException(f'Data must be a dictionary. Your data is {type(value)}')
        if self._data is None:
            self._data = value
        else:
            raise SetVacancyDataException('Data is not none')

    @property
    def area(self):
        return self._area

    @area.setter
    def area(self, value):
        self._area = value

    @property
    def specialization(self):
        return self._specialization

    @specialization.setter
    def specialization(self, value):
        self._specialization = value


class Actions:
    @staticmethod
    def parsing_data():
        vacancy = Vacancy(25886815, VDMConfig.area_ids[0], VDMConfig.specializations_ids[0])
        response = get(vacancy.url, headers=VDMConfig.HEADERS)
        vacancy.data = response.json()
        logging.info(vacancy)

        """https://api.hh.ru/vacancies?area=1&specialization=1.117&page=0&per_page=1&no_magic=true"""
        pass

    @staticmethod
    def get_areas():
        res = get('https://api.hh.ru/areas', headers=VDMConfig.HEADERS)
        with open(f"areas{str(datetime.datetime.utcnow()).replace(':', '').replace('-', '').replace('.', '')}.txt",
                  mode="w+", encoding="UTF8") as file:
            file.write(res.text)

    @staticmethod
    def get_specializations():
        res = get('https://api.hh.ru/specializations', headers=VDMConfig.HEADERS)
        with open(f"specializations{str(datetime.datetime.utcnow()).replace(':', '').replace('-', '').replace('.', '')}"
                  f".txt", mode="w+", encoding="UTF8") as file:
            file.write(res.text)


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


class VDMConfig:
    APP_NAME = 'VDS'
    __version__ = '0.0.1'
    APP_EMAIL = 'alexeysvetlov92@gmail.com'
    HEADERS = {'user-agent': f'{APP_NAME}/{__version__} ({APP_EMAIL})'}

    LOGGER_STR_FORMAT = u'%(filename)s[LINE:%(lineno)d] Level:%(levelname)-8s [%(asctime)s]  %(message)s'
    area_ids: list = [
        Area('Moscow', 1),
    ]
    specializations_ids: list = [
        Specialization('Banking software', 1.395),
        Specialization('Testing', 1.117),
        Specialization('Development', 1.221),
    ]


if __name__ == '__main__':
    args = parse_args()
    logger_level = None
    if args.debug is True:
        logger_level = logging.DEBUG
    else:
        logger_level = logging.INFO
    logging.basicConfig(format=VDMConfig.LOGGER_STR_FORMAT,
                        level=logger_level,
                        filename=args.logfilename)
    logging.debug(args)
    logging.info('Starting vds...')
    if args.action is 'parsing':
        logging.info('Parsing data...')
        Actions.parsing_data()
        logging.info('Parsing data complete')
    elif args.action is 'areas':
        logging.info('Getting areas data...')
        Actions.get_areas()
        logging.info('Getting areas data complete')
    elif args.action is 'specializations':
        logging.info('Getting specializations data...')
        Actions.get_specializations()
        logging.info('Getting specializations data complete')
    logging.info('Stopping vds')
