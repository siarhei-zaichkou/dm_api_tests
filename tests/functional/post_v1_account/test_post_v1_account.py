from dm_api_account.apis.account_api import AccountApi
from dm_api_account.apis.login_api import LoginApi
from api_mailhog.apis.mailhog_api import MailhogApi
from json import loads


def test_post_v1_account():
    # Регистрация пользователя
    account_api = AccountApi(host='http://5.63.153.31:5051')
    login_api = LoginApi(host='http://5.63.153.31:5051')
    mailhog_api = MailhogApi(host='http://5.63.153.31:5025')

    login = 'supermegatestlogin3'
    password = '123456'
    email = f'{login}@gmail.com'
    json_data = {
        'login': login,
        'password': password,
        'email': email
    }
    response = account_api.post_v1_account(json_data=json_data)
    assert response.status_code == 201, f"Пользователь не был создан {response.json()}"

    # Получение письма из почтового сервиса
    response = mailhog_api.get_api_v2_messages()
    assert response.status_code == 200, "Письма не были получены"

    # Получение активационного токена
    token = get_activation_token_by_login(login, response)
    print(token)

    # Активация пользователя
    response = account_api.put_v1_account_token(token)
    assert response.status_code == 200, "Пользователь не был активирован"

    # Авторизация
    json_data = {
        'login': login,
        'password': password,
        'rememberMe': True
    }
    response = login_api.post_v1_account_login(json_data=json_data)
    assert response.status_code == 200, "Пользователь не смог авторизоваться"
    print(response.text)


def get_activation_token_by_login(login, response):
    token = None
    for item in response.json()['items']:
        user_data = loads(item['Content']['Body'])
        user_login = user_data['Login']
        if user_login == login:
            token = user_data['ConfirmationLinkUrl'].split('/')[-1]
    return token
