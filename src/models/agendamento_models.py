from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Numeric, Text  # importar as classes do sqlalchemy
from sqlalchemy.orm import relationship
from src import db


class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    
    # Campos principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    dt_agendamento = Column(DateTime, nullable=False, default=datetime.utcnow)
    dt_atendimento = Column(DateTime, nullable=False)
    
    # Chaves estrangeiras
    id_user = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    id_profissional = Column(Integer, ForeignKey('profissionais.id'), nullable=False)
    id_servico = Column(Integer, ForeignKey('servicos.id'), nullable=False)
    
    # Campos adicionais
    status = Column(String(20), nullable=False, default='agendado')
    observacoes = Column(Text, nullable=True)
    valor_total = Column(Numeric(10, 2), nullable=False, default=0.00)
    taxa_cancelamento = Column(Numeric(10, 2), nullable=True, default=0.00)
    
    # Relacionamentos com outras tabelas
    usuario = relationship("Usuario", backref="agendamentos")  
    profissional = relationship("Profissional", backref="agendamentos")
    servico = relationship("Servico", backref="agendamentos")
    
    # Construtor: inicializa o objeto agendamento
    def __init__(self, dt_atendimento, id_user, id_profissional, id_servico, 
                 observacoes=None, valor_total=0.00):
        self.dt_atendimento = dt_atendimento
        self.id_user = id_user
        self.id_profissional = id_profissional
        self.id_servico = id_servico
        self.observacoes = observacoes
        self.valor_total = valor_total
        self.dt_agendamento = datetime.utcnow()
        self.status = 'agendado'
    
    # Transforma o objeto em dicionário/JSON para facilitar o retorno na API
    def transformar_dicionario(self):
        return {
            'id': self.id,
            'dt_agendamento': self.dt_agendamento.isoformat() if self.dt_agendamento else None,
            'dt_atendimento': self.dt_atendimento.isoformat() if self.dt_atendimento else None,
            'id_user': self.id_user,
            'id_profissional': self.id_profissional,
            'id_servico': self.id_servico,
            'status': self.status,
            'observacoes': self.observacoes,
            'valor_total': float(self.valor_total) if self.valor_total else 0.0,
            'taxa_cancelamento': float(self.taxa_cancelamento) if self.taxa_cancelamento else 0.0
        }
    
    # Salva o agendamento no banco de dados
    def salvar(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao salvar agendamento: {str(e)}")
    
    # Atualiza campos do agendamento no banco
    def atualizar(self, **kwargs):
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao atualizar agendamento: {str(e)}")
    
    # Deleta o agendamento do banco
    def deletar(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao deletar agendamento: {str(e)}")
    
    # Verifica se pode cancelar gratuitamente (com 2h de antecedência)
    def pode_cancelar_gratuito(self):
        agora = datetime.utcnow()
        diferenca = self.dt_atendimento - agora
        return diferenca.total_seconds() >= 7200  # 2 horas = 7200 segundos
    
    # Calcula a taxa de cancelamento conforme antecedência
    def calcular_taxa_cancelamento(self, valor_servico):
        agora = datetime.utcnow()
        diferenca = self.dt_atendimento - agora
        minutos_antecedencia = diferenca.total_seconds() / 60
        
        if minutos_antecedencia >= 120:  # 2 horas ou mais
            return 0.0
        elif minutos_antecedencia >= 90:  # 1h30min
            return valor_servico * 0.40
        elif minutos_antecedencia >= 60:  # 1h
            return valor_servico * 0.45
        elif minutos_antecedencia >= 30:  # 30min
            return valor_servico * 0.50
        else:  # Menos de 30min
            return valor_servico  # 100% do valor
    
    # Métodos estáticos para buscar agendamentos
    @staticmethod
    def find_by_id(agendamento_id):
        return Agendamento.query.filter_by(id=agendamento_id).first()
    
    @staticmethod
    def find_by_user(user_id):
        return Agendamento.query.filter_by(id_user=user_id).all()
    
    @staticmethod
    def find_by_profissional_data(profissional_id, data):
        inicio_dia = datetime.combine(data, datetime.min.time())
        fim_dia = datetime.combine(data, datetime.max.time())
        return Agendamento.query.filter(
            Agendamento.id_profissional == profissional_id,
            Agendamento.dt_atendimento.between(inicio_dia, fim_dia),
            Agendamento.status != 'cancelado'
        ).order_by(Agendamento.dt_atendimento).all()
    
    @staticmethod
    def find_conflitos_horario(profissional_id, dt_inicio, dt_fim):
        return Agendamento.query.filter(
            Agendamento.id_profissional == profissional_id,
            Agendamento.status != 'cancelado',
            Agendamento.dt_atendimento < dt_fim,
            # Assumindo que temos um campo dt_fim ou calculamos baseado na duração
        ).all()