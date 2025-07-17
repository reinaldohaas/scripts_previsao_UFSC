## **Documentação do Sistema de Previsão de Tempo WRF-ICON (Modelo UFSC)**

### 1. Visão Geral do Sistema

Este documento descreve o fluxo de trabalho (`workflow`) de um sistema automatizado para previsão numérica de tempo, implementado para rodar diariamente. O sistema utiliza dados do modelo global ICON (Icosahedral Nonhydrostatic), fornecidos pelo DWD (Serviço Meteorológico Alemão), para inicializar o modelo de mesoescala WRF (Weather Research and Forecasting).

O objetivo principal é gerar previsões de alta resolução para o Sul do Brasil, processar as saídas em produtos visuais (imagens) e disponibilizá-las em um portal web interativo. O processo é modular, composto por uma sequência de scripts que gerenciam desde o download dos dados até a publicação final.

A cadeia de execução é dividida nas seguintes etapas principais:
1.  **Aquisição e Preparação de Dados:** Download e remapeamento dos dados do ICON.
2.  **Execução do WRF:** Rodada do WPS (WRF Preprocessing System) e do próprio WRF.
3.  **Pós-processamento e Geração de Produtos:** Criação de imagens a partir das saídas brutas do modelo.
4.  **Publicação Web:** Geração de um visualizador HTML/JavaScript para os resultados.
5.  **Orquestração e Agendamento:** Gerenciamento do fluxo de trabalho e automação das execuções diárias.

### 2. Arquitetura e Fluxo de Execução

O sistema opera através da execução sequencial de scripts de shell e Python. A orquestração geral é gerenciada por um script mestre unificado (`executar_tudo.sh`) que invoca os demais componentes em ordem. Este script mestre é, por sua vez, agendado para execução automática via `cron`.

O fluxo de dados pode ser resumido da seguinte forma:

`CRON` -> `executar_tudo.sh` -> (`trazer_icon_sul_br.sh` -> `URLs ICON` -> **Download & Regrid** -> `GRIB2 ICON (regional)`) -> (`rodar_wps_wrf.sh` -> **WPS** -> `met_em*` -> **WRF (real.exe, wrf.exe)** -> `wrfout*`) -> (`plotar_rodadas_diaria.sh` -> **Plotagem (wrfplot)** -> `Imagens PNG`) -> (`orquestrador_web.py` -> **Gerador de Interface** -> `Visualizador Web (HTML/JS)`)

### 3. Detalhamento das Etapas e Scripts

#### 3.1. Configuração Inicial (One-Time Setup)

Antes da execução diária, alguns artefatos devem ser gerados.

* **`gerar_weights_sul_br_0125.sh`**:
    * **Propósito**: Criar um arquivo de pesos para interpolação. Este processo é computacionalmente caro e, por isso, é executado apenas uma vez.
    * **Funcionamento**:
        1.  Baixa a definição da grade nativa (icosaédrica) do modelo ICON.
        2.  Define uma grade de destino regular (lon-lat) com resolução de 0.125° cobrindo a América do Sul (`target_grid_sul_br_0125.txt`).
        3.  Utiliza o comando `cdo gennn` (Nearest Neighbor) do Climate Data Operators (CDO) para calcular os pesos de interpolação entre a grade ICON e a grade de destino.
    * **Saída**: Arquivos `weights_sul_br_0125.nc` e `target_grid_sul_br_0125.txt`, que são usados diariamente para acelerar o remapeamento.

* **`clip_simplify_shp_by_wrf.py`**:
    * **Propósito**: Preparar os arquivos de shapefile (limites políticos) usados na plotagem dos mapas.
    * **Funcionamento**:
        1.  Lê as dimensões (latitude/longitude) de um arquivo de saída do WRF (`wrfout`).
        2.  Usa essas dimensões para criar uma caixa delimitadora (`bounding box`).
        3.  Recorta (`clip`) um shapefile de entrada (e.g., contorno dos estados) para a área exata do domínio do modelo.
        4.  Simplifica a geometria do shapefile para reduzir o tamanho do arquivo e acelerar a plotagem, mantendo a topologia.
    * **Saída**: Um novo arquivo `.shp` ou `.geojson` otimizado para a visualização.

