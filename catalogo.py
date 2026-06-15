from back import Livro


def montar_catalogo():
    livro1 = Livro(
        "1",
        "O planeta do exílio",
        "Ursula K. Le Guin",
        "Enquanto o planeta Werel entra em seu longo inverno, tensões desgastam as relações entre suas duas populações: os foviali nômades nativos e a colônia de terranos perdidos. Entretanto, os dois povos compartilham não apenas uma herança genética, mas também inimigos em comum. Será que unirão suas forças ou serão aniquilados?",
    )

    livro2 = Livro(
        "2",
        "Frankenstein",
        "Mary Shelley",
        "O arrepiante romance gótico de Mary Shelley foi concebido quando a autora tinha apenas dezoito anos. A história, que se tornaria a mais célebre ficção de horror, continua sendo uma incursão devastadora pelos limites da invenção humana. Obcecado pela criação da vida, Victor Frankenstein saqueia cemitérios em busca de materiais para construir um novo ser. Mas, quando ganha vida, a estranha criatura é rejeitada por Frankenstein e lança-se com afinco à destruição de seu criador.",
    )

    livro3 = Livro(
        "3",
        "Crime e Castigo",
        "Fiódor Dostoiévski",
        "Publicado em 1866, Crime e castigo é a obra mais célebre de Fiódor Dostoiévski. Neste livro, Raskólnikov, um jovem estudante, pobre e desesperado, perambula pelas ruas de São Petersburgo até cometer um crime que tentará justificar por uma teoria: grandes homens, como César ou Napoleão, foram assassinos absolvidos pela História. Este ato desencadeia uma narrativa labiríntica que arrasta o leitor por becos, tabernas e pequenos cômodos, povoados de personagens que lutam para preservar sua dignidade contra as várias formas da tirania.",
    )

    livro4 = Livro(
        "4",
        "The essence of software",
        "Daniel Jackson",
        "Examining these issues in depth, The Essence of Software introduces a theory of software design that gives new answers to old questions. Daniel Jackson explains that a software system should be viewed as a collection of interacting concepts, breaking the functionality into manageable parts and providing a new framework for thinking about design. Through this radical and original perspective, Jackson lays out a practical and coherent path, accessible to anyone--from strategist and marketer to UX designer, architect, or programmer--for making software that is empowering, dependable, and a delight to use.",
    )

    livro5 = Livro(
        "5",
        "Memórias Póstumas de Brás Cubas",
        "Machado de Assis",
        "Brás Cubas está morto. Mas isso não o impede de relatar em seu livro os acontecimentos de sua existência e de sua grande ideia fixa: lançar o Emplasto Brás Cubas. Deus te livre, leitor, de uma ideia fixa. O medicamento anti-hipocondríaco torna-se o estopim de uma série de lembranças, reminiscências e digressões da vida do defunto autor. Publicado em 1881, escrito com a pena da galhofa e a tinta da melancolia, Memórias Póstumas de Brás Cubas é, possivelmente, o mais importante romance brasileiro de todos os tempos. Inovador, irônico, rebelde, toca no que há de mais profundo no ser humano.",
    )

    livro6 = Livro(
        "6",
        "Monster Vol 1",
        "Naoki Urasawa",
        "Em 1986, na Alemanha ocidental, o promissor neurocirurgião Kenzo Tenma salva um garoto, desobedecendo a ordens superiores. Ele só não imaginava que, ao fazê-lo, influenciaria a vida de inúmeras pessoas, incluindo a sua. Tenma então parte em busca do passado de seu paciente e descobre que Anna, a irmã gêmea do garoto, ainda está viva e corre grande perigo.",
    )

    return [livro1, livro2, livro3, livro4, livro5, livro6]