from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Numeric, Text, Float  # importar as classes do sqlalchemy
from sqlalchemy.orm import relationship
from src import db


class Agendamento_model(db.Model):
    __tablename__ = 'tb_agendamento'
    
    # Campos principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    dt_agendamento = Column(DateTime, nullable=False, default=datetime.utcnow)
    dt_atendimento = Column(DateTime, nullable=False)
    
    # Chaves estrangeiras
    id_user = Column(Integer, ForeignKey('tb_usuario.id'), nullable=False)
    id_profissional = Column(Integer, ForeignKey('tb_profissional.id'), nullable=False)
    id_servico = Column(Integer, ForeignKey('tb_servico.id'), nullable=False)
    
    # Campos adicionais
    status = Column(String(20), nullable=False, default='agendado')
    valor_total = Column(Float, nullable=False, default=0.00)
    taxa_cancelamento = Column(Float, nullable=True, default=0.00)
    
    # Relacionamentos com outras tabelas
    usuario = relationship("Usuario_model", backref="tb_agendamentos")  
    profissional = relationship("Profissional_model", backref="tb_agendamentos")
    servico = relationship("Servico_model", backref="tb_agendamentos")
    
   
    
    
   
    