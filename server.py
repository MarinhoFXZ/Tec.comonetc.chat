#!/usr/bin/env python3
import os
import json
import secrets
import smtplib
from random import randint
from email.message import EmailMessage
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')

PORT = int(os.getenv('PORT', '3002'))
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '9895')
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
FROM_EMAIL = os.getenv('FROM_EMAIL', SMTP_USER)

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
MESSAGES_FILE = os.path.join(DATA_DIR, 'messages.json')

os.makedirs(DATA_DIR, exist_ok=True)
for path in (USERS_FILE, MESSAGES_FILE):
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([], f)

def read_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

sessions = []

def send_recovery_email(email, code):
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        return {'ok': False, 'message': 'SMTP não configurado.'}

    msg = EmailMessage()
    msg['Subject'] = 'Código de recuperação de senha - TEC Comonetc Chat'
    msg['From'] = f'TEC Comonetc Chat <{FROM_EMAIL}>'
    msg['To'] = email
    msg.set_content(f'Olá!\n\nSeu código de recuperação para o TEC Comonetc Chat é: {code}\n\nUse este código para redefinir sua senha.')

    try:
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
                smtp.login(SMTP_USER, SMTP_PASS)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(SMTP_USER, SMTP_PASS)
                smtp.send_message(msg)
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'message': str(e)}

@app.route('/join', methods=['POST'])
def join():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    role = data.get('role') or 'cliente'
    provided = data.get('adminPassword')
    if not name:
        return jsonify({'ok': False, 'message': 'Informe um nome para entrar.'}), 400
    if role == 'admin' and provided != ADMIN_PASSWORD:
        return jsonify({'ok': False, 'message': 'Senha de administrador incorreta.'}), 401

    token = secrets.token_hex(12)
    sessions.append({'token': token, 'name': name, 'role': role, 'joinedAt': None})
    messages = read_json(MESSAGES_FILE)[-20:]
    return jsonify({'ok': True, 'token': token, 'user': {'name': name, 'role': role}, 'users': [{'name': s['name'], 'role': s['role']} for s in sessions], 'messages': messages})

@app.route('/online', methods=['GET'])
def online():
    return jsonify({'ok': True, 'users': sessions})

@app.route('/messages', methods=['GET'])
def messages():
    token = request.args.get('token')
    since_id = int(request.args.get('sinceId') or '0')
    session = next((s for s in sessions if s['token'] == token), None)
    if not session:
        return jsonify({'ok': False, 'message': 'Acesso inválido.'}), 401
    msgs = [m for m in read_json(MESSAGES_FILE) if m.get('id', 0) > since_id]
    return jsonify({'ok': True, 'messages': msgs})

@app.route('/leave', methods=['POST'])
def leave():
    data = request.get_json() or {}
    token = data.get('token')
    global sessions
    sessions = [s for s in sessions if s['token'] != token]
    return jsonify({'ok': True, 'message': 'Sessão encerrada.'})

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json() or {}
    token = data.get('token')
    text = (data.get('text') or '').strip()
    session = next((s for s in sessions if s['token'] == token), None)
    if not session or not text:
        return jsonify({'ok': False, 'message': 'Mensagem inválida.'}), 400
    messages = read_json(MESSAGES_FILE)
    message = {'id': int(secrets.token_hex(6), 16), 'from': session['name'], 'role': session['role'], 'text': text, 'createdAt': None}
    messages.append(message)
    write_json(MESSAGES_FILE, messages)
    return jsonify({'ok': True, 'message': message})

@app.route('/recover-password', methods=['POST'])
def recover_password():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    if not email:
        return jsonify({'ok': False, 'message': 'Informe um e-mail.'}), 400
    code = '{:06d}'.format(randint(100000, 999999))
    if SMTP_HOST and SMTP_USER and SMTP_PASS:
        result = send_recovery_email(email, code)
        if not result.get('ok'):
            return jsonify({'ok': False, 'message': result.get('message', 'Erro ao enviar.') }), 502
        # store code locally for testing
        write_json(os.path.join(DATA_DIR, 'last_recovery.json'), {'email': email, 'code': code})
        return jsonify({'ok': True, 'message': 'Código enviado para o e-mail informado.'})
    else:
        # fallback for static/testing: include code in response
        write_json(os.path.join(DATA_DIR, 'last_recovery.json'), {'email': email, 'code': code})
        return jsonify({'ok': True, 'code': code, 'message': 'SMTP não configurado — código retornado apenas para testes.'})

@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def static_proxy(path):
    # serve static files from repo root
    target = os.path.join(ROOT, path)
    if os.path.exists(target) and os.path.isfile(target):
        return send_from_directory(ROOT, path)
    return send_from_directory(ROOT, 'index.html')

if __name__ == '__main__':
    print(f'Servidor Python rodando em http://0.0.0.0:{PORT}')
    app.run(host='0.0.0.0', port=PORT)
