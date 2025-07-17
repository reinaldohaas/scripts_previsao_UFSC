#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para gerar um visualizador HTML para as saídas do wrfplot.

Este script deve ser executado após o 'rodada_diaria.sh', apontando para
o diretório da simulação. Ele irá gerar um 'index.html' e um 'data.js'
que contêm todos os dados necessários para a visualização.
"""

import os
import sys
import json
from datetime import datetime

def parse_filename_date(filename):
    """Extrai o objeto datetime do nome do arquivo para ordenação."""
    try:
        # Formato esperado: variavel_dd-mm-YYYY_HH:MM.png
        base_name = filename.replace('.png', '')
        date_str = base_name.split('_', 1)[1]
        # Substitui ':' para compatibilidade se necessário, mas strptime lida com isso.
        return datetime.strptime(date_str, '%d-%m-%Y_%H:%M')
    except (IndexError, ValueError):
        # Retorna uma data antiga se o formato falhar, para ordenação
        return datetime.min

def generate_viewer(root_dir):
    """
    Gera os arquivos index.html e data.js para visualização da rodada.
    """
    if not os.path.isdir(root_dir):
        print(f"ERRO: O diretório '{root_dir}' não foi encontrado.")
        sys.exit(1)

    print(f"Processando o diretório: {root_dir}")
    simulation_data = {}
    domains = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d)) and d.startswith('d0')]
    
    for domain in sorted(domains):
        domain_path = os.path.join(root_dir, domain)
        simulation_data[domain] = {}
        variables = [v for v in os.listdir(domain_path) if os.path.isdir(os.path.join(domain_path, v))]
        
        for variable in sorted(variables):
            variable_path = os.path.join(domain_path, variable)
            image_files = [f for f in os.listdir(variable_path) if f.endswith('.png')]
            
            # Ordena os arquivos de imagem com base na data/hora extraída do nome
            sorted_files = sorted(image_files, key=parse_filename_date)
            
            # Adiciona o caminho relativo para o JS
            simulation_data[domain][variable] = [os.path.join(domain, variable, f) for f in sorted_files]

    # --- Gera o arquivo data.js ---
    data_js_path = os.path.join(root_dir, 'data.js')
    print(f"Gerando {data_js_path}...")
    with open(data_js_path, 'w') as f:
        f.write("const simulationData = ")
        json.dump(simulation_data, f, indent=4)
        f.write(";")

    # --- Gera o arquivo index.html ---
    index_html_path = os.path.join(root_dir, 'index.html')
    print(f"Gerando {index_html_path}...")
    with open(index_html_path, 'w') as f:
        f.write(HTML_TEMPLATE)

    print("\nConcluído! Acesse o visualizador em seu navegador.")
    print(f"URL sugerido: http://<seu-servidor>/{os.path.basename(root_dir)}/")

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
        "u_winds_temp": "<b>Vento e Temperatura (Winds and Temperature)</b><br>Sobreposição de isotermas (linhas de temperatura constante) e barbelas de vento. Permite a análise da advecção de temperatura (transporte de ar quente ou frio pelo vento).",
        "u_cin": "<b>Inibição Convectiva (Convective Inhibition)</b><br>Campo 3D de CIN, mostrando a energia que impede a convecção em diferentes níveis. Útil para ver a profundidade de uma camada de inversão ('tampa').",
        "u_cape": "<b>Energia Potencial Convectiva Disponível (CAPE)</b><br>Campo 3D de CAPE. Mostra a distribuição vertical da instabilidade. Uma parcela pode encontrar CAPE significativo apenas acima de uma inversão de baixos níveis, o que é importante para prever convecção elevada."
    }


# ==============================================================================
# TEMPLATE HTML E JAVASCRIPT
# ==============================================================================
HTML_TEMPLATE = """
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
        .controls { display: flex; flex-wrap: wrap; gap: 20px; align-items: center; background-color: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .control-group { display: flex; flex-direction: column; }
        label { font-weight: bold; margin-bottom: 5px; font-size: 0.9em; }
        select, button { padding: 10px; border-radius: 5px; border: 1px solid #ccc; font-size: 1em; }
        button { background-color: #0056b3; color: white; cursor: pointer; border: none; }
        button:hover { background-color: #003d82; }
        .viewer { text-align: center; }
        #image-display { max-width: 100%; border: 1px solid #ddd; background-color: #fff; border-radius: 8px; }
        .animation-controls { display: flex; align-items: center; justify-content: center; gap: 15px; margin-top: 15px; flex-wrap: wrap; }
        #frame-slider { flex-grow: 1; max-width: 600px; cursor: pointer; }
        #frame-info { font-weight: bold; min-width: 180px; text-align: center; }
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
        // Objeto com as descrições das variáveis
        const variableDescriptions = {
            // ... (descrições serão inseridas aqui) ...
        };

        // Elementos da UI
        const domainSelect = document.getElementById('domain-select');
        const variableSelect = document.getElementById('variable-select');
        const imageDisplay = document.getElementById('image-display');
        const playPauseBtn = document.getElementById('play-pause-btn');
        const frameSlider = document.getElementById('frame-slider');
        const frameInfo = document.getElementById('frame-info');
        const descTitle = document.getElementById('desc-title');
        const descContent = document.getElementById('desc-content');
        const runDateElement = document.getElementById('run-date');

        let currentDomain, currentVariable, currentFrame = 0;
        let imagePaths = [];
        let animationInterval = null;
        const animationSpeed = 500; // ms

        // Inicialização
        function init() {
            // Extrai a data da URL
            const pathParts = window.location.pathname.split('/').filter(Boolean);
            runDateElement.textContent = `Rodada de: ${pathParts[pathParts.length - 1] || 'Data não encontrada'}`;

            const domains = Object.keys(simulationData);
            domainSelect.innerHTML = domains.map(d => `<option value="${d}">${d.toUpperCase()}</option>`).join('');
            
            domainSelect.addEventListener('change', onDomainChange);
            variableSelect.addEventListener('change', onVariableChange);
            frameSlider.addEventListener('input', onSliderChange);
            playPauseBtn.addEventListener('click', toggleAnimation);

            // Carrega o primeiro domínio e variável
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
            imagePaths = simulationData[currentDomain][currentVariable];
            
            frameSlider.max = imagePaths.length - 1;
            frameSlider.value = 0;
            currentFrame = 0;
            
            updateDisplay();
            updateDescription();
        }
        
        function updateDisplay() {
            if (imagePaths.length === 0) return;
            
            imageDisplay.src = imagePaths[currentFrame];
            frameSlider.value = currentFrame;

            const totalFrames = imagePaths.length;
            const filename = imagePaths[currentFrame].split('/').pop();
            const timePart = filename.replace('.png', '').split('_').slice(1).join('_');
            frameInfo.textContent = `Frame: ${currentFrame + 1}/${totalFrames} | Validade: ${timePart}`;
        }
        
        function updateDescription() {
            const desc = variableDescriptions[currentVariable] || "Descrição não disponível.";
            descTitle.textContent = currentVariable;
            descContent.innerHTML = desc; // Use innerHTML para renderizar tags como <br>
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
""".replace(
    '// ... (descrições serão inseridas aqui) ...',
    f'const variableDescriptions = {json.dumps(get_variable_descriptions(), indent=12)};'
)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python gerar_visualizador.py <caminho_para_diretorio_da_rodada>")
        print("Exemplo: python gerar_visualizador.py /var/www/html/2025071600")
        sys.exit(1)
    
    target_directory = sys.argv[1]
    generate_viewer(target_directory)

