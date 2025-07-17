#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SCRIPT PARA GERAR A PÁGINA PRINCIPAL (index.html) DO PORTAL DE PREVISÃO
Autor: Gemini AI / Reinaldo Haas
Data: 2025-07-17

Descrição:
Este script varre o diretório web em busca de rodadas de previsão,
gera um calendário HTML do mês corrente e insere links nos dias que
possuem uma previsão disponível.
"""

import os
import calendar
from datetime import date
import locale

# --- CONFIGURAÇÕES ---
# Diretório raiz do site.
WEB_ROOT = "/var/www/html"
# Nome do arquivo de saída
OUTPUT_FILE = "index.html"


def find_forecast_dirs(root_path):
    """
    Encontra os diretórios de previsão e os mapeia para objetos de data.

    Args:
        root_path (str): O caminho para o diretório raiz do site.

    Returns:
        dict: Um dicionário onde as chaves são objetos `datetime.date`
              e os valores são os nomes dos diretórios (ex: "2025071500").
    """
    forecasts = {}
    if not os.path.isdir(root_path):
        return forecasts

    for item in os.listdir(root_path):
        # Verifica se o item é um diretório e se o nome tem 10 caracteres e é numérico
        if os.path.isdir(os.path.join(root_path, item)) and len(item) == 10 and item.isdigit():
            try:
                year = int(item[0:4])
                month = int(item[4:6])
                day = int(item[6:8])
                forecast_date = date(year, month, day)
                # Armazena o primeiro diretório encontrado para um dia (caso haja 00Z e 12Z)
                if forecast_date not in forecasts:
                    forecasts[forecast_date] = item
            except ValueError:
                # Ignora diretórios que não representam uma data válida
                continue
    return forecasts


def generate_calendar_html(year, month, forecasts, today):
    """
    Gera o HTML de uma tabela de calendário para um determinado mês e ano.

    Args:
        year (int): O ano do calendário.
        month (int): O mês do calendário.
        forecasts (dict): Dicionário com as datas de previsão disponíveis.
        today (datetime.date): O dia atual, para destaque.

    Returns:
        str: Uma string contendo o HTML completo da tabela do calendário.
    """
    # Define a localidade para exibir nomes de meses e dias em Português
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except locale.Error:
        print("Aviso: Locale 'pt_BR.UTF-8' não encontrado. Usando locale padrão.")

    cal = calendar.monthcalendar(year, month)
    month_name = date(year, month, 1).strftime('%B').capitalize()

    # Inicia o HTML com o cabeçalho do mês
    html = f'<div class="calendar-header"><h2>{month_name} de {year}</h2></div>'
    html += '<table class="calendar">'
    # Cabeçalho com os dias da semana
    html += '<thead><tr>'
    for day in ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']:
        html += f'<th>{day}</th>'
    html += '</tr></thead>'

    # Corpo do calendário
    html += '<tbody>'
    for week in cal:
        html += '<tr>'
        for day in week:
            if day == 0:
                # Dia não pertence a este mês
                html += '<td class="empty"></td>'
            else:
                current_date = date(year, month, day)
                class_list = ["day-cell"]
                
                # Adiciona a classe 'today' se for o dia atual
                if current_date == today:
                    class_list.append("today")

                if current_date in forecasts:
                    # Dia com previsão: cria um link
                    dir_name = forecasts[current_date]
                    class_list.append("active")
                    classes = " ".join(class_list)
                    html += f'<td class="{classes}">'
                    html += f'<a href="./{dir_name}/index.html" title="Ver previsão de {day}/{month}/{year}">{day}</a>'
                    html += '</td>'
                else:
                    # Dia sem previsão
                    class_list.append("inactive")
                    classes = " ".join(class_list)
                    html += f'<td class="{classes}">{day}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html


def main():
    """Função principal que orquestra a geração da página."""
    print(f">> Iniciando geração da página em '{os.path.join(WEB_ROOT, OUTPUT_FILE)}'")
    
    forecast_map = find_forecast_dirs(WEB_ROOT)
    today = date.today()
    
    # Gera o HTML do calendário para o mês atual
    calendar_html = generate_calendar_html(today.year, today.month, forecast_map, today)

    # Template principal do HTML. A variável {calendar_html} será inserida aqui.
    html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Previsão do Tempo - UFSC</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f9; color: #333; }}
        .container {{ max-width: 900px; margin: 20px auto; padding: 25px; background-color: #fff; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 8px; }}
        header {{ border-bottom: 2px solid #005a9c; padding-bottom: 15px; margin-bottom: 25px; text-align: center; }}
        header h1 {{ color: #005a9c; margin: 0; }}
        a {{ color: #005a9c; text-decoration: none; }}
        hr {{ border: 0; border-top: 1px solid #eee; margin: 25px 0; }}
        footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ccc; font-size: 0.9em; text-align: center; }}

        /* Estilos do Calendário */
        .calendar-header {{ text-align: center; margin-bottom: 15px; }}
        .calendar-header h2 {{ margin: 0; color: #333; }}
        .calendar {{ width: 100%; border-collapse: collapse; }}
        .calendar th {{ padding: 10px; background-color: #e9f5ff; color: #005a9c; font-weight: bold; }}
        .calendar td {{ border: 1px solid #ddd; height: 80px; text-align: center; vertical-align: middle; }}
        .day-cell {{ font-size: 1.2em; font-weight: bold; transition: background-color 0.3s; }}
        .day-cell.inactive {{ color: #aaa; background-color: #f9f9f9; }}
        .day-cell.today {{ box-shadow: inset 0 0 0 3px #ff9800; }}
        .day-cell.active a {{ display: flex; align-items: center; justify-content: center; width: 100%; height: 100%; background-color: #c8e6c9; color: #2e7d32; font-weight: bold; }}
        .day-cell.active a:hover {{ background-color: #a5d6a7; text-decoration: none; }}
        .day-cell.empty {{ background-color: #fafafa; border: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Previsão UFSC</h1>
            <p>Curso FSC7115 - Modelagem Numérica da Atmosfera</p>
        </header>

        <h2>Boas-vindas!</h2>
        <p>Seja bem-vindo ao espaço do nosso grupo na Universidade Federal de Santa Catarina (UFSC), onde ciência, tecnologia e compromisso público se encontram para enfrentar desafios reais — e urgentes.</p>
        <p>Estamos prestes a lançar o <strong>primeiro modelo brasileiro capaz de prever lestadas com precisão operacional</strong>, um marco para a meteorologia no Sul do país. A ferramenta estará disponível em breve em <a href="https://tempo.ufsc.br">www.tempo.ufsc.br</a>, ampliando a capacidade de previsão de ventos costeiros intensos que impactam o cotidiano de milhares de pessoas em Santa Catarina e no litoral brasileiro.</p>
        
        <hr>

        <h2>Rodadas de Previsão Disponíveis</h2>
        {calendar_html}

        <footer>
            <p><strong>Contato:</strong> Reinaldo Haas | <a href="mailto:reinaldo.haas@ufsc.br">reinaldo.haas@ufsc.br</a></p>
            <p>Universidade Federal de Santa Catarina (UFSC)</p>
        </footer>
    </div>
</body>
</html>
    """

    # Escreve o conteúdo final no arquivo de saída
    try:
        with open(os.path.join(WEB_ROOT, OUTPUT_FILE), 'w', encoding='utf-8') as f:
            f.write(html_template)
        # Define permissões adequadas para o arquivo ser lido pelo servidor web
        os.chmod(os.path.join(WEB_ROOT, OUTPUT_FILE), 0o644)
        print(f"✅ Página '{OUTPUT_FILE}' gerada com sucesso!")
    except IOError as e:
        print(f"❌ ERRO ao escrever o arquivo: {e}")


if __name__ == "__main__":
    main()
