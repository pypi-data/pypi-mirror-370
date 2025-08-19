# HealthCheck
Healthchecks é um serviço usado para monitorar tarefas agendadas, como cronjobs.

O serviço a ser monitorado envia uma solicitação HTTP ou e-mail (pings) para o Healthchecks sempre que for executada. Normalmente, você envia um "ping" no início da execução, outro quando ela termina com sucesso, e se for o caso, um em caso de falha.

Se o Healthchecks não receber o ping dentro do tempo esperado, ele entende que algo deu errado e envia um alerta.

É uma forma prática de saber se os scripts e automações estão rodando como deveriam — e de ser avisado quando não estiverem.
# Lins Health Checks
![pyver](https://img.shields.io/badge/python-3.6%2B-blue)
[![codecov](https://codecov.io/bb/grupolinsferrao/pypck-lins-health-check/branch/master/graph/badge.svg?token=37SJO6KB8C)](https://codecov.io/bb/grupolinsferrao/pypck-lins-health-check)

Esse pacote tem como propósito, linkar os serviços da lins-ferrão ao sistema de checagem (healthchecks).

### Requirements:

* Python 3.6+

## Implementação
### 1 - Adicione o pacote lins-healthchecks aos requirements do projeto
```text
lins-healthchecks==1.0.1
```
### 2 - Adicione as variáveis de ambiente
#### Variáveis do Health Check:

| Variáveis                  | Descrição                                                           |
| -------------------------- | ------------------------------------------------------------------- |
| HEALTH_CHECKS_DESC         | Define a descrição do serviço a ser acompanhado                     |
| HEALTH_CHECKS_GRACE        | Define período em segundos entre o ping inicial e o envio do alerta |
| HEALTH_CHECKS_NAME         | Nome do serviço a ser acompanhado                                   |
| HEALTH_CHECKS_RETRYS       | Numero de tentativas de enviar os pings                             |
| HEALTH_CHECKS_SCHEDULE     | Define o cronograma de execução do serviço                          |
| HEALTH_CHECKS_TAG          | Tags que vão servir para ajudar a encontrar os logs no healthcheck  |
| HEALTH_CHECKS_TZ           | Define a timezone exibida nos logs                                  |
| HEALTH_CHECKS_API_KEY      | Chave necessária para autorizar o acesso aos endpoints              |
| LINS_HEALTH_CHECK_BASE_URL | Define a url base para consumo do pacote                            |
| SHOW_HEALTH_CHECKS_LOGS    | Ativa ou desativa a exibição de logs do pacote                      |
|                            |                                                                     |
### 3 - Adicione as variáveis de ambiente ao arquivo de settings conforme abaixo
```python
ENV = os.environ

HEALTH_CHECKS_DESC = ENV.get('HEALTH_CHECKS_DESC')
HEALTH_CHECKS_GRACE = int(ENV.get('HEALTH_CHECKS_GRACE'))
HEALTH_CHECK_NAME = ENV.get('HEALTH_CHECK_NAME')
HEALTH_CHECKS_RETRYS = ENV.get('HEALTH_CHECKS_RETRYS')
HEALTH_CHECKS_SCHEDULE = ENV.get('HEALTH_CHECKS_SCHEDULE')
HEALTH_CHECK_TAG = ENV.get('HEALTH_CHECK_TAG')
HEALTH_CHECKS_TZ = ENV.get('HEALTH_CHECKS_TZ')
HEALTH_CHECKS_API_KEY = ENV.get('HEALTH_CHECKS_API_KEY')
LINS_HEALTH_CHECK_BASE_URL = ENV.get('LINS_HEALTH_CHECK_BASE_URL')
SHOW_HEALTH_CHECKS_LOGS = ENV.get('SHOW_HEALTH_CHECKS_LOGS')

HEALTH_CHECK_DADOS = {
    'desc': HEALTH_CHECKS_DESC,
    'grace': HEALTH_CHECKS_GRACE,
    'name': HEALTH_CHECK_NAME,
    'schedule': HEALTH_CHECKS_SCHEDULE,
    'tags': HEALTH_CHECK_TAG,
    'tz': HEALTH_CHECKS_TZ,
    'unique': ['name',]
}
```
### 4 - Crie o arquivo health_check.py na raiz do projeto com o seguinte codigo:
```python
from datetime import datetime
from {{arquivo de settings}} import HEALTH_CHECK_DADOS
from lins_healthchecks.utils import cria_ou_busca_health_check


class FalhaHealthCheck():
    def reportar_inicio(self):
        print('### inicio - {} ###'.format(datetime.now()))

    def reportar_falha(self, erro):
        print('### Falha - {} >>> {} ###'.format(datetime.now(), erro))

    def reportar_sucesso(self):
        print('### sucesso - {} ###'.format(datetime.now()))

    def reportar_falha_por_exception(self, erro: Exception):
        print('### Exception - {} >>> {} ###'.format(datetime.now(), str(erro)))


def configura_health_check():
    try:
        health_check = cria_ou_busca_health_check(HEALTH_CHECK_DADOS)
    except Exception:
        health_check = FalhaHealthCheck()
    return health_check

```
### 5 - Ajuste na implementação do serviço:
```python
from health_check import configura_health_check

[...]

if __name__ == "__main__":
    health_check = configura_health_check()
    health_check.reportar_inicio()
    try:
        run() #Chame aqui a função que executa o serviço (por exemplo: run(), execute(), handler(), etc...)
    except Exception as erro:
        health_check.reportar_falha(str(erro))
    else:
        health_check.reportar_sucesso()
```
