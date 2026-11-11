from flask import Flask, render_template, request
from business.nota_fiscal import ler_nota_fiscal
from business.conferencia import conferir_produtos
from data.models import salvar_nota, nota_ja_existe, listar_notas, buscar_nota_por_id
from pathlib import Path
import tempfile

app = Flask(__name__, template_folder="presentation/templates")

app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/importacao")
def importacao():
    return render_template("importacao.html")

@app.route("/historico")
def historico():
    notas = listar_notas()
    return render_template("historico.html", notas=notas)

@app.route("/nota/<int:id_nota>")
def detalhes_nota(id_nota):
    nota = buscar_nota_por_id(id_nota)

    if nota is None:
        return "Nota fiscal não encontrada.", 404

    return render_template("detalhes_nota.html", nota=nota)

@app.route("/resultado", methods=["GET", "POST"])
def resultado():
    if request.method == "POST":
        arquivo = request.files.get("arquivo")

        if not arquivo or not arquivo.filename.lower().endswith(".xml"):
            return "Selecione um arquivo XML válido.", 400

        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "nota.xml"
            arquivo.save(caminho)

            try:
                nota = ler_nota_fiscal(caminho)
            except Exception:
                return "Não foi possível ler o arquivo XML.", 400

            nota["produtos"] = conferir_produtos(nota["produtos"])

        if nota_ja_existe(nota["numero"], nota["fornecedor"]):
            return render_template("duplicada.html"), 409

        salvar_nota(nota)

        return render_template("resultado.html", nota=nota)

    return "Importe uma nota fiscal para visualizar o resultado.", 400


if __name__ == "__main__":
    app.run(debug=True)