import pyfiglet

from rich import box, print
from rich.console import Console
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from back import Audiobook, Biblioteca_Pessoal, LivroFisico_Ebook, Usuario
from database import (
    BancoDadosErro,
    buscar_usuario_por_email_bd,
    cadastro_bd,
    ultimo_acesso_bd,
)

console = Console()
minha_biblioteca = Biblioteca_Pessoal()


def exibir_erro(mensagem):
    console.print(f"[bold red]{mensagem}[/bold red]")


def exibir_aviso(mensagem):
    console.print(f"[bold yellow]{mensagem}[/bold yellow]")


def pausar():
    Prompt.ask("[bold]Pressione Enter para continuar[/bold]", default="")


def perguntar_opcao(mensagem, opcoes_validas):
    while True:
        try:
            opcao = IntPrompt.ask(mensagem)
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow]Operação cancelada pelo usuário.[/bold yellow]")
            return None
        except Exception as erro:
            exibir_erro(f"Entrada inválida: {erro}")
            continue

        if opcao in opcoes_validas:
            return opcao

        opcoes = ", ".join(str(opcao_valida) for opcao_valida in opcoes_validas)
        exibir_erro(f"Opção inválida. Escolha uma das opções: {opcoes}.")


def perguntar_inteiro(mensagem, minimo=None, maximo=None):
    while True:
        try:
            valor = IntPrompt.ask(mensagem)
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow]Operação cancelada pelo usuário.[/bold yellow]")
            return None
        except Exception as erro:
            exibir_erro(f"Entrada inválida: {erro}")
            continue

        if minimo is not None and valor < minimo:
            exibir_erro(f"Informe um valor maior ou igual a {minimo}.")
            continue

        if maximo is not None and valor > maximo:
            exibir_erro(f"Informe um valor menor ou igual a {maximo}.")
            continue

        return valor


def criar_tabela_catalogo(catalogo):
    tabela_catalogo = Table(title="Catálogo de Livros", style="bold", box=box.ROUNDED, show_lines=True)
    tabela_catalogo.add_column("Nº")
    tabela_catalogo.add_column("Título", style="bold purple")
    tabela_catalogo.add_column("Autor(a)")
    tabela_catalogo.add_column("Sinopse", max_width=60)

    for livro in catalogo:
        tabela_catalogo.add_row(
            str(livro.numero),
            livro.titulo,
            livro.autor,
            livro.sinopse
        )

    return tabela_catalogo


def atualizar_tabela_usuario():
    biblioteca_usuario = Table(title="Biblioteca Pessoal", style="bold", box=box.ROUNDED, show_lines=True)

    biblioteca_usuario.add_column("Nº", header_style="deep_pink3", width=4)
    biblioteca_usuario.add_column("Tipo", header_style="violet")
    biblioteca_usuario.add_column("Título", header_style="indian_red")
    biblioteca_usuario.add_column("Autor(a)", header_style="indian_red")
    biblioteca_usuario.add_column("Etiqueta", header_style="indian_red")
    biblioteca_usuario.add_column("Nota", header_style="indian_red")
    biblioteca_usuario.add_column("Resenha", header_style="indian_red")
    biblioteca_usuario.add_column("Data de leitura iniciada", header_style="indian_red")
    biblioteca_usuario.add_column("Data de leitura finalizada", header_style="indian_red")

    for numero, leitura in enumerate(minha_biblioteca.iterar_leituras(), start=1):
        tipo = "Audiobook" if isinstance(leitura, Audiobook) else "Físico/Ebook"

        biblioteca_usuario.add_row(
            str(numero),
            tipo,
            leitura.livro.titulo,
            leitura.livro.autor,
            str(leitura.etiqueta or "-"),
            str(leitura.nota if leitura.nota is not None else "-"),
            str(leitura.resenha or "-"),
            leitura.inicio_leitura.strftime("%d/%m/%Y") if leitura.inicio_leitura else "-",
            leitura.final_leitura.strftime("%d/%m/%Y") if leitura.final_leitura else "-"
        )

    return biblioteca_usuario


