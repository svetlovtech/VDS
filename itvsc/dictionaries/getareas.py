from itvsc.config import headers
import datetime
import requests

if __name__ == '__main__':
    response = requests.get('https://api.hh.ru/areas', headers=headers)
    with open(f"{str(datetime.datetime.utcnow()).replace(':', '').replace('-', '').replace('.', '')}"
              f"areas.txt", mode="w+", encoding="UTF8") as file:
        file.write(response.text)
