from src import db

class Servico(db.Model):
    __tablename__ = "tb_servico"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(120), nullable=False)
    valor = db.Column(db.float, nullable=False)

    def ___init__(self, descricao, valor):
        self.descricao = descricao
        self.valor = valor