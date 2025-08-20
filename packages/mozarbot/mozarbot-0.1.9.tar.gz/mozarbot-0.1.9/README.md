# RPA Client

## Instalação

```bash
pip install mozarbot
```

## Como usar?

```python
from mozarbot.sdk import rpa

rpa.info(task_id, message)
```

## Documentação

### Para gerar alertas

```python
rpa.info(task_id, message)
rpa.error(task_id, message)
rpa.warning(task_id, message)
```

### Para retornar informações da execução atual

```python
rpa.get_execution_data()
```
O retorno é um JSON com as informações da execução atual, com os seguintes campos:

```json
{
  task: {
    id: string # ID da execução
    robotId: string # ID do robô
    runnerId: string # ID do runner
    automationId: string # ID da automação
  } | null
}
```

### Para retornar informações dos parametros da execução atual

```python
rpa.get_params(automation_id)
```
O retorno é um JSON com os parametros da execução atual, com os seguintes campos:

```json
{
  parameters: [
    {
      id: string # ID do parametro
      type: string # Tipo do parametro
      label: string # Label do parametro
      required: boolean # Se o parametro é obrigatório
      defaultValue: string # Valor default do parametro
    }
  ]
}
```

### Para retornar os secrets do automação

```python
# label é opcional
rpa.get_secrets(label)
```
O retorno é um JSON com os secrets da automação, com os seguintes campos:

```json
{
  secrets: [
    {
      id: string
      label: string
      value: string
    }
  ]
}
```

### Para reportar o tempo de execução da task

```python
rpa.report_saving(task_id, automation_id, time_spent)
```