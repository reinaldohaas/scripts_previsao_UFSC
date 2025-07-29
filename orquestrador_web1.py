#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ORQUESTRADOR WEB DE PREVISÃO DO TEMPO - UFSC (v5 - Adicionado Cabeçalho Institucional)

Script unificado que:
1. Adiciona um cabeçalho institucional com logo e informações da UFSC.
2. Realiza o download do logo da UFSC se ele não existir localmente.
3. Gera a página principal com um calendário de previsões.
4. Gera um visualizador detalhado para cada rodada de previsão.

Autor: Gemini AI / Reinaldo Haas
Data da Modificação: 2025-07-22
"""

import os
import sys
import json
import calendar
import re
from datetime import datetime, date
import locale
from collections import defaultdict
import urllib.request

# --- CONFIGURAÇÕES GLOBAIS ---
WEB_ROOT = "/var/www/html"

# ==============================================================================
# SEÇÃO AUXILIAR: DOWNLOAD DE RECURSOS
# ==============================================================================

def ensure_logo_exists(target_dir):
    """Verifica se o logo da UFSC existe e, se não, faz o download."""
    logo_url = "https://upload.wikimedia.org/wikipedia/commons/6/6f/Brasao_UFSC_vertical_extenso.svg"
    logo_filename = "Brasao_UFSC_vertical_extenso.svg"
    logo_path = os.path.join(target_dir, logo_filename)

    if not os.path.exists(logo_path):
        print(f"-> Baixando o logo da UFSC para '{logo_path}'...")
        try:
            with urllib.request.urlopen(logo_url) as response, open(logo_path, 'wb') as out_file:
                data = response.read()
                out_file.write(data)
            print("✅ Logo baixado com sucesso.")
            os.chmod(logo_path, 0o644)
        except Exception as e:
            print(f"❌ ERRO ao baixar o logo: {e}")

# ==============================================================================
# SEÇÃO 1: FUNÇÕES PARA A PÁGINA PRINCIPAL (CALENDÁRIO)
# ==============================================================================

def find_forecast_dirs(root_path):
    """Encontra os diretórios de previsão e os mapeia para objetos de data."""
    forecasts = {}
    if not os.path.isdir(root_path):
        print(f"AVISO: Diretório raiz '{root_path}' não encontrado.")
        return forecasts
    for item in os.listdir(root_path):
        if os.path.isdir(os.path.join(root_path, item)) and len(item) == 10 and item.isdigit():
            try:
                forecast_date = date(int(item[0:4]), int(item[4:6]), int(item[6:8]))
                if forecast_date not in forecasts:
                    forecasts[forecast_date] = item
            except ValueError:
                continue
    return forecasts

def generate_calendar_html(year, month, forecasts, today):
    """Gera o HTML de uma tabela de calendário para o mês e ano fornecidos."""
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except locale.Error:
        print("AVISO: Locale 'pt_BR.UTF-8' não disponível.")
    cal = calendar.monthcalendar(year, month)
    month_name = date(year, month, 1).strftime('%B').capitalize()
    html = f'<div class="calendar-header"><h2>{month_name} de {year}</h2></div>'
    html += '<table class="calendar">'
    html += '<thead><tr>' + ''.join(f'<th>{day}</th>' for day in ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']) + '</tr></thead>'
    html += '<tbody>'
    for week in cal:
        html += '<tr>'
        for day in week:
            if day == 0:
                html += '<td class="empty"></td>'
            else:
                current_date = date(year, month, day)
                classes = ["day-cell", "today"] if current_date == today else ["day-cell"]
                if current_date in forecasts:
                    dir_name = forecasts[current_date]
                    classes.append("active")
                    html += f'<td class="{" ".join(classes)}"><a href="./{dir_name}/index.html" title="Ver previsão de {day}/{month}/{year}">{day}</a></td>'
                else:
                    classes.append("inactive")
                    html += f'<td class="{" ".join(classes)}">{day}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

def generate_main_index(root_path, forecasts):
    """Gera o arquivo index.html principal com o calendário e novo cabeçalho."""
    print(">> Gerando a página principal (index.html)...")
    ensure_logo_exists(root_path) # Garante que o logo da UFSC está presente
    
    today = date.today()
    calendar_html = generate_calendar_html(today.year, today.month, forecasts, today)
    main_page_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Previsão do Tempo - UFSC</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f9; color: #333; }}
        .container {{ max-width: 900px; margin: 20px auto; padding: 25px; background-color: #fff; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 8px; }}
        
        /* --- NOVO CABEÇALHO INSTITUCIONAL --- */
        .main-header {{
            display: flex;
            align-items: center;
            gap: 25px;
            padding-bottom: 15px;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }}
        .main-header .logo-container {{
            flex: 0 0 20%;
            max-width: 120px;
        }}
        .main-header .logo-container img {{
            width: 100%;
            height: auto;
        }}
        .main-header .header-text {{
            flex: 1;
        }}
        .header-text h2, .header-text p {{
            margin: 0;
            line-height: 1.3;
        }}
        .header-text h2 {{
            font-size: 1.3em;
            font-weight: 600;
            color: #000;
        }}
        .header-text p {{
            font-size: 1em;
            color: #444;
        }}
        /* --- FIM DO NOVO CABEÇALHO --- */
        
        header {{ border-bottom: 2px solid #005a9c; padding-bottom: 15px; margin-bottom: 25px; text-align: center; }}
        header h1 {{ color: #005a9c; margin: 0; }}
        a {{ color: #005a9c; text-decoration: none; }}
        hr {{ border: 0; border-top: 1px solid #eee; margin: 25px 0; }}
        footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ccc; font-size: 0.9em; text-align: center; }}
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
        <div class="main-header">
            <div class="logo-container">
                <img src="Brasao_UFSC_vertical_extenso.svg" alt="Brasão da UFSC">
            </div>
            <div class="header-text">
                <h2>Universidade Federal de Santa Catarina</h2>
                <p>Centro de Ciências Físicas e Matemáticas (CFM)</p>
                <p>Departamento de Física</p>
            </div>
        </div>

        <header>
            <h1>Previsão UFSC</h1>
            <p>Curso FSC7115 - Modelagem Numérica da Atmosfera</p>
        </header>
        <h2>Boas-vindas!</h2>
        <p>Seja bem-vindo ao espaço do nosso grupo na Universidade Federal de Santa Catarina (UFSC), onde ciência, tecnologia e compromisso público se encontram para enfrentar desafios reais — e urgentes.</p>
        <p>Estamos prestes a lançar o <strong>primeiro modelo brasileiro capaz de prever lestadas com precisão operacional</strong>, um marco para a meteorologia no Sul do país. A ferramenta estará disponível em breve em <a href="https://tempo.ufsc.br">www.tempo.ufsc.br</a>, ampliando a capacidade de previsão de ventos costeiros intensos que impactam o cotidiano de milhares de pessoas em Santa Catarina e no litoral brasileiro.</p>
        <p>Esse avanço é resultado do esforço conjunto de pesquisadores, estudantes e técnicos. <strong>Todas as ideias desta página foram desenvolvidas por alunos dos cursos de Modelagem Numérica da Atmosfera e Meteorologia de Mesoescala da UFSC</strong>, refletindo a qualidade da formação em meteorologia na universidade, que hoje abriga uma das gerações mais qualificadas de sua história.</p>
        <p>Este espaço é mais do que uma vitrine de projetos. É um convite à reflexão e à ação. Queremos construir pontes entre o conhecimento científico e a sociedade — e isso exige investimento, escuta e valorização.</p>
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
    try:
        output_path = os.path.join(root_path, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(main_page_html)
        os.chmod(output_path, 0o644)
        print("✅ Página principal gerada com sucesso.")
    except IOError as e:
        print(f"❌ ERRO ao gerar a página principal: {e}")

# ==============================================================================
# SEÇÃO 2: FUNÇÕES PARA O VISUALIZADOR (LÓGICA CORRIGIDA COM REGEX)
# ==============================================================================

# Regex CORRIGIDO: Note o HH_MM no final
ML_PATTERN = re.compile(r"^(.+?)_(\d+)_(\d{2}-\d{2}-\d{4}_\d{2}_\d{2})\.png$")
SL_PATTERN = re.compile(r"^(.+?)_(\d{2}-\d{2}-\d{4}_\d{2}_\d{2})\.png$")

def parse_info_from_filename(filename, is_multilevel):
    """
    Extrai informações (nível, data) de um nome de arquivo usando Regex.
    Retorna uma tupla (nível, objeto_datetime).
    """
    pattern = ML_PATTERN if is_multilevel else SL_PATTERN
    match = pattern.match(filename)
    
    if not match:
        return None, datetime.min

    try:
        # Formato de data CORRIGIDO: %H_%M
        datetime_format = '%d-%m-%Y_%H_%M'
        if is_multilevel:
            level = match.group(2)
            datetime_obj = datetime.strptime(match.group(3), datetime_format)
            return level, datetime_obj
        else:
            datetime_obj = datetime.strptime(match.group(2), datetime_format)
            return None, datetime_obj
    except (ValueError, IndexError):
        return None, datetime.min
def get_variable_descriptions():
    """Retorna um dicionário com as descrições detalhadas das variáveis."""
    return {
        "slp": "<b>Pressão ao Nível do Mar (Sea Level Pressure)</b><br>Pressão atmosférica reduzida ao nível médio do mar. É fundamental para identificar sistemas de alta e baixa pressão, frentes e cavados, que governam os padrões de tempo em escala sinótica. Mapas de SLP são uma ferramenta clássica e essencial na meteorologia.",
        "winds": "<b>Vento a 10 metros (Winds)</b><br>Velocidade e direção do vento na altura padrão de 10 metros acima da superfície. Essencial para previsões de tempo locais, segurança na navegação, dispersão de poluentes e avaliação do potencial de energia eólica.",
        "rh2": "<b>Umidade Relativa a 2 metros (Relative Humidity)</b><br>Razão entre a quantidade de vapor d'água presente no ar e a quantidade máxima que o ar poderia conter a uma dada temperatura, medida a 2 metros de altura. Valores altos indicam maior sensação de abafamento e potencial para neblina ou nevoeiro.",
        "T2": "<b>Temperatura a 2 metros (Temperature)</b><br>Temperatura do ar na altura padrão de 2 metros, convertida para Graus Celsius. É a variável de temperatura mais comum em previsões do tempo para o público geral, usada para prever máximas, mínimas e ondas de calor ou frio.",
        "mcape": "<b>CAPE Máxima na Coluna (Maximum CAPE)</b><br>CAPE (Energia Potencial Convectiva Disponível) é a quantidade de energia que uma parcela de ar teria se fosse elevada verticalmente. 'MCAPE' representa o valor máximo de CAPE em uma coluna atmosférica, indicando o potencial máximo para o desenvolvimento de tempestades severas e correntes ascendentes fortes.",
        "mcin": "<b>CIN Máxima na Coluna (Maximum CIN)</b><br>CIN (Inibição Convectiva) é a energia necessária para iniciar a convecção; funciona como uma 'tampa' que impede o ar de subir. 'MCIN' é o valor máximo dessa inibição. Uma CIN forte pode impedir tempestades, mas se for rompida por aquecimento ou forçante dinâmica, pode levar a tempestades explosivas.",
        "lcl": "<b>Nível de Condensação por Ascensão (Lifting Condensation Level)</b><br>A altura na qual uma parcela de ar ascendente se torna saturada (umidade relativa de 100%) e nuvens começam a se formar. É a base da nuvem convectiva.",
        "lfc": "<b>Nível de Convecção Livre (Level of Free Convection)</b><br>A altura na qual uma parcela de ar ascendente se torna mais quente que o ambiente ao redor, começando a subir livremente sem necessidade de forçante externa. O desenvolvimento de tempestades profundas ocorre acima do LFC.",
        "ctt": "<b>Temperatura do Topo das Nuvens (Cloud Top Temperature)</b><br>A temperatura no ponto mais alto de uma nuvem. Topos de nuvens muito frios (-60 a -80°C) estão associados a correntes ascendentes muito fortes (overshooting tops) e indicam um alto potencial para tempo severo, como granizo grande, ventos fortes e tornados.",
        "low_cloudfrac": "<b>Fração de Nuvens Baixas (Low Cloud Fraction)</b><br>A porcentagem do céu coberta por nuvens com base abaixo de 2 km. Relevante para aviação (teto) e previsão de tempo local (nebulosidade, garoa).",
        "mid_cloudfrac": "<b>Fração de Nuvens Médias (Mid Cloud Fraction)</b><br>A porcentagem do céu coberta por nuvens com base entre 2 e 7 km (Altocumulus, Altostratus).",
        "high_cloudfrac": "<b>Fração de Nuvens Altas (High Cloud Fraction)</b><br>A porcentagem do céu coberta por nuvens com base acima de 7 km (Cirrus, Cirrostratus, Cirrocumulus), compostas principalmente de cristais de gelo.",
        "mdbz": "<b>Reflectividade Máxima (Maximum Reflectivity)</b><br>O valor máximo de refletividade de radar (em dBZ) em toda a coluna vertical. É um excelente indicador da intensidade da precipitação e da presença de granizo. Valores acima de 50-60 dBZ frequentemente sugerem granizo.",
        "helicity": "<b>Helicidade Relativa à Tempestade (Storm Relative Helicity)</b><br>Uma medida da tendência de rotação em uma corrente ascendente de tempestade. Valores elevados de SRH (geralmente > 150 m²/s²) em baixos níveis (0-3 km) são um ingrediente chave para o desenvolvimento de supercélulas e tornados.",
        "pw": "<b>Água Precipitável (Precipitable Water)</b><br>A quantidade total de vapor d'água contida em uma coluna vertical da atmosfera. É um indicador do potencial máximo de chuva. Valores altos são uma condição necessária, mas não suficiente, para a ocorrência de chuvas intensas e inundações.",
        "td2": "<b>Temperatura do Ponto de Orvalho a 2 metros (Dew Point)</b><br>A temperatura para a qual o ar deve ser resfriado para se tornar saturado. É uma medida direta da umidade absoluta no ar. Valores de ponto de orvalho elevados indicam maior umidade e desconforto térmico.",
        "ppn_accum": "<b>Precipitação Acumulada Total</b><br>A quantidade total de precipitação (convectiva + não convectiva) acumulada desde o início da simulação do modelo. Útil para monitorar o total de chuva ao longo de um evento.",
        "ppn_conv": "<b>Precipitação Convectiva Horária</b><br>A precipitação gerada pelos processos convectivos do modelo (chuvas de verão, tempestades) na última hora. Geralmente associada a chuvas de alta intensidade e curta duração.",
        "ppn": "<b>Precipitação Total Horária</b><br>A precipitação total (convectiva + não convectiva/estratiforme) acumulada na última hora. Esta é a variável mais comum para previsão de intensidade de chuva.",
        "updraft_helicity": "<b>Helicidade da Corrente Ascendente (Updraft Helicity)</b><br>Uma medida direta da rotação dentro da corrente ascendente de uma tempestade simulada, sendo um forte indicador da presença de um mesociclone, a estrutura rotativa que pode gerar tornados.",
        "inv1": "<b>Índice de Inversão 1 (950-975 hPa)</b><br>Diferença de temperatura entre 950 hPa e 975 hPa. Valores positivos indicam uma inversão térmica de baixíssimo nível, relevante para a formação de nevoeiro e a dispersão de poluentes.",
        "inv2": "<b>Índice de Inversão 2 (850-900 hPa)</b><br>Diferença de temperatura entre 850 hPa e 900 hPa. Indica a presença de uma inversão de subsidência ou 'tampa' (capping inversion) que pode inibir a convecção ou, se rompida, levar a tempestades severas.",
        "u_stream": "<b>Linhas de Corrente (Streamlines)</b><br>Trajetórias instantâneas do fluxo de vento em um determinado nível de pressão. Excelentes para visualizar padrões de escoamento, como centros de alta/baixa pressão, e áreas de confluência ou difluência.",
        "u_theta_e": "<b>Temperatura Potencial Equivalente (Equivalent Potential Temperature)</b><br>A temperatura que uma parcela de ar teria se todo o seu vapor d'água condensasse e ela fosse trazida adiabaticamente para o nível de 1000 hPa. É conservada em processos úmidos e secos, sendo um excelente traçador para identificar diferentes massas de ar e instabilidade convectiva.",
        "u_avo": "<b>Vorticidade Absoluta (Absolute Vorticity)</b><br>Soma da vorticidade relativa (curvatura e cisalhamento do fluxo) e da vorticidade planetária (efeito Coriolis). Advecção de vorticidade ciclônica positiva em altos níveis é um mecanismo chave para forçar movimento ascendente e o desenvolvimento de ciclones em superfície.",
        "u_dbz": "<b>Reflectividade (Reflectivity)</b><br>Simulação da refletividade de radar em um nível de pressão específico. Útil para visualizar a estrutura vertical da precipitação em uma tempestade.",
        "u_geopotential": "<b>Altura Geopotencial (Geopotential Height)</b><br>A altura de uma superfície de pressão constante (ex: 500 hPa) acima do nível do mar. É a variável padrão para análise de cartas de altitude, usada para identificar cavados e cristas que direcionam os sistemas de tempo.",
        "u_omg": "<b>Ômega (Omega)</b><br>Velocidade vertical em coordenadas de pressão (hPa/s). Valores negativos indicam movimento ascendente (associado a nuvens e precipitação), enquanto valores positivos indicam subsidência e tempo bom.",
        "u_pressure": "<b>Pressão (Pressure)</b><br>Campo de pressão interpolado para um nível de pressão. Em uma análise isobárica (em um nível de pressão fixo), este campo será constante e igual ao nível selecionado. Pode ser útil em outras projeções ou análises.",
        "u_pvo": "<b>Vorticidade Potencial (Potential Vorticity)</b><br>Uma quantidade conservada que combina a vorticidade absoluta e a estabilidade estática. Anomalias de Vorticidade Potencial, especialmente as que descem da estratosfera, são diagnósticos poderosos para o desenvolvimento de ciclones explosivos.",
        "u_td": "<b>Ponto de Orvalho (Dew Point)</b><br>Temperatura do ponto de orvalho em um determinado nível de pressão. A proximidade entre a temperatura e o ponto de orvalho indica alta umidade relativa e potencial para formação de nuvens naquele nível.",
        "u_rh": "<b>Umidade Relativa (Relative Humidity)</b><br>Umidade relativa em um determinado nível de pressão. Essencial para prever a formação de nuvens em diferentes altitudes e a intensidade da precipitação.",
        "u_theta": "<b>Temperatura Potencial (Potential Temperature)</b><br>A temperatura que uma parcela de ar teria se fosse trazida adiabaticamente para o nível de referência de 1000 hPa. É usada para avaliar a estabilidade estática da atmosfera.",
        "u_temp": "<b>Temperatura (Temperature)</b><br>Temperatura do ar (em Celsius) em um determinado nível de pressão. Fundamental para identificar frentes frias/quentes em altitude e a presença da isoterma de 0°C (nível de congelamento).",
        "u_tv": "<b>Temperatura Virtual (Virtual Temperature)</b><br>A temperatura que o ar seco precisaria ter para ter a mesma densidade que o ar úmido na mesma pressão. É usada em cálculos de flutuabilidade e estabilidade que levam em conta a umidade.",
        "u_twb": "<b>Temperatura de Bulbo Úmido (Wet-Bulb Temperature)</b><br>A menor temperatura que o ar pode atingir por evaporação. É uma medida combinada de calor e umidade, importante para prever o tipo de precipitação (chuva, neve, chuva congelante).",
        "u_winds": "<b>Vento (Winds)</b><br>Velocidade e direção do vento em um determinado nível de pressão, geralmente visualizado com barbelas. Crucial para identificar os jatos de altos níveis (Jet Stream) e o cisalhamento do vento.",
        "u_cin": "<b>Inibição Convectiva (Convective Inhibition)</b><br>Campo 3D de CIN, mostrando a energia que impede a convecção em diferentes níveis. Útil para ver a profundidade de uma camada de inversão ('tampa').",
        "u_cape": "<b>Energia Potencial Convectiva Disponível (CAPE)</b><br>Campo 3D de CAPE. Mostra a distribuição vertical da instabilidade. Uma parcela pode encontrar CAPE significativo apenas acima de uma inversão de baixos níveis, o que é importante para prever convecção elevada."
    }



def generate_forecast_viewer(forecast_dir):
    """Gera os arquivos do visualizador usando Regex para robustez."""
    print(f"  -> Processando visualizador para: {os.path.basename(forecast_dir)}")
    simulation_data = {}
    domains = [d for d in os.listdir(forecast_dir) if os.path.isdir(os.path.join(forecast_dir, d)) and d.startswith('d0')]
    for domain in sorted(domains):
        domain_path = os.path.join(forecast_dir, domain)
        simulation_data[domain] = {}
        variables = [v for v in os.listdir(domain_path) if os.path.isdir(os.path.join(domain_path, v))]
        for variable in sorted(variables):
            variable_path = os.path.join(domain_path, variable)
            image_files = [f for f in os.listdir(variable_path) if f.endswith('.png')]
            
            is_multilevel = variable.startswith('u_')
            
            if is_multilevel:
                levels_data = defaultdict(list)
                for f in image_files:
                    level, _ = parse_info_from_filename(f, is_multilevel=True)
                    if level:
                        levels_data[level].append(os.path.join(domain, variable, f))
                
                sorted_levels_data = {}
                for level, files in levels_data.items():
                    sorted_levels_data[level] = sorted(files, key=lambda f: parse_info_from_filename(os.path.basename(f), is_multilevel=True)[1])
                simulation_data[domain][variable] = sorted_levels_data
            else:
                sorted_files = sorted(image_files, key=lambda f: parse_info_from_filename(f, is_multilevel=False)[1])
                simulation_data[domain][variable] = [os.path.join(domain, variable, f) for f in sorted_files]

    data_js_path = os.path.join(forecast_dir, 'data.js')
    with open(data_js_path, 'w', encoding='utf-8') as f:
        f.write("const simulationData = ")
        json.dump(simulation_data, f, indent=4)
        f.write(";")

    viewer_html_path = os.path.join(forecast_dir, 'index.html')
    descriptions_json = json.dumps(get_variable_descriptions(), indent=12)
    viewer_template = HTML_TEMPLATE_VISUALIZADOR.replace("'%%VARIABLE_DESCRIPTIONS%%'", descriptions_json)
    with open(viewer_html_path, 'w', encoding='utf-8') as f:
        f.write(viewer_template)
    
    os.chmod(data_js_path, 0o644)
    os.chmod(viewer_html_path, 0o644)

# ==============================================================================
# TEMPLATE HTML PARA O VISUALIZADOR (JAVASCRIPT TAMBÉM CORRIGIDO)
# ==============================================================================
HTML_TEMPLATE_VISUALIZADOR = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualizador de Rodadas WRF</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 0; background-color: #f4f4f9; color: #333; }
        .container { max-width: 1200px; margin: auto; padding: 20px; }
        header { background-color: #004b8d; color: white; padding: 20px; text-align: center; }
        header h1 { margin: 0; font-size: 2em; }
        header p { margin: 5px 0 0; }
        .controls { display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-end; background-color: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .control-group { display: flex; flex-direction: column; }
        label { font-weight: bold; margin-bottom: 5px; font-size: 0.9em; }
        select, button { padding: 10px; border-radius: 5px; border: 1px solid #ccc; font-size: 1em; }
        button { background-color: #0056b3; color: white; cursor: pointer; border: none; height: 40px; }
        button:hover { background-color: #003d82; }
        .viewer { text-align: center; }
        #image-display { max-width: 100%; border: 1px solid #ddd; background-color: #fff; border-radius: 8px; }
        .animation-controls { display: flex; align-items: center; justify-content: center; gap: 15px; margin-top: 15px; flex-wrap: wrap; }
        #frame-slider { flex-grow: 1; max-width: 600px; cursor: pointer; }
        #frame-info { font-weight: bold; min-width: 220px; text-align: center; }
        .description { margin-top: 30px; padding: 20px; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .description h3 { margin-top: 0; color: #004b8d; }
    </style>
</head>
<body>
    <header>
        <h1>Visualizador de Rodadas do Modelo WRF</h1>
        <p id="run-date"></p>
    </header>
    <div class="container">
        <div class="controls">
            <div class="control-group">
                <label for="domain-select">Domínio:</label>
                <select id="domain-select"></select>
            </div>
            <div class="control-group">
                <label for="variable-select">Variável:</label>
                <select id="variable-select"></select>
            </div>
            <div class="control-group" id="level-control-group" style="display: none;">
                <label for="level-select">Nível (hPa):</label>
                <select id="level-select"></select>
            </div>
        </div>
        <div class="viewer">
            <img id="image-display" src="" alt="Visualização do modelo">
            <div class="animation-controls">
                <button id="play-pause-btn">Play</button>
                <input type="range" id="frame-slider" min="0" max="1" value="0">
                <span id="frame-info">Frame: 0/0 | Time: --</span>
            </div>
        </div>
        <div class="description">
            <h3 id="desc-title">Descrição da Variável</h3>
            <p id="desc-content"></p>
        </div>
    </div>
    <script src="data.js"></script>
    <script>
        const variableDescriptions = '%%VARIABLE_DESCRIPTIONS%%';
        const domainSelect = document.getElementById('domain-select');
        const variableSelect = document.getElementById('variable-select');
        const levelSelect = document.getElementById('level-select');
        const levelControlGroup = document.getElementById('level-control-group');
        const imageDisplay = document.getElementById('image-display');
        const playPauseBtn = document.getElementById('play-pause-btn');
        const frameSlider = document.getElementById('frame-slider');
        const frameInfo = document.getElementById('frame-info');
        const descTitle = document.getElementById('desc-title');
        const descContent = document.getElementById('desc-content');
        const runDateElement = document.getElementById('run-date');
        let currentDomain, currentVariable, currentLevel;
        let imagePaths = [];
        let animationInterval = null;
        const animationSpeed = 500;
        function init() {
            const pathParts = window.location.pathname.split('/').filter(Boolean);
            runDateElement.textContent = `Rodada de: ${pathParts[pathParts.length - 2] || 'Data não encontrada'}`;
            const domains = Object.keys(simulationData);
            if (domains.length === 0) {
                alert("Dados de simulação não encontrados ou vazios. Verifique o arquivo data.js");
                return;
            }
            domainSelect.innerHTML = domains.map(d => `<option value="${d}">${d.toUpperCase()}</option>`).join('');
            domainSelect.addEventListener('change', onDomainChange);
            variableSelect.addEventListener('change', onVariableChange);
            levelSelect.addEventListener('change', onLevelChange);
            frameSlider.addEventListener('input', onSliderChange);
            playPauseBtn.addEventListener('click', toggleAnimation);
            onDomainChange();
        }
        function onDomainChange() {
            currentDomain = domainSelect.value;
            const variables = Object.keys(simulationData[currentDomain]);
            variableSelect.innerHTML = variables.map(v => `<option value="${v}">${v}</option>`).join('');
            onVariableChange();
        }
        function onVariableChange() {
            stopAnimation();
            currentVariable = variableSelect.value;
            updateDescription();
            const varData = simulationData[currentDomain][currentVariable];
            if (Array.isArray(varData)) {
                levelControlGroup.style.display = 'none';
                currentLevel = null;
                imagePaths = varData;
                updateAnimationUI();
            } else {
                levelControlGroup.style.display = 'flex';
                const levels = Object.keys(varData).sort((a, b) => parseInt(b) - parseInt(a));
                levelSelect.innerHTML = levels.map(l => `<option value="${l}">${l}</option>`).join('');
                onLevelChange();
            }
        }
        function onLevelChange() {
            stopAnimation();
            currentLevel = levelSelect.value;
            imagePaths = simulationData[currentDomain][currentVariable][currentLevel];
            updateAnimationUI();
        }
        function updateAnimationUI() {
            currentFrame = 0;
            frameSlider.max = imagePaths.length > 0 ? imagePaths.length - 1 : 0;
            frameSlider.value = 0;
            updateDisplay();
        }
        function updateDisplay() {
            if (imagePaths.length === 0) {
                imageDisplay.src = "";
                imageDisplay.alt = "Nenhuma imagem disponível para esta seleção.";
                frameInfo.textContent = "Frame: 0/0 | Validade: --";
                return;
            };
            imageDisplay.src = imagePaths[currentFrame];
            frameSlider.value = currentFrame;
            const totalFrames = imagePaths.length;
            const filename = imagePaths[currentFrame].split('/').pop();
            const timeParts = filename.replace('.png','').split('_');
            const timeStr = currentLevel ? timeParts.slice(2).join('_') : timeParts.slice(1).join('_');
            const prefix = currentLevel ? `Nível ${currentLevel}hPa | ` : "";
            frameInfo.textContent = `${prefix}Frame: ${currentFrame + 1}/${totalFrames} | Validade: ${timeStr}`;
        }
        function updateDescription() {
            const desc = variableDescriptions[currentVariable] || "Descrição não disponível.";
            descTitle.textContent = currentVariable.toUpperCase();
            descContent.innerHTML = desc;
        }
        function onSliderChange() {
            stopAnimation();
            currentFrame = parseInt(frameSlider.value, 10);
            updateDisplay();
        }
        function toggleAnimation() {
            if (animationInterval) {
                stopAnimation();
            } else {
                startAnimation();
            }
        }
        function startAnimation() {
            if (imagePaths.length < 2) return;
            playPauseBtn.textContent = "Pause";
            animationInterval = setInterval(() => {
                currentFrame = (currentFrame + 1) % imagePaths.length;
                updateDisplay();
            }, animationSpeed);
        }
        function stopAnimation() {
            clearInterval(animationInterval);
            animationInterval = null;
            playPauseBtn.textContent = "Play";
        }
        document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>
"""

# ==============================================================================
# FUNÇÃO PRINCIPAL (ORQUESTRADOR)
# ==============================================================================
def main():
    """Função principal que orquestra todo o processo de geração das páginas web."""
    print("="*50)
    print("INICIANDO ORQUESTRADOR WEB DE PREVISÃO DO TEMPO (UFSC)")
    print("="*50)
    forecast_dirs_map = find_forecast_dirs(WEB_ROOT)
    if not forecast_dirs_map:
        print("Nenhum diretório de previsão encontrado. Saindo.")
        return
    generate_main_index(WEB_ROOT, forecast_dirs_map)
    print("\n>> Gerando visualizadores para cada rodada...")
    for dir_name in sorted(forecast_dirs_map.values(), reverse=True):
        forecast_path = os.path.join(WEB_ROOT, dir_name)
        generate_forecast_viewer(forecast_path)
    print("\n" + "="*50)
    print("Orquestração concluída com sucesso!")
    print("="*50)

if __name__ == "__main__":
    main()
