import logging
from operator import attrgetter
from typing import List, Union

from fastapi import HTTPException, status
from starlette.status import HTTP_400_BAD_REQUEST
from edat_utils.api import (
    ApiAcademicoService,
    ApiColegiosTecnicosService,
    ApiFuncionarioService,
)
from edat_utils.api.models import TipoUsuario, Usuario            

logger = logging.getLogger(__name__)


class UsuarioService:
    def __init__(self,
                 funcionario_service: ApiFuncionarioService,
                 academico_service: ApiAcademicoService,
                 colegio_service: ApiColegiosTecnicosService):
        self._funcionario_service = funcionario_service
        self._academico_service = academico_service
        self._colegios_tecnicos = colegio_service

    def get_usuario(self, identificador: int) -> Usuario:
        """ Método para buscar usuario da unicamp pelo identificador/matrícula

            :param identificador: identificador/matricula do usuario
            :return: DataMembro
            :raises: PermissaoException
        """
        query = f'eq: {{ matricula: {identificador}}}'
        membro = self._funcionario_service.get(query=query)
        if not membro or len(membro) == 0:
            query = f'eq: {{ra: {identificador}}}'
            membro = self._academico_service.get(query=query)

        if not membro or len(membro) == 0:
            query = f'eq: {{ra: {identificador}}}'
            membro = self._colegios_tecnicos.get(query=query)

        if not membro or len(membro) == 0:
            message = f'Membro com matricula/ra {identificador} não encontrado no sistema.'
            logger.error(msg=f'{message}')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

        return membro[0]

    def get_usuarios(
        self,
        termo_busca: Union[str, None] = None,
        tipo_usuario: Union[TipoUsuario, None] = None
    ) -> List[Usuario]:
        """ Método para buscar usuários na unicamp

            :param data: objeto do tipo DataBuscarUsuarioUnicamp
            :return: lista de usuários
        """
        candidatos = []
        is_nome = False

        if not termo_busca:
            message = f'É obrigatório informar um termo de busca'
            logger.error(msg=message)
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=message)

        # verificar se é matricula/ra ou nome de usuário
        try:
            int(termo_busca)
        except Exception:
            is_nome = True

        if (not tipo_usuario or
                tipo_usuario == TipoUsuario.FUNCIONARIO or
                tipo_usuario == TipoUsuario.DOCENTE or
                tipo_usuario == TipoUsuario.FUNCAMP):
            # verificar se a busca é por matricula ou nome
            filtro = f'eq: {{situacao: "Ativo", matricula: {termo_busca}}}' \
                if not is_nome \
                else f'termsListTranslate: {{nome: "{termo_busca}"}}, eq: {{situacao: "Ativo"}}'
            candidatos = self._funcionario_service.get(query=filtro) or []

        if not tipo_usuario or tipo_usuario in [TipoUsuario.ALUNO, TipoUsuario.ALUNO_COTIL, TipoUsuario.ALUNO_COTUCA]:

            # verificar se a busca é por ra ou nome
            filtro = f'eq: {{ra: {termo_busca}}}' \
                if not is_nome \
                else f'termsListTranslate: {{nome_civil_aluno: "{termo_busca}"}}, eq: {{periodo_saida: 0}}'
            _candidatos = self._academico_service.get(query=filtro)
            candidatos.extend(_candidatos)

            # buscar alunos de colégios técnicos
            filtro = f'{filtro.replace("nome_civil_aluno", "nome_aluno")}, notNull: {{ nome_aluno: null}}'
            filtro = f'termsListTranslate: {{nome_aluno: "{termo_busca}"}}, eq: {{situacao: "Ativo"}}'
            _candidatos_tecnicos = self._colegios_tecnicos.get(query=filtro)
            candidatos.extend(_candidatos_tecnicos)

        return sorted(candidatos, key=attrgetter('nome'))
