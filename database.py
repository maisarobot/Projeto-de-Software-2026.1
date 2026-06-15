import os

import psycopg2
from dotenv import load_dotenv
from psycopg2 import errors

load_dotenv()


class BancoDadosErro(Exception):
    """Erro tratado para falhas de conexão ou operação no banco de dados."""


def _database_url():
    url = os.getenv("DATABASE_URL")

    if not url:
        raise BancoDadosErro(
            "DATABASE_URL não foi configurada. Verifique se o arquivo .env existe e possui essa variável."
        )

    return url


def _conectar():
    try:
        return psycopg2.connect(_database_url())
    except psycopg2.Error as erro:
        raise BancoDadosErro(f"Não foi possível conectar ao banco de dados: {erro}") from erro


def criar_tabela_usuarios():
    try:
        with _conectar() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS perfis_usuarios (
                        id SERIAL NOT NULL PRIMARY KEY,
                        nome_usuario TEXT NOT NULL,
                        email_usuario TEXT NOT NULL UNIQUE,
                        senha_usuario TEXT NOT NULL,
                        ultimo_acesso TIMESTAMP
                    )
                """)
    except BancoDadosErro:
        raise
    except psycopg2.Error as erro:
        raise BancoDadosErro(f"Erro ao preparar tabela de usuários: {erro}") from erro


def cadastro_bd(usuario):
    criar_tabela_usuarios()

    try:
        with _conectar() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO perfis_usuarios
                    (nome_usuario, email_usuario, senha_usuario, ultimo_acesso)
                    VALUES (%s, %s, %s, %s)
                """, (usuario.nome, usuario.email, usuario.senha, None))
        return True

    except errors.UniqueViolation:
        return False
    except BancoDadosErro:
        raise
    except psycopg2.Error as erro:
        raise BancoDadosErro(f"Erro ao cadastrar usuário: {erro}") from erro


def buscar_usuario_por_email_bd(string_email):
    criar_tabela_usuarios()

    try:
        with _conectar() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute("""
                    SELECT nome_usuario, email_usuario, senha_usuario, ultimo_acesso
                    FROM perfis_usuarios
                    WHERE email_usuario = %s
                """, (string_email,))

                resultado = cursor.fetchone()

        if not resultado:
            return None

        nome, email, senha, ultimo_acesso = resultado
        return {
            "nome": nome,
            "email": email,
            "senha": senha,
            "ultimo_acesso": ultimo_acesso,
        }

    except BancoDadosErro:
        raise
    except psycopg2.Error as erro:
        raise BancoDadosErro(f"Erro ao buscar usuário: {erro}") from erro


def login_bd(string_email):
    usuario = buscar_usuario_por_email_bd(string_email)

    if not usuario:
        return False

    return usuario["senha"]


def ultimo_acesso_bd(usuario):
    criar_tabela_usuarios()

    try:
        with _conectar() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute("""
                    UPDATE perfis_usuarios
                    SET ultimo_acesso = %s
                    WHERE email_usuario = %s
                """, (usuario.ultimo_acesso, usuario.email))
        return usuario.ultimo_acesso

    except BancoDadosErro:
        raise
    except psycopg2.Error as erro:
        raise BancoDadosErro(f"Erro ao atualizar último acesso: {erro}") from erro


def comparar_ultimo_acesso_bd(string_email):
    usuario = buscar_usuario_por_email_bd(string_email)

    if usuario and usuario["ultimo_acesso"]:
        return usuario["ultimo_acesso"]

    return None