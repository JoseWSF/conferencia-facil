import sqlite3
from data.database import conectar


def salvar_nota(nota):
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO notas_fiscais (numero, fornecedor)
            VALUES (?, ?)
        """, (
            nota["numero"],
            nota["fornecedor"]
        ))

        id_nota = cursor.lastrowid

        for produto in nota["produtos"]:
            cursor.execute("""
                INSERT INTO itens_nota (
                    id_nota,
                    codigo,
                    descricao,
                    quantidade,
                    situacao
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                id_nota,
                produto["codigo"],
                produto["descricao"],
                float(produto["quantidade"]),
                produto["situacao"]
            ))

        return id_nota


def nota_ja_existe(numero, fornecedor):
    with conectar() as conexao:
        resultado = conexao.execute("""
            SELECT id
            FROM notas_fiscais
            WHERE numero = ? AND fornecedor = ?
            LIMIT 1
        """, (numero, fornecedor)).fetchone()

        return resultado is not None


def listar_notas():
    with conectar() as conexao:
        conexao.row_factory = sqlite3.Row

        resultado = conexao.execute("""
            SELECT
                n.id,
                n.numero,
                n.fornecedor,
                COUNT(i.id) AS total_produtos
            FROM notas_fiscais n
            LEFT JOIN itens_nota i
                ON i.id_nota = n.id
            GROUP BY n.id, n.numero, n.fornecedor
            ORDER BY n.id DESC
        """).fetchall()

        return [dict(nota) for nota in resultado]


def buscar_nota_por_id(id_nota):
    with conectar() as conexao:
        conexao.row_factory = sqlite3.Row

        nota = conexao.execute("""
            SELECT id, numero, fornecedor
            FROM notas_fiscais
            WHERE id = ?
        """, (id_nota,)).fetchone()

        if nota is None:
            return None

        produtos = conexao.execute("""
            SELECT codigo, descricao, quantidade, situacao
            FROM itens_nota
            WHERE id_nota = ?
            ORDER BY id
        """, (id_nota,)).fetchall()

        resultado = dict(nota)
        resultado["produtos"] = [dict(produto) for produto in produtos]

        return resultado