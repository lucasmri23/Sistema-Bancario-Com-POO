from abc import ABC, abstractmethod
from datetime import datetime
import textwrap

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__ (self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "1001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    
    def sacar(self, valor):
        saldo = self._saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente para realizar o saque.@@@")
            pause = input("Pressione Enter para continuar...")
            limpa_tela()

        elif valor > 0:
            self._saldo -= valor
            print("\n|||| Saque realizado com sucesso! ||||")
            pause = input("Pressione Enter para continuar...")
            limpa_tela()
            return True
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            pause = input("Pressione Enter para continuar...")
            limpa_tela()
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n|||| Depósito realizado com sucesso! ||||")
            pause = input("Pressione Enter para continuar...")
            limpa_tela()
            return True
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            pause = input("Pressione Enter para continuar...")
            limpa_tela()
            return False
        
        return True

class Conta_Corrente(Conta):
    def __init__ (self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == "Saque"]
        )

        excedeulimite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeulimite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite da conta. @@@")
        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques diários excedido. @@@")
        
        else:
            return super().sacar(valor)
        return False
    def __str__ (self):
        return f"""
            Agencia:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

class Historico:
    def __init__(self):
        self._transacoes = []
    
    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        )

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    menu = '''
    ========== MENU ==========
    [t] Transação
    [e] Extrato
    [u] Criar usuário
    [c] Criar conta corrente
    [l] Listar contas
    [q] Sair
    ==========================
    '''
    return input(textwrap.dedent(menu))

def limpa_tela():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("@@@ Cliente não possui contas cadastradas! @@@")
        return
    # FIXME: Não permite o cliente escolher a conta
    return cliente.contas[0]

def transacao(clientes):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("@@@ Cliente não encontrado! @@@")
        pause = input("Pressione Enter para continuar...")
        limpa_tela()
        return
    switch = input("\nDigite 'd' para depósito ou 's' para saque: ").lower()
    if switch == 'd':
        valor = float(input("Informe o valor do depósito: R$ "))
        transacao = Deposito(valor)
    elif switch == 's':
        valor = float(input("Informe o valor do saque: R$ "))
        transacao = Saque(valor)
    else:
        print("Opção inválida! Tente novamente.")
        return
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def exibir_extratos(clientes):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("@@@ Cliente não encontrado! @@@")
        pause = input("Pressione Enter para continuar...")
        limpa_tela()
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n========= EXTRATO =========")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\t\t\t data: {transacao['data']} \n\tR$ {transacao['valor']:.2f} "
    print(extrato)
    print (f"\nSaldo atual:\n\t R$ {conta.saldo:.2f}")
    print("\n===========================")
    pause = input("Pressione Enter para continuar...")
    # Limpa a tela após a operação
    limpa_tela()
    return

def criar_cliente(clientes):
    cpf = input("Digite o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("@@@ Cliente já cadastrado com esse número de CPF! @@@")
        pause = input("Pressione Enter para continuar...")
        limpa_tela()
        return

    nome = input("Digite o nome completo: ")
    data_nascimento = input("Digite a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Digite o endereço (logradouro, número - bairro - cidade/UF): ")

    cliente = PessoaFisica(cpf=cpf, nome=nome, data_nascimento=data_nascimento, endereco=endereco)
    clientes.append(cliente)

    print(f"\n|||| Cliente criado com sucesso! ||||\n")
    
    pause = input("Pressione Enter para continuar...")
    limpa_tela()
    return

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Digite o CPF do usuário: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Usuário não encontrado, a conta não foi criada! @@@")
        pause = input("Pressione Enter para continuar...")
        limpa_tela()
        return None

    conta = Conta_Corrente.nova_conta(numero=numero_conta, cliente=cliente)
    contas.append(conta)
    cliente.contas.append(conta)
    print(f"\n|||| Conta criada com sucesso! ||||\n{conta}")

    pause = input("Pressione Enter para continuar...")
    limpa_tela()
    return None

def listar_contas(contas):
    for conta in contas:
        print("=" * 50)
        print(textwrap.dedent(str(conta)))
        pause = input("Pressione Enter para continuar...")
        limpa_tela()

def main():
    clientes = []
    contas= []

    while True:
        switch = menu()

        if switch == 't':
            transacao(clientes)

        elif switch == 'e':
            exibir_extratos(clientes)

        elif switch == 'u':
            criar_cliente(clientes);

        elif switch == 'c':
            numero_conta = len(contas) + 1
            conta = criar_conta(numero_conta, clientes, contas);

        elif switch == 'l':
            listar_contas(contas)

        elif switch == 'q':
            print("Saindo do sistema...")
            break

        else:
            print("Opção inválida! Tente novamente.")

main()