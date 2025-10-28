import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Configurações - PROTON MAIL
todoist_token = os.environ.get('TODOIST_TOKEN')
proton_email = 'jp@jphub.com.br'
proton_token = os.environ.get('PROTON_MAIL_TOKEN')  # 3PDSKEP7W14Z45AQ
smtp_host = 'smtp.protonmail.ch'
smtp_port = 587
recipients = ['jp@jphub.com.br', 'joaohomem@falconi.com']

def get_todoist_tasks():
    """Busca tarefas do Todoist"""
    headers = {'Authorization': f'Bearer {todoist_token}'}
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
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 700px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
        }}
        .content {{
            padding: 30px;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
        }}
        .stat {{
            text-align: center;
            color: white;
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: 700;
            display: block;
        }}
        .stat-label {{
            font-size: 12px;
            text-transform: uppercase;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }}
        .task {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }}
        .task:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .task-overdue {{
            border-left-color: #e74c3c;
            background: #fff5f5;
        }}
        .task-today {{
            border-left-color: #f39c12;
            background: #fffbf0;
        }}
        .task-upcoming {{
            border-left-color: #27ae60;
            background: #f0fff4;
        }}
        .task-title {{
            font-size: 16px;
            font-weight: 500;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        .task-date {{
            font-size: 13px;
            color: #7f8c8d;
            margin-bottom: 8px;
        }}
        .task-link {{
            display: inline-block;
            padding: 6px 12px;
            background: #667eea;
            color: white !important;
            text-decoration: none;
            border-radius: 5px;
            font-size: 12px;
            font-weight: 500;
        }}
        .task-link:hover {{
            background: #5568d3;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #7f8c8d;
            font-size: 13px;
        }}
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

    if overdue:
        html += f'<div class="section"><div class="section-title">🔴 Tarefas Vencidas ({len(overdue)})</div>'
        for task in overdue:
            html += f'''<div class="task task-overdue">
                <div class="task-title">{task["content"]}</div>
                <div class="task-date">📅 Venceu em: {task["due_date"]}</div>
                <a href="{task["url"]}" class="task-link" target="_blank">Abrir no Todoist →</a>
            </div>'''
        html += '</div>'

    if today_tasks:
        html += f'<div class="section"><div class="section-title">🟠 Para Hoje ({len(today_tasks)})</div>'
        for task in today_tasks:
            html += f'''<div class="task task-today">
                <div class="task-title">{task["content"]}</div>
                <div class="task-date">📅 Vence hoje: {task["due_date"]}</div>
                <a href="{task["url"]}" class="task-link" target="_blank">Abrir no Todoist →</a>
            </div>'''
        html += '</div>'

    if upcoming:
        html += f'<div class="section"><div class="section-title">🟢 Próximos 3 Dias ({len(upcoming)})</div>'
        for task in upcoming:
            html += f'''<div class="task task-upcoming">
                <div class="task-title">{task["content"]}</div>
                <div class="task-date">📅 Vence em: {task["due_date"]}</div>
                <a href="{task["url"]}" class="task-link" target="_blank">Abrir no Todoist →</a>
            </div>'''
        html += '</div>'

    if not overdue and not today_tasks and not upcoming:
        html += '<div style="text-align:center;padding:30px;color:#95a5a6;"><h2>🎉 Parabéns!</h2><p>Você não tem tarefas urgentes.</p></div>'

    html += '''</div><div class="footer"><p>✉️ Email gerado automaticamente via Proton Mail - GitHub Actions</p></div></div></body></html>'''
    return html

def send_email_proton(html_body):
    """Envia email via Proton Mail SMTP para múltiplos destinatários"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '📋 Suas Tarefas do Dia - Todoist'
        msg['From'] = proton_email
        msg['To'] = ', '.join(recipients)

        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)

        # Conectar ao Proton Mail SMTP
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(proton_email, proton_token)
        server.sendmail(proton_email, recipients, msg.as_string())
        server.quit()

        print("✅ Email enviado com sucesso via Proton Mail!")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False

if __name__ == '__main__':
    print("🔍 Buscando tarefas do Todoist...")
    tasks = get_todoist_tasks()

    print("📌 Categorizando tarefas...")
    overdue, today_tasks, upcoming = categorize_tasks(tasks)

    print(f"  🔴 Vencidas: {len(overdue)}")
    print(f"  🟠 Hoje: {len(today_tasks)}")
    print(f"  🟢 Próximos 3 dias: {len(upcoming)}")

    print("🎨 Criando email HTML...")
    html = create_html_email(overdue, today_tasks, upcoming)

    print(f"📧 Enviando email para {len(recipients)} destinatários via Proton Mail...")
    if send_email_proton(html):
        print("✅ Email enviado com sucesso!")
    else:
        print("❌ Erro ao enviar email")