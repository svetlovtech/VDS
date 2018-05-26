from requests import get
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
        self._logger = logging.getLogger('__main__')
        self._id_number: int = id_number
        self._area: Area = area
        self._specialization: Specialization = specialization
        self._data: str = None
        self._url = f"https://api.hh.ru/vacancies/{self.id}"
        self._logger.debug(str(self))

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


class VDSConfig:
    logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG)

    app_name = 'VDS'
    app_version = '0.1'
    app_email = 'alexeysvetlov92@gmail.com'
    headers = {'user-agent': f'{app_name}/{app_version} ({app_email})'}

    area_ids: list = [
        Area('Moscow', 1),
    ]

    specializations_ids: list = [
        Specialization('Banking software', 1.395),
        Specialization('Testing', 1.117),
        Specialization('Development', 1.221),
    ]


if __name__ == '__main__':
    vacancy = Vacancy(25886815, VDSConfig.area_ids[0], VDSConfig.specializations_ids[0])
    print(vacancy)
    response = get(vacancy.url, headers=VDSConfig.headers)
    vacancy.data = response.json()
    print(vacancy)

    response = get('https://api.hh.ru/areas', headers=VDSConfig.headers)
    with open(f"{str(datetime.datetime.utcnow()).replace(':', '').replace('-', '').replace('.', '')}"
              f"areas.txt", mode="w+", encoding="UTF8") as file:
        file.write(response.text)

    response = get('https://api.hh.ru/specializations', headers=VDSConfig.headers)
    with open(f"{str(datetime.datetime.utcnow()).replace(':', '').replace('-', '').replace('.', '')}"
              f"specializations.txt", mode="w+", encoding="UTF8") as file:
        file.write(response.text)

    """https://api.hh.ru/vacancies?area=1&specialization=1.117&page=0&per_page=1&no_magic=true"""
