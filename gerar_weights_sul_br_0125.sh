#!/bin/bash

# Diretório de trabalho
WORKDIR="/trabalho/icon/weights"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

# Nome dos arquivos
ICON_GRID_BZ2="icon_grid_0026_R03B07_G.nc.bz2"
ICON_GRID_NC="icon_grid_0026_R03B07_G.nc"
TARGET_GRID_TXT="target_grid_sul_br_0125.txt"
WEIGHTS_FILE="weights_sul_br_0125.nc"

# 1. Baixar grade ICON se necessário
if [ ! -f "$ICON_GRID_NC" ]; then
if [ ! -f "$ICON_GRID_BZ2" ]; then

  echo "🔽 Baixando grade ICON: $ICON_GRID_BZ2"
  wget -q "https://opendata.dwd.de/weather/lib/cdo/$ICON_GRID_BZ2"
  echo "📦 Descompactando $ICON_GRID_BZ2"
  bzip2  -d "$ICON_GRID_BZ2"
fi
else
  echo "✅ Grade ICON já presente: $ICON_GRID_NC"
fi

# 2. Criar grade de destino: grade regular 0.125° sobre o Sul do Brasil
if [ ! -f "$TARGET_GRID_TXT" ]; then
  echo "🧭 Criando grade regular 0.125° Sul do Brasil → $TARGET_GRID_TXT"
  cat <<EOF > "$TARGET_GRID_TXT"
gridtype = lonlat
xsize    = 177
ysize    = 113
xfirst   = -64.0
xinc     = 0.125
yfirst   = -36.0
yinc     = 0.125
EOF
else
  echo "✅ Grade regular já presente: $TARGET_GRID_TXT"
fi

# 3. Gerar pesos com remapbil (bilinear) — pode demorar um pouco
if [ ! -f "$WEIGHTS_FILE" ]; then
  echo "⚙️  Gerando pesos de interpolação bilinear → $WEIGHTS_FILE"
  cdo -f nc gennn,"$TARGET_GRID_TXT" "$ICON_GRID_NC" "$WEIGHTS_FILE"
else
  echo "✅ Arquivo de pesos já existe: $WEIGHTS_FILE"
fi

cp $WEIGHTS_FILE $TARGET_GRID_TXT ../template/.
