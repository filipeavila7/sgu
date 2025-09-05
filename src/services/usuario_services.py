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

def listar_usuario_id(id):
    try:
        #buscar usuario
        usuario_encontrado = usuario_models.Usuario.query.get(id)
        return usuario_encontrado
    except Exception as e:
        print(f"erro ao listar usuário por id {e}")
        return None

def excluir_usuario(id):
    # Busca o usuário pelo id
    usuario = usuario_models.Usuario.query.get(id)
    if usuario:
        # Se encontrar, exclui o usuário do banco
        db.session.delete(usuario)
        db.session.commit()
        return True  # Retorna True se excluiu com sucesso
    else:
        return False  # Retorna False se não encontrou o usuário

def editar_usuario(id, novo_usuario):
    # Busca o usuário pelo id
    usuario = usuario_models.Usuario.query.get(id)
    if usuario:
        # Atualiza os dados do usuário
        usuario.nome = novo_usuario.nome
        usuario.email = novo_usuario.email
        usuario.telefone = novo_usuario.telefone

        # Se foi informada uma nova senha, atualiza e criptografa
        if novo_usuario.senha:
            usuario.gen_senha(novo_usuario.senha)
        
        db.session.commit()  # Salva as alterações no banco
        return usuario  # Retorna o usuário atualizado
    



def listar_usuario_email(email):
    return usuario_models.Usuario.query.filter_by(email = email).first()