import pyfiglet

from rich import print
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich import box
from rich.progress_bar import ProgressBar

from database import cadastro_bd, login_bd, ultimo_acesso_bd, comparar_ultimo_acesso_bd
from back import Usuario, Biblioteca_Pessoal, LivroFisico_Ebook, Audiobook

console = Console()

print('[on grey][bold][purple]Bem vindo(a) ao sistema "Minha Estante"![/][purple][/]')

tabela_catalogo = Table(title="Catálogo de Livros", style="bold", box=box.ROUNDED, show_lines=True)
tabela_catalogo.add_column("Nº")
tabela_catalogo.add_column("Título", style="bold purple")
tabela_catalogo.add_column("Autor(a)")
tabela_catalogo.add_column("Sinopse", max_width=60)

minha_biblioteca = Biblioteca_Pessoal()


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

    numero = 1

    for leitura in minha_biblioteca.iterar_leituras():
        tipo = "Audiobook" if isinstance(leitura, Audiobook) else "Físico/Ebook"

        biblioteca_usuario.add_row(
            str(numero),
            tipo,
            leitura.livro.titulo,
            leitura.livro.autor,
            str(leitura.etiqueta or "-"),
            str(leitura.nota or "-"),
            str(leitura.resenha or "-"),
            leitura.inicio_leitura.strftime("%d/%m/%Y") if leitura.inicio_leitura else "-",
            leitura.final_leitura.strftime("%d/%m/%Y") if leitura.final_leitura else "-"
        )

        numero += 1

    return biblioteca_usuario

def exibir_categorias(biblioteca):
    if not biblioteca.lista_categorias:
        console.print("[bold red]Nenhuma categoria criada ainda.[/bold red]")
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

        i = 1

        for leitura in categoria:
            tipo = "Audiobook" if isinstance(leitura, Audiobook) else "Físico/Ebook"

            tabela_categorias.add_row(
                str(i),
                tipo,
                leitura.livro.titulo,
                leitura.livro.autor,
                str(leitura.etiqueta or "-"),
                str(leitura.nota or "-"),
                str(leitura.resenha or "-"),
                leitura.inicio_leitura.strftime("%d/%m/%Y") if leitura.inicio_leitura else "-",
                leitura.final_leitura.strftime("%d/%m/%Y") if leitura.final_leitura else "-"
            )

            i += 1

        console.print(tabela_categorias)


def exibir_tabela_leituras(lista, titulo):
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

    i = 1

    for leitura in lista:
        tipo = "Audiobook" if isinstance(leitura, Audiobook) else "Físico/Ebook"

        tabela.add_row(
            str(i),
            tipo,
            leitura.livro.titulo,
            leitura.livro.autor,
            str(leitura.etiqueta or "-"),
            str(leitura.nota or "-"),
            str(leitura.resenha or "-"),
            leitura.inicio_leitura.strftime("%d/%m/%Y") if leitura.inicio_leitura else "-",
            leitura.final_leitura.strftime("%d/%m/%Y") if leitura.final_leitura else "-"
        )

        i += 1

    console.print(tabela)


