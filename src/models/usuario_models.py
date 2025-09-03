from src import db  # Importa a instância do banco de dados (SQLAlchemy)
from passlib.hash import pbkdf2_sha256 as sha256  # Biblioteca para hash seguro de senhas

# Modelo de usuário para o banco de dados
class Usuario(db.Model):
    __tablename__ = "tb_usuario"  # Nome da tabela no banco

    # Campos da tabela
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Identificador único
    nome = db.Column(db.String(120), nullable=False)                  # Nome do usuário
    email = db.Column(db.String(120), nullable=False, unique=True)    # Email único
    senha = db.Column(db.String(255), nullable=False)                 # Senha (armazenada como hash)
    telefone = db.Column(db.String(120), nullable=False)              # Telefone do usuário

    #construtor da classe
    def __init__(self, nome, email, telefone, senha):
        self.nome = nome #esat vindo da view
        self.nome = email
        self.telefone = telefone
        self.senha = senha

    # Gera o hash da senha e armazena no campo 'senha'
    def gen_senha(self, senha):
        self.senha = sha256.hash(senha)

    # Verifica se a senha informada corresponde ao hash armazenado
    def verificar_senha(self, senha):
        return sha256.verify(senha, self.senha)