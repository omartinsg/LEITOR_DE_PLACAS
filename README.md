1 - Processamento de Imagens com OpenCV: As imagens são pré-processadas para melhorar a detecção das placas. Isso inclui conversão para escala de cinza, aplicação de desfoque gaussiano e binarização.

2 - OCR com Tesseract: A biblioteca Tesseract é utilizada para reconhecer e extrair texto das regiões de placas detectadas nas imagens processadas.

3 - Banco de Dados SQLite: Um banco de dados SQLite é empregado para armazenar informações sobre placas autorizadas e correções realizadas. São mantidas tabelas para placas autorizadas e para correções de leitura.

4 -Funcionalidades Principais:

    - Detecção e leitura de placas de veículos em imagens.
    - Verificação automática se a placa detectada está na lista de placas autorizadas.
    - Possibilidade de correção manual de leitura de placas incorretas, armazenando as correções no banco de dados.
    
 5 -Fluxo de Execução:

    - O sistema percorre uma pasta especificada contendo imagens de placas de veículos.
    - Para cada imagem, realiza a detecção da placa e sua leitura utilizando técnicas de processamento de imagens e OCR.
    - Verifica se a placa detectada está na lista de autorizadas no banco de dados.
    - Permite ao usuário corrigir manualmente leituras incorretas, atualizando o banco de dados com as correções.
  
6 - Objetivos:

    - Automatizar o processo de verificação de placas de veículos.
    - Facilitar o controle de acesso baseado em placas autorizadas.
    - Melhorar a eficiência e precisão na detecção e leitura de placas através de técnicas avançadas de processamento de imagens e OCR.
