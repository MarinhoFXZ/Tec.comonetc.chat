# Conversa local

Este projeto pode ser hospedado no GitHub Pages como um site estático.

## Arquivos principais
- login.html: tela de entrada com nome e senha de administrador
- chat.html: tela de conversa
- desig.css: estilos

## Publish to GitHub Pages (free hosting)

1. Create a new GitHub repository (for example `tec-comonetc-chat`) and push this folder as the repository root.

2. Make sure the repository contains an `index.html` at the root. This project includes `index.html` that redirects to `login.html` so the site opens correctly.

3. Push to GitHub and enable Pages in the repository settings:

	- Go to the repo Settings → Pages
	- Under "Source" choose the branch (`main` or `master`) and folder `/ (root)`
	- Save — the site will publish at `https://<your-username>.github.io/<repo>`

4. Alternatively, publish from the `gh-pages` branch. You can use the `gh-pages` npm package or GitHub Actions to automate deployments.

## Important notes

- GitHub Pages serves only static files. The Node.js backend (`server.js`) has been removed from this project. To have automatic email sending you must run the included Python backend locally or on a separate host.
- For local testing with email sending enabled, run the Python server included here (`server.py`). It supports the recovery email endpoint and can send messages when you provide SMTP credentials.

Python quick start (WSL / Linux / macOS):

```bash
cd /home/Marin/PrimeiroProgm/programa/site
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# start without SMTP (useful for static testing)
PORT=3002 python3 server.py
# or start with Gmail app password (replace YOUR_APP_PASSWORD):
SMTP_HOST=smtp.gmail.com SMTP_PORT=587 SMTP_USER=TEC.comonetc.chat@gmail.com SMTP_PASS=YOUR_APP_PASSWORD FROM_EMAIL=TEC.comonetc.chat@gmail.com PORT=3002 python3 server.py
```

PowerShell (Windows) equivalent:

```powershell
cd /home/Marin/PrimeiroProgm/programa/site
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PORT='3002'; python server.py
# with SMTP:
$env:SMTP_HOST='smtp.gmail.com'; $env:SMTP_PORT='587'; $env:SMTP_USER='TEC.comonetc.chat@gmail.com'; $env:SMTP_PASS='YOUR_APP_PASSWORD'; $env:FROM_EMAIL='TEC.comonetc.chat@gmail.com'; $env:PORT='3002'; python server.py
```

This project already includes a GitHub Actions workflow that deploys the site automatically whenever you push to `main`.

## Como publicar no GitHub Pages
1. Envie estes arquivos para um repositório no GitHub.
2. No GitHub, vá em Settings > Pages.
3. Selecione a branch principal e a pasta raiz.
4. Salve e aguarde a publicação.

## Observação
A versão para GitHub Pages usa o localStorage do navegador para guardar as mensagens e o login localmente no dispositivo do usuário.
