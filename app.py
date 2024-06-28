import cv2
import pytesseract
import sqlite3
import os
import numpy as np

# Configurar o caminho para o executável do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocessar_imagem(imagem):
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    cinza = cv2.GaussianBlur(cinza, (5, 5), 0)
    _, binaria = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binaria

def ajustar_bordas(contorno):
    epsilon = 0.02 * cv2.arcLength(contorno, True)
    aproximacao = cv2.approxPolyDP(contorno, epsilon, True)
    return aproximacao

def ler_placa(imagem):
    imagem_preprocessada = preprocessar_imagem(imagem)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    morfologia = cv2.morphologyEx(imagem_preprocessada, cv2.MORPH_CLOSE, kernel)
    contornos, _ = cv2.findContours(morfologia, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    texto_placa = ""
    imagem_destacada = imagem.copy()
    for contorno in contornos:
        contorno_ajustado = ajustar_bordas(contorno)
        x, y, w, h = cv2.boundingRect(contorno_ajustado)
        if w / h > 2 and w / h < 6 and w > 50 and h > 15:
            regiao_placa = imagem[y:y+h, x:x+w]
            texto = pytesseract.image_to_string(regiao_placa, config='--psm 7')
            texto = texto.strip()
            texto_placa += texto + "\n"
            imagem_destacada = cv2.rectangle(imagem_destacada, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return texto_placa.strip(), imagem_destacada

def conectar_banco_dados():
    conexao = sqlite3.connect('placas_autorizadas.db')
    cursor = conexao.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS autorizadas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        placa TEXT NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS correcao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        placa_lida TEXT NOT NULL,
        placa_corrigida TEXT NOT NULL
    )
    ''')
    conexao.commit()
    return conexao, cursor

def adicionar_placa_autorizada(cursor, conexao, placa):
    cursor.execute("INSERT INTO autorizadas (placa) VALUES (?)", (placa,))
    conexao.commit()

def placa_autorizada(cursor, placa):
    cursor.execute("SELECT * FROM autorizadas WHERE placa = ?", (placa,))
    resultado = cursor.fetchone()
    return resultado is not None

def salvar_correcao(cursor, conexao, placa_lida, placa_corrigida):
    cursor.execute("INSERT INTO correcao (placa_lida, placa_corrigida) VALUES (?, ?)", (placa_lida, placa_corrigida))
    conexao.commit()

def obter_correcao(cursor, placa_lida):
    cursor.execute("SELECT placa_corrigida FROM correcao WHERE placa_lida = ?", (placa_lida,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

# Função principal para ler e verificar placas
def verificar_placas(caminho_pasta):
    conexao, cursor = conectar_banco_dados()

    # Adicionar algumas placas autorizadas
    placas_autorizadas = ['CMG-3164', 'XYZ-5678', 'AAA-1111']
    for placa in placas_autorizadas:
        adicionar_placa_autorizada(cursor, conexao, placa)

    # Listar todos os arquivos na pasta
    arquivos_imagens = [f for f in os.listdir(caminho_pasta) if os.path.isfile(os.path.join(caminho_pasta, f))]

    for arquivo in arquivos_imagens:
        caminho_imagem = os.path.join(caminho_pasta, arquivo)
        imagem = cv2.imread(caminho_imagem)
        placa_detectada, imagem_destacada = ler_placa(imagem)
        print(f"Placa detectada na imagem {arquivo}: {placa_detectada}")

        # Verificar se a placa detectada está corrigida
        placa_corrigida = obter_correcao(cursor, placa_detectada)
        if placa_corrigida:
            print(f"Placa corrigida encontrada: {placa_corrigida}")
            if placa_autorizada(cursor, placa_corrigida):
                print(f"Entrada liberada para a placa corrigida: {placa_corrigida}")
            else:
                print(f"Entrada ainda negada para a placa corrigida: {placa_corrigida}")
        else:
            if placa_autorizada(cursor, placa_detectada):
                print(f"Entrada liberada para a placa: {placa_detectada}")
            else:
                print(f"Entrada negada para a placa: {placa_detectada}")
                placa_corrigida = input("Por favor, corrija a placa detectada: ")
                salvar_correcao(cursor, conexao, placa_detectada, placa_corrigida)
                if placa_autorizada(cursor, placa_corrigida):
                    print(f"Entrada liberada para a placa corrigida: {placa_corrigida}")
                else:
                    print(f"Entrada ainda negada para a placa corrigida: {placa_corrigida}")

    conexao.close()

# Chamar a função principal com o caminho para a pasta de imagens
caminho_pasta = r'G:\Projetos\Projeto Leitura de Placas\PLACAS AUTORIZADAS'
verificar_placas(caminho_pasta)
