from dataclasses import dataclass


@dataclass
class Organization:
    organization_id: str
    name: str
    email: str
    cpf_cnpj: str
    is_active: bool = True
