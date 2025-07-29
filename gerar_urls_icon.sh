#!/bin/bash
cd /trabalho/icon/template/
# Data do run (00Z do dia atual em UTC)
DATA=$(date -u +%Y%m%d)00
echo $DATA
# Horas de previsão: de 0 a 24 em passos de 3
HORAS=$(seq -w 0 1 36)

# Diretório de saída
OUTFILE="urls.txt"
echo "🔧 Gerando $OUTFILE para data $DATA..."
rm -f "$OUTFILE"

# Níveis de pressão
NIVEIS=(1000 950 925 900 850 800 700 600 500 400 300 250 200 150 100 70 50)
PRESSURE_VARS=(t u v relhum fi)

# Variáveis de nível único
SINGLE_LEVEL_VARS=(t_2m u_10m v_10m relhum_2m ps pmsl t_g )

# Variáveis de solo
SOIL_VARS=(
  0_T_SO 1458_T_SO 162_T_SO 18_T_SO 2_T_SO 486_T_SO 54_T_SO 5_T_SO 6_T_SO
  0_W_SO 1_W_SO 243_W_SO 27_W_SO 3_W_SO 729_W_SO 81_W_SO 9_W_SO
  0_W_SO_ICE 1_W_SO_ICE 243_W_SO_ICE 27_W_SO_ICE 3_W_SO_ICE 729_W_SO_ICE 81_W_SO_ICE 9_W_SO_ICE
)

# Adiciona HSURF (apenas uma vez)
echo "https://opendata.dwd.de/weather/nwp/icon/grib/00/hsurf/icon_global_icosahedral_time-invariant_${DATA}_HSURF.grib2.bz2" >> "$OUTFILE"
echo "https://opendata.dwd.de/weather/nwp/icon/grib/00/clat/icon_global_icosahedral_time-invariant_${DATA}_CLAT.grib2.bz2" >> "$OUTFILE"
echo "https://opendata.dwd.de/weather/nwp/icon/grib/00/clon/icon_global_icosahedral_time-invariant_${DATA}_CLON.grib2.bz2" >> "$OUTFILE"

# Laço para todas as horas
for H in $HORAS; do

  # PRESSÃO
  for VAR in "${PRESSURE_VARS[@]}"; do
    for NIVEL in "${NIVEIS[@]}"; do
      URL="https://opendata.dwd.de/weather/nwp/icon/grib/00/${VAR}/icon_global_icosahedral_pressure-level_${DATA}_0${H}_${NIVEL}_${VAR^^}.grib2.bz2"
      echo "$URL" >> "$OUTFILE"
    done
  done

  # NÍVEL ÚNICO
  for VAR in "${SINGLE_LEVEL_VARS[@]}"; do
    URL="https://opendata.dwd.de/weather/nwp/icon/grib/00/${VAR}/icon_global_icosahedral_single-level_${DATA}_0${H}_${VAR^^}.grib2.bz2"
    echo "$URL" >> "$OUTFILE"
  done

  # SOLO
  for VAR in "${SOIL_VARS[@]}"; do
    VAR_BASE=$(echo "$VAR" | sed -E 's/^[0-9]+_//; s/_[0-9.]+//g' | tr '[:upper:]' '[:lower:]')
    URL="https://opendata.dwd.de/weather/nwp/icon/grib/00/${VAR_BASE}/icon_global_icosahedral_soil-level_${DATA}_0${H}_${VAR}.grib2.bz2"
    echo "$URL" >> "$OUTFILE"
  done

done

echo "✅ URLs salvas em $OUTFILE"

