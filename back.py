from script import enviar_email

from abc import ABC, abstractmethod
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from datetime import datetime, timedelta

from rich.prompt import Prompt, IntPrompt
from rich.console import Console

console = Console()


class BibliotecaIterator:
    def __init__(self, itens):
        self.itens = list(itens)
        self.indice = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.indice >= len(self.itens):
            raise StopIteration

        item = self.itens[self.indice]
        self.indice += 1
        return item


class ComponenteBiblioteca(ABC):
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
    def __init__(
        self,
        livro,
        inicio_leitura=None,
        final_leitura=None,
        etiqueta=None,
        nota=None,
        resenha=None
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
        self.nota = nota

    def remover_nota(self):
        self.nota = None

    def escrever_resenha(self, resenha):
        self.resenha = resenha

    def remover_resenha(self):
        self.resenha = None

    def data_inicio(self, inicio_leitura):
        self.inicio_leitura = datetime.strptime(inicio_leitura, "%d/%m/%Y").date()

    def data_final(self, final_leitura):
        self.final_leitura = datetime.strptime(final_leitura, "%d/%m/%Y").date()

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
        self.total_paginas = total_paginas
        self.pagina_atual = pagina_atual
        self.emprestado_para = emprestado_para

    def calcular_porcentagem(self):
        if self.total_paginas <= 0:
            return 0

        return (self.pagina_atual / self.total_paginas) * 100

    def progresso_leitura(self):
        pagina = IntPrompt.ask("[bold]Informe a página atual:[/bold]")

        if pagina > 0 and pagina <= self.total_paginas:
            self.pagina_atual = pagina
            porcentagem = self.calcular_porcentagem()

            console.print("[bold green]Página atualizada![/bold green]")
            print(f"Progresso atualizado: {self.pagina_atual}/{self.total_paginas} ({porcentagem:.1f}%)")

            if self.pagina_atual >= self.total_paginas:
                console.print("[bold purple]Livro concluído![/bold purple]")

            return porcentagem

        console.print("[bold red]Página inválida.[/bold red]")
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
        self.tempo_ouvido = tempo_ouvido

    def converter_tempo_para_segundos(self, tempo):
        tempo_convertido = datetime.strptime(tempo, "%H:%M:%S")
        return (
            tempo_convertido.hour * 3600
            + tempo_convertido.minute * 60
            + tempo_convertido.second
        )

    def converter_segundos_para_tempo(self, segundos):
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
        segundos_totais = self.converter_tempo_para_segundos(tempo)

        if segundos_totais <= self.tempo_total:
            self.tempo_ouvido = segundos_totais
            porcentagem = self.calcular_porcentagem()

            console.print("[bold green]Timestamp atualizada![/bold green]")
            print(f"Progresso atualizado: ({porcentagem:.1f}%)")
            print(f"Tempo ouvido: {tempo} de {self.converter_segundos_para_tempo(self.tempo_total)}")

            if self.tempo_ouvido >= self.tempo_total:
                console.print("[bold purple]Audiobook concluído![/bold purple]")

            return porcentagem

        console.print("[bold red]Timestamp inválida.[/bold red]")
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

        if narrador is None:
            raise ValueError("O narrador é obrigatório para audiobook.")

        if tempo_total is None:
            raise ValueError("O tempo total é obrigatório para audiobook.")

        return Audiobook(livro, narrador, tempo_total)


class Categoria(ComponenteBiblioteca):
    def __init__(self, nome):
        self.nome = nome
        self.itens = []
        self.leituras_adicionadas = self.itens

    def descricao(self):
        return self.nome

    def adicionar(self, componente):
        self.itens.append(componente)
        return componente

    def remover(self, componente):
        self.itens.remove(componente)

    def __iter__(self):
        return BibliotecaIterator(self.itens)

    def adicionar_leitura(self, livro):
        return self.adicionar(livro)

    def retirar_livro(self, livro):
        self.remover(livro)

    def printar_categoria(self):
        return list(self)

    def __str__(self):
        return f"{self.nome}"


class Biblioteca_Pessoal(ComponenteBiblioteca):
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

    def __iter__(self):
        return BibliotecaIterator(self.itens)

    def iterar_leituras(self):
        return BibliotecaIterator(self.lista_leituras)

    def iterar_categorias(self):
        return BibliotecaIterator(self.lista_categorias)

    def obter_criador_leitura(self, formato):
        if formato == 1:
            return LivroFisicoEbookCreator()

        if formato == 2:
            return AudiobookCreator()

        raise ValueError("Formato de leitura inválido.")

    def adicionar_leitura(self, livro, formato, total_paginas=None, narrador=None, tempo_total=None):
        criador = self.obter_criador_leitura(formato)

        leitura = criador.criar_leitura(
            livro,
            total_paginas=total_paginas,
            narrador=narrador,
            tempo_total=tempo_total
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
        for categoria in self.iterar_categorias():
            if leitura in categoria.leituras_adicionadas:
                categoria.retirar_livro(leitura)

        self.remover(leitura)

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
        retrospectiva_anual = []

        for leitura in self.iterar_leituras():
            if leitura.final_leitura is not None:
                if leitura.final_leitura.year == ano:
                    retrospectiva_anual.append(leitura)

        return retrospectiva_anual

    def definir_meta_anual(self, livro):
        self.meta_literaria_anual.append(livro)
        return self.meta_literaria_anual

    def definir_meta_mensal(self, livro):
        self.meta_literaria_mensal.append(livro)
        return self.meta_literaria_mensal


class Usuario:
    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.biblioteca_pessoal = []
        self.ultimo_acesso = None
        self.ph = PasswordHasher()
        self.__senha = self.ph.hash(senha)

    @property
    def senha(self):
        return self.__senha

    def login(self, email_dado, senha_dada):
        try:
            senha_valida = self.ph.verify(self.__senha, senha_dada)
        except (VerifyMismatchError, VerificationError):
            senha_valida = False

        if self.email == email_dado and senha_valida:
            self.ultimo_acesso = datetime.now()
            return True

        return False

    def verificar_inatividade(self):
        if self.ultimo_acesso is not None:
            diferenca_dias = datetime.now() - self.ultimo_acesso

            if diferenca_dias > timedelta(days=30):
                enviar_email(self.email)