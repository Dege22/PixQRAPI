from fastapi import FastAPI, Response
from pydantic import BaseModel
from datetime import datetime
import hashlib
from pixqrcodegen import Payload
import sys
import io
import qrcode
from fastapi.responses import FileResponse
import os

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
        output = new_stdout.getvalue().strip()
        sys.stdout = old_stdout

        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(output if codigo_pix is None else codigo_pix)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save("pix_qrcode.png")

        # Return the QR Code as a file response
        return FileResponse("pix_qrcode.png", media_type="image/png", filename="pix_qrcode.png")
    except Exception as e:
        sys.stdout = old_stdout
        return {
            "message": "Erro ao gerar o Pix Copia e Cola",
            "error": str(e),
            "Console Output": new_stdout.getvalue().strip()
        }

# Este script requer um servidor ASGI como o uvicorn para ser executado.
# Exemplo de comando para executar: uvicorn nome_do_arquivo:app --reload

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
