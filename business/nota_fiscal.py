import xml.etree.ElementTree as ET


def ler_nota_fiscal(caminho_arquivo):
    arvore = ET.parse(caminho_arquivo)
    raiz = arvore.getroot()

    namespace = {"nfe": "http://www.portalfiscal.inf.br/nfe"}

    numero = raiz.find(".//nfe:ide/nfe:nNF", namespace)
    fornecedor = raiz.find(".//nfe:emit/nfe:xNome", namespace)

    produtos = []

    for item in raiz.findall(".//nfe:det", namespace):
        codigo = item.find("nfe:prod/nfe:cProd", namespace)
        descricao = item.find("nfe:prod/nfe:xProd", namespace)
        quantidade = item.find("nfe:prod/nfe:qCom", namespace)

        produtos.append({
            "codigo": codigo.text if codigo is not None else "",
            "descricao": descricao.text if descricao is not None else "",
            "quantidade": quantidade.text if quantidade is not None else "0"
        })

    dados_nota = {
        "numero": numero.text if numero is not None else "",
        "fornecedor": fornecedor.text if fornecedor is not None else "",
        "produtos": produtos
    }

    if not dados_nota["numero"] or not dados_nota["fornecedor"]:
        raise ValueError("Número da nota ou fornecedor não informado.")

    if not dados_nota["produtos"]:
        raise ValueError("A nota fiscal não possui produtos.")

    for produto in dados_nota["produtos"]:
        if not produto["codigo"] or not produto["descricao"]:
            raise ValueError("Produto com informações obrigatórias ausentes.")

        try:
            quantidade = float(produto["quantidade"])
        except (ValueError, TypeError):
            raise ValueError("Quantidade inválida no XML.")

        if quantidade <= 0:
            raise ValueError("A quantidade do produto deve ser maior que zero.")

    return dados_nota