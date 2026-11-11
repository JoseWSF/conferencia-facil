# Pedidos e ordens de serviço fictícios para teste
pedidos_os = [
    {"numero": "125", "tipo": "Pedido", "codigo_produto": "001"},
    {"numero": "230", "tipo": "OS", "codigo_produto": "003"}
]


def conferir_produtos(produtos):
    for produto in produtos:
        produto["situacao"] = "Nenhuma correspondência encontrada"
        produto["correspondencia"] = False

        for registro in pedidos_os:
            if produto["codigo"] == registro["codigo_produto"]:
                produto["situacao"] = (
                    f"Possível correspondência — "
                    f"{registro['tipo']} {registro['numero']}"
                )
                produto["correspondencia"] = True
                break

    return produtos