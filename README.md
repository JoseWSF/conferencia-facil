
# Conferência Fácil

MVP desenvolvido como parte do curso de Análise e Desenvolvimento de Sistemas (ADS).

## Objetivo

Facilitar a conferência de mercadorias em uma livraria, reduzindo a necessidade de verificar manualmente cada produto de uma nota fiscal.

## Funcionalidades

- Importação de notas fiscais em XML.
- Leitura automática dos dados da nota e dos produtos.
- Identificação de possíveis correspondências com pedidos e ordens de serviço (OS).
- Histórico de notas fiscais importadas.
- Visualização dos detalhes dos produtos.
- Identificação de notas duplicadas.
- Validação de informações obrigatórias do XML.

## Tecnologias utilizadas

- Python
- Flask
- SQLite
- HTML e CSS
- Pytest

## Como executar

1. Instale o Python.
2. Clone o repositório.
3. Instale as dependências:

```cmd
python -m pip install -r requirements.txt
```

4. Crie o banco de dados:

```cmd
python -m data.database
```

5. Inicie a aplicação:

```cmd
python app.py
```

6. Acesse `http://127.0.0.1:5000` no navegador.

## Testes automatizados

Execute:

```cmd
python -m pytest tests/test_app.py -v
```

O projeto possui 14 testes automatizados.

## Observações

O Conferência Fácil é um protótipo acadêmico. As correspondências com pedidos e OS utilizam dados fictícios. Não existe integração direta com o sistema da empresa.

A tela inicial apresenta um acesso visual, mas ainda não possui autenticação real.

O projeto está relacionado ao ODS 9 — Indústria, Inovação e Infraestrutura.
