import requests
import os
from datetime import datetime, timedelta

# Configurações (vem das secrets do GitHub)
TODOIST_TOKEN = os.environ.get('TODOIST_TOKEN')
OUTLOOK_CLIENT_ID = os.environ.get('OUTLOOK_CLIENT_ID')
OUTLOOK_CLIENT_SECRET = os.environ.get('OUTLOOK_CLIENT_SECRET')
OUTLOOK_REFRESH_TOKEN = os.environ.get('OUTLOOK_REFRESH_TOKEN')
YOUR_EMAIL = os.environ.get('YOUR_EMAIL', 'joaopaulo.homem@outlook.com')

def get_todoist_tasks():
    """Busca tarefas do Todoist"""
    headers = {'Authorization': f'Bearer {TODOIST_TOKEN}'}
    response = requests.get('https://api.todoist.com/rest/v2/tasks', headers=headers)
    return response.json()

def categorize_tasks(tasks):
    """Categoriza tarefas por data"""
    today = datetime.now().date()
    overdue, today_tasks, upcoming = [], [], []
    
    for task in tasks:
        if not task.get('due'):
            continue
        due_date = datetime.strptime(task['due']['date'], '%Y-%m-%d').date()
        
        task_info = {
            'content': task['content'],
            'due_date': due_date.strftime('%d/%m/%Y'),
            'url': task['url'],
            'priority': task.get('priority', 1)
        }
        
        if due_date < today:
            overdue.append(task_info)
        elif due_date == today:
            today_tasks.append(task_info)
        elif due_date <= today + timedelta(days=3):
            upcoming.append(task_info)
    
    return overdue, today_tasks, upcoming

def create_html_email(overdue, today_tasks, upcoming):
    """Cria o HTML do email"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; }}
        .container {{ max-width: 700px; margin: 0 auto; background: white; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 32px; }}
        .content {{ padding: 30px; }}
        .stats {{ display: flex; justify-content: space-around; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; }}
        .stat {{ text-align: center; color: white; }}
        .stat-number {{ font-size: 32px; font-weight: 700; display: block; }}
        .stat-label {{ font-size: 12px; text-transform: uppercase; }}
        .section {{ margin-bottom: 30px; }}
        .section-title {{ font-size: 20px; font-weight: 600; margin-bottom: 15px; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; }}
        .task {{ background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px; margin-bottom: 10px; border-radius: 8px; }}
        .task-overdue {{ border-left-color: #e74c3c; background: #fff5f5; }}
        .task-today {{ border-left-color: #f39c12; background: #fffbf0; }}
        .task-upcoming {{ border-left-color: #27ae60; background: #f0fff4; }}
        .task-title {{ font-size: 16px; font-weight: 500; color: #2c3e50; }}
        .task-date {{ font-size: 13px; color: #7f8c8d; margin-top: 5px; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #7f8c8d; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Suas Tarefas do Dia</h1>
            <p>{datetime.now().strftime('%d de %B de %Y')}</p>
        </div>
        <div class="content">
            <div class="stats">
                <div class="stat"><span class="stat-number">{len(overdue)}</span><span class="stat-label">Vencidas</span></div>
                <div class="stat"><span class="stat-number">{len(today_tasks)}</span><span class="stat-label">Hoje</span></div>
                <div class="stat"><span class="stat-number">{len(upcoming)}</span><span class="stat-label">Próximos Dias</span></div>
            </div>
"""
    
    # Tarefas vencidas
    if overdue:
        html += f'<div class="section"><div class="section-title">🔴 Tarefas Vencidas ({len(overdue)})</div>'
        for task in overdue:
            html += f'<div class="task task-overdue"><div class="task-title">{task["content"]}</div><div class="task-date">📅 Venceu em: {task["due_date"]}</div></div>'
        html += '</div>'
    
    # Tarefas de hoje
    if today_tasks:
        html += f'<div class="section"><div class="section-title">🟡 Para Hoje ({len(today_tasks)})</div>'
        for task in today_tasks:
            html += f'<div class="task task-today"><div class="task-title">{task["content"]}</div><div class="task-date">📅 Vence hoje: {task["due_date"]}</div></div>'
        html += '</div>'
    
    # Próximas tarefas
    if upcoming:
        html += f'<div class="section"><div class="section-title">🟢 Próximos 3 Dias ({len(upcoming)})</div>'
        for task in upcoming:
            html += f'<div class="task task-upcoming"><div class="task-title">{task["content"]}</div><div class="task-date">📅 Vence em: {task["due_date"]}</div></div>'
        html += '</div>'
    
    if not overdue and not today_tasks and not upcoming:
        html += '<div style="text-align:center;padding:30px;color:#95a5a6;"><h2>🎉 Parabéns!</h2><p>Você não tem tarefas urgentes.</p></div>'
    
    html += '</div><div class="footer"><p>💙 Email gerado automaticamente</p></div></div></body></html>'
    return html

def send_email_outlook(html_body):
    """Envia email via Microsoft Graph API"""
    # Renovar token
    token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    token_data = {
        'client_id': OUTLOOK_CLIENT_ID,
        'client_secret': OUTLOOK_CLIENT_SECRET,
        'refresh_token': OUTLOOK_REFRESH_TOKEN,
        'grant_type': 'refresh_token'
    }
    token_response = requests.post(token_url, data=token_data)
    access_token = token_response.json()['access_token']
    
    # Enviar email
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    email_data = {
        'message': {
            'subject': '📋 Suas Tarefas do Dia - Todoist',
            'body': {'contentType': 'HTML', 'content': html_body},
            'toRecipients': [{'emailAddress': {'address': YOUR_EMAIL}}]
        }
    }
    response = requests.post(
        'https://graph.microsoft.com/v1.0/me/sendMail',
        headers=headers,
        json=email_data
    )
    return response.status_code == 202

if __name__ == '__main__':
    print("🔍 Buscando tarefas do Todoist...")
    tasks = get_todoist_tasks()
    
    print("📊 Categorizando tarefas...")
    overdue, today_tasks, upcoming = categorize_tasks(tasks)
    
    print(f"   🔴 Vencidas: {len(overdue)}")
    print(f"   🟡 Hoje: {len(today_tasks)}")
    print(f"   🟢 Próximos 3 dias: {len(upcoming)}")
    
    print("📧 Criando email HTML...")
    html = create_html_email(overdue, today_tasks, upcoming)
    
    print("📤 Enviando email...")
    if send_email_outlook(html):
        print("✅ Email enviado com sucesso!")
    else:
        print("❌ Erro ao enviar email")
