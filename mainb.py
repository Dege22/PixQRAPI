from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import hashlib
from pixqrcodegen import Payload
import sys
import io


class PixData(BaseModel):
    chave_aleatoria: str
    nome_beneficiario: str
    cidade_beneficiario: str
    valor_transferencia: float


app = FastAPI()


def generate_txid() -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_digest = hashlib.sha1(timestamp.encode()).hexdigest()[:10]
    txid = f"{timestamp}{hash_digest}"
    return txid


@app.get("/generate-pix/{chave_aleatoria}/{nome_beneficiario}/{cidade_beneficiario}/{valor_transferencia:float}")
async def generate_pix(chave_aleatoria: str, nome_beneficiario: str, cidade_beneficiario: str,
                       valor_transferencia: float):
    # Redirect stdout to capture output
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    try:
        txid = generate_txid()
        cidade_beneficiario_formatada = cidade_beneficiario.lower().replace(" ", "")
        valor_em_string = f"{valor_transferencia:.2f}"
        payload = Payload(nome_beneficiario, chave_aleatoria, valor_em_string, cidade_beneficiario_formatada, txid)
        codigo_pix = payload.gerarPayload()

        # Capture output and revert stdout
        output = new_stdout.getvalue()
        sys.stdout = old_stdout

        if codigo_pix:
            return {
                "message": "Pix Copia e Cola gerado com sucesso!",
                "pix": output.strip()
            }
        else:
            return {
                "message": "Pix Copia e Cola gerado com sucesso!",
                "pix": output.strip()
            }
    except Exception as e:
        sys.stdout = old_stdout
        return {
            "message": "Erro ao gerar o Pix Copia e Cola",
            "error": str(e),
            "Console Output": new_stdout.getvalue().strip()
        }

# Este script requer um servidor ASGI como o uvicorn para ser executado.
# Exemplo de comando para executar: uvicorn nome_do_arquivo:app --reload
