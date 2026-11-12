from pathlib import Path
from business.nota_fiscal import ler_nota_fiscal
from business.conferencia import conferir_produtos
from app import app
from io import BytesIO
import data.database as database
from data.database import criar_banco
import pytest
import xml.etree.ElementTree as ET


def test_leitura_xml():
    caminho = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "nota_fiscal_4582.xml"
    )

    nota = ler_nota_fiscal(caminho)

    assert nota["numero"] == "4582"
    assert nota["fornecedor"] == "Editora Exemplo"
    assert len(nota["produtos"]) == 2

    assert nota["produtos"][0]["codigo"] == "001"
    assert nota["produtos"][0]["quantidade"] == "5"

    assert nota["produtos"][1]["codigo"] == "002"
    assert nota["produtos"][1]["quantidade"] == "3"

def test_correspondencia_pedido():
    produtos = [
        {
            "codigo": "001",
            "descricao": "Livro A",
            "quantidade": "5"
        },
        {
            "codigo": "002",
            "descricao": "Livro B",
            "quantidade": "3"
        }
    ]

    resultado = conferir_produtos(produtos)

    assert resultado[0]["correspondencia"] is True
    assert resultado[0]["situacao"] == (
        "Possível correspondência — Pedido 125"
    )

    assert resultado[1]["correspondencia"] is False
    assert resultado[1]["situacao"] == (
        "Nenhuma correspondência encontrada"
    )

def test_xml_invalido(tmp_path):
    caminho = tmp_path / "nota_invalida.xml"

    caminho.write_text(
        "<nota><produto>Livro A</nota>",
        encoding="utf-8"
    )

    with pytest.raises(ET.ParseError):
        ler_nota_fiscal(caminho)

def test_pagina_inicial():
    app.config["TESTING"] = True

    cliente = app.test_client()
    resposta = cliente.get("/")

    assert resposta.status_code == 200

def test_pagina_importacao():
    cliente = app.test_client()

    resposta = cliente.get("/importacao")

    assert resposta.status_code == 200


def test_pagina_historico():
    cliente = app.test_client()

    resposta = cliente.get("/historico")

    assert resposta.status_code == 200


def test_nota_inexistente():
    cliente = app.test_client()

    resposta = cliente.get("/nota/999999")

    assert resposta.status_code == 404

def test_importacao_arquivo_invalido():
    cliente = app.test_client()

    resposta = cliente.post(
        "/resultado",
        data={
            "arquivo": (
                BytesIO(b"conteudo de teste"),
                "arquivo.txt"
            )
        },
        content_type="multipart/form-data"
    )

    assert resposta.status_code == 400
    assert b"Selecione um arquivo XML" in resposta.data

