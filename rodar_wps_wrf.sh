#!/bin/bash

# ==============================================================================
#                 SCRIPT PARA EXECUÇÃO DA CADEIA WPS-WRF (VERSÃO REFINADA)
# ==============================================================================
# Descrição:
#   Este script automatiza a execução do WPS e WRF.
#   Assume que o caminho para os dados geográficos (geog_data_path)
#   está corretamente configurado no arquivo namelist.wps.
#
# Autor: Reinaldo Haas/Gemini AI
# Data: 2025-07-13
# ==============================================================================

set -e

# ========================================
# CONFIGURAÇÃO DE AMBIENTE E DATA
# ========================================
echo ">> 1. CONFIGURANDO AMBIENTE"

if [[ ! -n $1 ]] ; then
    export DATE=$(date -u +%Y%m%d)00
    export AMANHA=$(date -u -d "+1 day" +%Y%m%d)00
else
    export DATE=$1
# Gerar AMANHA baseado na DATE
    export AMANHA=$(date -u -d "${DATE:0:8} +1 day" +%Y%m%d)00
fi
DATE_FORMATTED=$(echo $DATE | sed 's/\(....\)\(..\)\(..\)\(..\)/\1-\2-\3_\4:00:00/')
AMANHA_FORMATTED=$(echo $AMANHA | sed 's/\(....\)\(..\)\(..\)\(..\)/\1-\2-\3_\4:00:00/')

export WORK_DIR="/trabalho/icon"
export TEMPLATE_DIR="$WORK_DIR/template"
export WPS_HOME="/home/geral1/gis4wrf/dist/WPS-4.6.0"
export WRF_HOME="/home/geral1/gis4wrf/dist/WRF-4.7.1"
export ICON_DATA_DIR="$WORK_DIR/$DATE/regrid/concatenado"
export RUN_DIR="$WORK_DIR/$DATE/WRF_RUN"
export WPS_RUN_DIR="$RUN_DIR/run_wps"
export WRF_RUN_DIR="$RUN_DIR/run_wrf"
export VTABLE_FILE="Vtable.ICONp"
export NUM_CORES_WRF=6

echo "   - Data da Simulação: $DATE"
echo "   - Diretório de Trabalho: $RUN_DIR"

if [ ! -d "$ICON_DATA_DIR" ]; then
    echo "❌ ERRO: Diretório de dados do ICON não encontrado: $ICON_DATA_DIR"
    exit 1
fi

mkdir -p "$WPS_RUN_DIR"
mkdir -p "$WRF_RUN_DIR"

# ========================================
# ETAPA WPS (WRF Preprocessing System)
# ========================================
echo -e "\n>> 2. INICIANDO ETAPA WPS EM: $WPS_RUN_DIR"
cd "$WPS_RUN_DIR"

# --- 2.1. geogrid.exe ---
echo "   -> 2.1. Executando geogrid.exe"
ln -sf "$WPS_HOME/geogrid.exe" .
cp -rf "$TEMPLATE_DIR/namelist.wps" .
echo ">> 2. ATUALIZANDO namelist.wps"
sed -i "/start_date/s/'.*'/'${DATE_FORMATTED}', '${DATE_FORMATTED}'/" namelist.wps
sed -i "/end_date/s/'.*'/'${AMANHA_FORMATTED}', '${AMANHA_FORMATTED}'/" namelist.wps

# O executável geogrid.exe procura o arquivo GEOGRID.TBL no diretório atual.
# Por isso, criamos um link aqui apontando para o arquivo original na instalação do WPS.
mkdir -p geogrid
ln -sf "$WPS_HOME/geogrid/GEOGRID.TBL.ARW" ./geogrid/GEOGRID.TBL
# NOTA: O link para os dados geográficos não é criado, pois assumimos que a variável
# 'geog_data_path' está configurada corretamente dentro do 'namelist.wps'.

./geogrid.exe >& geogrid.log

if [ ! -f "geo_em.d01.nc" ]; then
    echo "❌ ERRO: geogrid.exe falhou. Verifique o arquivo $WPS_RUN_DIR/geogrid.log"
    exit 1
fi
echo "      ✔️  geogrid.exe concluído com sucesso."

# --- 2.2. ungrib.exe ---
echo "   -> 2.2. Executando ungrib.exe"
ln -sf "$WPS_HOME/ungrib.exe" .
ln -sf "$TEMPLATE_DIR/link_grib.csh" .
ln -sf "$TEMPLATE_DIR/$VTABLE_FILE" ./Vtable
./link_grib.csh "$ICON_DATA_DIR"/icon_sulbr_*.grib2
./ungrib.exe >& ungrib.log

