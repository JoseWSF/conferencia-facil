import sqlite3
from pathlib import Path

import os

CAMINHO_BANCO = Path(
    os.environ.get(
        "CONFERENCIA_DB",
        Path(__file__).resolve().parent / "conferencia.db"
    )
)


def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_banco():
    with conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS notas_fiscais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL,
                fornecedor TEXT NOT NULL,
                chave_acesso TEXT UNIQUE
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS itens_nota (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_nota INTEGER NOT NULL,
                codigo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                quantidade REAL NOT NULL,
                situacao TEXT NOT NULL,
                FOREIGN KEY (id_nota)
                    REFERENCES notas_fiscais(id)
            )
        """)


if __name__ == "__main__":
    criar_banco()
    print("Banco de dados criado com sucesso!")