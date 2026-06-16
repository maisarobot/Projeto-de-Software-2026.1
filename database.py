import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class BancoDadosErro(Exception):
    """Erro tratado para falhas de conexão ou operação no banco de dados."""


def _caminho_banco():
    url = os.getenv("DATABASE_URL", "").strip()

    if not url:
        raise BancoDadosErro(
            "DATABASE_URL não foi configurada. Verifique se o arquivo .env existe e possui essa variável."
        )

    if url.startswith("sqlite:///"):
        caminho = url.replace("sqlite:///", "", 1)
    else:
        caminho = url

    caminho = os.path.expanduser(caminho)
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    return caminho


def _conectar():
    try:
        conexao = sqlite3.connect(_caminho_banco())
        conexao.row_factory = sqlite3.Row
        return conexao
    except sqlite3.Error as erro:
        raise BancoDadosErro(f"Não foi possível conectar ao banco de dados: {erro}") from erro


def criar_tabela_usuarios():
    try:
        with _conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS perfis_usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_usuario TEXT NOT NULL,
                    email_usuario TEXT NOT NULL UNIQUE,
                    senha_usuario TEXT NOT NULL,
                    ultimo_acesso TEXT
                )
            """)
            conexao.commit()
    except BancoDadosErro:
        raise
    except sqlite3.Error as erro:
        raise BancoDadosErro(f"Erro ao preparar tabela de usuários: {erro}") from erro


def cadastro_bd(usuario):
    criar_tabela_usuarios()

    try:
        with _conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO perfis_usuarios
                (nome_usuario, email_usuario, senha_usuario, ultimo_acesso)
                VALUES (?, ?, ?, ?)
            """, (usuario.nome, usuario.email, usuario.senha, None))
            conexao.commit()
        return True

    except sqlite3.IntegrityError:
        return False
    except BancoDadosErro:
        raise
    except sqlite3.Error as erro:
        raise BancoDadosErro(f"Erro ao cadastrar usuário: {erro}") from erro


def buscar_usuario_por_email_bd(string_email):
    criar_tabela_usuarios()

    try:
        with _conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT nome_usuario, email_usuario, senha_usuario, ultimo_acesso
                FROM perfis_usuarios
                WHERE email_usuario = ?
            """, (string_email,))

            resultado = cursor.fetchone()

        if not resultado:
            return None

        return {
            "nome": resultado["nome_usuario"],
            "email": resultado["email_usuario"],
            "senha": resultado["senha_usuario"],
            "ultimo_acesso": resultado["ultimo_acesso"],
        }

    except BancoDadosErro:
        raise
    except sqlite3.Error as erro:
        raise BancoDadosErro(f"Erro ao buscar usuário: {erro}") from erro


def login_bd(string_email):
    usuario = buscar_usuario_por_email_bd(string_email)

    if not usuario:
        return False

    return usuario["senha"]


def ultimo_acesso_bd(usuario):
    criar_tabela_usuarios()

    try:
        ultimo_acesso = usuario.ultimo_acesso.isoformat(sep=" ") if usuario.ultimo_acesso else None

        with _conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE perfis_usuarios
                SET ultimo_acesso = ?
                WHERE email_usuario = ?
            """, (ultimo_acesso, usuario.email))
            conexao.commit()
        return usuario.ultimo_acesso

    except BancoDadosErro:
        raise
    except sqlite3.Error as erro:
        raise BancoDadosErro(f"Erro ao atualizar último acesso: {erro}") from erro


def comparar_ultimo_acesso_bd(string_email):
    usuario = buscar_usuario_por_email_bd(string_email)

    if usuario and usuario["ultimo_acesso"]:
        return usuario["ultimo_acesso"]

    return None
