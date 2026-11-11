from pathlib import Path
from business.nota_fiscal import ler_nota_fiscal
from business.conferencia import conferir_produtos
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