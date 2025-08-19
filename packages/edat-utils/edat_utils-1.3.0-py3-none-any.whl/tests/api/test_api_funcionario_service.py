from typing import List, Union
from edat_utils.api import ApiFuncionarioService
from edat_utils.api.models import TipoUsuario, Usuario


def test_get_funcionarios(get_api_funcionario_service: ApiFuncionarioService):
    query = f'startWith: {{nome: "MaRC"}}'
    funcionarios: Union[List[Usuario], None] = get_api_funcionario_service.get(query=query)

    if not funcionarios:
        assert False

    assert len(funcionarios) > 0

    for funcionario in funcionarios:
        print(funcionario)
        assert funcionario.tipo_usuario in [TipoUsuario.FUNCIONARIO, TipoUsuario.FUNCAMP, TipoUsuario.DOCENTE]
        assert funcionario.email
        assert funcionario.telefone
