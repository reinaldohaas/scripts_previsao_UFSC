#!/bin/bash

# ========================================
# CONFIGURAÇÃO DE AMBIENTE E DATA
# ========================================
export WORKDIR="/trabalho/icon"
if [[ ! -n $1 ]] ; then
export DATE=$(date -u +%Y%m%d)00
else 
export DATE=$1
fi
export RUNDIR="$WORKDIR/$DATE"
mkdir -p "$RUNDIR"
cd "$RUNDIR"
echo $DATE
echo ">> Diretório de trabalho: $RUNDIR"

# ========================================
# SUBSTITUIR DATA ANTIGA PELO RUN ATUAL
# ========================================
OLD_DATE=$(head -n1 $WORKDIR/template/urls.txt | grep -oP '\d{10}')
NEW_DATE=$DATE
awk -v old="$OLD_DATE" -v new="$NEW_DATE" '{ gsub(old, new); print }' $WORKDIR/template/urls.txt > urls_tmp && mv urls_tmp urls.txt

# ========================================
# DOWNLOAD COM ARIA2C
# ========================================
if [ ! -f urls.txt ]; then
  echo "❌ Arquivo urls.txt não encontrado!"
  exit 1
fi

echo ">> Filtrando urls.txt: removendo arquivos já descompactados..."

awk -F/ -v pwd="$PWD" '
{
  # extrai o nome do arquivo .bz2
  split($NF, parts, ".bz2")
  grib = parts[1]
  grib2 = pwd "/" grib
  if (!system("[ -f \"" grib2 "\" ]")) {
    # arquivo .grib2 já existe — não baixar
    next
  }
  print
}' urls.txt > urls_para_baixar.txt

# Caso todos os arquivos já existam
if [ ! -s urls_para_baixar.txt ]; then
  echo "✔️ Todos os arquivos já foram descompactados. Nada para baixar."
else
  echo ">> Iniciando download apenas dos arquivos necessários com aria2c..."
  aria2c -x 15 -j 10 --file-allocation=none -i urls_para_baixar.txt -l aria2.log
fi

# ========================================
# DESCOMPACTAÇÃO .bz2 (apenas se necessário)
# ========================================
echo ">> Descompactando arquivos .bz2 apenas se necessário..."
for f in *.bz2; do
  grib="${f%.bz2}"
  if [ ! -f "$grib" ]; then
    echo " - Descompactando $f → $grib"
    bunzip2 -k "$f"
  else
    echo " - Pulando $f (já descompactado)"
  fi
done

# ========================================
# REGRID COM CDO EM PARALELO (ATÉ 10 THREADS)
# ========================================
echo ">> Regradeando com até 10 núcleos usando GNU parallel..."
mkdir -p regrid

find . -maxdepth 1 -name "*.grib2" | parallel -j 10 '
  infile={}
  outfile=regrid/sulbr_$(basename "$infile")
  if [ ! -f "$outfile" ]; then
    echo " -> Processando $infile → $outfile"
    cdo -f grb2 remap,$WORKDIR/template/target_grid_sul_br_0125.txt,$WORKDIR/template/weights_sul_br_0125.nc "$infile" "$outfile"
  else
    echo " -> Pulando $infile (já regradeado)"
  fi
'

# Diretório de entrada: arquivos regrid já separados por hora
REGRID_DIR="$WORKDIR/$DATE/regrid"
OUT_DIR="$REGRID_DIR/concatenado"
mkdir -p "$OUT_DIR"

echo "🔗 Concatenando arquivos GRIB2 com grib_copy no diretório: $REGRID_DIR"

# Extrai todas as horas únicas dos arquivos
HORAS=$(ls "$REGRID_DIR"/*.grib2 2>/dev/null | grep -oP '_\d{3}_' | sort -u | tr -d '_')

for hora in $HORAS; do
  echo "⏱️  Processando hora $hora..."

  # Lista os arquivos da hora atual
  arquivos=$(ls "$REGRID_DIR"/*_${hora}_*.grib2 2>/dev/null)

  if [ -z "$arquivos" ]; then
    echo "⚠️ Nenhum arquivo encontrado para hora $hora"
    continue
  fi

  OUTFILE="$OUT_DIR/icon_sulbr_${hora}.grib2"

  echo " - Concatenando $(echo "$arquivos" | wc -l) arquivos com grib_copy → $OUTFILE"

  # Usar grib_copy corretamente
  grib_copy $arquivos   "$OUTFILE"
done

