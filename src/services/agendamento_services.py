"""
Service para gerenciamento de agendamentos
Contém toda a lógica de negócio relacionada aos agendamentos
"""

from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Tuple
from src.models.agendamento_models import Agendamento  # Importa o modelo de agendamento
from src.models.servico_models import Servico          # Importa o modelo de serviço
from src.models.profissional_models import Profissional # Importa o modelo de profissional
from src.models.usuario_models import Usuario           # Importa o modelo de usuário


class AgendamentoService:
    """
    Service responsável pela lógica de negócio dos agendamentos
    """
    
    # Configurações de horário de funcionamento do estabelecimento
    HORA_ABERTURA = 9  # Horário de abertura (9h)
    HORA_FECHAMENTO = 20  # Horário de fechamento (20h)
    HORA_ALMOCO_INICIO = 12  # Início do horário de almoço (12h)
    HORA_ALMOCO_FIM = 13  # Fim do horário de almoço (13h)
    
    # Durações dos serviços em minutos
    DURACAO_SERVICOS = {
        'alisamento': 30,
        'corte tesoura': 60,
        'corte maquina': 60,
        'barba': 30,
        'sobrancelha': 10,
        'pintura': 120
    }
    
    @staticmethod
    def criar_agendamento(dt_atendimento: datetime, id_user: int, 
                         id_profissional: int, servicos_ids: List[int],
                         observacoes: str = None) -> Dict:
        """
        Cria um ou mais agendamentos para um usuário e profissional, considerando os serviços escolhidos.
        Realiza validações de dados, horário, disponibilidade e salva os agendamentos no banco.
        Retorna os agendamentos criados ou mensagem de erro.
        """
        try:
            # Validações básicas dos dados recebidos
            if not AgendamentoService._validar_dados_basicos(
                dt_atendimento, id_user, id_profissional, servicos_ids):
                return {"erro": "Dados inválidos fornecidos"}
            
            # Verifica se a data de atendimento não é no passado
            if dt_atendimento <= datetime.utcnow():
                return {"erro": "Não é possível agendar para datas passadas"}
            
            # Verifica se está dentro do horário de funcionamento
            if not AgendamentoService._verificar_horario_funcionamento(dt_atendimento):
                return {"erro": "Horário fora do funcionamento do estabelecimento"}
            
            # Busca os serviços e calcula duração e valor total
            servicos = []
            duracao_total = 0
            valor_total = 0
            
            for servico_id in servicos_ids:
                servico = Servico.find_by_id(servico_id)  # Busca serviço pelo id
                if not servico:
                    return {"erro": f"Serviço com ID {servico_id} não encontrado"}
                
                servicos.append(servico)
                duracao_total += AgendamentoService.DURACAO_SERVICOS.get(
                    servico.nome.lower(), 60)  # Se não encontrar, assume 60min
                valor_total += float(servico.preco)
            
            # Verifica se o profissional está disponível no horário
            dt_fim = dt_atendimento + timedelta(minutes=duracao_total)
            if not AgendamentoService._verificar_disponibilidade(
                id_profissional, dt_atendimento, dt_fim):
                return {"erro": "Horário não disponível para o profissional"}
            
            # Cria os agendamentos (um para cada serviço)
            agendamentos_criados = []
            dt_atual = dt_atendimento
            
            for i, servico in enumerate(servicos):
                duracao_servico = AgendamentoService.DURACAO_SERVICOS.get(
                    servico.nome.lower(), 60)
                
                agendamento = Agendamento(
                    dt_atendimento=dt_atual,
                    id_user=id_user,
                    id_profissional=id_profissional,
                    id_servico=servico.id,
                    observacoes=observacoes if i == 0 else None,  # Observação só no primeiro
                    valor_total=float(servico.preco)
                )
                
                agendamento.save()  # Salva no banco
                agendamentos_criados.append(agendamento)
                
                # Atualiza o horário para o próximo serviço
                dt_atual += timedelta(minutes=duracao_servico)
            
            # Retorna os agendamentos criados, valor e duração total
            return {
                "sucesso": True,
                "agendamentos": [ag.to_dict() for ag in agendamentos_criados],
                "valor_total": valor_total,
                "duracao_total": duracao_total
            }
            
        except Exception as e:
            # Retorna erro interno se ocorrer exceção
            return {"erro": f"Erro interno: {str(e)}"}
    
    @staticmethod
    def cancelar_agendamento(agendamento_id: int, user_id: int) -> Dict:
        """
        Cancela um agendamento, calculando taxa de cancelamento se necessário.
        Só permite cancelar se o agendamento pertencer ao usuário e não estiver finalizado/cancelado.
        """
        try:
            agendamento = Agendamento.find_by_id(agendamento_id)  # Busca agendamento pelo id
            
            if not agendamento:
                return {"erro": "Agendamento não encontrado"}
            
            if agendamento.id_user != user_id:
                return {"erro": "Acesso negado: agendamento não pertence ao usuário"}
            
            if agendamento.status == 'cancelado':
                return {"erro": "Agendamento já foi cancelado"}
            
            if agendamento.status == 'finalizado':
                return {"erro": "Não é possível cancelar um agendamento finalizado"}
            
            # Calcula taxa de cancelamento se não for gratuito
            servico = Servico.find_by_id(agendamento.id_servico)
            taxa = 0.0
            
            if not agendamento.pode_cancelar_gratuito():
                taxa = agendamento.calcular_taxa_cancelamento(float(servico.preco))
            
            # Atualiza status e taxa no agendamento
            agendamento.update(
                status='cancelado',
                taxa_cancelamento=taxa
            )
            
            # Retorna dados do cancelamento
            return {
                "sucesso": True,
                "agendamento": agendamento.to_dict(),
                "taxa_cancelamento": taxa,
                "cancelamento_gratuito": taxa == 0
            }
            
        except Exception as e:
            # Retorna erro interno se ocorrer exceção
            return {"erro": f"Erro interno: {str(e)}"}
    
    @staticmethod
    def listar_horarios_disponiveis(profissional_id: int, data: datetime.date) -> Dict:
        """
        Lista todos os horários disponíveis para um profissional em um dia.
        Considera horários ocupados, funcionamento e horário de almoço.
        """
        try:
            # Verifica se o profissional existe
            if not Profissional.find_by_id(profissional_id):
                return {"erro": "Profissional não encontrado"}
            
            # Busca agendamentos do profissional no dia
            agendamentos = Agendamento.find_by_profissional_data(profissional_id, data)
            
            # Gera slots de horário (intervalos de 30 min)
            horarios_disponiveis = []
            horarios_ocupados = set()
            
            # Marca horários ocupados
            for agendamento in agendamentos:
                servico = Servico.find_by_id(agendamento.id_servico)
                duracao = AgendamentoService.DURACAO_SERVICOS.get(
                    servico.nome.lower(), 60)
                
                inicio = agendamento.dt_atendimento
                fim = inicio + timedelta(minutes=duracao)
                
                # Marca todos os slots ocupados
                slot_atual = inicio
                while slot_atual < fim:
                    horarios_ocupados.add(slot_atual.strftime("%H:%M"))
                    slot_atual += timedelta(minutes=30)
            
            # Gera horários disponíveis, pulando horário de almoço
            data_completa = datetime.combine(data, time(AgendamentoService.HORA_ABERTURA))
            
            while data_completa.hour < AgendamentoService.HORA_FECHAMENTO:
                # Pula horário de almoço
                if (data_completa.hour >= AgendamentoService.HORA_ALMOCO_INICIO and 
                    data_completa.hour < AgendamentoService.HORA_ALMOCO_FIM):
                    data_completa += timedelta(minutes=30)
                    continue
                
                horario_str = data_completa.strftime("%H:%M")
                
                # Adiciona horário se não estiver ocupado
                if horario_str not in horarios_ocupados:
                    horarios_disponiveis.append({
                        "horario": horario_str,
                        "timestamp": data_completa.isoformat()
                    })
                
                data_completa += timedelta(minutes=30)
            
            # Retorna lista de horários disponíveis
            return {
                "sucesso": True,
                "data": data.isoformat(),
                "horarios_disponiveis": horarios_disponiveis
            }
            
        except Exception as e:
            # Retorna erro interno se ocorrer exceção
            return {"erro": f"Erro interno: {str(e)}"}
    
    @staticmethod
    def listar_agendamentos_usuario(user_id: int, 
                                   status: str = None,
                                   data_inicio: datetime = None,
                                   data_fim: datetime = None) -> Dict:
        """
        Lista agendamentos de um usuário, podendo filtrar por status e datas.
        Enriquecer dados com informações do serviço e profissional.
        """
        try:
            agendamentos = Agendamento.find_by_user(user_id)  # Busca agendamentos do usuário
            
            # Aplica filtros de status e datas
            if status:
                agendamentos = [ag for ag in agendamentos if ag.status == status]
            
            if data_inicio:
                agendamentos = [ag for ag in agendamentos 
                               if ag.dt_atendimento >= data_inicio]
            
            if data_fim:
                agendamentos = [ag for ag in agendamentos 
                               if ag.dt_atendimento <= data_fim]
            
            # Adiciona dados detalhados de serviço e profissional
            agendamentos_detalhados = []
            for agendamento in agendamentos:
                ag_dict = agendamento.to_dict()
                
                # Dados do serviço
                servico = Servico.find_by_id(agendamento.id_servico)
                ag_dict['servico'] = {
                    'nome': servico.nome,
                    'preco': float(servico.preco),
                    'duracao': AgendamentoService.DURACAO_SERVICOS.get(
                        servico.nome.lower(), 60)
                }
                
                # Dados do profissional
                profissional = Profissional.find_by_id(agendamento.id_profissional)
                ag_dict['profissional'] = {
                    'nome': profissional.nome,
                    'especialidade': profissional.especialidade
                }
                
                agendamentos_detalhados.append(ag_dict)
            
            # Retorna lista de agendamentos detalhados
            return {
                "sucesso": True,
                "agendamentos": agendamentos_detalhados
            }
            
        except Exception as e:
            # Retorna erro interno se ocorrer exceção
            return {"erro": f"Erro interno: {str(e)}"}
    
    @staticmethod
    def _validar_dados_basicos(dt_atendimento: datetime, id_user: int,
                              id_profissional: int, servicos_ids: List[int]) -> bool:
        """
        Valida os dados básicos para criação de agendamento.
        Verifica tipos e valores mínimos.
        """
        if not isinstance(dt_atendimento, datetime):
            return False
        
        if not isinstance(id_user, int) or id_user <= 0:
            return False
        
        if not isinstance(id_profissional, int) or id_profissional <= 0:
            return False
        
        if not servicos_ids or not isinstance(servicos_ids, list):
            return False
        
        return True
    
    @staticmethod
    def _verificar_horario_funcionamento(dt_atendimento: datetime) -> bool:
        """
        Verifica se o horário está dentro do funcionamento do estabelecimento e não é horário de almoço.
        """
        hora = dt_atendimento.hour
        
        # Fora do horário de funcionamento
        if hora < AgendamentoService.HORA_ABERTURA or hora >= AgendamentoService.HORA_FECHAMENTO:
            return False
        
        # Horário de almoço
        if (hora >= AgendamentoService.HORA_ALMOCO_INICIO and 
            hora < AgendamentoService.HORA_ALMOCO_FIM):
            return False
        
        return True
    
    @staticmethod
    def _verificar_disponibilidade(profissional_id: int, dt_inicio: datetime,
                                  dt_fim: datetime) -> bool:
        """
        Verifica se o profissional está disponível entre dt_inicio e dt_fim.
        Não permite sobreposição de horários.
        """
        agendamentos_conflito = Agendamento.query.filter(
            Agendamento.id_profissional == profissional_id,
            Agendamento.status != 'cancelado',
            Agendamento.dt_atendimento < dt_fim
        ).all()
        
        for agendamento in agendamentos_conflito:
            # Calcula fim do agendamento existente
            servico = Servico.find_by_id(agendamento.id_servico)
            duracao = AgendamentoService.DURACAO_SERVICOS.get(
                servico.nome.lower(), 60)
            ag_fim = agendamento.dt_atendimento + timedelta(minutes=duracao)
            
            # Verifica sobreposição de horários
            if not (dt_fim <= agendamento.dt_atendimento or dt_inicio >= ag_fim):
                return False
        
        return True