def exibir_categorias(biblioteca):
    if not biblioteca.lista_categorias:
        exibir_aviso("Nenhuma categoria criada ainda.")
        return

    for categoria in biblioteca.iterar_categorias():
        tabela_categorias = Table(title=f"{categoria.nome}", box=box.ROUNDED, show_lines=True)

        tabela_categorias.add_column("Nº", header_style="deep_pink3", width=4)
        tabela_categorias.add_column("Tipo", header_style="violet")
        tabela_categorias.add_column("Título", header_style="indian_red")
        tabela_categorias.add_column("Autor(a)", header_style="indian_red")
        tabela_categorias.add_column("Etiqueta", header_style="indian_red")
        tabela_categorias.add_column("Nota", header_style="indian_red")
        tabela_categorias.add_column("Resenha", header_style="indian_red")
        tabela_categorias.add_column("Data de leitura iniciada", header_style="indian_red")
        tabela_categorias.add_column("Data de leitura finalizada", header_style="indian_red")

        for indice, leitura in enumerate(categoria, start=1):
            tipo = "Audiobook" if isinstance(leitura, Audiobook) else "Físico/Ebook"

            tabela_categorias.add_row(
                str(indice),
                tipo,
                leitura.livro.titulo,
                leitura.livro.autor,
                str(leitura.etiqueta or "-"),
                str(leitura.nota if leitura.nota is not None else "-"),
                str(leitura.resenha or "-"),
                leitura.inicio_leitura.strftime("%d/%m/%Y") if leitura.inicio_leitura else "-",
                leitura.final_leitura.strftime("%d/%m/%Y") if leitura.final_leitura else "-"
            )

        console.print(tabela_categorias)


def exibir_tabela_leituras(lista, titulo):
    if not lista:
        exibir_aviso("Nenhum livro encontrado para exibir.")
        return

    tabela = Table(title=titulo, box=box.ROUNDED, show_lines=True)

    tabela.add_column("Nº", header_style="deep_pink3", width=4)
    tabela.add_column("Tipo", header_style="violet")
    tabela.add_column("Título", header_style="indian_red")
    tabela.add_column("Autor(a)", header_style="indian_red")
    tabela.add_column("Etiqueta", header_style="indian_red")
    tabela.add_column("Nota", header_style="indian_red")
    tabela.add_column("Resenha", header_style="indian_red")
    tabela.add_column("Data de leitura iniciada", header_style="indian_red")
    tabela.add_column("Data de leitura finalizada", header_style="indian_red")

    for indice, leitura in enumerate(lista, start=1):
        tipo = "Audiobook" if isinstance(leitura, Audiobook) else "Físico/Ebook"

        tabela.add_row(
            str(indice),
            tipo,
            leitura.livro.titulo,
            leitura.livro.autor,
            str(leitura.etiqueta or "-"),
            str(leitura.nota if leitura.nota is not None else "-"),
            str(leitura.resenha or "-"),
            leitura.inicio_leitura.strftime("%d/%m/%Y") if leitura.inicio_leitura else "-",
            leitura.final_leitura.strftime("%d/%m/%Y") if leitura.final_leitura else "-"
        )

    console.print(tabela)


def realizar_cadastro():
    console.print(Panel("[bold]Cadastro de novo usuário[/bold]", border_style="white"))

    nome = Prompt.ask("[bold]Nome[/bold]").strip()
    email = Prompt.ask("[bold]Email[/bold]").strip()
    senha = Prompt.ask("[bold]Senha[/bold]", password=True)

    if not nome or not email or not senha:
        exibir_erro("Nome, e-mail e senha são obrigatórios.")
        return None

    usuario = Usuario(nome, email, senha)
    cadastro_realizado = cadastro_bd(usuario)

    if not cadastro_realizado:
        exibir_erro("Este e-mail já está cadastrado. Faça login ou use outro e-mail.")
        return None

    console.print("[bold green]Cadastro realizado com sucesso! Agora faça login para acessar o sistema.[/bold green]")
    return usuario


def realizar_login():
    console.print(Panel("[bold]Login[/bold]", border_style="white"))

    email_dado = Prompt.ask("[bold]Email[/bold]").strip()
    senha_dada = Prompt.ask("[bold]Senha[/bold]", password=True)

    if not email_dado or not senha_dada:
        exibir_erro("E-mail e senha são obrigatórios.")
        return None

    dados_usuario = buscar_usuario_por_email_bd(email_dado)

    if not dados_usuario:
        exibir_erro("E-mail ou senha incorretos.")
        return None

    usuario = Usuario.carregar_do_banco(
        nome=dados_usuario["nome"],
        email=dados_usuario["email"],
        senha_hash=dados_usuario["senha"],
        ultimo_acesso=dados_usuario["ultimo_acesso"]
    )

    acesso_anterior = usuario.ultimo_acesso
    logado = usuario.login(email_dado, senha_dada)

    if not logado:
        exibir_erro("E-mail ou senha incorretos.")
        return None

    acesso_atual = ultimo_acesso_bd(usuario)

    if acesso_anterior:
        usuario.ultimo_acesso = acesso_anterior
        usuario.verificar_inatividade()
        usuario.ultimo_acesso = acesso_atual

    console.print(f"[bold green]Bem-vindo, {usuario.nome}![/]")
    console.print(f"[bold green]Acesso em: {acesso_atual.strftime('%d/%m/%Y')}[/]")
    return usuario


