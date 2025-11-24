# pip install matplotlib pyaudio numpy scipy

import tkinter as tk
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

import pyaudio
import numpy as np
from time import sleep
from scipy.signal import butter, lfilter, TransferFunction, bode, freqz
from scipy.io import wavfile
import threading

def mostrar_grafico_frequencias_captadas():
    ani = FuncAnimation(plt.gcf(), grafico_frequencias_captadas, interval=500)
    plt.tight_layout()        
    plt.show()


# Graficos com as frequencias captadas

def grafico_frequencias_captadas(i):
    valoresEixoX.pop(0)
    valoresEixoX.append(valoresEixoX[-1]+1)
    plt.cla()

    plt.plot(valoresEixoX[-10:],frequencia_sem_fitro_buffer[-10:],color="purple",label="Captado sem filtro")
    plt.plot(valoresEixoX[-10:],frequencia_com_fitro_buffer[-10:],color="green",label="Captado com filtro")
    plt.legend()
    plt.title("Gráfico com valores das frequências")
    plt.xlabel("Tempo")
    plt.ylabel("Frequência (Hz)")
    
    plt.ylim(0,int(frequencia_maxima))

    for i,j in zip(valoresEixoX,frequencia_com_fitro_buffer):
         plt.text(i, j, str(round(j)), ha='center', va='bottom')

# Mostrar diagrama de Bode do Filtro

def grafico_filtro():
    filtro_nun, filtro_den = butter_FT(lowcut=frequencia_minima, highcut=frequencia_maxima, fs=RATE, order=4)

    w, h = freqz(filtro_nun, filtro_den, worN = 8000)

    freq = (w/np.pi)*(RATE/2)

    plt.figure(figsize=(10, 6))
    plt.subplot(2,1,1)
    plt.semilogx(freq, abs(h))
    plt.title('Diagrama de Bode - Magnitude')
    plt.xlabel('Frequência (Hz)')
    plt.ylabel('Magnitude')
    plt.grid(True)

    # Diagrama de fase
    plt.subplot(2,1,2)
    plt.semilogx(freq, np.unwrap(np.angle(h)) * 180 / np.pi)
    plt.title('Diagrama de Bode - Fase')
    plt.xlabel('Frequência (Hz)')
    plt.ylabel('Fase (graus)')
    plt.grid(True)

    plt.tight_layout()
    plt.show()


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

    global frequencia_minima
    global frequencia_maxima

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


def captar_frequencias_do_micro():

    global frequencia_sem_fitro_buffer
    global frequencia_com_fitro_buffer
    global fft_coeficientes
    global fft_frequencias

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        dados = stream.read(CHUNK)
        frames.append(dados)

    dados_do_audio = np.frombuffer(b''.join(frames),dtype=np.int16)

    dados_do_audio_filtrado = butter_passa_banda(dados_do_audio,frequencia_minima, frequencia_maxima,RATE, order = 4)

    # AUDIO NÃO FILTRADO

     # Gerar um array de N frequencias, de 0 hz até a máxima frequencia
    frequencias_nao_filtrado = np.fft.rfftfreq(len(dados_do_audio), 1/RATE)

     # Gerar os coeficientes (fase e intensidade) das frequencias presentes no áudio e pega frequencia de maior intensidade
    frequencias_nao_filtrado_nota = frequencias_nao_filtrado[np.argmax(np.abs(np.fft.rfft(dados_do_audio)))]

    # AUDIO FILTRADO

    frequencias_filtrado = np.fft.rfftfreq(len(dados_do_audio_filtrado), 1/RATE)


    fft_coeficientes = np.abs(np.fft.rfft(dados_do_audio_filtrado))
    fft_frequencias = frequencias_filtrado


    frequencias_filtrado_nota = frequencias_filtrado[np.argmax(np.abs(np.fft.rfft(dados_do_audio_filtrado)))]

    frames.clear()

    frequencia_da_nota = round(frequencias_filtrado_nota,2)
    frequencia_com_ruido = round(frequencias_nao_filtrado_nota,2)
  

    print("{} Hz (com ruido)".format(frequencias_nao_filtrado_nota))
    print("{} Hz".format(frequencias_filtrado_nota))

    nome_das_notas = []
    status_das_notas = []
    cor_das_notas = []

    for nota, valor in notas_musicais.items():

        cor = ""
        status = ""

        if valor[0] <= frequencia_da_nota <= valor[2]:
            if valor[1] - 10 <= frequencia_da_nota <= valor[1] + 10:
                status = "OK"
                cor = "green"

            if frequencia_da_nota < valor[1]-10:
                status = ">>muito grave>>"
                cor = "red"
            elif frequencia_da_nota > valor[1]+10:
                status = "<<muito fino<<"
                cor = "red"
            else:
                status = "OK"
                cor = "green"
        else:
            status = "--"
            cor = "black"
        
        nome_das_notas.append(nota)
        status_das_notas.append(status)
        cor_das_notas.append(cor)

        print("{}: {}".format(nota, status))

       
    print("---------")

    frequencia_sem_fitro_buffer.pop(0)
    frequencia_sem_fitro_buffer.append(frequencias_nao_filtrado_nota)

    frequencia_com_fitro_buffer.pop(0)
    frequencia_com_fitro_buffer.append(frequencias_filtrado_nota)

    freq_show.config(text="Frequência: {} Hz".format(frequencia_da_nota))

    
    sol_show.config(text=f"{nome_das_notas[0]}:{status_das_notas[0]}",fg=cor_das_notas[0])
    re_show.config(text=f"{nome_das_notas[1]}:{status_das_notas[1]}",fg=cor_das_notas[1])
    la_show.config(text=f"{nome_das_notas[2]}:{status_das_notas[2]}",fg=cor_das_notas[2])
    mi_show.config(text=f"{nome_das_notas[3]}:{status_das_notas[3]}",fg=cor_das_notas[3])


    root.update()
    root.after(10,captar_frequencias_do_micro())

# Filtro - Função de Transferência

global filtro_num
global filtro_den

# Espectro das Frequencias

fft_coeficientes = []
fft_frequencias = []

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
valoresEixoX = [i for i in range(len(frequencia_com_fitro_buffer))]

# Dicionário - {Nota musical:Frequencia}

notas_musicais = {}

# Frames do áudio

frames = []


inserir_notas()

grafico_filtro()

# Iniciar o pyaudio e abrir microfone

p = pyaudio.PyAudio()

#stream = p.open(FORMAT,CHANNELS,RATE,input=True,frames_per_buffer=CHUNK)
stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)


root = tk.Tk()
root.title("Afinador de Violino")
root.geometry("500x400")

freq_show = tk.Label(root, font=("calibri",15),fg="black")
freq_show.pack(pady=20)

sol_show = tk.Label(root, font=("calibri",15),fg="black")
sol_show.pack(pady=20)

re_show = tk.Label(root, font=("calibri",15),fg="black")
re_show.pack(pady=20)

la_show = tk.Label(root, font=("calibri",15),fg="black")
la_show.pack(pady=20)

mi_show = tk.Label(root, font=("calibri",15),fg="black")
mi_show.pack(pady=20)


#thread_2 = threading.Thread(target=grafico_filtro)
#thread_2.start()

thread_1 = threading.Thread(target=mostrar_grafico_frequencias_captadas)
thread_1.start()

root.after(10,captar_frequencias_do_micro())
root.mainloop()