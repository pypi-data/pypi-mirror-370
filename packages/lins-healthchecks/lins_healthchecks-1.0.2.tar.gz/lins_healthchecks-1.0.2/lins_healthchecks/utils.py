from datetime import datetime
from functools import wraps
from json import dumps

import requests

from . import settings


def agora():
    return datetime.now(tz=settings.TIMEZONE)


def ts_logger(mensagem):
    print(f'{agora()}: {mensagem}')


def cria_resposta_erro(url, log):
    response = requests.models.Response()
    response.encoding = 'utf-8'
    response.status_code = settings.NO_RESPONSE
    response.url = url
    response._content = dumps({'erro': log}).encode('utf-8')
    return response


def auth_header(function):

    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(headers={'X-Api-Key': settings.HEALTH_CHECKS_API_KEY}, *args, **kwargs)

    return wrapper


@auth_header
def request(method, url, headers={}, json={}, show_logs=settings.SHOW_HEALTH_CHECKS_LOGS):
    timeout = settings.HEALTH_CHECKS_REQUEST_TIMEOUT
    retrys = settings.HEALTH_CHECKS_RETRYS
    try:
        request_method = getattr(requests, method)
        response = request_method(url=url, json=json, headers=headers, timeout=timeout)
        while not response.ok and retrys > 0:
            response = request_method(url=url, json=json, headers=headers, timeout=timeout)
            retrys -= 1
        return response
    except requests.RequestException as erro:
        log = f'Um {erro.__class__.__name__} ocorreu ao executar um {method.upper()} na url {url}.'
        ts_logger(log) if show_logs else None
        return cria_resposta_erro(url, log)


class FalhaHeathCheck():

    def reportar_inicio(self):
        print('### inicio - {} ###'.format(datetime.now()))

    def reportar_falha(self, erro):
        print('### Falha - {} >>> {} ###'.format(datetime.now(), erro))

    def reportar_sucesso(self):
        print('### sucesso - {} ###'.format(datetime.now()))

    def reportar_falha_por_exception(self):
        print('### Reportar falha por exception - {} ###'.format(datetime.now()))


class HealthCheck:

    def __init__(self, uuid):
        self.uuid = uuid

    def reportar_inicio(self):
        return request('get', f'{settings.LINS_HEALTH_CHECKS_PING_URL}{self.uuid}/start')

    def reportar_sucesso(self):
        return request('get', f'{settings.LINS_HEALTH_CHECKS_PING_URL}{self.uuid}')

    def reportar_falha(self, motivo: str):
        return request(
            'post',
            f'{settings.LINS_HEALTH_CHECKS_PING_URL}{self.uuid}/fail',
            json={'motivo': motivo},
        )

    def reportar_falha_por_exception(self, exception: Exception):
        return request(
            'post',
            f'{settings.LINS_HEALTH_CHECKS_PING_URL}{self.uuid}/fail',
            json={'exception': exception.args},
        )


def cria_ou_busca_health_check(json):
    unique_data = json.get('unique', [])
    unique_data.append('name')
    json['unique'] = list(set(unique_data))
    response = request('post', settings.LINS_HEALTH_CHECKS_CHECKS_URL, json=json)
    if response.ok:
        return HealthCheck(uuid=response.json()['ping_url'].split('/')[-1])
    print(f'Não foi possível comunicar com a url {response.url}.')
    return FalhaHeathCheck()