def abrir_catalogo(catalogo):
    while True:
        try:
            console.print("[bold green]Navegue pelo catálogo para personalizar sua biblioteca pessoal.[/]")
            console.print(criar_tabela_catalogo(catalogo))

            acao = perguntar_opcao(
                """
                [bold][1] Adicionar livro à biblioteca[/bold]
                [bold][2] Voltar ao menu anterior[/bold]
                """,
                [1, 2]
            )

            if acao is None or acao == 2:
                return

            opcao_livro = perguntar_inteiro(
                "[bold]Digite o número do livro escolhido:[/bold]",
                minimo=1,
                maximo=len(catalogo)
            )

            if opcao_livro is None:
                continue

            tipo_livro = perguntar_opcao(
                """
                [bold]Selecione o tipo de leitura:[/bold]
                [bold][1] Livro Físico/Ebook[/bold]
                [bold][2] Audiobook[/bold]
                """,
                [1, 2]
            )

            if tipo_livro is None:
                continue

            novo_livro = catalogo[opcao_livro - 1]

            if tipo_livro == 1:
                paginas = perguntar_inteiro("[bold]Informe o total de páginas:[/bold]", minimo=1)

                if paginas is None:
                    continue

                minha_biblioteca.adicionar_leitura(
                    novo_livro,
                    formato=1,
                    total_paginas=paginas
                )

            elif tipo_livro == 2:
                duracao_total = Prompt.ask("[bold]Informe a duração do Audiobook (formato HH:MM:SS):[/bold]").strip()
                narracao = Prompt.ask("[bold]Informe o/a narrador(a):[/bold]").strip()

                if not duracao_total or not narracao:
                    exibir_erro("Duração e narrador(a) são obrigatórios para audiobook.")
                    pausar()
                    continue

                minha_biblioteca.adicionar_leitura(
                    novo_livro,
                    formato=2,
                    narrador=narracao,
                    tempo_total=duracao_total
                )

            console.print("[bold green]Livro adicionado à biblioteca com sucesso![/bold green]")
            console.print(atualizar_tabela_usuario())
            pausar()

        except Exception as erro:
            exibir_erro(f"Não foi possível concluir a ação no catálogo: {erro}")
            exibir_aviso("Você continua na tela do catálogo.")
            pausar()


