import tkinter as tk
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import pyaudio
import numpy as np
from scipy.signal import butter, lfilter
import threading

def executarComoThread():
    ani = FuncAnimation(plt.gcf(), atualizarGrafico, interval=500)
    plt.tight_layout()        
    plt.show()

def atualizarGrafico(i):
    valoresEixoX.pop(0)
    valoresEixoX.append(valoresEixoX[-1] + 1)
    plt.cla()
    plt.plot(valoresEixoX[-10:], FrequenciasSemFiltro[-10:], color='red', label='Sem filtro')
    plt.plot(valoresEixoX[-10:], FrequenciasComFiltro[-10:], color='blue', label='Com filtro')
    plt.legend()
    plt.title("Gráfico com valores das frequências")
    plt.xlabel('Tempo')
    plt.ylabel('Frequência (Hz)')
    
    # Definir limite do eixo y
    plt.ylim(0, int(maiorValor))

    # Adicionar valores no gráfico
    for i, j in zip(valoresEixoX, FrequenciasComFiltro):
        plt.text(i, j, str(round(j)), ha='center', va='bottom')
        

def butterBandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butterBandpassFilter(data, lowcut, highcut, fs, order=5):
    b, a = butterBandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def buscarBlocoNotas(option):
    global blocoNotas
    if option == "Notas Gerais":
        blocoNotas = "notas.txt"
    elif option == "Bandolim":
        blocoNotas = "notasBandolim.txt"
    elif option == "Guitarra":
        blocoNotas = "notasGuitarra.txt"
    elif option == "Ukulele":
        blocoNotas = "notasUkulele.txt"
    elif option == "Violino":
        blocoNotas = "notasViolino.txt"

def introduzirNotas(*args):
    global menorValor
    global maiorValor

    buscarBlocoNotas(selected_option.get())
    notas.clear()

    print("\n",selected_option.get(),"\n")

    with open(blocoNotas, 'r') as arquivo:
        for linha in arquivo:
            chave, valor_str = linha.strip().split(',')
            valor = float(valor_str)
            if chave in notas:
                notas[chave].append(valor)
            else:
                notas[chave] = [valor]
    #Serve para ir buscar o menor e maior valor do dicionario
    menorValor = min([min(notas[chave]) for chave in notas])
    maiorValor = max([max(notas[chave]) for chave in notas])
    print(menorValor, "   ", maiorValor,"\n")
        
    # Serve para verificar se o dicionário está correto
    for chave, valor in notas.items():
        print(chave, valor)

def ouvir():

    simbolo = ""
    nota = ""
    oitava = ""
    cor = "black"

    # Captura do sinal de áudio
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    # Conversão do sinal de áudio para um array NumPy
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)

    # Aplicação do filtro passa-banda
    filtered_audio_data = butterBandpassFilter(audio_data, menorValor, maiorValor, RATE, order = 4)

    #Calculo da frequencia com o audio sem filtro
    freqSemFiltro = np.fft.rfftfreq(len(audio_data), 1/RATE)
    frequenciaSemFiltro = freqSemFiltro[np.argmax(np.abs(np.fft.rfft(audio_data)))]

    #Calculo da frequencia com o audio filtrado
    freq = np.fft.rfftfreq(len(filtered_audio_data), 1/RATE)
    frequencia = freq[np.argmax(np.abs(np.fft.rfft(filtered_audio_data)))]
    
    frames.clear()
    
    frequencia = round(frequencia, 2)

    if selected_option.get() == "Notas Gerais":
        
        diferenca_mais_proxima = None

        for chave, valores in notas.items():
            for posicao, valor_atual in enumerate(valores):
                diferenca_atual = abs(valor_atual - frequencia)
                if diferenca_mais_proxima is None or diferenca_atual < diferenca_mais_proxima:
                    nota = chave
                    oitava = posicao + 1
                    diferenca_mais_proxima = diferenca_atual

    else:
        oitava = "--"
        for chave, valor in notas.items():
            if valor[0] <= frequencia <= valor[2]:
                nota = chave
                if frequencia<valor[1]-5:
                    simbolo = "--->"
                    cor = "red"
                elif frequencia>valor[1]+5:
                    simbolo = "<---"
                    cor = "red"
                else:
                    simbolo = "OK"
                    cor = "green"
                break
            
    FrequenciasComFiltro.pop(0)
    FrequenciasComFiltro.append(frequencia)

    FrequenciasSemFiltro.pop(0)
    FrequenciasSemFiltro.append(frequenciaSemFiltro)

    label.config(text=f"Frequência: {frequencia} Hz\nOitava:{oitava}\n{nota}")
    label2.config(text=f"{simbolo}", fg=cor)

    root.update()
    root.after(10, ouvir())


#Definir constantes que sao as configuracoes da gravacao
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 0.5

#Define a array para construir o grafico
FrequenciasComFiltro = [0,0,0,0,0,0,0,0,0,0]
FrequenciasSemFiltro = [0,0,0,0,0,0,0,0,0,0]
valoresEixoX = [i for i in range(len(FrequenciasComFiltro))]

#Define o dicionario para introduzir as frequências das notas musicais
notas={}

#Definir uma array para guardar os dados da gravacao
frames = []

#Iniciar o PyAudio
p = pyaudio.PyAudio()

# Abrir o microfone
stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)

root = tk.Tk()
root.title('Afinador')
root.geometry('500x400')

# Adicionado para definir o ícone da janela
root.iconbitmap("icon.ico")

label = tk.Label(root, font=('calibri', 30), fg="black")
label2 = tk.Label(root, font=('calibri', 30), fg="green")
label.pack(pady=20)
label2.pack()

options = ['Notas Gerais', 'Bandolim', 'Guitarra', 'Ukulele', 'Violino']
selected_option = tk.StringVar(value=options[0])

option_menu = tk.OptionMenu(root, selected_option, *options, command=introduzirNotas)
option_menu.pack()

#Preenche o dicionario das notas com o ficheiro txt pre-definido no inicio
introduzirNotas()

#Cria e inicia uma thread para mostrar o grafico
thread = threading.Thread(target=executarComoThread)
thread.start()

root.after(10, ouvir())
root.mainloop()


