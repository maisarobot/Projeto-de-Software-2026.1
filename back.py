from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from rich.console import Console
from rich.prompt import IntPrompt, Prompt

from script import enviar_email

console = Console()


FORMATO_LIVRO_FISICO_EBOOK = 1
FORMATO_AUDIOBOOK = 2


class BibliotecaIterator:
    """Iterator concreto para percorrer componentes da biblioteca.

    O iterator recebe uma cópia dos itens para evitar que mudanças na coleção
    durante a iteração alterem o fluxo que já está em andamento.
    """

    def __init__(self, itens):
        self._itens = tuple(itens)
        self._indice = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._indice >= len(self._itens):
            raise StopIteration

        item = self._itens[self._indice]
        self._indice += 1
        return item


class ComponenteBiblioteca(ABC):
    """Componente base do Composite da biblioteca.

    Leitura é folha. Categoria e Biblioteca_Pessoal são compostos.
    """

    def adicionar(self, componente):
        raise NotImplementedError("Este componente não pode adicionar itens.")

    def remover(self, componente):
        raise NotImplementedError("Este componente não pode remover itens.")

    def __iter__(self):
        return BibliotecaIterator([])

    @abstractmethod
    def descricao(self):
        pass


class Livro:
    def __init__(self, numero, titulo, autor, sinopse):
        self.numero = numero
        self.titulo = titulo
        self.autor = autor
        self.sinopse = sinopse

    def __str__(self):
        return f"TÍTULO: {self.titulo}, AUTOR/A: {self.autor}"


class Leitura(ComponenteBiblioteca, ABC):
    """Folha do Composite.

    Uma leitura não possui filhos, mas participa da mesma interface dos
    componentes compostos para permitir tratamento uniforme quando necessário.
    """

    def __init__(
        self,
        livro,
        inicio_leitura=None,
        final_leitura=None,
        etiqueta=None,
        nota=None,
        resenha=None,
    ):
        self.etiqueta = etiqueta
        self.nota = nota
        self.inicio_leitura = inicio_leitura
        self.final_leitura = final_leitura
        self.resenha = resenha
        self.livro = livro

    def descricao(self):
        return self.livro.titulo

    def adicionar_etiqueta(self, etiqueta):
        self.etiqueta = etiqueta

    def excluir_etiqueta(self):
        self.etiqueta = None

    def atribuir_nota(self, nota):
        nota = int(nota)

        if nota < 0 or nota > 5:
            raise ValueError("A nota deve estar entre 0 e 5.")

        self.nota = nota

    def remover_nota(self):
        self.nota = None

    def escrever_resenha(self, resenha):
        self.resenha = resenha

    def remover_resenha(self):
        self.resenha = None

    def data_inicio(self, inicio_leitura):
        if not inicio_leitura:
            self.inicio_leitura = None
            return

        try:
            self.inicio_leitura = datetime.strptime(inicio_leitura, "%d/%m/%Y").date()
        except ValueError as erro:
            raise ValueError("Data de início inválida. Use o formato DD/MM/AAAA.") from erro


    def data_final(self, final_leitura):
        if not final_leitura:
            self.final_leitura = None
            return

        try:
            self.final_leitura = datetime.strptime(final_leitura, "%d/%m/%Y").date()
        except ValueError as erro:
            raise ValueError("Data de conclusão inválida. Use o formato DD/MM/AAAA.") from erro

    @abstractmethod
    def progresso_leitura(self):
        pass

    @abstractmethod
    def calcular_porcentagem(self):
        pass

    def __str__(self):
        infos_livro = self.livro.__str__()
        return (
            f"{infos_livro}, ETIQUETA: {self.etiqueta}, NOTA: {self.nota}, "
            f"RESENHA: {self.resenha}, DATA INÍCIO: {self.inicio_leitura}, "
            f"DATA FINAL: {self.final_leitura}"
        )


