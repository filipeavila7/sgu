from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_restful import Api

# Instanciar e criar objetos principais do Flask
app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
api = Api(app)
CORS(app)


# Criar as tabelas do banco de dados ao acessar o endpoint 'index'
@app.before_request
def create_tables():
    if request.endpoint == 'index': # Executa apenas na primeira requisição ao endpoint 'index'
        db.create_all()

from .models import agendamento_models, login_models, profissional_models, servico_models, usuario_models # Importa os modelos para garantir que o SQLAlchemy reconheça as tabelas

