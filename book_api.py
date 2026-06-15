import requests

from back import Livro


class LivroApiErro(Exception):
    pass


def buscar_livros_open_library(termo, max_resultados=12):
    termo = termo.strip()

    if not termo:
        return []

    try:
        resposta = requests.get(
            "https://openlibrary.org/search.json",
            params={
                "q": termo,
                "limit": max_resultados,
                "fields": ",".join(
                    [
                        "title",
                        "author_name",
                        "first_publish_year",
                        "cover_i",
                        "number_of_pages_median",
                        "publisher",
                        "isbn",
                        "language",
                    ]
                ),
            },
            timeout=(10, 30),
        )

        resposta.raise_for_status()
        dados = resposta.json()

    except requests.RequestException as erro:
        raise LivroApiErro(f"Não foi possível buscar livros na Open Library: {erro}") from erro

    livros = []

    for indice, item in enumerate(dados.get("docs", []), start=1):
        titulo = item.get("title")
        autores = item.get("author_name", [])

        if not titulo:
            continue

        autor = ", ".join(autores) if autores else "Autor desconhecido"

        livro = Livro(
            numero=str(indice),
            titulo=titulo,
            autor=autor,
            sinopse="Sinopse não disponível.",
        )

        cover_id = item.get("cover_i")

        if cover_id:
            livro.capa = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
        else:
            livro.capa = None

        livro.total_paginas = item.get("number_of_pages_median")
        livro.data_publicacao = item.get("first_publish_year")

        editoras = item.get("publisher", [])
        livro.editora = ", ".join(editoras[:2]) if editoras else None

        isbns = item.get("isbn", [])
        livro.isbn = isbns[0] if isbns else None

        livros.append(livro)

    return livros


def buscar_livros_google_books(termo, max_resultados=12):
    """
    Mantive esse nome para não precisar alterar seu web_app.py.

    Mesmo que o nome diga google_books, agora ele usa Open Library.
    Assim você não precisa mexer no import:
    from book_api import LivroApiErro, buscar_livros_google_books
    """
    return buscar_livros_open_library(termo, max_resultados)