#### 3.2. Etapa 1: Aquisição e Preparação de Dados (ICON)

Esta etapa é responsável por obter os dados meteorológicos que servirão de entrada para o WRF.

* **`gerar_urls_icon.sh`**:
    * **Propósito**: Gerar a lista de URLs para download dos dados do ICON para a data da rodada.
    * **Funcionamento**:
        1.  Gera uma sequência de horas de previsão (e.g., de 0 a 24 horas).
        2.  Monta as URLs para diversas variáveis (temperatura, vento, umidade, etc.) em diferentes níveis (pressão, superfície, solo) para cada hora de previsão.
    * **Saída**: Um arquivo `urls.txt` contendo centenas de links para os arquivos GRIB2 do servidor da DWD.

* **`trazer_icon_sul_br.sh`**:
    * **Propósito**: Orquestrar o download, descompactação e remapeamento dos dados do ICON.
    * **Funcionamento**:
        1.  **Download**: Utiliza o `aria2c` para baixar os arquivos listados em `urls.txt` de forma paralela e eficiente. Verifica arquivos já existentes para evitar re-download.
        2.  **Descompactação**: Descompacta os arquivos `.bz2` usando `bunzip2`.
        3.  **Remapeamento (Regrid)**: Usa o `cdo` com os pesos pré-calculados (`weights_sul_br_0125.nc`) para converter os dados da grade global do ICON para a grade regional do Sul do Brasil. Este passo é executado em paralelo (`GNU parallel`) para otimizar o tempo.
        4.  **Concatenação**: Utiliza `grib_copy` para agrupar todos os campos meteorológicos de uma mesma hora de previsão em um único arquivo GRIB2.
    * **Saída**: Arquivos GRIB2 concatenados por hora (`icon_sulbr_HHH.grib2`), prontos para serem lidos pelo WPS.

#### 3.3. Etapa 2: Execução do Modelo WRF

O coração do sistema, onde a simulação numérica é de fato realizada.

* **`rodar_wps_wrf.sh`**:
    * **Propósito**: Automatizar a execução completa da cadeia WPS-WRF. Este script também verifica a existência e integridade dos arquivos de saída WRF (`wrfout_d01*` e `wrfout_d02*`) e evita a reexecução desnecessária se eles já estiverem presentes e não vazios.
    * **Funcionamento**:
        1.  **Configuração**: Define os diretórios de trabalho e as datas de início e fim da simulação com base na data da rodada.
        2.  **Verificação de Saída**: Checa se os arquivos `wrfout` já existem e não estão vazios; se sim, o script é encerrado.
        3.  **Execução do WPS**:
            * **`geogrid.exe`**: Interpola dados geográficos estáticos (topografia, uso do solo, etc.) para os domínios do modelo definidos no `namelist.wps`.
            * **`ungrib.exe`**: Lê os arquivos GRIB2 do ICON e extrai as variáveis meteorológicas. Utiliza um `Vtable` (Variable Table), especificamente `Vtable.ICONp`, para mapear os nomes das variáveis do ICON para os nomes esperados pelo WRF.
            * **`metgrid.exe`**: Interpola os campos meteorológicos extraídos pelo `ungrib` para os domínios do modelo, criando os arquivos `met_em.d*.nc`.
        4.  **Execução do WRF**:
            * **`real.exe`**: Prepara as condições iniciais (`wrfinput_d01`) e de fronteira (`wrfbdy_d01`) a partir dos dados do `metgrid`. As datas e outros parâmetros físicos são lidos do `namelist.input`.
            * **`wrf.exe`**: O solver principal do modelo. Integra as equações atmosféricas no tempo para gerar a previsão. A execução é feita em paralelo usando `mpirun`.
    * **Saída**: Os arquivos `wrfout_d*`, que contêm a previsão completa em formato NetCDF.

#### 3.4. Etapa 3: Pós-processamento e Geração de Produtos

Esta etapa traduz os dados brutos do `wrfout` em produtos visuais compreensíveis.

