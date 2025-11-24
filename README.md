
# Afinador de Violino

Este projeto tem como fim servir de auxílio no ajuste da vibração das cordas do violino na frequência adequada.

## Para começar a usar

No arquivo `reqs.txt` é listada as bibliotecas utilizadas bem como suas respectivas versões.

É aconselhável criar um ambiente virtual em python (`venv`) para que não haja conflito de versões de bibliotecas já instaladas no seu ambiente.

```
python -m venv venv
\venv\Scripts\Activate.ps1
pip install reqs.txt
```

## Como usar

Posteriormente, execute o arquivo `a.py` no diretório do repositório.

```
py a.py
```

A primeira janela que irá mostar será o diagrama de Bode do filtro ultilizado. Ao fechar tal janela, você terá livre acesso ao afinador propriamente dito.

## Como funciona

O som é captado via o microfone do dispositivo ultilizado e posteriormente filtrado por meio de um **filtro Butterworth passa-banda digital**, que captura frequências de 100 Hz à 700 Hz, menor e maior frequências produzidas nas cordas de um violino respectivamente.

A para captar o som, foi adotada uma **frequência de amostragem** de 44.100,00 Hz, a qual respeita o **teorema de  Shannon-Nyquist**, que dita que a frequência de amostragem deve ser mais do que o dobro da maior frequência registrada no sinal. Como queriamos pegar a maior gama de sons possível, considerou-se a maior frequência com 20 kHz, o máximo que o ouvido humano consegue captar. Além disso, **44.1 kHz é um importante padrão da industria** para digitalização de ondas sonoras em CDs (mais uma razão sua adoção).

O som captado é armazenado na sua forma bruta (com possíveis ruídos do ambiente) e em sua forma filtrada. A seguir, passamos esses 2 sinais pela Transformada de Fourier Rápida (via`FFT`), armazenamos o espectro de frequências e pegamos a frequência de maior amplitude.

A razão disso reside no fato que, ao tocarmos uma determinada nota no violino, não apenas a frequência da nota estará presente, mas haverá outros harmonicos também: sinais de frequência propocional à frequência principal e de menor intesidade (como na imagem abaixo). Esse conjunto de hamôrnicos e a frequência da nota caracterizam o timbre do instrumento violino, fator ativo para que possamos diferenciar o som do violino do som de outros instrumentos por exemplo.

![Timbre de um instrumento](https://blog.santoangelo.com.br/wp-content/uploads/2016/03/2016-03-02-004.jpg)

*Nota Lá 440 Hz de um instrumento.*

Portanto, como a frequência da nota tocada é a que terá maior intensidade, esta é a que pegamos. Isso no contexto do som filtrado. O análogo é feito no som não filtrado, embora neste caso isso apenas sirva de comparação, pois com os ruídos do ambiente, dificilmente teriamos a frequência da nota do violino.


No contexto do som filtrado, considerando a maior frequência do espectro captado, comparamos-na com um range de frequência já predefinidadas. Por exemplo, a frequência da nota Sol do violino se encontrar entre 100 Hz e 244.81 Hz. Se a frequência captada se econtrar nesta margem, então a comparamos com a frequência de 196 Hz, a qual é a frequência da nota Sol idealmente. No nosso afinador, ainda consideramos uma margem de 10 Hz para ou para menos de 196 Hz para considerarmos a respectiva corda como afinada.   

