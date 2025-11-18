# pip install matplotlib pyaudio numpy scipy

#import tkinter as tk
#from matplotlib.animation import FuncAnimation
#import matplotlib.pyplot as plt
import pyaudio
import numpy as np
from time import sleep
#from scipy.signal import butter, lfilter
#import threading


# Criar função de transferência para o nosso filtro
def butter_FT(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs # frequencia de Nyquist

    # Como é um filtro digital, os valores para frequencia minima e maxima de corte variam de 0 a 1
    # sendo 1 o equivalente a Frequência de Nyquist

    low = lowcut / nyq
    high = highcut / nyq

    nun, den = butter(order,[low,high],btype='band')
    return nun, den

# Retorna o sinal de áudio já filtrado
def butter_passa_banda(dados, lowcut, highcut, fs, order=5):
    nun, den = butter_FT(lowcut,highcut, fs,order)

    sinal_filtrado = lfilter(nun, den, dados)

    return sinal_filtrado



def inserir_notas():

    notas_musicais.clear()

    with open("notasViolino.txt", 'r') as file:
        for line in file:
            nota, freq_nota = line.strip().split(",")
            
            freq_nota = float(freq_nota)
            if nota in notas_musicais:
                notas_musicais[nota].append(freq_nota)
            else:
                notas_musicais[nota] = []
                notas_musicais[nota].append(freq_nota)

    frequencia_minima = min([min(notas_musicais[nota]) for nota in notas_musicais])
    frequencia_maxima = max([max(notas_musicais[nota]) for nota in notas_musicais])

    print("Filtro:\nMin:{}\nMax:{}".format(frequencia_minima,frequencia_maxima))

    for nota, freq_nota in notas_musicais.items():
        print("{} - {}".format(nota,freq_nota))


def captar_frequencias_do_audio():

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        dados = stream.read(CHUNK)
        frames.append(dados)

    dados_do_audio = np.frombuffer(b''.join(frames),dtype=np.int16)
    dados_do_audio_filtrado = butter_passa_banda(dados_do_audio,frequencia_minima, frequencia_maxima,RATE, order = 5)


# Frequencia mínima e máxima para o filtro passa-banda
global frequencia_minima
global frequencia_maxima

#Constantes para captura de áudio

CHUNK = 1024 # Quantidade de frames por buffer
FORMAT = pyaudio.paInt16 # Para maior resolução, pegue os dados no formato de 16 bits
CHANNELS = 1
RATE = 44100 # Taxa de amostragem
RECORD_SECONDS = 0.5 # Quanto tempo devo gravar o áudio amostrado?

# Buffers para armazenar as 10 últimas frequências
frequencia_sem_fitro_buffer = [0 for i in range(10)]
frequencia_com_fitro_buffer = [0 for i in range(10)]

# Dicionário - {Nota musical:Frequencia}

notas_musicais = {}

# Frames do áudio

frames = []

# Iniciar o pyaudio e abrir microfone

p = pyaudio.PyAudio()

#stream = p.open(FORMAT,CHANNELS,RATE,input=True,frames_per_buffer=CHUNK)
stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)

inserir_notas()

while True:
    captar_frequencias_do_audio()
    sleep(5/1000)