def cadastro_login(catalogo):
    print(pyfiglet.figlet_format("my", font="ogre", justify="center"))
    print(pyfiglet.figlet_format("bookshelf", font="ogre", justify="center"))

    for livro in catalogo:
        tabela_catalogo.add_row(
            livro.numero,
            livro.titulo,
            livro.autor,
            livro.sinopse
        )

    console.print(Panel("[bold]Cadastro[/bold]", border_style="white"))

    nome = Prompt.ask("[bold]Nome[/bold]")
    email = Prompt.ask("[bold]Email[/bold]")
    senha = Prompt.ask("[bold]Senha[/bold]", password=True)

    usuario = Usuario(nome, email, senha)
    cadastro_realizado = cadastro_bd(usuario)

    if not cadastro_realizado:
        console.print("[bold red]Este e-mail já está cadastrado. Use outro e-mail.[/bold red]")
        return

    console.print(Panel("[bold]Faça seu login para acessar as funcionalidades![/bold]"))
    console.print(Panel("[bold]Login[/bold]", border_style="white"))

    email_dado = Prompt.ask("[bold]Email[/bold]")
    senha_dada = Prompt.ask("[bold]Senha[/bold]", password=True)

    checagem_banco = login_bd(email_dado)

    if checagem_banco:
        logado = usuario.login(email_dado, senha_dada)

        if logado:
            acesso_anterior = comparar_ultimo_acesso_bd(usuario.email)
            data_visivel = ultimo_acesso_bd(usuario)

            if acesso_anterior:
                usuario.ultimo_acesso = acesso_anterior
                usuario.verificar_inatividade()

            console.print(f"[bold green]Bem-vindo, {usuario.nome}![/]")
            console.print(f"[bold green]Acesso em: {data_visivel.strftime('%d/%m/%Y')}[/]")

            while True:
                console.print("[bold]Você deseja navegar pelo catálogo de livros ou visitar sua biblioteca pessoal?[/bold]")

                opcao = IntPrompt.ask("""
                    [bold][1] Abrir catálogo de livros[/bold]
                    [bold][2] Abrir biblioteca pessoal[/bold]
                    [bold][3] Sair[/bold]
                """)

                if opcao == 1:
                    console.print("[bold green]Navegue pelo catálogo para personalizar sua biblioteca pessoal.[/]")
                    console.print(tabela_catalogo)

                    opcao_livro = IntPrompt.ask("""
                        [bold]Deseja adicionar livros na sua biblioteca?
                        Digite o número do livro escolhido:[/bold]
                    """)

                    if opcao_livro > len(catalogo) or opcao_livro < 1:
                        console.print("[bold red]Livro não encontrado.[/bold red]")
                        continue

                    tipo_livro = IntPrompt.ask("""
                        [bold]Selecione o tipo de leitura:
                        [1] Livro Físico/Ebook
                        [2] Audiobook[/bold]
                    """)

                    novo_livro = catalogo[opcao_livro - 1]

                    if tipo_livro == 1:
                        paginas = IntPrompt.ask("[bold]Informe o total de páginas:[/bold]")

                        minha_biblioteca.adicionar_leitura(
                            novo_livro,
                            formato=1,
                            total_paginas=paginas
                        )

                        biblioteca_usuario = atualizar_tabela_usuario()
                        console.print(biblioteca_usuario)
                        continue

                    elif tipo_livro == 2:
                        duracao_total = Prompt.ask("[bold]Informe a duração do Audiobook (formato HH:MM:SS):[/bold]")
                        narracao = Prompt.ask("[bold]Informe o/a narrador(a):[/bold]")

                        minha_biblioteca.adicionar_leitura(
                            novo_livro,
                            formato=2,
                            narrador=narracao,
                            tempo_total=duracao_total
                        )

                        biblioteca_usuario = atualizar_tabela_usuario()
                        console.print(biblioteca_usuario)
                        continue

                    else:
                        console.print("[bold red]Tipo de leitura inválido.[/bold red]")
                        continue

                elif opcao == 2:
                    biblioteca_usuario = atualizar_tabela_usuario()
                    console.print(biblioteca_usuario)

                    console.print("[bold green]Selecione o que deseja fazer:[/]")
                    opcao_biblioteca = IntPrompt.ask("""
                        [bold][1] Criar categoria[/bold]
                        [bold][2] Excluir livro[/bold]
                        [bold][3] Preencher categoria[/bold]
                        [bold][4] Ver livros em ordem alfabética[/bold]
                        [bold][5] Ver retrospectiva anual[/bold]
                        [bold][6] Definir meta de leitura anual[/bold]
                        [bold][7] Definir meta de leitura mensal[/bold]
                        [bold][8] Adicionar informações de um livro[/bold]
                        [bold][9] Ver livros por categoria[/bold]
                        [bold][10] Voltar para o menu[/bold]
                    """)

                    if opcao_biblioteca == 1:
                        nome_categoria = Prompt.ask("[bold]Digite o nome da categoria[/bold]")
                        minha_biblioteca.adicionar_categoria(nome_categoria)
                        console.print(f"[bold purple]Categoria '{nome_categoria}' adicionada com sucesso![/]")

                    elif opcao_biblioteca == 2:
                        if not minha_biblioteca.lista_leituras:
                            console.print("[bold red]Nenhum livro na biblioteca ainda.[/bold red]")
                        else:
                            biblioteca_usuario = atualizar_tabela_usuario()
                            console.print(biblioteca_usuario)
                            num = IntPrompt.ask("[bold]Digite o número do livro que deseja excluir[/bold]")

                        if num < 1 or num > len(minha_biblioteca.lista_leituras):
                            console.print("[bold red]Livro não encontrado.[/bold red]")
                            continue

                        leitura_escolhida = minha_biblioteca.lista_leituras[num - 1]

                        minha_biblioteca.excluir_livro(leitura_escolhida)

                        biblioteca_usuario = atualizar_tabela_usuario()
                        console.print("[bold green]Livro removido com sucesso![/bold green]")
                        console.print(biblioteca_usuario)
                        exibir_categorias(minha_biblioteca)

                    elif opcao_biblioteca == 3:
                        if not minha_biblioteca.lista_leituras:
                            console.print("[bold red]Nenhum livro na biblioteca ainda.[/bold red]")
                        elif not minha_biblioteca.lista_categorias:
                            console.print("[bold red]Nenhuma categoria criada ainda.[/bold red]")
                        else:
                            console.print(atualizar_tabela_usuario())

                            num_livro = IntPrompt.ask("[bold]Digite o número do livro que deseja adicionar na categoria.[/bold]")

                            if num_livro < 1 or num_livro > len(minha_biblioteca.lista_leituras):
                                console.print("[bold red]Livro não encontrado.[/bold red]")
                                continue

                            leitura_escolhida = minha_biblioteca.lista_leituras[num_livro - 1]

                            i = 1
                            for cat in minha_biblioteca.iterar_categorias():
                                console.print(f"[bold][{i}][/bold] {cat.nome}")
                                i += 1

                            num_categoria = IntPrompt.ask("[bold]Digite o número da categoria[/bold]")

                            if num_categoria < 1 or num_categoria > len(minha_biblioteca.lista_categorias):
                                console.print("[bold red]Categoria não encontrada.[/bold red]")
                                continue

                            categoria_escolhida = minha_biblioteca.lista_categorias[num_categoria - 1]
                            categoria_escolhida.adicionar_leitura(leitura_escolhida)

                            console.print(f"[bold green]Livro adicionado à categoria '{categoria_escolhida.nome}' com sucesso![/bold green]")
                            exibir_categorias(minha_biblioteca)

                    elif opcao_biblioteca == 4:
                        lista_ordenada = minha_biblioteca.ver_ordem_alfabetica()
                        exibir_tabela_leituras(lista_ordenada, "Biblioteca em Ordem Alfabética")

                    elif opcao_biblioteca == 5:
                        ano = IntPrompt.ask("[bold]Digite o ano da sua retrospectiva.[/bold]")
                        retrospectiva_lista = minha_biblioteca.retrospectiva(ano)

                        console.print(f"\n[bold purple]-- Retrospectiva {ano} --[/bold purple]\n")

                        if not retrospectiva_lista:
                            console.print("[red]Lista vazia.[/red]")
                        else:
                            for indice in range(len(retrospectiva_lista)):
                                leitura = retrospectiva_lista[indice]
                                console.print(f"{indice + 1}. {leitura.livro.titulo}")

                    elif opcao_biblioteca == 6:
                        console.print(biblioteca_usuario)

                        num = IntPrompt.ask("[bold]Digite o número do livro desejado para a meta literária ANUAL.[/bold]")

                        if num > len(minha_biblioteca.lista_leituras) or num < 1:
                            console.print("[bold red]Livro não encontrado.[/bold red]")
                            continue

                        objeto_leitura = minha_biblioteca.lista_leituras[num - 1]
                        ano_desejado = IntPrompt.ask("[bold]Digite o ano da sua meta.[/bold]")

                        meta_anual = minha_biblioteca.definir_meta_anual(objeto_leitura)

                        console.print(f"\n[bold purple]-- Meta Literária Anual {ano_desejado} --[/bold purple]\n")

                        if not meta_anual:
                            console.print("[red]Lista vazia.[/red]")
                        else:
                            for indice in range(len(meta_anual)):
                                leitura = meta_anual[indice]
                                console.print(f"{indice + 1}. {leitura.livro.titulo}")

                    elif opcao_biblioteca == 7:
                        console.print(biblioteca_usuario)

                        num = IntPrompt.ask("[bold]Digite o número do livro desejado para a meta literária MENSAL.[/bold]")

                        if num > len(minha_biblioteca.lista_leituras) or num < 1:
                            console.print("[bold red]Livro não encontrado.[/bold red]")
                            continue

                        objeto_leitura = minha_biblioteca.lista_leituras[num - 1]
                        mes = IntPrompt.ask("[bold]Digite o mês da sua meta.[/bold]")

                        meta_mensal = minha_biblioteca.definir_meta_mensal(objeto_leitura)

                        console.print(f"\n[bold purple]-- Meta Literária Mensal {mes} --[/bold purple]\n")

                        if not meta_mensal:
                            console.print("[red]Lista vazia.[/red]")
                        else:
                            for indice in range(len(meta_mensal)):
                                leitura = meta_mensal[indice]
                                console.print(f"{indice + 1}. {leitura.livro.titulo}")

                    elif opcao_biblioteca == 8:
                        console.print(biblioteca_usuario)

                        num = IntPrompt.ask("[bold]Digite o número do livro desejado para adicionar informações.[/bold]")

                        if num < 1 or num > len(minha_biblioteca.lista_leituras):
                            console.print("[bold red]Livro não encontrado.[/bold red]")
                            continue

                        livro_escolhido = minha_biblioteca.lista_leituras[num - 1]

                        while True:
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
                                [bold][8] Sair[/bold]
                                """
                            else:
                                str_menu += """
                                [bold][6] Progresso de leitura (tempo ouvido)[/bold]
                                [bold][7] Avaliar narração[/bold]
                                [bold][8] Sair[/bold]
                                """

                            opcao_desejada = IntPrompt.ask(str_menu)

                            if opcao_desejada == 1:
                                data_informada = Prompt.ask("[bold]Informe a data de início (DD/MM/AAAA):[/bold]")
                                livro_escolhido.data_inicio(data_informada)

                                console.print("[bold green]Data de início de leitura definida.[/bold green]")
                                console.print(atualizar_tabela_usuario())

                            elif opcao_desejada == 2:
                                data_informada = Prompt.ask("[bold]Informe a data de conclusão (DD/MM/AAAA):[/bold]")
                                livro_escolhido.data_final(data_informada)

                                console.print("[bold green]Data de conclusão de leitura definida.[/bold green]")
                                console.print(atualizar_tabela_usuario())

                            elif opcao_desejada == 3:
                                nota_informada = IntPrompt.ask("[bold]Informe a nota que você deseja adicionar (0 a 5):[/bold]")
                                livro_escolhido.atribuir_nota(nota_informada)

                                console.print("[bold green]Nota atribuída.[/bold green]")
                                console.print(atualizar_tabela_usuario())

                            elif opcao_desejada == 4:
                                etiqueta_informada = Prompt.ask("[bold]Escreva a etiqueta que você deseja adicionar:[/bold]")
                                livro_escolhido.adicionar_etiqueta(etiqueta_informada)

                                console.print("[bold green]Etiqueta atribuída.[/bold green]")
                                console.print(atualizar_tabela_usuario())

                            elif opcao_desejada == 5:
                                resenha_informada = Prompt.ask("[bold]Escreva a resenha que você deseja adicionar:[/bold]")
                                livro_escolhido.escrever_resenha(resenha_informada)

                                console.print("[bold green]Resenha atribuída.[/bold green]")
                                console.print(atualizar_tabela_usuario())

                            elif opcao_desejada == 6:
                                porcentagem = livro_escolhido.progresso_leitura()
                                barra = ProgressBar(total=100, completed=porcentagem, width=40, pulse=False)

                                console.print(barra)
                                console.print("\n")
                                console.print(atualizar_tabela_usuario())

                            elif opcao_desejada == 7:
                                if isinstance(livro_escolhido, LivroFisico_Ebook):
                                    emprestimo_pessoa = Prompt.ask("[bold]Informe para quem você emprestou o livro:[/bold]")
                                    livro_escolhido.emprestar(emprestimo_pessoa)

                                    console.print(f"[bold green]Empréstimo registrado para {emprestimo_pessoa}![/bold green]")
                                    console.print(atualizar_tabela_usuario())
                                else:
                                    avaliacao_narracao = Prompt.ask("[bold]Escreva sua avaliação da narração:[/bold]")
                                    livro_escolhido.avaliar_narracao(avaliacao_narracao)

                                    console.print("[bold green]Avaliação da narração registrada![/bold green]")
                                    console.print(atualizar_tabela_usuario())

                            elif opcao_desejada == 8:
                                break

                    elif opcao_biblioteca == 9:
                        console.rule("[bold purple]Sua Biblioteca por Categorias[/bold purple]")
                        exibir_categorias(minha_biblioteca)
                        console.print("\n")

                    elif opcao_biblioteca == 10:
                        continue

                elif opcao == 3:
                    break

        else:
            console.print("[bold red]Email ou senha incorretos.[/]")

    else:
        console.print("[bold red]Email ou senha incorretos.[/]")