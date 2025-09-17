from ..models import usuario_models
from src import db
from ..schemas import usuario_schemas
from ..entities import usuario_entitie 
from ..entities.usuario_entitie import Usuario





def cadastrar_usuario(usuario_entitie):
     # Cria uma instância do modelo Usuario com os dados recebidos do front(usuario)
    usuario_db = usuario_models.Usuario_model(nome=usuario_entitie.nome, email=usuario_entitie.email, telefone=usuario_entitie.telefone, senha=usuario_entitie.senha)
    usuario_db.gen_senha(usuario_entitie.senha) # criptografa a senha
    db.session.add(usuario_db)  # Adiciona o novo usuário à sessão do banco de dados
    db.session.commit()  # Salva (commita) as alterações no banco de dados
    return usuario_db  # Retorna o usuário cadastrado


#listar usuarios
def listar_usuario():
    usuario_db = usuario_models.Usuario_model.query.all()  #faz uma busca e retorna todos os usuários do banco
    usuario_enti = [
        Usuario(u.nome, u.email, u.senha, u.telefone) for u in usuario_db
    ]
    return usuario_enti

def listar_usuario_id(id):
    try:
        #buscar usuario
        usuario_encontrado = usuario_models.Usuario_model.query.get(id)
        if usuario_encontrado:
            return Usuario(usuario_encontrado.nome, usuario_encontrado.email, usuario_encontrado.telefone, usuario_encontrado.senha)
    except Exception as e:
        print(f"erro ao listar usuário por id {e}")
        return None

def excluir_usuario(id):
    # Busca o usuário pelo id
    usuario_db = usuario_models.Usuario_model.query.get(id)
    if usuario_db:
        # Se encontrar, exclui o usuário do banco
        db.session.delete(usuario_db)
        db.session.commit()
        return True  # Retorna True se excluiu com sucesso
    else:
        return False  # Retorna False se não encontrou o usuário

def editar_usuario(id, usuario_entitie):
    # Busca o usuário pelo id
    usuario_db = usuario_models.Usuario_model.query.get(id)
    if usuario_db:
        # Atualiza os dados do usuário
        usuario_db.nome = usuario_entitie.nome
        usuario_db.email = usuario_entitie.email
        usuario_db.telefone = usuario_entitie.telefone

        # Se foi informada uma nova senha, atualiza e criptografa
        if usuario_entitie.senha:
            usuario_db.gen_senha(usuario_entitie.senha)
        
        db.session.commit()  # Salva as alterações no banco
        return Usuario(usuario_db.nome, usuario_db.email, usuario_db.telefone, usuario_db.senha)
    



def listar_usuario_email(email):
    usuario_db = usuario_models.Usuario_model.query.filter_by(email = email).first()

    if usuario_db:
        return Usuario(usuario_db.nome, usuario_db.email, usuario_db.telefone, usuario_db.senha)