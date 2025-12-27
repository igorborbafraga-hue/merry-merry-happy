# Merry OK - Wedding Site (Local)

Projeto mínimo em Python/Flask que implementa um "gate" de RSVP antes de permitir acesso ao site.

Como rodar localmente:

1. Abra PowerShell e vá para a pasta do projeto:

```powershell
cd "C:\Users\igorb\Documents\Merry OK"
```

2. Crie um ambiente virtual (opcional) e instale dependências:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Rode o servidor:

```powershell
python app.py
```

4. Abra no navegador: http://localhost:5000

Notas:
- O formulário de entrada salva confirmações em `rsvps.json`.
- Para deploy real, configure `WEDDING_SECRET` como variável de ambiente e use um servidor WSGI.
# Merry OK