if ! ls GRIBFILE.* 1> /dev/null 2>&1 || ! ls FILE:* 1> /dev/null 2>&1; then
    echo "❌ ERRO: ungrib.exe falhou. Verifique $WPS_RUN_DIR/ungrib.log e a Vtable."
    exit 1
fi
echo "      ✔️  ungrib.exe concluído com sucesso."

# --- 2.3. metgrid.exe ---
echo "   -> 2.3. Executando metgrid.exe"
ln -sf "$WPS_HOME/metgrid.exe" .
# Assim como o geogrid, o metgrid.exe procura o METGRID.TBL no diretório atual.
mkdir -p metgrid
ln -sf "$WPS_HOME/metgrid/METGRID.TBL.ARW" ./metgrid/METGRID.TBL
./metgrid.exe >& metgrid.log

if ! ls met_em.d0*.nc 1> /dev/null 2>&1; then
    echo "❌ ERRO: metgrid.exe falhou. Verifique o arquivo $WPS_RUN_DIR/metgrid.log"
    exit 1
fi
echo "      ✔️  metgrid.exe concluído com sucesso."
echo "✅ ETAPA WPS CONCLUÍDA"

# ========================================
# ETAPA WRF (Weather Research and Forecasting Model)
# ========================================
echo -e "\n>> 3. INICIANDO ETAPA WRF EM: $WRF_RUN_DIR"
cd "$WRF_RUN_DIR"
# Data inicial
START_YEAR=${DATE:0:4}
START_MONTH=${DATE:4:2}
START_DAY=${DATE:6:2}
START_HOUR=${DATE:8:2}

# Data final
END_YEAR=${AMANHA:0:4}
END_MONTH=${AMANHA:4:2}
END_DAY=${AMANHA:6:2}
END_HOUR=${AMANHA:8:2}


# --- 3.1. real.exe ---
echo "   -> 3.1. Executando real.exe com $NUM_CORES_WRF núcleos"
ln -sf "$WRF_HOME/main/real.exe" .
ln -sf "$WRF_HOME/main/wrf.exe" .


# Cria links para todos arquivos que batem com os padrões
for pattern in "ozon*" "*TBL*" "*DATA"; do
    for file in $TEMPLATE_DIR/$pattern; do
        # Só cria se o arquivo realmente existir
        if [ -e "$file" ]; then
            ln -sf "$file" .
        fi
    done
done

cp -rf $TEMPLATE_DIR/namelist.input .
# Substitui cada linha relevante no namelist.input
sed -i "/start_year/c\ start_year = ${START_YEAR}, ${START_YEAR}" namelist.input
sed -i "/start_month/c\ start_month = ${START_MONTH}, ${START_MONTH}" namelist.input
sed -i "/start_day/c\ start_day = ${START_DAY}, ${START_DAY}" namelist.input
sed -i "/start_hour/c\ start_hour = ${START_HOUR}, ${START_HOUR}" namelist.input

sed -i "/end_year/c\ end_year = ${END_YEAR}, ${END_YEAR}" namelist.input
sed -i "/end_month/c\ end_month = ${END_MONTH}, ${END_MONTH}" namelist.input
sed -i "/end_day/c\ end_day = ${END_DAY}, ${END_DAY}" namelist.input
sed -i "/end_hour/c\ end_hour = ${END_HOUR}, ${END_HOUR}" namelist.input



ln -sf $WPS_RUN_DIR/met_em.*.nc .
mpirun -np "$NUM_CORES_WRF" ./real.exe

if [[ ! -f "wrfinput_d01" || ! -f "wrfbdy_d01" ]]; then
    echo "❌ ERRO: real.exe falhou. Verifique os arquivos rsl.error.* em $WRF_RUN_DIR"
    exit 1
fi
echo "      ✔️  real.exe concluído com sucesso."

# --- 3.2. wrf.exe ---
echo "   -> 3.2. Executando wrf.exe com $NUM_CORES_WRF núcleos"
mpirun -np "$NUM_CORES_WRF" ./wrf.exe

if ! ls wrfout_d01_* 1> /dev/null 2>&1; then
    echo "❌ ERRO: wrf.exe falhou. Verifique os arquivos rsl.error.* em $WRF_RUN_DIR"
    exit 1
fi
echo "      ✔️  wrf.exe concluído com sucesso."

# ========================================
# FINALIZAÇÃO
# ========================================
echo -e "\n🎉🎉🎉 CADEIA WPS-WRF EXECUTADA COM SUCESSO! 🎉🎉🎉"
echo '> Os arquivos de saída (wrfout) estão localizados em:'
echo "   $WRF_RUN_DIR"

