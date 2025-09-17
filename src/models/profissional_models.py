from src import db

class Profissional_model(db.Model):
    __tablename__ = "tb_profissional"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(120), nullable=False)

    