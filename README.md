
# My Bookshelf - Etapa 1

Repositório para a disciplina de Projeto de Software  
Engenharia de computação - UFAL  
---
### Passo a passo para executar   

1. `git clone <url do repositório>`  

O banco de dados para a primeira parte do projeto começou a ser implementado para cadastro e login, pelo uso do **PostgreSQL** e hospedagem no **NeonConsole**. Para ter acesso à tabela gerada:
1. Acesse: [Neon Console](https://console.neon.tech/) e crie uma conta gratuitamente; 
2. Crie um novo projeto (banco de dados) para gerar uma `DATABASE_URL`; 
3. Utilize essa URL no seu arquivo **.env**. 

O script para envio do e-mail requer que você defina um e-mail **Gmail**  como remetente. Para isso, você precisará acessar/gerar sua senha de app (não é a senha da conta) em:
1. [Minha Conta - Google](https://myaccount.google.com/)
2. Segurança -> Senhas de app   
- **Obs.:** A verificação em duas etapas precisa estar ativa.

Após isso, crie um arquivo nomeado **.env** na raiz do projeto e inclua suas variáveis:
```
EMAIL_REMETENTE=seu_email@gmail.com
EMAIL_SENHA=sua_senha_de_app
DATABASE_URL=url_criada_do_neon
```

**Após configurar os passos acima, execute:**  
1. `python -m venv venv`  
2.  - WSL/Linux/Mac -> `source venv/bin/activate`  
    - Windows -> `venv\Scripts\activate`  

3.`pip install -r requirements.txt`  
4.`python main.py`  

## Descrição das funcionalidades
### Funcionalidades do My Bookshelf - Minha Estante
1. Cadastro e Login:  
- `class Usuario`(back.py)
- `cadastro_bd,login_bd,ultimo_acesso_bd,comparar_ultimo_acesso_bd`(database.py)
- `cadastro_login()`(interface.py)
- Usuário informa nome, e-mail e senha para ter acesso ao seu perfil (biblioteca pessoal) e outras funcionalidades do sistema.  

2. Catálogo de livros para navegação e seleção;  
- `class Livro`(back.py)
- `catalogo = [livro1, livro2, livro3, livro4, livro5, livro6]` (main.py)
- Criação dos objetos da classe Livro passando os atributos nome, autor(a) e sinopse, que serão os elementos da lista `catálogo`.
- O catálogo representa os títulos disponibilizados na aba principal para o usuário interagir e adicionar em seu perfil.

3. Diferenciar tipos de leitura: Audiobook e Livro Físico / Ebook (avaliar narração/efinir empréstimo)
-   ``` 
    class LivroFisico_Ebook(Leitura)
    class Audiobook(Leitura)
    ``` 
    (back.py)
- Ao adicionar um livro do catálogo na biblioteca, o usuário pode especificar o tipo de leitura (audiobook ou livro físico/ebook) e ter acesso a funções específicas para cada caso.
    - Audiobook: `avaliar_narracao()` 
    - Livro físico/ebook: `emprestar()` (gerenciar empréstimos daquela edição)

4. Incentivo via e-mail;  
- `class Usuario, verificar_inatividade()`(back.py)
- `cadastro_login()` (interface.py)  
- `ultimo_acesso_bd(), comparar_ultimo_acesso_bd()` (database.py)
- Caso o usuário realize o login após um período maior que 30 dias, uma mensagem de incentivo é enviada para o e-mail cadastrado.

5. Biblioteca pessoal do usuário: adição de livros no perfil e visualização em ordem alfabética;  
- `class Biblioteca_Pessoal,ver_ordem_alfabetica() (uma das funções)` (back.py)
- Local para armazenar e gerenciar os livros selecionados pelo usuário, acesso às funções de gerenciamento de leituras.

6. Adicionar avaliações para livros da biblioteca (nota de 0 a 5 ou resenha literária);
- `class Leitura,atribuir_nota(),escrever_resenha()`(back.py)
- Para os livros adicionados na biblioteca, é possível atribuir uma nota de 0 a 5 estrelas e também adicionar uma avaliação/resenha por escrito sobre o livro selecionado.

7. Criação de categorias para os livros salvos na biblioteca;
- `class Categoria,class Biblioteca_Pessoal` (back.py)
- Organização da biblioteca pessoal: criar categorias e preencher/visualizar com livros salvos.

8. Adicionar etiquetas para livros salvos na biblioteca;  
- `class Leitura,adicionar_etiqueta()` (back.py)
- Usuário pode categorizar de forma mais específica ao adicionar uma etiqueta para o livro salvo em sua biblioteca, contendo qualquer informação desejada.

9. Definição de metas literárias mensais ou anuais; 
- `class Biblioteca_Pessoal,definir_meta_anual(),definir_meta_mensal()`(back.py)
- Dentro da biblioteca do usuário, há a possibilidade de definir uma meta de livros (lista de leitura desejada) para determinado ano ou mês.

10. Armazenar datas;  
- `class Leitura,data_inicio(),data_final()` (back.py)
- Usuário pode atribuir data de início e conclusão de leituras em sua biblioteca.

11. Ver retrospectiva de leituras; 
- `class Biblioteca_Pessoal, retrospectiva()` (back.py)
- Visualização de leituras concluídas no ano informado pelo usuário.

12. Acompanhar progresso de leitura;  
-   ``` 
    class LivroFisico_Ebook(Leitura)
    class Audiobook(Leitura)
    ```
    (back.py)
- Barra de progressão de leitura (porcentagem atualizada) adaptada para o tipo de leitura cadastrada. Usuário informa timestamp (audiobook) ou página atual (livro físico/ebook).


## Uso de Herança e Polimorfismo

### Herança Abstrata
```
class Leitura(ABC):
(...)
class LivroFisico_Ebook(Leitura):
(...)
class Audiobook(Leitura):
(...)
```

- Nesse sistema, o livro disponibilizado no catálogo é da `class Livro` e possui a base de atributos (passados por composição), como título, autor(a) e sinopse. Ao adicionar o livro na biblioteca, ele ganha acesso a mais atributos e métodos que estarão visíveis apenas para o usuário. Esses livros salvos pelo usuário serão da `class LivroFisico_Ebook` ou da `class Audiobook` e são subclasses da superclasse `Leitura` (que é abstrata, não instanciada diretamente) pela necessidade de compartilhar as mesmas funcionalidades, porém, pela natureza distinta de cada forma de leitura, também possuem seu método específico (`emprestar()` e `avaliar_narracao()`) e implementação distinta do método abstrato `progresso_leitura()` declarado em `Leitura`.  
- Métodos concretos herdados pelas subclasses: `adicionar_etiqueta()`,`atribuir_nota()`,`escrever_resenha()`,`data_inicio()`,`data_final()`  
- Método abstrato herdado pelas subclasses: `progresso_leitura()` 
- A utilização da herança facilitou o **gerenciamento** dos objetos e a **organização**  de seus métodos base, suas características em comum e seus diferenciais. O uso também demonstra a praticidade de incrementar funcionalidades específicas para cada tipo de leitura.  


### Polimorfismo
Método abstrato:
```
class Leitura(ABC):
    (...)
    @abstractmethod
    def progresso_leitura(self):
```
Chamada do método:
```
    (...)
    minha_biblioteca = Biblioteca_Pessoal()
    (...)
    livro_escolhido = minha_biblioteca.lista_leituras[num-1]
    porcentagem = livro_escolhido.progresso_leitura()
```
- O polimorfismo acontece quando o usuário seleciona a opção de ver o progresso de leitura para o livro selecionado. Antes disso, no momento em que ele especifica o tipo de leitura ao adicionar na biblioteca, o sistema irá pedir a duração total (Audiobook) ou o total de páginas (LivroFisico_Ebook) e armazenar. Para cada caso, o método será implementado de forma distinta ao ser chamado. Um precisará passar pela conversão de tempo usando a biblioteca `datetime` e o outro poderá calcular a porcentagem diretamente. Ambos também informam quando a leitura estiver marcada como 100% concluída.
- O objeto (livro selecionado pelo índice) é armazenado em `livro_escolhido` e o método `progresso_leitura` é acionado sem distinção na hora da chamada. O tratamento diferente ocorrerá apenas dentro das determinadas classes.
- O uso do polimorfismo é essencial para reuso de código e gerenciamento de objetos na funcionalidade existente e para futuras implementações.
