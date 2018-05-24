import requests

if __name__ == '__main__':
    search_text = 'java'
    area_id = '1'
    page_number = 0
    per_page = 100
    request_url = f'https://api.hh.ru/vacancies?text={search_text}&area={area_id}&page={page_number}&per_page={per_page}'

    app_name = 'HHVSC'
    app_version = '0.1'
    app_email = 'alexeysvetlov92@gmail.com'
    headers = {'user-agent': f'{app_name}/{app_version} ({app_email})'}
    response = requests.get(request_url, headers=headers)
    print(response.text)
