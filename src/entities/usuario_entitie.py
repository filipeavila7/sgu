class Usuario:   
    def __init__(self, nome, email, telefone, senha):
        self.__nome = nome #esat vindo da view
        self.__email = email
        self.__telefone = telefone
        self.__senha = senha

    # get e set para manipular os atributos encapsulados

    @property
    def nome(self):
        return self.__nome
    
    @nome.setter
    def nome(self, nome):
        self.nome = nome
        
    @property
    def email(self):
        return self.__email
    
    @email.setter
    def email(self, email):
        self.email = email
        
    @property
    def telefone(self):
        return self.__telefone
    
    @telefone.setter
    def telefone(self, telefone):
        self.telefone = telefone
        
    @property
    def senha(self):
        return self.__senha
    
    @senha.setter
    def senha(self, senha):
        self.senha = senha
        