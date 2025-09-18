# PrivyForge — Anonimizador de Dados (CSV/JSON) com Web UI (FastAPI + Pandas)

**PrivyForge** é um utilitário auto‑hospedado para **anonimizar** dados tabulares (CSV/JSON) com regras declarativas.
Foquei em uma área diferente das suas integrações/bots: **privacidade & compliance** (LGPD/GDPR). Ideal para gerar
datasets de desenvolvimento, compartilhamento com terceiros ou publicar amostras sem expor PII.

---

## Principais Recursos

- **Upload** de CSV (ou JSON‑lines) e **download** do arquivo anonimizado.
- **Regras declarativas** via JSON (hash, mask, drop, keep, randomize_number).
- **Hash determinístico** com *salt* (SHA‑256) — reidêntico para o mesmo valor + salt.
- **Máscara** configurável (últimos N, primeiros N, substituto).
- **Randomização determinística** de números, via seed do hash (mantém faixas coerentes).
- **Sem persistência**: nada é salvo em disco (processamento em memória).

> Exemplo de regras no README logo abaixo. Você pode salvar suas regras em um arquivo e colar no painel.

---

## Estrutura

```
PrivyForge/
├─ app/
│  ├─ main.py
│  ├─ rules.py
│  ├─ templates/
│  │  └─ index.html   # painel web
│  └─ static/
│     └─ styles.css   # estilo básico
├─ .env.example
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ LICENSE
└─ README.md
```

---

## Instalação (local)

Pré‑requisitos: Python 3.11+

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 7600
```

Acesse: `http://localhost:7600/`

---

## Regras (JSON)

As regras definem o que fazer com cada coluna. Estrutura básica:

```json
{
  "salt": "troque-este-salt",
  "columns": {
    "email":   { "strategy": "hash" },
    "cpf":     { "strategy": "mask", "show_last": 2 },
    "nome":    { "strategy": "drop" },
    "idade":   { "strategy": "randomize_number", "min": 18, "max": 65 },
    "cidade":  { "strategy": "keep" }
  }
}
```

### Estratégias suportadas
- **hash**: aplica SHA‑256(salt + valor) e retorna os primeiros 16 caracteres por padrão. Parâmetros:
  - `length` (opcional, padrão 16): tamanho do recorte do hash retornado.
- **mask**: troca por asteriscos preservando parte do valor.
  - `show_first` (opcional): mantém primeiros N caracteres.
  - `show_last` (opcional): mantém últimos N caracteres.
  - `char` (opcional, padrão `"*"`): caractere de máscara.
- **drop**: remove a coluna do resultado.
- **keep**: mantém a coluna como está.
- **randomize_number**: gera número pseudoaleatório **determinístico** por linha (usando hash como seed).
  - `min` (obrigatório): mínimo inteiro.
  - `max` (obrigatório): máximo inteiro.

> Para JSON‑lines (um objeto por linha), converta para CSV antes de enviar ou use ferramentas externas. O app foca em CSV tabular.

---

## Exemplo de Uso

1. Abra o painel e **cole** suas regras JSON no campo apropriado (ou use o exemplo inicial).
2. Faça **upload** do CSV.
3. Clique em **Anonimizar** → o download do CSV já virá anonimizado.

### Exemplo de CSV de entrada

```csv
email,cpf,nome,idade,cidade
ana@example.com,12345678900,Ana,29,Campinas
bob@example.com,98765432100,Bob,41,Santos
```

### Saída com as regras acima (exemplo)

```csv
email,cpf,idade,cidade
b1a2c3d4e5f6a7b8,*********00,33,Campinas
09f8e7d6c5b4a3f2,*********00,22,Santos
```

- `nome` foi **dropado**.
- `email` virou hash recortado (16 chars).
- `cpf` foi mascarado preservando 2 últimos dígitos.
- `idade` recebeu um número determinístico dentro de `[18,65]`.

---

## API

- `POST /api/anonymize`  
  **Form‑data**:  
  - `file`: CSV
  - `rules`: JSON das regras (string)  
  **Resposta**: CSV anonimizado (como arquivo).  

- `GET /health` — simples `{"status":"ok"}`.

> A interface web chama esse endpoint internamente.

---

## Docker

```bash
docker build -t privyforge:latest .
docker run -p 7600:7600 privyforge:latest
```
Ou com `docker-compose`:
```bash
docker compose up --build
```

---

## Boas Práticas & Limitações

- Use um `salt` **secreto e consistente** para manter determinismo entre execuções.
- Sem *faker*: números aleatórios preservam coerência sem inventar nomes fictícios.
- Para produção, coloque atrás de um **reverse proxy** com autenticação (painel é aberto por padrão).
- O processamento é em memória: arquivos muito grandes podem exigir *streaming* (não incluso neste MVP).

---

## Roadmap Sugerido

- Upload e parsing de planilhas Excel (`.xlsx`).
- Suporte a JSON‑lines e Parquet.
- Regras com expressões por coluna (regex, map).
- Pré‑sets de regras para PII comuns (email, CPF, telefone).
- Relatório de colunas sensíveis detectadas heurísticamente.

---

## Licença

MIT — veja `LICENSE`.
