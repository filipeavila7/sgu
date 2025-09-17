from flask_restful import Resource
from marshmallow import ValidationError
from src.schemas import usuario_schemas
from flask import request, jsonify, make_response
from src.services import usuario_services
from src import api
from src.models.usuario_models import Usuario_model
from src.entities import usuario_entitie

# post, get, put, delete
# lidar com todos os usuários
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
            novo_usuario = usuario_entitie.Usuario (
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


class UsuarioResource(Resource):
    # Método GET: busca um usuário pelo id
    def get(self, id_usuario):
        usuario_encontrado = usuario_services.listar_usuario_id(id_usuario)  # Busca usuário pelo id
        if not usuario_encontrado:
            # Retorna mensagem se não encontrar o usuário
            return make_response(jsonify({'message': 'usuario não encontrado'}), 400)
        
        schema = usuario_schemas.UsuarioSchema()  # Instancia o schema para serializar o usuário
        # Retorna o usuário serializado em formato JSON
        return make_response(jsonify(schema.dump(usuario_encontrado)), 200)
    
    # Método PUT: será implementado para editar usuário
    def put(self, id_usuario):
        ...

    # Método DELETE: exclui um usuário pelo id
    def delete(self, id_usuario):
        usuario_encontrado = usuario_services.listar_usuario_id(id_usuario)  # Busca usuário pelo id
        if not usuario_encontrado:
            # Retorna mensagem se não encontrar o usuário
            return make_response(jsonify({'message': 'usuario não encontrado'}), 400)
        try:
            usuario_services.excluir_usuario(id_usuario)  # Exclui o usuário do banco
            # Retorna mensagem de sucesso
            return make_response(jsonify({'message': 'usuario excluído com sucesso'}), 200)
        except Exception as e:
            # Retorna mensagem de erro e status 400 em caso de exceção
            return make_response(jsonify({'message': f'Erro ao excluir usuário: {str(e)}'}), 400)


api.add_resource(UsuarioResource, "/usuario/<int:id_usuario>")