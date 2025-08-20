import os
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class TaskStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"

class RPAClientError(Exception):
    """Exceção customizada para erros do cliente RPA"""
    pass

class RPAClient:
    """Cliente para interação com a API RPA"""
    
    def __init__(self):
        self.company_id = os.getenv('COMPANY_ID')
        self.runner_id = os.getenv('RUNNER_ID')
        
        if not self.company_id:
            raise RPAClientError("Variável de ambiente COMPANY_ID não definida")
        if not self.runner_id:
            raise RPAClientError("Variável de ambiente RUNNER_ID não definida")
            
        self.base_url = "http://api-mozarbot.172.16.0.77.sslip.io"
        self.session = requests.Session()
    
    def info(self, task_id: str, message: str) -> Dict[str, Any]:
        """
        Gera logs para uma task

        Args:
            task_id: ID da task
            message: Mensagem do log
        """
        now = datetime.now()
        url = f"{self.base_url}/logs"
        payload = {
            "type": "info",
            "taskId": task_id,
            "message": message,
            "generatedAt": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        # print(payload)
        response = self.session.post(url, json=payload)
        return response.raise_for_status()

    def warning(self, task_id: str, message: str) -> Dict[str, Any]:
        """
        Gera logs para uma task

        Args:
            task_id: ID da task
            message: Mensagem do log
        """
        now = datetime.now()
        url = f"{self.base_url}/logs"
        payload = {
            "type": "warning",
            "taskId": task_id,
            "message": message,
            "generatedAt": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        response = self.session.post(url, json=payload)
        return response.raise_for_status()

    def error(self, task_id: str, message: str) -> Dict[str, Any]:
        """
        Gera logs para uma task

        Args:
            task_id: ID da task
            message: Mensagem do log
        """
        now = datetime.now()
        url = f"{self.base_url}/logs"
        payload = {
            "type": "error",
            "taskId": task_id,
            "message": message,
            "generatedAt": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        response = self.session.post(url, json=payload)
        return response.raise_for_status()
    
    def get_execution_data(self) -> Dict[str, Any]:
        """Retorna informações da execução atual"""
        url = f"{self.base_url}/tasks/running/{self.runner_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_params(self, automation_id: str) -> Dict[str, Any]:
        """Retorna os parâmetros da execução atual"""
        url = f"{self.base_url}/parameters/{automation_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_secrets(self, label: Optional[str] = None) -> Dict[str, Any]:
        """
        Retorna os secrets do automação

        Args:
            label: Label opcional para filtrar os secrets
        """
        url = f"{self.base_url}/my-secrets/{self.company_id}"
        params = {"label": label} if label else None
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def report_saving(self, task_id: str, automation_id: str, time_spent: int) -> Dict[str, Any]:
        """
        Reporta o tempo de execução da task

        Args:
            task_id: ID da task
            automation_id: ID da automação
            time_spent: Tempo de execução em segundos
        """
        url = f"{self.base_url}/automations/saving"
        payload = {"taskId": task_id, "automationId": automation_id, "secondsSpent": time_spent}
        response = self.session.post(url, json=payload)
        return response.raise_for_status()

# Criar uma instância global do cliente
rpa = RPAClient()
