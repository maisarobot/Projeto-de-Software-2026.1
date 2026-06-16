# My Bookshelf - Etapa 1

Repositório para a disciplina de **Projeto de Software**  
Engenharia de Computação - UFAL

---

## Site online

O projeto foi preparado para publicação no PythonAnywhere.

**Link do sistema:** [https://maisa.pythonanywhere.com/](https://maisa.pythonanywhere.com)


---

## Descrição do projeto

O **My Bookshelf - Minha Estante** é um sistema para gerenciamento de uma biblioteca pessoal. O usuário pode se cadastrar, fazer login, navegar pelo catálogo de livros, adicionar leituras à sua biblioteca, organizar livros por categorias, registrar avaliações, acompanhar progresso de leitura e visualizar retrospectivas.

O projeto utiliza conceitos de Programação Orientada a Objetos, como **herança**, **classe abstrata**, **polimorfismo**, **composição**, além da aplicação dos padrões de projeto **Factory Method**, **Composite** e **Iterator**.

---

## Tecnologias utilizadas

- Python
- Flask
- SQLite
- HTML/CSS
- Open Library API
- PythonAnywhere
- Argon2 para criptografia de senhas
- Gmail SMTP para envio de e-mail de incentivo

---

## Passo a passo para executar localmente

1. Clone o repositório:

```bash
git clone <url do repositório>
cd Projeto-de-Software-2026.1
```

2. Crie e ative o ambiente virtual:

```bash
python -m venv venv
```

No WSL/Linux/Mac:

```bash
source venv/bin/activate
```

No Windows:

```bash
venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Crie um arquivo chamado `.env` na raiz do projeto:

```env
SECRET_KEY=uma-chave-grande-e-aleatoria
DATABASE_URL=sqlite:///app.db
EMAIL_REMETENTE=seu_email@gmail.com
EMAIL_SENHA=sua_senha_de_app
```

O script para envio de e-mail requer que você defina um e-mail **Gmail** como remetente. Para isso, será necessário gerar uma senha de app, e não usar a senha normal da conta.

Caminho no Google:

1. Acesse [Minha Conta - Google](https://myaccount.google.com/)
2. Vá em **Segurança**
3. Acesse **Senhas de app**
4. Gere uma senha para usar no projeto

> Observação: a verificação em duas etapas precisa estar ativa na conta Google.

5. Execute o projeto:

```bash
python main.py
```

---

## Deploy no PythonAnywhere

Na versão preparada para hospedagem gratuita no PythonAnywhere, o projeto utiliza **SQLite**, evitando a necessidade de conexão externa com PostgreSQL/Neon.

No PythonAnywhere, o arquivo `.env` deve seguir este formato:

```env
SECRET_KEY=uma-chave-grande-e-aleatoria
DATABASE_URL=sqlite:////home/SEU_USUARIO/Projeto-de-Software-2026.1/app.db
EMAIL_REMETENTE=seu_email@gmail.com
EMAIL_SENHA=sua_senha_de_app_do_gmail
```

Após configurar o ambiente virtual, dependências, WSGI e arquivos estáticos, o sistema fica disponível no endereço:

```text
https://SEU_USUARIO.pythonanywhere.com
```

---

## Descrição das funcionalidades

### Funcionalidades do My Bookshelf - Minha Estante

1. Cadastro e Login:

- `class Usuario` (`back.py`)
- `cadastro_bd`, `login_bd`, `ultimo_acesso_bd`, `comparar_ultimo_acesso_bd` (`database.py`)
- Usuário informa nome, e-mail e senha para ter acesso ao seu perfil, biblioteca pessoal e demais funcionalidades do sistema.

2. Catálogo de livros para navegação e seleção:

- `class Livro` (`back.py`)
- Catálogo definido no sistema com objetos da classe `Livro`, contendo título, autor(a) e sinopse.
- O catálogo representa os títulos disponibilizados na aba principal para o usuário interagir e adicionar em seu perfil.

3. Diferenciação entre tipos de leitura: Audiobook e Livro Físico/Ebook:

```python
class LivroFisico_Ebook(Leitura)
class Audiobook(Leitura)
```

- Ao adicionar um livro do catálogo na biblioteca, o usuário pode especificar o tipo de leitura.
- Audiobook: permite avaliar narração com `avaliar_narracao()`.
- Livro físico/ebook: permite gerenciar empréstimos com `emprestar()`.

4. Incentivo via e-mail:

- `class Usuario`, `verificar_inatividade()` (`back.py`)
- `ultimo_acesso_bd()`, `comparar_ultimo_acesso_bd()` (`database.py`)
- Caso o usuário realize login após um período maior que 30 dias, uma mensagem de incentivo é enviada para o e-mail cadastrado.

5. Biblioteca pessoal do usuário:

- `class Biblioteca_Pessoal` (`back.py`)
- Armazena e gerencia os livros selecionados pelo usuário.
- Permite visualizar os livros em ordem alfabética por meio de `ver_ordem_alfabetica()`.

6. Adicionar avaliações para livros da biblioteca:

- `class Leitura`, `atribuir_nota()`, `escrever_resenha()` (`back.py`)
- Para os livros adicionados à biblioteca, é possível atribuir nota de 0 a 5 estrelas e escrever uma resenha literária.

7. Criação de categorias para os livros salvos:

- `class Categoria`, `class Biblioteca_Pessoal` (`back.py`)
- Organização da biblioteca pessoal em categorias criadas pelo usuário.

8. Adicionar etiquetas para livros salvos:

- `class Leitura`, `adicionar_etiqueta()` (`back.py`)
- Usuário pode categorizar de forma mais específica ao adicionar uma etiqueta para o livro salvo.

9. Definição de metas literárias mensais ou anuais:

- `class Biblioteca_Pessoal`, `definir_meta_anual()`, `definir_meta_mensal()` (`back.py`)
- Permite definir uma lista de leitura desejada para determinado mês ou ano.

10. Armazenar datas:

- `class Leitura`, `data_inicio()`, `data_final()` (`back.py`)
- Usuário pode atribuir data de início e conclusão das leituras.

11. Ver retrospectiva de leituras:

- `class Biblioteca_Pessoal`, `retrospectiva()` (`back.py`)
- Visualização de leituras concluídas no ano informado pelo usuário.

12. Acompanhar progresso de leitura:

```python
class LivroFisico_Ebook(Leitura)
class Audiobook(Leitura)
```

- Barra de progressão de leitura adaptada ao tipo cadastrado.
- Para livro físico/ebook, o progresso é calculado pela página atual.
- Para audiobook, o progresso é calculado pelo tempo ouvido.

---

## Uso de Herança e Polimorfismo

### Herança abstrata

```python
class Leitura(ABC):
    (...)

class LivroFisico_Ebook(Leitura):
    (...)

class Audiobook(Leitura):
    (...)
```

Nesse sistema, o livro disponibilizado no catálogo é representado pela `class Livro`, contendo os atributos básicos, como título, autor(a) e sinopse. Ao ser adicionado na biblioteca pessoal, esse livro passa a ser tratado como uma leitura, podendo assumir os formatos `LivroFisico_Ebook` ou `Audiobook`.

Essas duas classes são subclasses da classe abstrata `Leitura`, pois compartilham funcionalidades comuns, como adicionar etiqueta, atribuir nota, escrever resenha e registrar datas. Ao mesmo tempo, cada uma possui comportamentos específicos relacionados ao seu formato.

Métodos concretos herdados pelas subclasses:

- `adicionar_etiqueta()`
- `atribuir_nota()`
- `escrever_resenha()`
- `data_inicio()`
- `data_final()`

Métodos abstratos herdados pelas subclasses:

- `progresso_leitura()`
- `calcular_porcentagem()`

A utilização da herança facilita o gerenciamento dos objetos e evita duplicação de código, mantendo em `Leitura` os comportamentos comuns entre diferentes formas de leitura.

### Polimorfismo

Método abstrato:

```python
class Leitura(ABC):
    (...)

    @abstractmethod
    def progresso_leitura(self):
        pass
```

Chamada do método:

```python
livro_escolhido = minha_biblioteca.lista_leituras[num - 1]
porcentagem = livro_escolhido.progresso_leitura()
```

O polimorfismo acontece quando o sistema chama o método `progresso_leitura()` sem precisar saber se o objeto é um `LivroFisico_Ebook` ou um `Audiobook`.

Cada classe implementa o método de acordo com sua própria regra:

- Em `LivroFisico_Ebook`, o progresso é calculado a partir da página atual e do total de páginas.
- Em `Audiobook`, o progresso é calculado a partir do tempo ouvido e do tempo total.

Assim, a chamada é a mesma, mas o comportamento executado muda conforme o tipo real do objeto.

---

## Padrões de projeto aplicados

### Factory Method

O padrão **Factory Method** foi aplicado para separar a lógica de criação dos objetos de leitura da classe `Biblioteca_Pessoal`.

Antes da aplicação do padrão, a criação dos objetos estava concentrada diretamente no método `adicionar_leitura`, utilizando condicionais para decidir qual classe concreta deveria ser instanciada:

```python
def adicionar_leitura(self, livro, formato, total_paginas=None, narrador=None, tempo_total=None):
    if formato == 1:
        leitura = LivroFisico_Ebook(livro, total_paginas)
    elif formato == 2:
        leitura = Audiobook(livro, narrador, tempo_total)

    self.lista_leituras.append(leitura)
    return leitura
```

O problema dessa abordagem é que a classe `Biblioteca_Pessoal` passa a ter mais de uma responsabilidade. Além de gerenciar a lista de leituras do usuário, ela também fica responsável por saber como cada tipo de leitura deve ser criado.

Para resolver isso, foram criadas classes responsáveis pela criação das leituras:

```python
class LeituraCreator(ABC):
    @abstractmethod
    def factory_method(self, livro, **kwargs):
        pass

    def criar_leitura(self, livro, **kwargs):
        return self.factory_method(livro, **kwargs)
```

Criadores concretos:

```python
class LivroFisicoEbookCreator(LeituraCreator):
    (...)

class AudiobookCreator(LeituraCreator):
    (...)
```

Na classe `Biblioteca_Pessoal`, os criadores são registrados em um dicionário:

```python
_criadores_leitura = {
    FORMATO_LIVRO_FISICO_EBOOK: LivroFisicoEbookCreator,
    FORMATO_AUDIOBOOK: AudiobookCreator,
}
```

Com isso, a biblioteca apenas solicita a criação da leitura ao criador adequado, reduzindo o acoplamento com as classes concretas e facilitando a inclusão de novos formatos no futuro.

---

### Composite

O padrão **Composite** foi aplicado para representar a estrutura da biblioteca pessoal de forma hierárquica.

No sistema, existem objetos simples, como uma leitura individual, e objetos compostos, como categorias e a própria biblioteca pessoal. Com o Composite, esses elementos podem ser tratados a partir de uma interface comum.

Estrutura utilizada:

```python
class ComponenteBiblioteca(ABC):
    def adicionar(self, componente):
        raise NotImplementedError(...)

    def remover(self, componente):
        raise NotImplementedError(...)

    def __iter__(self):
        return BibliotecaIterator([])

    @abstractmethod
    def descricao(self):
        pass
```

No padrão aplicado:

- `ComponenteBiblioteca` é o componente base.
- `Leitura` é a folha, pois representa uma leitura individual e não possui filhos.
- `Categoria` é um composto, pois agrupa várias leituras.
- `Biblioteca_Pessoal` é o composto raiz, pois pode conter leituras e categorias.

Exemplo da folha:

```python
class Leitura(ComponenteBiblioteca, ABC):
    (...)
```

Exemplo de composto:

```python
class Categoria(ComponenteBiblioteca):
    def adicionar(self, componente):
        if not isinstance(componente, Leitura):
            raise TypeError("Categorias só podem receber objetos do tipo Leitura.")

        if componente not in self.itens:
            self.itens.append(componente)

        return componente
```

Na classe `Biblioteca_Pessoal`, a biblioteca também atua como um composto:

```python
class Biblioteca_Pessoal(ComponenteBiblioteca):
    def adicionar(self, componente):
        if not isinstance(componente, (Leitura, Categoria)):
            raise TypeError("A biblioteca só pode receber leituras ou categorias.")

        (...)
```

Esse padrão foi útil porque a biblioteca do usuário não é apenas uma lista simples. Ela pode conter livros individuais e agrupamentos de livros por categoria. Com o Composite, o sistema fica mais organizado e preparado para crescer, por exemplo, permitindo futuramente categorias dentro de outras categorias ou novas formas de agrupamento.

---

### Iterator

O padrão **Iterator** foi aplicado para percorrer os elementos da biblioteca sem expor diretamente a estrutura interna das listas.

A classe responsável por essa iteração é:

```python
class BibliotecaIterator:
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
```

A classe `Categoria` utiliza o iterator para percorrer suas leituras:

```python
class Categoria(ComponenteBiblioteca):
    def __iter__(self):
        return BibliotecaIterator(self.itens)
```

A classe `Biblioteca_Pessoal` também utiliza o iterator para percorrer seus elementos:

```python
class Biblioteca_Pessoal(ComponenteBiblioteca):
    def __iter__(self):
        return BibliotecaIterator(self.itens)

    def iterar_leituras(self):
        return BibliotecaIterator(self.lista_leituras)

    def iterar_categorias(self):
        return BibliotecaIterator(self.lista_categorias)
```

Esse padrão aparece em métodos como:

```python
def ver_ordem_alfabetica(self):
    return sorted(self.iterar_leituras(), key=lambda leitura: leitura.livro.titulo)
```

E também em métodos que percorrem categorias e leituras:

```python
for categoria in self.iterar_categorias():
    (...)

for leitura in self.iterar_leituras():
    (...)
```

O Iterator melhora o encapsulamento, pois o restante do sistema não precisa acessar diretamente as listas internas da biblioteca. Dessa forma, é possível mudar a estrutura de armazenamento no futuro sem alterar todos os pontos do código que percorrem os dados.

---

## Relação entre os padrões aplicados

Os três padrões se complementam no projeto:

- O **Factory Method** organiza a criação dos objetos de leitura.
- O **Composite** organiza a estrutura da biblioteca, categorias e leituras.
- O **Iterator** organiza a forma de percorrer os elementos dessa estrutura.

Com isso, o sistema fica mais modular, com menor acoplamento e mais facilidade de manutenção.

---