class LivroFisico_Ebook(Leitura):
    def __init__(self, livro, total_paginas, pagina_atual=0, emprestado_para=None):
        super().__init__(livro)
        self.total_paginas = self._validar_total_paginas(total_paginas)
        self.pagina_atual = 0
        self.atualizar_pagina_atual(pagina_atual)
        self.emprestado_para = emprestado_para

    def _validar_total_paginas(self, total_paginas):
        try:
            total_paginas = int(total_paginas)
        except (TypeError, ValueError) as erro:
            raise ValueError("O total de páginas deve ser um número inteiro.") from erro

        if total_paginas <= 0:
            raise ValueError("O total de páginas deve ser maior que zero.")

        return total_paginas

    def calcular_porcentagem(self):
        return (self.pagina_atual / self.total_paginas) * 100

    def progresso_leitura(self):
        pagina = IntPrompt.ask("[bold]Informe a página atual:[/bold]")
        porcentagem = self.atualizar_pagina_atual(pagina)

        console.print("[bold green]Página atualizada![/bold green]")
        print(f"Progresso atualizado: {self.pagina_atual}/{self.total_paginas} ({porcentagem:.1f}%)")

        if self.pagina_atual >= self.total_paginas:
            console.print("[bold purple]Livro concluído![/bold purple]")

        return porcentagem

    def atualizar_pagina_atual(self, pagina):
        try:
            pagina = int(pagina)
        except (TypeError, ValueError) as erro:
            raise ValueError("A página atual deve ser um número inteiro.") from erro

        if pagina < 0 or pagina > self.total_paginas:
            raise ValueError(f"A página atual deve estar entre 0 e {self.total_paginas}.")

        self.pagina_atual = pagina
        return self.calcular_porcentagem()

    def emprestar(self, pessoa):
        self.emprestado_para = pessoa

    def devolvido(self):
        self.emprestado_para = None

    def __str__(self):
        infos_mae = super().__str__()
        return (
            f"{infos_mae}, PÁGINA ATUAL: {self.pagina_atual}/{self.total_paginas}, "
            f"PROGRESSO: {self.calcular_porcentagem():.1f}%, "
            f"EMPRESTADO PARA: {self.emprestado_para}"
        )


class Audiobook(Leitura):
    def __init__(self, livro, narrador, tempo_total, nota_narracao=None, tempo_ouvido=0):
        super().__init__(livro)
        self.narrador = narrador
        self.nota_narracao = nota_narracao
        self.tempo_total = self.converter_tempo_para_segundos(tempo_total)
        self.tempo_ouvido = 0
        self.atualizar_tempo_ouvido(tempo_ouvido)

    def converter_tempo_para_segundos(self, tempo):
        if isinstance(tempo, int):
            return tempo

        if tempo is None:
            raise ValueError("Tempo inválido. Use o formato HH:MM:SS.")

        try:
            tempo_convertido = datetime.strptime(str(tempo), "%H:%M:%S")
        except ValueError as erro:
            raise ValueError("Tempo inválido. Use o formato HH:MM:SS.") from erro

        return (
            tempo_convertido.hour * 3600
            + tempo_convertido.minute * 60
            + tempo_convertido.second
        )

    def converter_segundos_para_tempo(self, segundos):
        segundos = int(segundos)
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos = segundos % 60
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    def calcular_porcentagem(self):
        if self.tempo_total <= 0:
            return 0

        return (self.tempo_ouvido / self.tempo_total) * 100

    def progresso_leitura(self):
        tempo = Prompt.ask("[bold]Informe a timestamp atual (HH:MM:SS):[/bold]")
        porcentagem = self.atualizar_tempo_ouvido(tempo)

        console.print("[bold green]Timestamp atualizada![/bold green]")
        print(f"Progresso atualizado: ({porcentagem:.1f}%)")
        print(f"Tempo ouvido: {tempo} de {self.converter_segundos_para_tempo(self.tempo_total)}")

        if self.tempo_ouvido >= self.tempo_total:
            console.print("[bold purple]Audiobook concluído![/bold purple]")

        return porcentagem

    def atualizar_tempo_ouvido(self, tempo):
        segundos_totais = self.converter_tempo_para_segundos(tempo)

        if segundos_totais < 0 or segundos_totais > self.tempo_total:
            raise ValueError(
                f"O tempo ouvido deve estar entre 00:00:00 e {self.converter_segundos_para_tempo(self.tempo_total)}."
            )

        self.tempo_ouvido = segundos_totais
        return self.calcular_porcentagem()

    def avaliar_narracao(self, nota):
        self.nota_narracao = nota

    def __str__(self):
        infos_mae = super().__str__()
        return (
            f"{infos_mae}, NARRADOR: {self.narrador}, "
            f"NOTA DA NARRAÇÃO: {self.nota_narracao}, "
            f"PROGRESSO: {self.calcular_porcentagem():.1f}%"
        )


