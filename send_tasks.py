import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Configurações - PROTON MAIL
todoist_token = os.environ.get('TODOIST_TOKEN')
proton_email = 'jp@jphub.com.br'
proton_token = os.environ.get('PROTON_MAIL_TOKEN')
smtp_host = 'smtp.protonmail.ch'
smtp_port = 587
recipients = ['jp@jphub.com.br', 'joaohomem@falconi.com']

def get_todoist_tasks():
    """Busca tarefas do Todoist"""
    print("🔍 Buscando tarefas do Todoist...")
    headers = {'Authorization': f'Bearer {todoist_token}'}
    response = requests.get('https://api.todoist.com/rest/v2/tasks', headers=headers)
    return response.json()

def categorize_tasks(tasks):
    """Categoriza tarefas por data"""
    print("📋 Categorizando tarefas...")
    today = datetime.now().date()
    overdue = []
    today_tasks = []
    upcoming = []
    
    for task in tasks:
        if not task.get('due'):
            continue
        
        due_date = datetime.fromisoformat(task['due']['date']).date()
        
        if due_date < today:
            overdue.append(task)
        elif due_date == today:
            today_tasks.append(task)
        elif due_date <= today + timedelta(days=3):
            upcoming.append(task)
    
    return {
        'overdue': overdue,
        'today': today_tasks,
        'upcoming': upcoming
    }

def create_html_email(categorized_tasks):
    """Cria o HTML do email"""
    print("🎨 Criando email HTML...")
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='UTF-8'>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f4f4f4; }
            .container { background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #1a73e8; border-bottom: 3px solid #1a73e8; padding-bottom: 10px; }
            h2 { color: #1a73e8; margin-top: 30px; font-size: 1.2em; }
            .task-item { background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #1a73e8; border-radius: 5px; }
            .task-item strong { color: #1a73e8; }
            .overdue { border-left-color: #d32f2f; }
            .today { border-left-color: #f57c00; }
            .upcoming { border-left-color: #1976d2; }
            .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #e0e0e0; text-align: center; color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class='container'>
            <h1>📅 Suas Tarefas do Todoist - """ + datetime.now().strftime("%d/%m/%Y") + """</h1>
    """
    
    # Tarefas Vencidas
    if categorized_tasks['overdue']:
        html += "<h2>⚠️ Tarefas Vencidas (" + str(len(categorized_tasks['overdue'])) + ")</h2>"
        for task in categorized_tasks['overdue']:
            due_date = task['due']['date'] if task.get('due') else 'Sem data'
            html += f"""
            <div class='task-item overdue'>
                <strong>❌ {task['content']}</strong><br>
                <small>Venceu em: {due_date}</small>
            </div>
            """
    
    # Tarefas para Hoje
    if categorized_tasks['today']:
        html += "<h2>🎯 Tarefas para Hoje (" + str(len(categorized_tasks['today'])) + ")</h2>"
        for task in categorized_tasks['today']:
            html += f"""
            <div class='task-item today'>
                <strong>📌 {task['content']}</strong>
            </div>
            """
    
    # Próximas Tarefas
    if categorized_tasks['upcoming']:
        html += "<h2>📆 Próximos 3 Dias (" + str(len(categorized_tasks['upcoming'])) + ")</h2>"
        for task in categorized_tasks['upcoming']:
            due_date = task['due']['date'] if task.get('due') else 'Sem data'
            html += f"""
            <div class='task-item upcoming'>
                <strong>✓ {task['content']}</strong><br>
                <small>Vencimento: {due_date}</small>
            </div>
            """
    
    html += """
            <div class='footer'>
                <p><strong>📧 Email automático via GitHub Actions</strong></p>
                <p>🤖 Powered by Rube</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_email_proton(subject, html_content):
    """Envia email via Proton Mail SMTP"""
    print(f"📧 Enviando email para {len(recipients)} destinatários via Proton Mail...")
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = proton_email
        msg['To'] = ', '.join(recipients)
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            print(f"🔐 Conectando a {smtp_host}:{smtp_port}...")
            server.starttls()
            print(f"🔑 Autenticando com {proton_email}...")
            server.login(proton_email, proton_token)
            print(f"✉️ Enviando email...")
            server.sendmail(proton_email, recipients, msg.as_string())
        
        print(f"✅ Email enviado com sucesso! {datetime.now()}")
        return True
    
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False

def main():
    print("=" * 50)
    print("🚀 Iniciando automação de envio de tarefas")
    print("=" * 50)
    
    try:
        # Buscar tarefas
        tasks = get_todoist_tasks()
        print(f"✅ {len(tasks)} tarefas encontradas")
        
        # Categorizar
        categorized = categorize_tasks(tasks)
        print(f"📊 Vencidas: {len(categorized['overdue'])}")
        print(f"📊 Hoje: {len(categorized['today'])}")
        print(f"📊 Próximos 3 dias: {len(categorized['upcoming'])}")
        
        # Criar HTML
        html = create_html_email(categorized)
        
        # Enviar email
        subject = f"📅 Suas Tarefas do Todoist - {datetime.now().strftime('%d/%m/%Y')}"
        success = send_email_proton(subject, html)
        
        if success:
            print("\n✅ Automação concluída com sucesso!")
        else:
            print("\n❌ Falha ao enviar email")
            return False
    
    except Exception as e:
        print(f"\n❌ Erro na automação: {e}")
        return False
    
    return True

if __name__ == '__main__':
    main()
