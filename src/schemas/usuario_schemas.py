from src import ma  # Importa a instância do Marshmallow
from src.models import usuario_models  # Importa o modelo de usuário
from marshmallow import fields  # Importa tipos de campos para validação


# Schema para serializar e validar dados do usuário
class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = usuario_models.Usuario_model  # Modelo associado ao schema
        fields = ('id', 'nome', 'email', 'senha', 'telefone')  # Campos que serão serializados

    # Campos obrigatórios para validação na criação de usuário, o id não é obrigatório
    nome = fields.String(required=True)
    email = fields.String(required=True)
    telefone = fields.String(required=True)
    senha = fields.String(required=True)