class LeituraCreator(ABC):
    """Creator abstrato do Factory Method."""

    @abstractmethod
    def factory_method(self, livro, **kwargs):
        pass

    def criar_leitura(self, livro, **kwargs):
        return self.factory_method(livro, **kwargs)


class LivroFisicoEbookCreator(LeituraCreator):
    def factory_method(self, livro, **kwargs):
        total_paginas = kwargs.get("total_paginas")

        if total_paginas is None:
            raise ValueError("O total de páginas é obrigatório para livro físico/ebook.")

        return LivroFisico_Ebook(livro, total_paginas)


class AudiobookCreator(LeituraCreator):
    def factory_method(self, livro, **kwargs):
        narrador = kwargs.get("narrador")
        tempo_total = kwargs.get("tempo_total")

        if not narrador:
            raise ValueError("O narrador é obrigatório para audiobook.")

        if not tempo_total:
            raise ValueError("O tempo total é obrigatório para audiobook.")

        return Audiobook(livro, narrador, tempo_total)


class Categoria(ComponenteBiblioteca):
    """Composite que agrupa leituras dentro de uma categoria."""

    def __init__(self, nome):
        nome = str(nome).strip()

        if not nome:
            raise ValueError("O nome da categoria não pode ficar vazio.")

        self.nome = nome
        self.itens = []

    @property
    def leituras_adicionadas(self):
        return self.itens

    def descricao(self):
        return self.nome

    def adicionar(self, componente):
        if not isinstance(componente, Leitura):
            raise TypeError("Categorias só podem receber objetos do tipo Leitura.")

        if componente not in self.itens:
            self.itens.append(componente)

        return componente

    def remover(self, componente):
        if componente in self.itens:
            self.itens.remove(componente)

        return componente

    def __iter__(self):
        return BibliotecaIterator(self.itens)

    def adicionar_leitura(self, leitura):
        return self.adicionar(leitura)

    def retirar_livro(self, leitura):
        return self.remover(leitura)

    def printar_categoria(self):
        return list(self)

    def __str__(self):
        return self.nome


class Biblioteca_Pessoal(ComponenteBiblioteca):
    """Composite raiz da biblioteca pessoal.

    Pode conter leituras e categorias. A criação de leituras é delegada para
    creators registrados, preservando o Factory Method e evitando if/elif para
    instanciar classes concretas.
    """

    _criadores_leitura = {
        FORMATO_LIVRO_FISICO_EBOOK: LivroFisicoEbookCreator,
        FORMATO_AUDIOBOOK: AudiobookCreator,
    }

    def __init__(self):
        self.nome = "Biblioteca Pessoal"
        self.itens = []
        self.lista_leituras = []
        self.lista_categorias = []
        self.meta_literaria_anual = []
        self.meta_literaria_mensal = []

    def descricao(self):
        return self.nome

    def adicionar(self, componente):
        if not isinstance(componente, (Leitura, Categoria)):
            raise TypeError("A biblioteca só pode receber leituras ou categorias.")

        if componente in self.itens:
            return componente

        self.itens.append(componente)

        if isinstance(componente, Categoria):
            self.lista_categorias.append(componente)
        elif isinstance(componente, Leitura):
            self.lista_leituras.append(componente)

        return componente

    def remover(self, componente):
        if componente in self.itens:
            self.itens.remove(componente)

        if isinstance(componente, Categoria) and componente in self.lista_categorias:
            self.lista_categorias.remove(componente)

        if isinstance(componente, Leitura) and componente in self.lista_leituras:
            self.lista_leituras.remove(componente)

        return componente

    def __iter__(self):
        return BibliotecaIterator(self.itens)

    def iterar_leituras(self):
        return BibliotecaIterator(self.lista_leituras)

    def iterar_categorias(self):
        return BibliotecaIterator(self.lista_categorias)

    @classmethod
    def registrar_criador_leitura(cls, formato, criador):
        if not isinstance(formato, int):
            raise TypeError("O formato da leitura deve ser um número inteiro.")

        if not isinstance(criador, type) or not issubclass(criador, LeituraCreator):
            raise TypeError("O criador deve ser uma classe filha de LeituraCreator.")

        cls._criadores_leitura[formato] = criador

    def obter_criador_leitura(self, formato):
        try:
            formato = int(formato)
        except (TypeError, ValueError) as erro:
            raise ValueError("Formato de leitura inválido.") from erro

        criador = self._criadores_leitura.get(formato)

        if criador is None:
            raise ValueError("Formato de leitura inválido.")

        return criador()

    def adicionar_leitura(self, livro, formato, total_paginas=None, narrador=None, tempo_total=None):
        criador = self.obter_criador_leitura(formato)

        leitura = criador.criar_leitura(
            livro,
            total_paginas=total_paginas,
            narrador=narrador,
            tempo_total=tempo_total,
        )

        self.adicionar(leitura)
        return leitura

    def ver_ordem_alfabetica(self):
        return sorted(self.iterar_leituras(), key=lambda leitura: leitura.livro.titulo)

    def adicionar_categoria(self, categoria):
        nova_categoria = Categoria(categoria)
        self.adicionar(nova_categoria)
        return nova_categoria

    def excluir_livro(self, leitura):
        if not isinstance(leitura, Leitura):
            raise TypeError("Só é possível excluir objetos do tipo Leitura.")

        for categoria in self.iterar_categorias():
            if leitura in categoria.leituras_adicionadas:
                categoria.retirar_livro(leitura)

        return self.remover(leitura)

    def ver_infos(self):
        return list(self.iterar_leituras())

    def ver_pastas_conteudo(self):
        biblioteca = {}

        for categoria in self.iterar_categorias():
            biblioteca[categoria.nome] = list(categoria)

        return biblioteca

    def ver_categorias(self):
        return list(self.iterar_categorias())

    def retrospectiva(self, ano):
        try:
            ano = int(ano)
        except (TypeError, ValueError) as erro:
            raise ValueError("O ano da retrospectiva deve ser um número inteiro.") from erro

        retrospectiva_anual = []

        for leitura in self.iterar_leituras():
            if leitura.final_leitura is not None and leitura.final_leitura.year == ano:
                retrospectiva_anual.append(leitura)

        return retrospectiva_anual

    def definir_meta_anual(self, livro):
        if livro not in self.meta_literaria_anual:
            self.meta_literaria_anual.append(livro)

        return self.meta_literaria_anual

    def definir_meta_mensal(self, livro):
        if livro not in self.meta_literaria_mensal:
            self.meta_literaria_mensal.append(livro)

        return self.meta_literaria_mensal


