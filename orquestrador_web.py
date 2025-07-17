#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ORQUESTRADOR WEB DE PREVISÃO DO TEMPO - UFSC (Versão com Suporte a Múltiplos Níveis)

Script unificado que:
1. Gera a página principal com um calendário.
2. Itera sobre cada rodada e gera um visualizador detalhado que suporta
   variáveis de nível único e de múltiplos níveis verticais.

Autor: Gemini AI / Reinaldo Haas
Data da Modificação: 2025-07-17
"""

import os
import sys
import json
import calendar
from datetime import datetime, date
import locale
from collections import defaultdict

# --- CONFIGURAÇÕES GLOBAIS ---
WEB_ROOT = "/var/www/html"

# ==============================================================================
# SEÇÃO 1: FUNÇÕES PARA A PÁGINA PRINCIPAL (CALENDÁRIO) - Sem alterações
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
    """Gera o arquivo index.html principal com o calendário."""
    print(">> Gerando a página principal (index.html)...")
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
# SEÇÃO 2: FUNÇÕES PARA O VISUALIZADOR (COM LÓGICA DE NÍVEIS)
# ==============================================================================

def parse_date_from_filename(filename, has_level=False):
    """Extrai o datetime de um nome de arquivo, com ou sem nível."""
    try:
        parts = filename.replace('.png', '').split('_')
        date_str_index = 2 if has_level else 1
        date_str = '_'.join(parts[date_str_index:])
        return datetime.strptime(date_str, '%d-%m-%Y_%H:%M')
    except (IndexError, ValueError):
        return datetime.min

def get_variable_descriptions():
    """Retorna um dicionário com as descrições das variáveis."""
    # O dicionário completo de descrições é incluído aqui...
    return {
        "slp": "<b>Pressão ao Nível do Mar (Sea Level Pressure)</b><br>Pressão atmosférica reduzida ao nível médio do mar. É fundamental para identificar sistemas de alta e baixa pressão, frentes e cavados, que governam os padrões de tempo em escala sinótica. Mapas de SLP são uma ferramenta clássica e essencial na meteorologia.",
        "winds": "<b>Vento a 10 metros (Winds)</b><br>Velocidade e direção do vento na altura padrão de 10 metros acima da superfície. Essencial para previsões de tempo locais, segurança na navegação, dispersão de poluentes e avaliação do potencial de energia eólica.",
        "mcape": "<b>CAPE Máxima na Coluna (Maximum CAPE)</b><br>CAPE (Energia Potencial Convectiva Disponível) é a quantidade de energia que uma parcela de ar teria se fosse elevada verticalmente. 'MCAPE' representa o valor máximo de CAPE em uma coluna atmosférica, indicando o potencial máximo para o desenvolvimento de tempestades severas e correntes ascendentes fortes.",
        "mcin": "<b>CIN Máxima na Coluna (Maximum CIN)</b><br>CIN (Inibição Convectiva) é a energia necessária para iniciar a convecção; funciona como uma 'tampa' que impede o ar de subir. 'MCIN' é o valor máximo dessa inibição. Uma CIN forte pode impedir tempestades, mas se for rompida por aquecimento ou forçante dinâmica, pode levar a tempestades explosivas.",
        "ctt": "<b>Temperatura do Topo das Nuvens (Cloud Top Temperature)</b><br>A temperatura no ponto mais alto de uma nuvem. Topos de nuvens muito frios (-60 a -80°C) estão associados a correntes ascendentes muito fortes (overshooting tops) e indicam um alto potencial para tempo severo, como granizo grande, ventos fortes e tornados.",
        "low_cloudfrac": "<b>Fração de Nuvens Baixas (Low Cloud Fraction)</b><br>A porcentagem do céu coberta por nuvens com base abaixo de 2 km. Relevante para aviação (teto) e previsão de tempo local (nebulosidade, garoa).",
        "mid_cloudfrac": "<b>Fração de Nuvens Médias (Mid Cloud Fraction)</b><br>A porcentagem do céu coberta por nuvens com base entre 2 e 7 km (Altocumulus, Altostratus).",
        "high_cloudfrac": "<b>Fração de Nuvens Altas (High Cloud Fraction)</b><br>A porcentagem do céu coberta por nuvens com base acima de 7 km (Cirrus, Cirrostratus, Cirrocumulus), compostas principalmente de cristais de gelo.",
        "mdbz": "<b>Reflectividade Máxima (Maximum Reflectivity)</b><br>O valor máximo de refletividade de radar (em dBZ) em toda a coluna vertical. É um excelente indicador da intensidade da precipitação e da presença de granizo. Valores acima de 50-60 dBZ frequentemente sugerem granizo.",
        "helicity": "<b>Helicidade Relativa à Tempestade (Storm Relative Helicity)</b><br>Uma medida da tendência de rotação em uma corrente ascendente de tempestade. Valores elevados de SRH (geralmente > 150 m²/s²) em baixos níveis (0-3 km) são um ingrediente chave para o desenvolvimento de supercélulas e tornados.",
        "pw": "<b>Água Precipitável (Precipitable Water)</b><br>A quantidade total de vapor d'água contida em uma coluna vertical da atmosfera. É um indicador do potencial máximo de chuva. Valores altos são uma condição necessária, mas não suficiente, para a ocorrência de chuvas intensas e inundações.",
        "ppn": "<b>Precipitação Total Horária</b><br>A precipitação total (convectiva + não convectiva/estratiforme) acumulada na última hora. Esta é a variável mais comum para previsão de intensidade de chuva.",
        "updraft_helicity": "<b>Helicidade da Corrente Ascendente (Updraft Helicity)</b><br>Uma medida direta da rotação dentro da corrente ascendente de uma tempestade simulada, sendo um forte indicador da presença de um mesociclone, a estrutura rotativa que pode gerar tornados.",
        "u_pvo": "<b>Vorticidade Potencial (Potential Vorticity)</b><br>Uma quantidade conservada que combina a vorticidade absoluta e a estabilidade estática. Anomalias de Vorticidade Potencial, especialmente as que descem da estratosfera, são diagnósticos poderosos para o desenvolvimento de ciclones explosivos.",
        "u_temp": "<b>Temperatura (Temperature)</b><br>Temperatura do ar (em Celsius) em um determinado nível de pressão. Fundamental para identificar frentes frias/quentes em altitude e a presença da isoterma de 0°C (nível de congelamento).",
        # Adicione outras descrições conforme necessário
    }

def generate_forecast_viewer(forecast_dir):
    """Gera os arquivos do visualizador, agora com suporte a múltiplos níveis."""
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
            
            # LÓGICA DE DETECÇÃO DE NÍVEIS
            if variable.startswith('u_'):
                levels_data = defaultdict(list)
                for f in image_files:
                    try:
                        level = f.split('_')[1]
                        levels_data[level].append(os.path.join(domain, variable, f))
                    except IndexError:
                        continue
                
                # Ordena as imagens dentro de cada nível e armazena
                sorted_levels_data = {}
                for level, files in levels_data.items():
                    sorted_levels_data[level] = sorted(files, key=lambda f: parse_date_from_filename(f, has_level=True))
                simulation_data[domain][variable] = sorted_levels_data
            else:
                # Variável de nível único (lógica antiga)
                sorted_files = sorted(image_files, key=lambda f: parse_date_from_filename(f, has_level=False))
                simulation_data[domain][variable] = [os.path.join(domain, variable, f) for f in sorted_files]

    # --- Gera o arquivo data.js ---
    data_js_path = os.path.join(forecast_dir, 'data.js')
    with open(data_js_path, 'w', encoding='utf-8') as f:
        f.write("const simulationData = ")
        json.dump(simulation_data, f, indent=4)
        f.write(";")

    # --- Gera o arquivo index.html (visualizador) ---
    viewer_html_path = os.path.join(forecast_dir, 'index.html')
    descriptions_json = json.dumps(get_variable_descriptions(), indent=12)
    viewer_template = HTML_TEMPLATE_VISUALIZADOR.replace(
        "'%%VARIABLE_DESCRIPTIONS%%'", descriptions_json
    )
    with open(viewer_html_path, 'w', encoding='utf-8') as f:
        f.write(viewer_template)
    
    os.chmod(data_js_path, 0o644)
    os.chmod(viewer_html_path, 0o644)

# ==============================================================================
# TEMPLATE HTML PARA O VISUALIZADOR (COM JAVASCRIPT MODIFICADO)
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
            runDateElement.textContent = `Rodada de: ${pathParts[pathParts.length - 1] || 'Data não encontrada'}`;
            const domains = Object.keys(simulationData);
            if (domains.length === 0) return;
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
            const timePart = filename.replace('.png', '').split('_').slice(currentLevel ? 2 : 1).join('_');
            frameInfo.textContent = `Frame: ${currentFrame + 1}/${totalFrames} | Validade: ${timePart}`;
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