def test_banco_temporario(tmp_path, monkeypatch):
    caminho_teste = tmp_path / "teste_conferencia.db"

    monkeypatch.setattr(
        database,
        "CAMINHO_BANCO",
        caminho_teste
    )

    criar_banco()

    with database.conectar() as conexao:
        tabelas = conexao.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
        """).fetchall()

    nomes_tabelas = [tabela[0] for tabela in tabelas]

    assert "notas_fiscais" in nomes_tabelas
    assert "itens_nota" in nomes_tabelas

def test_importacao_xml_completa(tmp_path, monkeypatch):
    caminho_banco = tmp_path / "teste_importacao.db"

    monkeypatch.setattr(
        database,
        "CAMINHO_BANCO",
        caminho_banco
    )

    criar_banco()

    caminho_xml = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "nota_fiscal_4582.xml"
    )

    cliente = app.test_client()

    with open(caminho_xml, "rb") as arquivo:
        resposta = cliente.post(
            "/resultado",
            data={"arquivo": (arquivo, "nota_fiscal_4582.xml")},
            content_type="multipart/form-data"
        )

    assert resposta.status_code == 200

    with database.conectar() as conexao:
        total_notas = conexao.execute(
            "SELECT COUNT(*) FROM notas_fiscais"
        ).fetchone()[0]

        total_produtos = conexao.execute(
            "SELECT COUNT(*) FROM itens_nota"
        ).fetchone()[0]

    assert total_notas == 1
    assert total_produtos == 2

def test_nota_duplicada(tmp_path, monkeypatch):
    caminho_banco = tmp_path / "teste_duplicada.db"

    monkeypatch.setattr(
        database,
        "CAMINHO_BANCO",
        caminho_banco
    )

    criar_banco()

    caminho_xml = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "nota_fiscal_4582.xml"
    )

    cliente = app.test_client()

    with open(caminho_xml, "rb") as arquivo:
        primeira = cliente.post(
            "/resultado",
            data={"arquivo": (arquivo, "nota_fiscal_4582.xml")},
            content_type="multipart/form-data"
        )

    with open(caminho_xml, "rb") as arquivo:
        segunda = cliente.post(
            "/resultado",
            data={"arquivo": (arquivo, "nota_fiscal_4582.xml")},
            content_type="multipart/form-data"
        )

    assert primeira.status_code == 200
    assert segunda.status_code == 409

    with database.conectar() as conexao:
        total_notas = conexao.execute(
            "SELECT COUNT(*) FROM notas_fiscais"
        ).fetchone()[0]

    assert total_notas == 1

def test_produtos_salvos_com_situacao(tmp_path, monkeypatch):
    caminho_banco = tmp_path / "teste_produtos.db"

    monkeypatch.setattr(
        database,
        "CAMINHO_BANCO",
        caminho_banco
    )

    criar_banco()

    caminho_xml = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "nota_fiscal_4582.xml"
    )

    cliente = app.test_client()

    with open(caminho_xml, "rb") as arquivo:
        resposta = cliente.post(
            "/resultado",
            data={"arquivo": (arquivo, "nota_fiscal_4582.xml")},
            content_type="multipart/form-data"
        )

    assert resposta.status_code == 200

    with database.conectar() as conexao:
        produtos = conexao.execute("""
            SELECT codigo, descricao, quantidade, situacao
            FROM itens_nota
            ORDER BY codigo
        """).fetchall()

    assert len(produtos) == 2

    assert produtos[0][0] == "001"
    assert produtos[0][1] == "Livro A"
    assert produtos[0][2] == 5
    assert produtos[0][3] == "Possível correspondência — Pedido 125"

    assert produtos[1][0] == "002"
    assert produtos[1][1] == "Livro B"
    assert produtos[1][2] == 3
    assert produtos[1][3] == "Nenhuma correspondência encontrada"

def test_xml_sem_dados_obrigatorios(tmp_path):
    caminho = tmp_path / "nota_incompleta.xml"

    caminho.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
        <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
            <NFe>
                <infNFe>
                    <ide>
                        <nNF>4582</nNF>
                    </ide>
                    <emit>
                        <xNome></xNome>
                    </emit>
                </infNFe>
            </NFe>
        </nfeProc>
        """,
        encoding="utf-8"
    )

    with pytest.raises(ValueError):
        ler_nota_fiscal(caminho)

def test_importacao_xml_incompleto(tmp_path, monkeypatch):
    caminho_banco = tmp_path / "teste_incompleto.db"

    monkeypatch.setattr(
        database,
        "CAMINHO_BANCO",
        caminho_banco
    )

    criar_banco()

    xml_incompleto = b"""<?xml version="1.0" encoding="UTF-8"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
        <NFe>
            <infNFe>
                <ide>
                    <nNF>4582</nNF>
                </ide>
                <emit>
                    <xNome></xNome>
                </emit>
            </infNFe>
        </NFe>
    </nfeProc>
    """

    cliente = app.test_client()

    resposta = cliente.post(
        "/resultado",
        data={
            "arquivo": (
                BytesIO(xml_incompleto),
                "nota_incompleta.xml"
            )
        },
        content_type="multipart/form-data"
    )

    assert resposta.status_code == 400
    assert b"N\xc3\xa3o foi poss\xc3\xadvel ler o arquivo XML" in resposta.data

    with database.conectar() as conexao:
        total_notas = conexao.execute(
            "SELECT COUNT(*) FROM notas_fiscais"
        ).fetchone()[0]

    assert total_notas == 0


def test_xml_fornecedor_apenas_espacos(tmp_path):
    caminho = tmp_path / "nota_fornecedor_invalido.xml"

    caminho.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
        <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
            <NFe>
                <infNFe>
                    <ide>
                        <nNF>4583</nNF>
                    </ide>
                    <emit>
                        <xNome>   </xNome>
                    </emit>
                    <det nItem="1">
                        <prod>
                            <cProd>001</cProd>
                            <xProd>Livro A</xProd>
                            <qCom>2</qCom>
                        </prod>
                    </det>
                </infNFe>
            </NFe>
        </nfeProc>
        """,
        encoding="utf-8"
    )

    with pytest.raises(ValueError):
        ler_nota_fiscal(caminho)
