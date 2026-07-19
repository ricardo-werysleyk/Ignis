# Firebox

Firebox é um sistema eletrônico de aquisição de dados em tempo real para os testes de queima irrestrita de propelentes usados em foguetes acadêmicos, utilizando o microcontrolador Esp32-S3 para o processamento de dados, célula de carga para variação de massa do propelente e termopares para temperatura. Os dados são salvos em um arquivo .csv no formato (time,mass,termopar_start,termopar_mid,infrared) a uma taxa de 3340Hz para dar uma boa precisão.


# Ignis

O Ignis é um software desktop de alta performance desenvolvido em Python projetado para atuar como interface de análise de dados gerados por ensaios da caixa de testes Firebox. Ele realiza a fusão de dados e o pós-processamento automatizado de ensaios estáticos com propelente sólido (KNSU).

O software carrega um arquivo .csv no formato (time,mass,termopar_start,termopar_mid,infrared) e processa os dados, retirando informações importantes como taxa de queima do propelente, taxa de queima máxima, tempo total de queima e temperatura máxima de cada termopar. Ele faz o tratamento dos dados da célula de carga para remover interferências elétricas, térmicas ou efeito mola, aplica a derivada e monta os gráficos.

Grid de exibição na interface:

[0,0] Gráfico da massa atual do propelente no tempo t, dados brutos e tratados com filtro passa-baixas.
[0,1] Gráfico de taxa de variação mássica do propelente.
[1,0] Gráfico de temperaturas, termopar posicionado na ponta inicial de queima do propelente, termopar posicionado no meio do propelente e sensor infravermelho.
[1,1] Visualização de video realizado no teste de queima se existir.

Ignis conta com botões de controle, play/pause e reset, slider de linha de tempo que permite visualizar qualquer instante do ensaio e botão para abrir o explorador de arquivos e selecionar o arquivo .csv para análise.

# Como executar

1- Instale o Python 3.11.9
2- Crie um ambiente de desenvolvimento virtual executando esse comando na pasta do projeto: ```pithon -m venv .venv```
3- Ative o venv com o comando: ```./.venv/Scripts/activate```
4- Execute o comando para instalar as dependências: ```pip install -r requirements.txt```

Se não possuir a parte eletrônica Firebox ou um arquivo .csv no formato (time,mass,termopar_start,termopar_mid,infrared) para analisar, utilize o gêmeo digital desse projeto para gerar dados simulados próximos a realidade executando o passo 5, se já possui dados pule para o passo 6.

5- Execute o arquivo python main.py

Se já pussuir o arquivo .csv
6- Execute o arquivo python ignis_desktop.py

# Tecnologia utilizadas

* **Python 3.11+:** Linguagem central utilizada para processamento vetorial de dados e do sistema.
* **PyQt6:** Framework industrial utilizado para a construção da interface gráfica (GUI) desktop nativa, garantindo estabilidade e execução multi-threaded.
* **PyQtGraph:** Biblioteca gráfica acelerada por hardware (GPU) via C++, responsável por renderizar curvas com mais de 40.000 pontos a 60 FPS cravados sem latência.
* **OpenCV (cv2):** Motor de processamento de imagem utilizado para decodificar e sincronizar gravações de vídeo `.mp4` quadro a quadro com a linha do tempo da queima.
* **Pandas & NumPy:** Ferramentas fundamentais de ciência de dados utilizadas para manipulação de arrays e ingestão rápida dos arquivos CSV.
* **SciPy (signal):** Biblioteca matemática utilizada para implementar o Filtro Digital Butterworth de 4ª ordem (fase zero) para eliminação de ruídos harmônicos.

# Status do projeto