def menu_biblioteca():
    while True:
        try:
            console.print(atualizar_tabela_usuario())
            console.print("[bold green]Selecione o que deseja fazer:[/]")

            opcao_biblioteca = perguntar_opcao(
                """
                [bold][1] Criar categoria[/bold]
                [bold][2] Excluir livro[/bold]
                [bold][3] Preencher categoria[/bold]
                [bold][4] Ver livros em ordem alfabética[/bold]
                [bold][5] Ver retrospectiva anual[/bold]
                [bold][6] Definir meta de leitura anual[/bold]
                [bold][7] Definir meta de leitura mensal[/bold]
                [bold][8] Adicionar informações de um livro[/bold]
                [bold][9] Ver livros por categoria[/bold]
                [bold][10] Voltar para o menu anterior[/bold]
                """,
                list(range(1, 11))
            )

            if opcao_biblioteca is None or opcao_biblioteca == 10:
                return

            if opcao_biblioteca == 1:
                nome_categoria = Prompt.ask("[bold]Digite o nome da categoria[/bold]").strip()

                if not nome_categoria:
                    exibir_erro("O nome da categoria não pode ficar vazio.")
                    pausar()
                    continue

                minha_biblioteca.adicionar_categoria(nome_categoria)
                console.print(f"[bold purple]Categoria '{nome_categoria}' adicionada com sucesso![/]")
                pausar()
                continue

            if opcao_biblioteca == 2:
                if not minha_biblioteca.lista_leituras:
                    exibir_aviso("Nenhum livro na biblioteca ainda.")
                    pausar()
                    continue

                console.print(atualizar_tabela_usuario())
                num = perguntar_inteiro(
                    "[bold]Digite o número do livro que deseja excluir[/bold]",
                    minimo=1,
                    maximo=len(minha_biblioteca.lista_leituras)
                )

                if num is None:
                    continue

                leitura_escolhida = minha_biblioteca.lista_leituras[num - 1]
                minha_biblioteca.excluir_livro(leitura_escolhida)

                console.print("[bold green]Livro removido com sucesso![/bold green]")
                console.print(atualizar_tabela_usuario())
                exibir_categorias(minha_biblioteca)
                pausar()
                continue

            if opcao_biblioteca == 3:
                if not minha_biblioteca.lista_leituras:
                    exibir_aviso("Nenhum livro na biblioteca ainda.")
                    pausar()
                    continue

                if not minha_biblioteca.lista_categorias:
                    exibir_aviso("Nenhuma categoria criada ainda.")
                    pausar()
                    continue

                console.print(atualizar_tabela_usuario())
                num_livro = perguntar_inteiro(
                    "[bold]Digite o número do livro que deseja adicionar na categoria.[/bold]",
                    minimo=1,
                    maximo=len(minha_biblioteca.lista_leituras)
                )

                if num_livro is None:
                    continue

                leitura_escolhida = minha_biblioteca.lista_leituras[num_livro - 1]

                for indice, categoria in enumerate(minha_biblioteca.iterar_categorias(), start=1):
                    console.print(f"[bold][{indice}][/bold] {categoria.nome}")

                num_categoria = perguntar_inteiro(
                    "[bold]Digite o número da categoria[/bold]",
                    minimo=1,
                    maximo=len(minha_biblioteca.lista_categorias)
                )

                if num_categoria is None:
                    continue

                categoria_escolhida = minha_biblioteca.lista_categorias[num_categoria - 1]
                categoria_escolhida.adicionar_leitura(leitura_escolhida)

                console.print(f"[bold green]Livro adicionado à categoria '{categoria_escolhida.nome}' com sucesso![/bold green]")
                exibir_categorias(minha_biblioteca)
                pausar()
                continue

            if opcao_biblioteca == 4:
                lista_ordenada = minha_biblioteca.ver_ordem_alfabetica()
                exibir_tabela_leituras(lista_ordenada, "Biblioteca em Ordem Alfabética")
                pausar()
                continue

            if opcao_biblioteca == 5:
                ano = perguntar_inteiro("[bold]Digite o ano da sua retrospectiva.[/bold]", minimo=1)

                if ano is None:
                    continue

                retrospectiva_lista = minha_biblioteca.retrospectiva(ano)
                console.print(f"\n[bold purple]-- Retrospectiva {ano} --[/bold purple]\n")

                if not retrospectiva_lista:
                    exibir_aviso("Lista vazia.")
                else:
                    for indice, leitura in enumerate(retrospectiva_lista, start=1):
                        console.print(f"{indice}. {leitura.livro.titulo}")

                pausar()
                continue

            if opcao_biblioteca == 6:
                if not minha_biblioteca.lista_leituras:
                    exibir_aviso("Nenhum livro na biblioteca ainda.")
                    pausar()
                    continue

                console.print(atualizar_tabela_usuario())
                num = perguntar_inteiro(
                    "[bold]Digite o número do livro desejado para a meta literária ANUAL.[/bold]",
                    minimo=1,
                    maximo=len(minha_biblioteca.lista_leituras)
                )

                if num is None:
                    continue

                objeto_leitura = minha_biblioteca.lista_leituras[num - 1]
                ano_desejado = perguntar_inteiro("[bold]Digite o ano da sua meta.[/bold]", minimo=1)

                if ano_desejado is None:
                    continue

                meta_anual = minha_biblioteca.definir_meta_anual(objeto_leitura)
                console.print(f"\n[bold purple]-- Meta Literária Anual {ano_desejado} --[/bold purple]\n")

                for indice, leitura in enumerate(meta_anual, start=1):
                    console.print(f"{indice}. {leitura.livro.titulo}")

                pausar()
                continue

            if opcao_biblioteca == 7:
                if not minha_biblioteca.lista_leituras:
                    exibir_aviso("Nenhum livro na biblioteca ainda.")
                    pausar()
                    continue

                console.print(atualizar_tabela_usuario())
                num = perguntar_inteiro(
                    "[bold]Digite o número do livro desejado para a meta literária MENSAL.[/bold]",
                    minimo=1,
                    maximo=len(minha_biblioteca.lista_leituras)
                )

                if num is None:
                    continue

                objeto_leitura = minha_biblioteca.lista_leituras[num - 1]
                mes = perguntar_inteiro("[bold]Digite o mês da sua meta.[/bold]", minimo=1, maximo=12)

                if mes is None:
                    continue

                meta_mensal = minha_biblioteca.definir_meta_mensal(objeto_leitura)
                console.print(f"\n[bold purple]-- Meta Literária Mensal {mes} --[/bold purple]\n")

                for indice, leitura in enumerate(meta_mensal, start=1):
                    console.print(f"{indice}. {leitura.livro.titulo}")

                pausar()
                continue

            if opcao_biblioteca == 8:
                adicionar_informacoes_livro()
                continue

            if opcao_biblioteca == 9:
                console.rule("[bold purple]Sua Biblioteca por Categorias[/bold purple]")
                exibir_categorias(minha_biblioteca)
                console.print("\n")
                pausar()
                continue

        except Exception as erro:
            exibir_erro(f"Não foi possível concluir a ação na biblioteca: {erro}")
            exibir_aviso("Você continua na tela da biblioteca pessoal.")
            pausar()


