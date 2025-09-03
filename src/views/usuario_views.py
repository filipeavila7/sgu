from flask_restful import Resource
from marshmallow import ValidationError
from src.schemas import usuario_schemas
from flask import request, jsonify, make_response
from src.services import usuario_services
from src import api
from src.models.usuario_models import Usuario

# post, get, put, delete
# lidar co todos os usuários
class UsuarioList(Resource):
    # Método GET: lista todos os usuários cadastrados
    def get(self):
        usuarios = usuario_services.listar_usuario()  # Busca usuários no banco

        if not usuarios:
            # Retorna mensagem se não houver usuários cadastrados
            return make_response(jsonify({"mensage": "Não existe usuários"}))
        
        schema = usuario_schemas.UsuarioSchema(many=True)  # Instancia o schema para serializar vários usuários
        # Retorna a lista de usuários serializada em formato JSON
        return make_response(jsonify(schema.dump(usuarios)), 200)
    
    # Método POST: será implementado para cadastrar novo usuário
    def post(self):
        schema = usuario_schemas.UsuarioSchema()  # Instancia o schema para validar os dados recebidos

        try:
            # Tenta carregar e validar os dados enviados na requisição
            dados = schema.load(request.json)
        except ValidationError as err:
            # Se houver erro de validação, retorna mensagem de erro e status 400
            return make_response(jsonify(err.messages), 400)
        
        # Verifica se já existe um usuário com o mesmo email
        if usuario_services.listar_usuario_email(dados['email']):
            return make_response(jsonify({'message': 'email ja cadastrado'}), 400)
        
        try:
            # Cria um novo objeto Usuario com os dados validados
            novo_usuario = Usuario(
                nome=dados['nome'],
                email=dados['email'],
                senha=dados['senha'],
                telefone=dados['telefone'],
            )

            # Chama o serviço para cadastrar o usuário no banco
            resultado = usuario_services.cadastrar_usuario(novo_usuario)
            # Retorna o usuário cadastrado (serializado) e status 201 (criado)
            return make_response(jsonify(schema.dump(resultado)), 201)
        
        except Exception as e:
            # Se ocorrer algum erro, retorna mensagem de erro e status 400
            return make_response(jsonify({'message': str(e)}), 400)

            


api.add_resource(UsuarioList, '/usuario')