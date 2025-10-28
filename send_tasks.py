import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Configurações - GMAIL SMTP
todoist_token = os.environ.get('TODOIST_TOKEN')
gmail_email = 'jptipworld@gmail.com'
gmail_password = os.environ.get('GMAIL_PASSWORD')
smtp_host = 'smtp.gmail.com'
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
    """Cria o HTML do email com layout melhorado"""
    print("🎨 Criando email HTML...")
    
    today = datetime.now().date()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='UTF-8'>
        <style>
            * { margin: 0; padding: 0; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: #f5f5f5;
                padding: 20px 0;
            }
            .container { 
                max-width: 700px; 
                margin: 0 auto; 
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px 30px;
                text-align: center;
                color: white;
            }
            .header h1 {
                font-size: 28px;
                font-weight: 600;
                margin-bottom: 5px;
            }
            .header p {
                font-size: 14px;
                opacity: 0.9;
            }
            .stats {
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 15px;
                padding: 30px;
                background: #f9f9f9;
                border-bottom: 1px solid #e5e5e5;
            }
            .stat-box {
                text-align: center;
                padding: 15px;
                background: white;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            .stat-box.overdue { border-left-color: #e74c3c; }
            .stat-box.today { border-left-color: #f39c12; }
            .stat-box.upcoming { border-left-color: #27ae60; }
            .stat-number {
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 5px;
            }
            .stat-overdue { color: #e74c3c; }
            .stat-today { color: #f39c12; }
            .stat-upcoming { color: #27ae60; }
            .stat-label {
                font-size: 12px;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-weight: 500;
            }
            .content {
                padding: 30px;
            }
            .section {
                margin-bottom: 30px;
            }
            .section-title {
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 8px;
                padding-bottom: 10px;
                border-bottom: 2px solid #f0f0f0;
            }
            .section-title.overdue { color: #e74c3c; }
            .section-title.today { color: #f39c12; }
            .section-title.upcoming { color: #27ae60; }
            .task-item {
                padding: 15px;
                margin-bottom: 10px;
                background: #f9f9f9;
                border-left: 4px solid #667eea;
                border-radius: 6px;
                transition: all 0.2s;
            }
            .task-item.overdue { border-left-color: #e74c3c; background: #fff5f5; }
            .task-item.today { border-left-color: #f39c12; background: #fffaf0; }
            .task-item.upcoming { border-left-color: #27ae60; background: #f5fdf9; }
            .task-content {
                font-size: 14px;
                color: #333;
                font-weight: 500;
                margin-bottom: 8px;
            }
            .task-date {
                font-size: 12px;
                color: #999;
                display: flex;
                align-items: center;
                gap: 5px;
            }
            .footer {
                background: #f9f9f9;
                padding: 20px 30px;
                text-align: center;
                border-top: 1px solid #e5e5e5;
                font-size: 12px;
                color: #999;
            }
        </style>
    </head>
    <body>
        <div class='container'>
            <div class='header'>
                <h1>📋 Suas Tarefas</h1>
                <p>Todoist • """ + today.strftime("%d de %B de %Y") + """</p>
            </div>
            
            <div class='stats'>
    """
    
    # Stats boxes
    html += f"""
                <div class='stat-box overdue'>
                    <div class='stat-number stat-overdue'>{len(categorized_tasks['overdue'])}</div>
                    <div class='stat-label'>Vencidas</div>
                </div>
                <div class='stat-box today'>
                    <div class='stat-number stat-today'>{len(categorized_tasks['today'])}</div>
                    <div class='stat-label'>Hoje</div>
                </div>
                <div class='stat-box upcoming'>
                    <div class='stat-number stat-upcoming'>{len(categorized_tasks['upcoming'])}</div>
                    <div class='stat-label'>Próximos 3 Dias</div>
                </div>
            </div>
            
            <div class='content'>
    """
    
    # Tarefas Vencidas
    if categorized_tasks['overdue']:
        html += f"""
                <div class='section'>
                    <div class='section-title overdue'>❌ Tarefas Vencidas ({len(categorized_tasks['overdue'])})</div>
        """
        for task in categorized_tasks['overdue']:
            due_date = task['due']['date'] if task.get('due') else 'Sem data'
            html += f"""
                    <div class='task-item overdue'>
                        <div class='task-content'>{task['content']}</div>
                        <div class='task-date'>📅 Vencimento: {due_date}</div>
                    </div>
            """
        html += """
                </div>
        """
    
    # Tarefas para Hoje
    if categorized_tasks['today']:
        html += f"""
                <div class='section'>
                    <div class='section-title today'>🎯 Tarefas para Hoje ({len(categorized_tasks['today'])})</div>
        """
        for task in categorized_tasks['today']:
            html += f"""
                    <div class='task-item today'>
                        <div class='task-content'>{task['content']}</div>
                    </div>
            """
        html += """
                </div>
        """
    
    # Próximas Tarefas
    if categorized_tasks['upcoming']:
        html += f"""
                <div class='section'>
                    <div class='section-title upcoming'>📆 Próximos 3 Dias ({len(categorized_tasks['upcoming'])})</div>
        """
        for task in categorized_tasks['upcoming']:
            due_date = task['due']['date'] if task.get('due') else 'Sem data'
            html += f"""
                    <div class='task-item upcoming'>
                        <div class='task-content'>{task['content']}</div>
                        <div class='task-date'>📅 Vencimento: {due_date}</div>
                    </div>
            """
        html += """
                </div>
        """
    
    html += """
            </div>
            
            <div class='footer'>
                <p>📧 Email automático via GitHub Actions • Powered by Rube 🤖</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_email_gmail(subject, html_content):
    """Envia email via Gmail SMTP"""
    print(f"📧 Enviando email para {len(recipients)} destinatários via Gmail...")
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = gmail_email
        msg['To'] = ', '.join(recipients)
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            print(f"🔐 Conectando a {smtp_host}:{smtp_port}...")
            server.starttls()
            print(f"🔑 Autenticando com {gmail_email}...")
            server.login(gmail_email, gmail_password)
            print(f"✉️ Enviando email...")
            server.sendmail(gmail_email, recipients, msg.as_string())
        
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
        subject = f"📋 Suas Tarefas - {datetime.now().strftime('%d/%m/%Y')}"
        success = send_email_gmail(subject, html)
        
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