def adicionar_informacoes_livro():
    while True:
        try:
            if not minha_biblioteca.lista_leituras:
                exibir_aviso("Nenhum livro na biblioteca ainda.")
                pausar()
                return

            console.print(atualizar_tabela_usuario())
            num = perguntar_inteiro(
                "[bold]Digite o número do livro desejado para adicionar informações.[/bold]",
                minimo=1,
                maximo=len(minha_biblioteca.lista_leituras)
            )

            if num is None:
                return

            livro_escolhido = minha_biblioteca.lista_leituras[num - 1]

            while True:
                try:
                    str_menu = """
                        [bold]Selecione a ação desejada:[/bold]
                        [bold][1] Adicionar data de início de leitura[/bold]
                        [bold][2] Adicionar data de conclusão de leitura[/bold]
                        [bold][3] Adicionar nota[/bold]
                        [bold][4] Adicionar etiqueta[/bold]
                        [bold][5] Adicionar resenha literária[/bold]
                    """

                    if isinstance(livro_escolhido, LivroFisico_Ebook):
                        str_menu += """
                        [bold][6] Progresso de leitura (páginas)[/bold]
                        [bold][7] Registrar empréstimo[/bold]
                        [bold][8] Escolher outro livro[/bold]
                        [bold][9] Voltar para biblioteca[/bold]
                        """
                    else:
                        str_menu += """
                        [bold][6] Progresso de leitura (tempo ouvido)[/bold]
                        [bold][7] Avaliar narração[/bold]
                        [bold][8] Escolher outro livro[/bold]
                        [bold][9] Voltar para biblioteca[/bold]
                        """

                    opcao_desejada = perguntar_opcao(str_menu, list(range(1, 10)))

                    if opcao_desejada is None or opcao_desejada == 9:
                        return

                    if opcao_desejada == 8:
                        break

                    if opcao_desejada == 1:
                        data_informada = Prompt.ask("[bold]Informe a data de início (DD/MM/AAAA):[/bold]").strip()
                        livro_escolhido.data_inicio(data_informada)

                        console.print("[bold green]Data de início de leitura definida.[/bold green]")
                        console.print(atualizar_tabela_usuario())
                        pausar()

                    elif opcao_desejada == 2:
                        data_informada = Prompt.ask("[bold]Informe a data de conclusão (DD/MM/AAAA):[/bold]").strip()
                        livro_escolhido.data_final(data_informada)

                        console.print("[bold green]Data de conclusão de leitura definida.[/bold green]")
                        console.print(atualizar_tabela_usuario())
                        pausar()

                    elif opcao_desejada == 3:
                        nota_informada = perguntar_inteiro(
                            "[bold]Informe a nota que você deseja adicionar (0 a 5):[/bold]",
                            minimo=0,
                            maximo=5
                        )

                        if nota_informada is None:
                            continue

                        livro_escolhido.atribuir_nota(nota_informada)
                        console.print("[bold green]Nota atribuída.[/bold green]")
                        console.print(atualizar_tabela_usuario())
                        pausar()

                    elif opcao_desejada == 4:
                        etiqueta_informada = Prompt.ask("[bold]Escreva a etiqueta que você deseja adicionar:[/bold]").strip()
                        livro_escolhido.adicionar_etiqueta(etiqueta_informada)

                        console.print("[bold green]Etiqueta atribuída.[/bold green]")
                        console.print(atualizar_tabela_usuario())
                        pausar()

                    elif opcao_desejada == 5:
                        resenha_informada = Prompt.ask("[bold]Escreva a resenha que você deseja adicionar:[/bold]").strip()
                        livro_escolhido.escrever_resenha(resenha_informada)

                        console.print("[bold green]Resenha atribuída.[/bold green]")
                        console.print(atualizar_tabela_usuario())
                        pausar()

                    elif opcao_desejada == 6:
                        porcentagem = livro_escolhido.progresso_leitura()
                        barra = ProgressBar(total=100, completed=porcentagem, width=40, pulse=False)

                        console.print(barra)
                        console.print("\n")
                        console.print(atualizar_tabela_usuario())
                        pausar()

                    elif opcao_desejada == 7:
                        if isinstance(livro_escolhido, LivroFisico_Ebook):
                            emprestimo_pessoa = Prompt.ask("[bold]Informe para quem você emprestou o livro:[/bold]").strip()
                            livro_escolhido.emprestar(emprestimo_pessoa)

                            console.print(f"[bold green]Empréstimo registrado para {emprestimo_pessoa}![/bold green]")
                            console.print(atualizar_tabela_usuario())
                            pausar()
                        else:
                            avaliacao_narracao = Prompt.ask("[bold]Escreva sua avaliação da narração:[/bold]").strip()
                            livro_escolhido.avaliar_narracao(avaliacao_narracao)

                            console.print("[bold green]Avaliação da narração registrada![/bold green]")
                            console.print(atualizar_tabela_usuario())
                            pausar()

                except Exception as erro:
                    exibir_erro(f"Não foi possível concluir a operação: {erro}")
                    exibir_aviso("Você continua na tela de informações do livro.")
                    pausar()

        except Exception as erro:
            exibir_erro(f"Não foi possível abrir a tela de informações do livro: {erro}")
            exibir_aviso("Você continua na tela de escolha do livro.")
            pausar()