* **`plotar_rodadas_diaria.sh`**:
    * **Propósito**: Gerencia a criação de imagens para a web a partir das saídas do WRF.
    * **Funcionamento**:
        1.  **Iteração**: Faz um loop sobre os domínios a serem plotados (e.g., `d01`, `d02`) e uma lista pré-definida de variáveis meteorológicas (e.g., `slp`, `mcape`, `winds`, `ppn`).
        2.  **Plotagem**: Para cada variável, invoca um script de plotagem customizado (`wrfplot`), passando o arquivo `wrfout` correspondente, a variável desejada, e um shapefile para sobrepor os contornos. A saída do `wrfplot` são imagens no formato PNG para cada passo de tempo.
        3.  **Renomeação**: Renomeia os arquivos de imagem para um formato limpo, removendo prefixos de domínio.
        4.  **Configuração da Web**: Gera um arquivo `config.js` que contém metadados sobre a simulação, como as variáveis e domínios disponíveis e o número total de quadros (imagens) por variável.
    * **Saída**: Uma estrutura de diretórios contendo as imagens PNG organizadas por domínio e variável, e o arquivo `config.js`.

#### 3.5. Etapa 4: Publicação e Visualização Web

A etapa final, que constrói a interface do usuário para explorar os resultados da previsão.

* **`orquestrador_web.py`**:
    * **Propósito**: Criar uma interface web completa e interativa para todas as rodadas de previsão disponíveis.
    * **Funcionamento**:
        1.  **Geração de Página Principal**: Encontra os diretórios de previsão existentes e gera um `index.html` principal com um calendário, permitindo a navegação entre as diferentes datas de previsão.
        2.  **Geração de Visualizadores por Rodada**: Para cada rodada de previsão, gera os arquivos `data.js` e `index.html` necessários para o visualizador interativo. O `data.js` mapeia domínios e variáveis para os caminhos das imagens PNG correspondentes, suportando variáveis de nível único e de múltiplos níveis verticais.
    * **Saída**: Os arquivos `index.html` e `data.js` para a página principal e para cada visualizador de rodada, a serem hospedados em um servidor web.

#### 3.6. Orquestração e Agendamento

Esta seção descreve o script mestre que coordena toda a cadeia de previsão e como ele é agendado para execução automática.

* **`executar_tudo.sh`**:
    * **Propósito**: É o script mestre que orquestra a execução sequencial de todas as etapas da cadeia de previsão. Ele garante que os dados sejam baixados, o modelo executado, os gráficos gerados e a interface web atualizada em uma única chamada.
    * **Funcionamento**:
        1.  Aceita opcionalmente uma data no formato `YYYYMMDDHH` como argumento. Se não fornecida, utiliza a data e hora UTC atuais (00Z).
        2.  Chama em sequência:
            * `trazer_icon_sul_br.sh` (para aquisição e regrade dos dados ICON).
            * `rodar_wps_wrf.sh` (para execução do WPS e WRF).
            * `plotar_rodadas_diaria.sh` (para plotagem das saídas do WRF).
            * `orquestrador_web.py` (para geração e atualização da interface web).
    * **Uso**: `./executar_tudo.sh [YYYYMMDDHH]`
    * **Exemplo**: `./executar_tudo.sh 2025071700`

* **Agendamento Cron (`crontab -l`)**:
    * **Propósito**: O `crontab` é utilizado para agendar a execução automática do script `executar_tudo.sh` em intervalos regulares.
    * **Configuração**: A linha abaixo no `crontab` do usuário `geral1` garante que o script seja executado a cada hora.
        ```
        1 * * * * /home/geral1/scripts_previsao_UFSC/executar_tudo.sh >> /dev/nul
        ```
        * `1`: O script será executado no minuto 1 de cada hora.
        * `* * * *`: Indica que a execução ocorrerá em qualquer hora, qualquer dia do mês, qualquer mês e qualquer dia da semana.
        * `/home/geral1/scripts_previsao_UFSC/executar_tudo.sh`: Caminho completo para o script mestre.
        * `>> /dev/nul`: Redireciona a saída padrão e de erro para `/dev/nul` (provavelmente um erro de digitação e deveria ser `/dev/null`) para evitar que o `cron` envie e-mails com o log da execução.

