#!/bin/bash

# ==============================================================================
# SCRIPT MESTRE PARA A RODADA DIÁRIA DO MODELO WRF E PUBLICAÇÃO NA WEB
#
# Versão Final: Usa um método robusto e portável (laço 'for' com 'mv')
# para renomear os arquivos de imagem.
# ==============================================================================

set -e

echo "=================================================="
echo "INICIANDO RODADA DIÁRIA: $(date)"
echo "=================================================="

# --- INICIALIZAÇÃO DO AMBIENTE CONDA ---
echo "-> Ativando ambiente Conda: wrf_enviroment"
CONDA_BASE_PATH=$(conda info --base)
source "${CONDA_BASE_PATH}/etc/profile.d/conda.sh"
conda activate wrf_enviroment

# --- CONFIGURAÇÃO DE DATA ---
if [[ ! -n $1 ]] ; then
    export DATE=$(date -u +%Y%m%d)00
else
    export DATE=$1
fi
echo "-> Data da rodada definida para: ${DATE}"

# --- CONFIGURAÇÃO DE CAMINHOS E VARIÁVEIS ---
WRF_INPUT_DIR="/trabalho/icon/${DATE}/WRF_RUN/run_wrf"
pwd
WEB_OUTPUT_DIR="/var/www/html/${DATE}"
DOMAINS_TO_PLOT=("d01" "d02")
ALL_VARIABLES=(
    "slp"
    "mcape"
    "mcin"
    "pw"
    "winds"
    "ppn"
    "mdbz"
    "helicity"
    "updraft_helicity"
    "ctt"
    "high_cloudfrac"
    "low_cloudfrac"
    "mid_cloudfrac"
    "u_pvo"
    "u_winds"
)
# --- FIM DA CONFIGURAÇÃO ---

echo "-> Verificando diretório de entrada: ${WRF_INPUT_DIR}"
if [ ! -d "$WRF_INPUT_DIR" ]; then
    echo "❌ ERRO: Diretório de entrada não encontrado para a data ${DATE}."
    exit 1
fi
cd "$WRF_INPUT_DIR"

echo "-> Limpando e criando diretório de saída: ${WEB_OUTPUT_DIR}"
mkdir -p "$WEB_OUTPUT_DIR"

CONFIG_JS_FILE="${WEB_OUTPUT_DIR}/config.js"
echo "const simulationConfig = {" > "$CONFIG_JS_FILE"

for domain in "${DOMAINS_TO_PLOT[@]}"; do
    echo -e "\n--- Processando Domínio: ${domain} ---"
    wrf_file=$(ls wrfout_${domain}_* 2>/dev/null | head -n 1)
    if [[ -z "$wrf_file" ]]; then
        echo "⚠️ AVISO: Nenhum arquivo wrfout encontrado para o domínio ${domain}. Pulando."
        continue
    fi
    echo "  -> Arquivo de entrada: ${wrf_file}"
    
    echo "    '${domain}': {" >> "$CONFIG_JS_FILE"
    
    num_frames=$(ncdump -h "$wrf_file" | grep 'Time = ' | sed 's/.* = \(.*\).*/\1/' | tr -d ';')
    echo "        totalFrames: ${num_frames}," >> "$CONFIG_JS_FILE"
    echo "        variables: [" >> "$CONFIG_JS_FILE"

    for variable in "${ALL_VARIABLES[@]}"; do
        domain_output_dir="${WEB_OUTPUT_DIR}/${domain}/${variable}"
        mkdir -p "$domain_output_dir"
        echo "  -> Processando variável '${variable}'..."
        if [[ "$domain" = 'd02' ]]  ; then
           shapefile='/home/geral1/scripts_previsao_UFSC/BR_SC_RS_d02/BR_SC_RS_d02.shp' 
         else
           shapefile='/home/geral1/scripts_previsao_UFSC/SC_RS_d01/SC_RS_d01.shp' 
        fi
        # Executa o wrfplot
        if compgen -G "${domain_output_dir}/${variable}_*.png" > /dev/null; then
           echo "  ✅ Arquivos de saída para '${variable}' já existem em ${domain_output_dir}. Pulando wrfplot."
            echo "            '${variable}'," >> "$CONFIG_JS_FILE"
           continue
        fi

        # Executa o wrfplot e redireciona a saída para /dev/null para um log mais limpo
        echo wrfplot --shapefile $shapefile  --input "${wrf_file}" --vars "${variable}" --ulevels '900,500,200' --output "${domain_output_dir}" 
        wrfplot --shapefile  $shapefile   --input "${wrf_file}" --vars "${variable}" --ulevels '900,500,200' --output "${domain_output_dir}" >/dev/null 2>&1

        if [ $? -eq 0 ]; then
            # ==========================================================
            # BLOCO CORRETO PARA RENOMEAR ARQUIVOS
            # Este bloco usa um laço 'for' e o comando 'mv', que é seguro e funciona em qualquer sistema.
            # ==========================================================
            echo "     - Renomeando arquivos de saída..."
            echo "pushd $domain_output_dir" 
            pushd "$domain_output_dir" > /dev/null
            for file in ${domain}_${variable}_*.png; do
                 echo " Verifica se o loop encontrou algum arquivo para evitar erros " $file 
                if [ -f "$file" ]; then
                    # Remove o prefixo 'd01_' ou 'd02_' do nome do arquivo
                    new_name="${file#${domain}_}"
                    mv -- "$file" "$new_name"
                fi
            done
            popd > /dev/null
            # ==========================================================
            
            echo "            '${variable}'," >> "$CONFIG_JS_FILE"
        else
            echo "      ❌ ERRO ao executar 'wrfplot' para a variável '${variable}' no domínio '${domain}'."
        fi
    done
    
    echo "        ]" >> "$CONFIG_JS_FILE"
    echo "    }," >> "$CONFIG_JS_FILE"
done

echo "};" >> "$CONFIG_JS_FILE"

echo -e "\n-> Desativando ambiente Conda."
conda deactivate

echo -e "\n-> Ajustando permissões finais para o diretório web..."
chmod -R 755 "$WEB_OUTPUT_DIR"

echo "=================================================="
echo "RODADA DIÁRIA CONCLUÍDA: $(date)"
echo "=================================================="