def menu_usuario(catalogo):
    while True:
        try:
            console.print("[bold]Você deseja navegar pelo catálogo de livros ou visitar sua biblioteca pessoal?[/bold]")

            opcao = perguntar_opcao(
                """
                [bold][1] Abrir catálogo de livros[/bold]
                [bold][2] Abrir biblioteca pessoal[/bold]
                [bold][3] Sair[/bold]
                """,
                [1, 2, 3]
            )

            if opcao is None or opcao == 3:
                console.print("[bold yellow]Saindo do sistema. Até logo![/bold yellow]")
                break

            if opcao == 1:
                abrir_catalogo(catalogo)
            elif opcao == 2:
                menu_biblioteca()

        except Exception as erro:
            exibir_erro(f"Ocorreu um erro inesperado no menu principal: {erro}")
            exibir_aviso("Você continua no menu principal.")
            pausar()


def cadastro_login(catalogo):
    console.print('[on grey][bold][purple]Bem vindo(a) ao sistema "Minha Estante"![/][purple][/]')
    print(pyfiglet.figlet_format("my", font="ogre", justify="center"))
    print(pyfiglet.figlet_format("bookshelf", font="ogre", justify="center"))

    while True:
        try:
            console.print(Panel("[bold]Acesso ao sistema[/bold]", border_style="white"))
            opcao = perguntar_opcao(
                """
                [bold]Escolha uma opção:[/bold]
                [bold][1] Cadastrar novo usuário[/bold]
                [bold][2] Logar em usuário existente[/bold]
                [bold][3] Sair[/bold]
                """,
                [1, 2, 3]
            )

            if opcao is None or opcao == 3:
                console.print("[bold yellow]Programa encerrado.[/bold yellow]")
                break

            if opcao == 1:
                realizar_cadastro()
                continue

            if opcao == 2:
                usuario = realizar_login()

                if usuario:
                    menu_usuario(catalogo)
                    break

        except BancoDadosErro as erro:
            exibir_erro(str(erro))
            exibir_aviso("Corrija a configuração do banco e tente novamente.")
            pausar()
        except Exception as erro:
            exibir_erro(f"Ocorreu um erro, mas o programa continuará aberto: {erro}")
            exibir_aviso("Você voltou ao menu de acesso.")
            pausar()