class Usuario:
    def __init__(self, nome, email, senha=None, senha_hash=None, ultimo_acesso=None):
        self.nome = nome
        self.email = email
        self.biblioteca_pessoal = []
        self.ph = PasswordHasher()
        self.ultimo_acesso = self._normalizar_ultimo_acesso(ultimo_acesso)

        if senha_hash is not None:
            self.__senha = senha_hash
        elif senha is not None:
            self.__senha = self.ph.hash(senha)
        else:
            raise ValueError("Informe uma senha nova ou uma senha já criptografada.")

    @classmethod
    def carregar_do_banco(cls, nome, email, senha_hash, ultimo_acesso=None):
        return cls(
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            ultimo_acesso=ultimo_acesso,
        )

    def _normalizar_ultimo_acesso(self, ultimo_acesso):
        if ultimo_acesso is None:
            return None

        if isinstance(ultimo_acesso, datetime):
            return ultimo_acesso.replace(tzinfo=None)

        if isinstance(ultimo_acesso, str):
            ultimo_acesso = ultimo_acesso.strip()

            if not ultimo_acesso:
                return None

            try:
                data = datetime.fromisoformat(ultimo_acesso.replace("Z", "+00:00"))
                return data.replace(tzinfo=None)
            except ValueError:
                pass

            formatos_validos = [
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y",
            ]

            for formato in formatos_validos:
                try:
                    return datetime.strptime(ultimo_acesso, formato)
                except ValueError:
                    continue

            raise ValueError("Último acesso salvo no banco está em formato inválido.")

        raise ValueError("Último acesso possui um tipo inválido.")

    @property
    def senha(self):
        return self.__senha

    def login(self, email_dado, senha_dada):
        try:
            senha_valida = self.ph.verify(self.__senha, senha_dada)
        except (VerifyMismatchError, VerificationError, ValueError):
            senha_valida = False

        if self.email == email_dado and senha_valida:
            self.ultimo_acesso = datetime.now()
            return True

        return False

    def verificar_inatividade(self):
        self.ultimo_acesso = self._normalizar_ultimo_acesso(self.ultimo_acesso)

        if self.ultimo_acesso is not None:
            diferenca_dias = datetime.now() - self.ultimo_acesso

            if diferenca_dias > timedelta(days=30):
                enviar_email(self.email)