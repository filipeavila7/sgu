from ..models import usuario_models
from src import db
from ..schemas import usuario_schemas



def cadastrar_usuario(usuario):
     # Cria uma instância do modelo Usuario com os dados recebidos do front(usuario)
    usuario_db = usuario_models.Usuario(nome=usuario.nome, email=usuario.email, telefone=usuario.telefone, senha=usuario.senha)
    usuario_db.gen_senha(usuario.senha) # criptografa a senha
    db.session.add(usuario_db)  # Adiciona o novo usuário à sessão do banco de dados
    db.session.commit()  # Salva (commita) as alterações no banco de dados
    return usuario_db  # Retorna o usuário cadastrado


#listar usuarios
def listar_usuario():
    return usuario_models.Usuario.query.all()  #faz uma busca e retorna todos os usuários do banco

def listar_usuario_id():
    ...

def excluir_usuario():
    ...

def editar_usuario():
    ...

def listar_usuario_email(email):
    return usuario_models.Usuario.query.filter_by(email = email).first()