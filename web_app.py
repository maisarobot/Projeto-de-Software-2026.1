import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for

from back import Audiobook, Biblioteca_Pessoal, Livro, LivroFisico_Ebook, Usuario
from book_api import LivroApiErro, buscar_livros_google_books
from database import BancoDadosErro, buscar_usuario_por_email_bd, cadastro_bd, ultimo_acesso_bd

load_dotenv()

bibliotecas_por_email = {}


def criar_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "troque-esta-chave-em-producao")

    @app.context_processor
    def injetar_usuario():
        return {"usuario_logado": session.get("usuario_nome")}

    def login_obrigatorio(funcao):
        @wraps(funcao)
        def wrapper(*args, **kwargs):
            if not session.get("usuario_email"):
                flash("Faça login para acessar essa página.", "erro")
                return redirect(url_for("login"))

            return funcao(*args, **kwargs)

        return wrapper

    def obter_biblioteca_usuario():
        email = session.get("usuario_email")

        if not email:
            raise ValueError("Usuário não está logado.")

        if email not in bibliotecas_por_email:
            bibliotecas_por_email[email] = Biblioteca_Pessoal()

        return bibliotecas_por_email[email]

    def obter_leitura_por_indice(biblioteca, indice):
        try:
            indice = int(indice)
        except ValueError as erro:
            raise ValueError("Livro inválido.") from erro

        if indice < 0 or indice >= len(biblioteca.lista_leituras):
            raise ValueError("Livro não encontrado na biblioteca.")

        return biblioteca.lista_leituras[indice]

    def obter_categoria_por_indice(biblioteca, indice):
        try:
            indice = int(indice)
        except ValueError as erro:
            raise ValueError("Categoria inválida.") from erro

        if indice < 0 or indice >= len(biblioteca.lista_categorias):
            raise ValueError("Categoria não encontrada.")

        return biblioteca.lista_categorias[indice]

    @app.errorhandler(404)
    def pagina_nao_encontrada(_erro):
        return render_template("erro.html", mensagem="Página não encontrada."), 404

    @app.errorhandler(500)
    def erro_interno(_erro):
        return render_template(
            "erro.html",
            mensagem="Ocorreu um erro inesperado, mas o site continua disponível.",
        ), 500

    @app.route("/")
    def index():
        if session.get("usuario_email"):
            return redirect(url_for("dashboard"))

        return render_template("index.html")

    @app.route("/cadastro", methods=["GET", "POST"])
    def cadastro():
        if request.method == "POST":
            try:
                nome = request.form.get("nome", "").strip()
                email = request.form.get("email", "").strip()
                senha = request.form.get("senha", "")

                if not nome or not email or not senha:
                    flash("Nome, e-mail e senha são obrigatórios.", "erro")
                    return redirect(url_for("cadastro"))

                usuario = Usuario(nome, email, senha)
                cadastro_realizado = cadastro_bd(usuario)

                if not cadastro_realizado:
                    flash("Este e-mail já está cadastrado. Faça login ou use outro e-mail.", "erro")
                    return redirect(url_for("cadastro"))

                flash("Cadastro realizado com sucesso. Agora faça login.", "sucesso")
                return redirect(url_for("login"))

            except BancoDadosErro as erro:
                flash(str(erro), "erro")
                return redirect(url_for("cadastro"))
            except Exception as erro:
                flash(f"Não foi possível cadastrar: {erro}", "erro")
                return redirect(url_for("cadastro"))

        return render_template("cadastro.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            try:
                email = request.form.get("email", "").strip()
                senha = request.form.get("senha", "")

                if not email or not senha:
                    flash("E-mail e senha são obrigatórios.", "erro")
                    return redirect(url_for("login"))

                dados_usuario = buscar_usuario_por_email_bd(email)

                if not dados_usuario:
                    flash("E-mail ou senha incorretos.", "erro")
                    return redirect(url_for("login"))

                usuario = Usuario.carregar_do_banco(
                    nome=dados_usuario["nome"],
                    email=dados_usuario["email"],
                    senha_hash=dados_usuario["senha"],
                    ultimo_acesso=dados_usuario["ultimo_acesso"],
                )

                acesso_anterior = usuario.ultimo_acesso

                if not usuario.login(email, senha):
                    flash("E-mail ou senha incorretos.", "erro")
                    return redirect(url_for("login"))

                acesso_atual = ultimo_acesso_bd(usuario)

                if acesso_anterior:
                    usuario.ultimo_acesso = acesso_anterior
                    usuario.verificar_inatividade()
                    usuario.ultimo_acesso = acesso_atual

                session["usuario_email"] = usuario.email
                session["usuario_nome"] = usuario.nome

                flash(f"Bem-vindo, {usuario.nome}!", "sucesso")
                return redirect(url_for("dashboard"))

            except BancoDadosErro as erro:
                flash(str(erro), "erro")
                return redirect(url_for("login"))
            except Exception as erro:
                flash(f"Não foi possível entrar: {erro}", "erro")
                return redirect(url_for("login"))

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Você saiu do sistema.", "sucesso")
        return redirect(url_for("index"))

    @app.route("/dashboard")
    @login_obrigatorio
    def dashboard():
        biblioteca = obter_biblioteca_usuario()

        return render_template(
            "dashboard.html",
            total_livros=len(biblioteca.lista_leituras),
            total_categorias=len(biblioteca.lista_categorias),
        )

    @app.route("/catalogo")
    @login_obrigatorio
    def pagina_catalogo():
        termo = request.args.get("q", "").strip()
        catalogo = []

        if termo:
            try:
                catalogo = buscar_livros_google_books(termo)
            except LivroApiErro as erro:
                flash(str(erro), "erro")

        return render_template(
            "catalogo.html",
            catalogo=catalogo,
            termo=termo,
        )

    @app.route("/catalogo/adicionar", methods=["POST"])
    @login_obrigatorio
    def adicionar_catalogo():
        termo = request.form.get("termo", "").strip()

        try:
            biblioteca = obter_biblioteca_usuario()

            titulo = request.form.get("titulo", "").strip()
            autor = request.form.get("autor", "").strip()
            sinopse = request.form.get("sinopse", "").strip()
            numero = request.form.get("numero", "0").strip()
            tipo = request.form.get("tipo")

            if not titulo:
                flash("Livro inválido: título não informado.", "erro")
                return redirect(url_for("pagina_catalogo", q=termo))

            livro = Livro(
                numero=numero,
                titulo=titulo,
                autor=autor or "Autor desconhecido",
                sinopse=sinopse or "Sinopse não disponível.",
            )

            if tipo == "fisico_ebook":
                total_paginas = request.form.get("total_paginas", "").strip()

                if not total_paginas:
                    flash("Informe o total de páginas.", "erro")
                    return redirect(url_for("pagina_catalogo", q=termo))

                biblioteca.adicionar_leitura(
                    livro,
                    formato=1,
                    total_paginas=int(total_paginas),
                )

            elif tipo == "audiobook":
                narrador = request.form.get("narrador", "").strip()
                tempo_total = request.form.get("tempo_total", "").strip()

                biblioteca.adicionar_leitura(
                    livro,
                    formato=2,
                    narrador=narrador,
                    tempo_total=tempo_total,
                )

            else:
                flash("Selecione um tipo de leitura válido.", "erro")
                return redirect(url_for("pagina_catalogo", q=termo))

            flash("Livro adicionado à biblioteca.", "sucesso")
            return redirect(url_for("biblioteca"))

        except Exception as erro:
            flash(f"Não foi possível adicionar o livro: {erro}", "erro")
            return redirect(url_for("pagina_catalogo", q=termo))

    @app.route("/biblioteca")
    @login_obrigatorio
    def biblioteca():
        biblioteca_usuario = obter_biblioteca_usuario()
        leituras = list(biblioteca_usuario.iterar_leituras())

        return render_template(
            "biblioteca.html",
            biblioteca=biblioteca_usuario,
            leituras=leituras,
        )

    @app.route("/biblioteca/ordem-alfabetica")
    @login_obrigatorio
    def biblioteca_ordem_alfabetica():
        biblioteca_usuario = obter_biblioteca_usuario()
        leituras = biblioteca_usuario.ver_ordem_alfabetica()

        return render_template(
            "biblioteca.html",
            biblioteca=biblioteca_usuario,
            leituras=leituras,
            titulo="Biblioteca em ordem alfabética",
        )

    @app.route("/biblioteca/excluir/<int:indice>", methods=["POST"])
    @login_obrigatorio
    def excluir_livro(indice):
        try:
            biblioteca_usuario = obter_biblioteca_usuario()
            leitura = obter_leitura_por_indice(biblioteca_usuario, indice)
            biblioteca_usuario.excluir_livro(leitura)

            flash("Livro removido da biblioteca.", "sucesso")
        except Exception as erro:
            flash(f"Não foi possível excluir o livro: {erro}", "erro")

        return redirect(url_for("biblioteca"))

    @app.route("/livro/<int:indice>/editar", methods=["GET", "POST"])
    @login_obrigatorio
    def editar_livro(indice):
        biblioteca_usuario = obter_biblioteca_usuario()

        try:
            leitura = obter_leitura_por_indice(biblioteca_usuario, indice)
        except Exception as erro:
            flash(str(erro), "erro")
            return redirect(url_for("biblioteca"))

        if request.method == "POST":
            try:
                inicio = request.form.get("inicio_leitura", "").strip()
                final = request.form.get("final_leitura", "").strip()
                etiqueta = request.form.get("etiqueta", "").strip()
                resenha = request.form.get("resenha", "").strip()
                nota = request.form.get("nota", "").strip()

                leitura.data_inicio(inicio)
                leitura.data_final(final)
                leitura.adicionar_etiqueta(etiqueta or None)
                leitura.escrever_resenha(resenha or None)

                if nota:
                    leitura.atribuir_nota(int(nota))
                else:
                    leitura.remover_nota()

                if isinstance(leitura, LivroFisico_Ebook):
                    pagina_atual = request.form.get("pagina_atual", "").strip()
                    emprestado_para = request.form.get("emprestado_para", "").strip()

                    if pagina_atual:
                        leitura.atualizar_pagina_atual(pagina_atual)

                    leitura.emprestar(emprestado_para or None)

                elif isinstance(leitura, Audiobook):
                    tempo_ouvido = request.form.get("tempo_ouvido", "").strip()
                    nota_narracao = request.form.get("nota_narracao", "").strip()

                    if tempo_ouvido:
                        leitura.atualizar_tempo_ouvido(tempo_ouvido)

                    leitura.avaliar_narracao(nota_narracao or None)

                flash("Informações atualizadas.", "sucesso")
                return redirect(url_for("biblioteca"))

            except Exception as erro:
                flash(f"Não foi possível salvar as informações: {erro}", "erro")
                return redirect(url_for("editar_livro", indice=indice))

        return render_template("editar_livro.html", leitura=leitura, indice=indice)

    @app.route("/categorias", methods=["GET", "POST"])
    @login_obrigatorio
    def categorias():
        biblioteca_usuario = obter_biblioteca_usuario()

        if request.method == "POST":
            try:
                nome = request.form.get("nome", "").strip()

                if not nome:
                    flash("Informe o nome da categoria.", "erro")
                    return redirect(url_for("categorias"))

                biblioteca_usuario.adicionar_categoria(nome)

                flash("Categoria criada com sucesso.", "sucesso")
                return redirect(url_for("categorias"))

            except Exception as erro:
                flash(f"Não foi possível criar a categoria: {erro}", "erro")
                return redirect(url_for("categorias"))

        return render_template("categorias.html", biblioteca=biblioteca_usuario)

    @app.route("/categorias/<int:indice_categoria>")
    @login_obrigatorio
    def categoria_detalhe(indice_categoria):
        biblioteca_usuario = obter_biblioteca_usuario()

        try:
            categoria = obter_categoria_por_indice(biblioteca_usuario, indice_categoria)

            return render_template(
                "categoria_detalhe.html",
                biblioteca=biblioteca_usuario,
                categoria=categoria,
                indice_categoria=indice_categoria,
            )

        except Exception as erro:
            flash(str(erro), "erro")
            return redirect(url_for("categorias"))

    @app.route("/categorias/<int:indice_categoria>/adicionar-livro", methods=["POST"])
    @login_obrigatorio
    def adicionar_livro_categoria(indice_categoria):
        biblioteca_usuario = obter_biblioteca_usuario()

        try:
            indice_livro = request.form.get("indice_livro")

            leitura = obter_leitura_por_indice(biblioteca_usuario, indice_livro)
            categoria = obter_categoria_por_indice(biblioteca_usuario, indice_categoria)

            if leitura in categoria.leituras_adicionadas:
                flash("Este livro já está nessa categoria.", "erro")
                return redirect(url_for("categoria_detalhe", indice_categoria=indice_categoria))

            categoria.adicionar_leitura(leitura)

            flash("Livro adicionado à categoria.", "sucesso")
            return redirect(url_for("categoria_detalhe", indice_categoria=indice_categoria))

        except Exception as erro:
            flash(f"Não foi possível adicionar o livro na categoria: {erro}", "erro")
            return redirect(url_for("categoria_detalhe", indice_categoria=indice_categoria))

    @app.route("/categorias/<int:indice_categoria>/remover-livro/<int:indice_livro>", methods=["POST"])
    @login_obrigatorio
    def remover_livro_categoria(indice_categoria, indice_livro):
        biblioteca_usuario = obter_biblioteca_usuario()

        try:
            categoria = obter_categoria_por_indice(biblioteca_usuario, indice_categoria)
            leitura = obter_leitura_por_indice(biblioteca_usuario, indice_livro)

            if leitura not in categoria.leituras_adicionadas:
                flash("Este livro não está nessa categoria.", "erro")
                return redirect(url_for("categoria_detalhe", indice_categoria=indice_categoria))

            categoria.retirar_livro(leitura)

            flash("Livro removido da categoria.", "sucesso")
            return redirect(url_for("categoria_detalhe", indice_categoria=indice_categoria))

        except Exception as erro:
            flash(f"Não foi possível remover o livro da categoria: {erro}", "erro")
            return redirect(url_for("categoria_detalhe", indice_categoria=indice_categoria))

    @app.route("/retrospectiva", methods=["GET", "POST"])
    @login_obrigatorio
    def retrospectiva():
        biblioteca_usuario = obter_biblioteca_usuario()
        leituras = None
        ano = None

        if request.method == "POST":
            try:
                ano = int(request.form.get("ano", ""))
                leituras = biblioteca_usuario.retrospectiva(ano)
            except Exception as erro:
                flash(f"Não foi possível gerar a retrospectiva: {erro}", "erro")
                return redirect(url_for("retrospectiva"))

        return render_template("retrospectiva.html", leituras=leituras, ano=ano)

    return app