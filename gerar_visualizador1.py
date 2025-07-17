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
    try:
        base_name = filename.replace('.png', '')
        date_str = base_name.split('_', 1)[1]
        return datetime.strptime(date_str, '%d-%m-%Y_%H:%M')
    except (IndexError, ValueError):
        return datetime.min

def get_variable_descriptions():
    return {
        "slp": "<b>Pressão ao Nível do Mar</b><br>Pressão reduzida ao nível do mar...",
        "winds": "<b>Vento a 10m</b><br>Vento na superfície...",
        # ... outras variáveis ...
    }

def generate_viewer(root_dir):
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
            sorted_files = sorted(image_files, key=parse_filename_date)
            simulation_data[domain][variable] = [os.path.join(domain, variable, f) for f in sorted_files]

    # Gera o data.js
    data_js_path = os.path.join(root_dir, 'data.js')
    print(f"Gerando {data_js_path}...")
    with open(data_js_path, 'w') as f:
        f.write("const simulationData = ")
        json.dump(simulation_data, f, indent=4)
        f.write(";")

    # Lê o template HTML
    template_path = os.path.join(os.path.dirname(__file__), 'template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html_template = f.read()

    # Substitui o marcador pelo bloco JS de descrições
    descriptions_js = f"<script>\nconst variableDescriptions = {json.dumps(get_variable_descriptions(), indent=4)};\n</script>"
    final_html = html_template.replace('<!-- %%VARIAVEL_DESCRICOES_JS%% -->', descriptions_js)

    # Salva o index.html final
    index_html_path = os.path.join(root_dir, 'index.html')
    print(f"Gerando {index_html_path}...")
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print("✔ Visualizador gerado com sucesso!")
    print(f"Abra no navegador: http://<seu-servidor>/{os.path.basename(root_dir)}/")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python gerar_visualizador.py <caminho_para_diretorio_da_rodada>")
        sys.exit(1)
    
    target_directory = sys.argv[1]
    generate_viewer(target_directory)

