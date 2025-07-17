#!/bin/bash

# Este é um script orquestrador para a cadeia de previsão do tempo WRF-ICON.
# Ele executa os scripts de aquisição de dados, modelagem, plotagem e publicação web.

# Uso: ./executar_tudo.sh [YYYYMMDDHH]
# Exemplo: ./executar_tudo.sh 2025071700

set -e # Sai imediatamente se um comando falhar

echo "Iniciando a orquestração da rodada WRF-ICON..."
echo "Data e hora atuais: $(date)"

# Verifica se um argumento de data foi fornecido
if [[ -n "$1" ]]; then
    DATE_ARG="$1"
    echo "Usando data fornecida: $DATE_ARG"
else
    # Se nenhum argumento for fornecido, usa a data atual (UTC 00Z)
    DATE_ARG=$(date -u +%Y%m%d)00
    echo "Nenhuma data fornecida, usando a data padrão (UTC 00Z): $DATE_ARG"
fi

# Define o diretório base onde os scripts originais estão localizados
# Ajuste este caminho conforme a sua instalação
SCRIPTS_DIR="/home/geral1/scripts_previsao_UFSC" 

if [ ! -d "$SCRIPTS_DIR" ]; then
    echo "❌ ERRO: Diretório de scripts não encontrado: $SCRIPTS_DIR"
    echo "Por favor, ajuste a variável SCRIPTS_DIR neste script para o caminho correto."
    exit 1
fi

# 1. Executa o script de download e pré-processamento ICON
echo -e "\n--- Executando trazer_icon_sul_br.sh ---"
"$SCRIPTS_DIR/trazer_icon_sul_br.sh" "$DATE_ARG"
echo "trazer_icon_sul_br.sh concluído."

# 2. Executa o script WPS-WRF
echo -e "\n--- Executando rodar_wps_wrf.sh ---"
"$SCRIPTS_DIR/rodar_wps_wrf.sh" "$DATE_ARG"
echo "rodar_wps_wrf.sh concluído."

# 3. Executa o script de plotagem
echo -e "\n--- Executando plotar_rodadas_diaria.sh ---"
"$SCRIPTS_DIR/plotar_rodadas_diaria.sh" "$DATE_ARG"
echo "plotar_rodadas_diaria.sh concluído."

# 4. Executa o script orquestrador web (Python)
# Nota: orquestrador_web.py escaneia /var/www/html para encontrar as rodadas,
# então não precisa de um argumento de data específico, apenas deve ser executado
# depois que a rodada atual foi processada e as imagens geradas.
echo -e "\n--- Executando orquestrador_web.py ---"
python3 "$SCRIPTS_DIR/orquestrador_web.py"
echo "orquestrador_web.py concluído."

echo -e "\n=================================================="
echo "ORQUESTRAÇÃO COMPLETA DA CADEIA WRF-ICON CONCLUÍDA!"
echo "=================================================="
