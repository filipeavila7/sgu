from src import db


class Login_model(db.Model):
    __tablename__ = "tb_login"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=True)
    senha =  db.Column(db.String(120), nullable=True)