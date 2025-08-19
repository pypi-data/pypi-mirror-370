from datetime import datetime, date, timedelta
import re
from pydantic import BaseModel, Field, field_validator

from libretificacaotjcore.enums.e_eventos import EEventos


class SolicitacaoDTO(BaseModel):
    solicitacaoId: int = Field(..., description="ID da solicitação")
    cnpj: str = Field(..., description="CNPJ da empresa")
    dataInicio: date = Field(..., description="Data de início no formato YYYY-MM-DD")
    dataFim: date = Field(..., description="Data de fim no formato YYYY-MM-DD")
    certificadoId: int = Field(..., description="ID do certificado")
    
    # Validar e transformar solicitacaoId
    @field_validator('solicitacaoId')
    @classmethod
    def validar_solicitacao_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("O solicitacaoId deve ser um inteiro positivo.")
        return v

    # Validar e transformar certificadoId
    @field_validator('certificadoId')
    @classmethod
    def validar_certificado_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("O certificadoId deve ser um inteiro positivo.")
        return v

    # Validar CNPJ (apenas estrutura com 14 dígitos)
    @field_validator('cnpj')
    @classmethod
    def validar_cnpj(cls, v: str) -> str:
        cnpj_limpo = re.sub(r'\D', '', v)
        if len(cnpj_limpo) != 14 or not cnpj_limpo.isdigit():
            raise ValueError("O CNPJ deve conter 14 dígitos numéricos.")
        return cnpj_limpo

    # Validar e transformar dataInicio
    @field_validator('dataInicio', mode='before')
    @classmethod
    def formatar_data_inicio(cls, value: str) -> date:
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("A dataInicio deve estar no formato YYYY-MM-DD.")

    # Validar e transformar dataFim (último dia do mês)
    @field_validator('dataFim', mode='before')
    @classmethod
    def ajustar_data_fim(cls, value: str) -> date:
        try:
            ano, mes = map(int, value.split("-")[:2])
            if mes < 1 or mes > 12:
                raise ValueError
            if mes == 12:
                proximo_mes = datetime(ano + 1, 1, 1)
            else:
                proximo_mes = datetime(ano, mes + 1, 1)
            return (proximo_mes - timedelta(days=1)).date()
        except Exception:
            raise ValueError("A dataFim deve estar no formato YYYY-MM-DD e conter um mês válido.")
