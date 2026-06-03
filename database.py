import os
import psycopg2

from dotenv import load_dotenv

load_dotenv()

conexao = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conexao.cursor()


def criar_tabela_usuarios():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perfis_usuarios (
            id SERIAL NOT NULL PRIMARY KEY,
            nome_usuario TEXT NOT NULL,
            email_usuario TEXT NOT NULL UNIQUE,
            senha_usuario TEXT NOT NULL,
            ultimo_acesso TIMESTAMP
        )
    """)

    conexao.commit()


def cadastro_bd(usuario):
    criar_tabela_usuarios()

    try:
        cursor.execute("""
            INSERT INTO perfis_usuarios
            (nome_usuario, email_usuario, senha_usuario, ultimo_acesso)
            VALUES (%s, %s, %s, %s)
        """, (usuario.nome, usuario.email, usuario.senha, None))

        conexao.commit()
        return True

    except psycopg2.errors.UniqueViolation:
        conexao.rollback()
        return False


def login_bd(string_email):
    criar_tabela_usuarios()

    cursor.execute("""
        SELECT senha_usuario 
        FROM perfis_usuarios 
        WHERE email_usuario = %s
    """, (string_email,))

    busca = cursor.fetchone()

    if not busca:
        return False

    return busca[0]


def ultimo_acesso_bd(usuario):
    criar_tabela_usuarios()

    cursor.execute("""
        UPDATE perfis_usuarios 
        SET ultimo_acesso = %s 
        WHERE email_usuario = %s
    """, (usuario.ultimo_acesso, usuario.email))

    conexao.commit()
    return usuario.ultimo_acesso


def comparar_ultimo_acesso_bd(string_email):
    criar_tabela_usuarios()

    cursor.execute("""
        SELECT ultimo_acesso 
        FROM perfis_usuarios 
        WHERE email_usuario = %s
    """, (string_email,))

    resultado = cursor.fetchone()

    if resultado and resultado[0]:
        return resultado[0]

    return None