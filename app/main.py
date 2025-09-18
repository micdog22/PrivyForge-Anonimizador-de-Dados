import io, os, json
import pandas as pd
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from .rules import apply_hash, apply_mask, apply_random_number

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "7600"))

app = FastAPI(title="PrivyForge")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/api/anonymize")
async def anonymize(file: UploadFile, rules: str = Form(...)):
    try:
        cfg = json.loads(rules)
    except Exception:
        raise HTTPException(status_code=400, detail="Regras JSON inválidas")

    salt = str(cfg.get("salt", ""))
    columns = cfg.get("columns", {})
    if not isinstance(columns, dict) or not columns:
        raise HTTPException(status_code=400, detail="Defina 'columns' nas regras")

    # ler CSV para DataFrame
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV inválido: {e}")

    # aplicar regras
    drop_cols = [col for col, rule in columns.items() if (rule or {}).get("strategy") == "drop"]
    for col, rule in columns.items():
        if col not in df.columns:  # coluna ausente é ignorada
            continue
        strat = (rule or {}).get("strategy", "keep")
        if strat == "keep":
            continue
        elif strat == "hash":
            length = int((rule or {}).get("length", 16))
            df[col] = df[col].astype(str).apply(lambda v: apply_hash(v, salt, length))
        elif strat == "mask":
            sf = int((rule or {}).get("show_first", 0))
            sl = int((rule or {}).get("show_last", 0))
            ch = str((rule or {}).get("char", "*"))[:1] or "*"
            df[col] = df[col].astype(str).apply(lambda v: apply_mask(v, sf, sl, ch))
        elif strat == "randomize_number":
            min_v = int((rule or {}).get("min", 0))
            max_v = int((rule or {}).get("max", 100))
            if min_v > max_v:
                min_v, max_v = max_v, min_v
            df[col] = df[col].astype(str).apply(lambda v: apply_random_number(v, salt, min_v, max_v))
        elif strat == "drop":
            # será removida depois
            pass
        else:
            raise HTTPException(status_code=400, detail=f"Estratégia desconhecida: {strat}")

    if drop_cols:
        df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # exportar CSV
    out = io.StringIO()
    df.to_csv(out, index=False)
    out.seek(0)
    return StreamingResponse(iter([out.getvalue().encode('utf-8')]), media_type="text/csv", headers={
        "Content-Disposition": f'attachment; filename="anonimizacao.csv"'
    })
