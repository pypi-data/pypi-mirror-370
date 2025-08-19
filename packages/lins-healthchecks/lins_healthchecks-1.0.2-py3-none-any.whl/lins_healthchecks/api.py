from functools import wraps
from urllib.parse import urlencode

from . import settings
from .utils import cria_ou_busca_health_check, request

# Management API
# https://healthchecks.io/docs/api/


def listar(json={}):
    query_params = urlencode(json, True)
    return request('get', f'{settings.LINS_HEALTH_CHECKS_CHECKS_URL}?{query_params}')


def buscar(uuid):
    return request('get', f'{settings.LINS_HEALTH_CHECKS_CHECKS_URL}{uuid}')


def criar(json):
    return request('post', settings.LINS_HEALTH_CHECKS_CHECKS_URL, json=json)


def atualizar(uuid, json):
    return request('post', f'{settings.LINS_HEALTH_CHECKS_CHECKS_URL}{uuid}', json=json)


def pausar_monitoramento(uuid):
    return request('post', f'{settings.LINS_HEALTH_CHECKS_CHECKS_URL}{uuid}/pause')


def deletar(uuid):
    return request('delete', f'{settings.LINS_HEALTH_CHECKS_CHECKS_URL}{uuid}')


def deletar_lote(lista_de_uuids):
    for uuid in lista_de_uuids:
        deletar(uuid)


def listar_pings(uuid):
    return request('get', f'{settings.LINS_HEALTH_CHECKS_CHECKS_URL}{uuid}/pings/')


def listar_mudancas_de_status(uuid):
    return request('get', f'{settings.LINS_HEALTH_CHECKS_CHECKS_URL}{uuid}/flips/')


def listar_integracoes():
    return request('get', settings.LINS_HEALTH_CHECKS_CHANNELS_URL)


def listar_badges():
    return request('get', settings.LINS_HEALTH_CHECKS_BADGES_URL)


# Pinging API
# https://healthchecks.io/docs/http_api/


def reportar_inicio(ping_url):
    return request('get', f'{ping_url}/start')


def reportar_sucesso(ping_url):
    return request('get', f'{ping_url}')


def reportar_falha(ping_url):
    return request('get', f'{ping_url}/fail')


def link(json):

    def decorator(function):

        @wraps(function)
        def wrapper(json=json, *args, **kwargs):
            kwargs['health_check'] = cria_ou_busca_health_check(json)
            return function(*args, **kwargs)

        return wrapper

    return decorator
