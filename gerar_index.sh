#!/bin/bash

# ==============================================================================
# SCRIPT PARA GERAR A PÁGINA PRINCIPAL (index.html) DO PORTAL DE PREVISÃO
# Autor: Gemini AI / Reinaldo Haas
# Data: 2025-07-17
#
# Descrição:
# Este script varre o diretório web em busca de subdiretórios de rodadas
# (ex: 2025071500) e gera uma página HTML com links para cada previsão,
# ordenados da mais recente para a mais antiga.
# ==============================================================================

# --- CONFIGURAÇÕES ---
# Diretório raiz do site. O script deve ser executado a partir daqui.
WEB_ROOT="/var/www/html"
# Nome do arquivo de saída
OUTPUT_FILE="index.html"

# Garante que o script está no diretório correto
cd "$WEB_ROOT" || { echo "ERRO: Diretório ${WEB_ROOT} não encontrado."; exit 1; }

# Define a localidade para que os nomes dos meses saiam em Português (ex: Julho)
export LC_TIME=pt_BR.UTF-8

# --- GERAÇÃO DA LISTA DE LINKS DINÂMICOS ---
# Inicia uma variável vazia para armazenar o HTML da lista de links
LINK_LIST=""

# Encontra todos os diretórios que começam com '20' (assumindo século 21)
# e os ordena em ordem reversa (mais novos primeiro)
for dir in $(ls -r -d 20*/ 2>/dev/null); do
    # Remove a barra final do nome do diretório (ex: 2025071500/ -> 2025071500)
    dirname="${dir%/}"

    # Extrai o ano, mês e dia do nome do diretório
    year=${dirname:0:4}
    month=${dirname:4:2}
    day=${dirname:6:2}

    # Formata a data para um formato legível (ex: "17 de Julho de 2025")
    # O comando 'date' é usado para converter a data para o formato desejado
    formatted_date=$(date -d "${year}-${month}-${day}" "+%d de %B de %Y")

    # Adiciona o item da lista (<li>) com o link para o diretório da previsão
    # O link aponta para o index.html dentro de cada diretório de rodada
    LINK_LIST+="      <li><a href=\"./${dirname}/index.html\">Previsão de ${formatted_date}</a></li>\n"
done

# Se nenhum diretório de previsão for encontrado, exibe uma mensagem
if [ -z "$LINK_LIST" ]; then
    LINK_LIST="<p>Nenhuma rodada de previsão disponível no momento.</p>"
fi

# --- GERAÇÃO DO ARQUIVO HTML COMPLETO ---
# Utiliza um "Here Document" (cat <<EOF) para escrever o conteúdo no arquivo de saída.
# A variável $LINK_LIST será expandida para incluir a lista de links gerada acima.
echo ">> Gerando arquivo ${OUTPUT_FILE}..."

cat <<EOF > "$OUTPUT_FILE"
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Previsão do Tempo - UFSC</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f4f4f9;
            color: #333;
        }
        .container {
            max-width: 900px;
            margin: 20px auto;
            padding: 25px;
            background-color: #fff;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        header {
            border-bottom: 2px solid #005a9c;
            padding-bottom: 15px;
            margin-bottom: 25px;
            text-align: center;
        }
        header h1 {
            color: #005a9c;
            margin: 0;
        }
        a {
            color: #005a9c;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .forecast-list {
            list-style: none;
            padding: 0;
        }
        .forecast-list li a {
            display: block;
            padding: 15px;
            margin-bottom: 10px;
            background-color: #e9f5ff;
            border-radius: 5px;
            border: 1px solid #bce0fd;
            font-weight: bold;
            transition: background-color 0.3s, transform 0.2s;
        }
        .forecast-list li a:hover {
            background-color: #d1eaff;
            transform: translateY(-2px);
            text-decoration: none;
        }
        footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ccc;
            font-size: 0.9em;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Previsão UFSC</h1>
            <p>Curso FSC7115 - Modelagem Numérica da Atmosfera</p>
        </header>

        <h2>Boas-vindas!</h2>
        <p>
            Seja bem-vindo ao espaço do nosso grupo na Universidade Federal de Santa Catarina (UFSC), onde ciência, tecnologia e compromisso público se encontram para enfrentar desafios reais — e urgentes.
        </p>
        <p>
            Estamos prestes a lançar o <strong>primeiro modelo brasileiro capaz de prever lestadas com precisão operacional</strong>, um marco para a meteorologia no Sul do país. A ferramenta estará disponível em breve em <a href="https://tempo.ufsc.br">www.tempo.ufsc.br</a>, ampliando a capacidade de previsão de ventos costeiros intensos que impactam o cotidiano de milhares de pessoas em Santa Catarina e no litoral brasileiro.
        </p>
        <p>
            Esse avanço é resultado do esforço conjunto de pesquisadores, estudantes e técnicos — fruto direto da qualidade da formação em meteorologia da UFSC, que hoje abriga uma das gerações mais qualificadas de sua história.
        </p>
        <p>
            Este espaço é mais do que uma vitrine de projetos. É um convite à reflexão e à ação. Queremos construir pontes entre o conhecimento científico e a sociedade — e isso exige investimento, escuta e valorização.
        </p>
        <p>
            Obrigado por nos visitar. Acompanhe nossas atualizações, apoie a ciência, e ajude a construir o futuro que queremos — e precisamos.
        </p>

        <hr>

        <h2>Rodadas de Previsão Disponíveis</h2>
        <ul class="forecast-list">
$LINK_LIST
        </ul>

        <footer>
            <p><strong>Contato:</strong> Reinaldo Haas | <a href="mailto:reinaldo.haas@ufsc.br">reinaldo.haas@ufsc.br</a></p>
            <p>Universidade Federal de Santa Catarina (UFSC)</p>
        </footer>
    </div>
</body>
</html>
EOF

# Define permissões adequadas para o arquivo ser lido pelo servidor web
chmod 644 "$OUTPUT_FILE"

echo "✅ Página ${OUTPUT_FILE} gerada com sucesso!"
