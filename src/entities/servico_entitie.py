class Servico:
    def ___init__(self, descricao, valor: float, horario_duracao: float):
        self.__descricao = descricao
        self.__valor = valor
        self.__horario_duracao = horario_duracao


    @property
    def descricao(self):
        return self.__descricao
    
    @descricao.setter
    def descricao(self, descricao):
        self.descricao =  descricao
   

    @property
    def valor(self):
        return self.__valor
    
    @valor.setter
    def descricao(self, valor):
        self.valor =  valor
    
    
    @property
    def horario_duracao(self):
        return self.__horario_duracao
    
    @horario_duracao.setter
    def horario_duracao(self, horario_duracao):
        self.horario_duracao =  horario_duracao
    