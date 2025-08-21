# Graphite - Interface Gráfica Python

Graphite é uma biblioteca Python para criação de interfaces gráficas de forma simples e intuitiva, construída sobre Tkinter.

## Versão 0.4.6

### Novidades na Função `animateObject`

A função `animateObject` agora suporta **múltiplos formatos de cor** e **diversos tipos de animação** para criar interfaces mais dinâmicas e interativas.

#### Formatos de Cor Suportados:

1. **RGB (Tupla/Lista)**: `(255, 0, 0)` ou `[255, 0, 0]`
2. **Hexadecimal**: `#FF0000` ou `FF0000`
3. **Nomes de Cor**: `"red"`, `"blue"`, `"green"`, etc.

#### Tipos de Animação Disponíveis:

##### Animações Básicas:
- **`"move"`**: Move o objeto de uma posição para outra
- **`"color"`**: Anima a cor de fundo do objeto
- **`"textcolor"`**: Anima a cor do texto do objeto

##### Animações de Tamanho:
- **`"size"`**: Anima o tamanho do objeto (largura e altura)
- **`"width"`**: Anima apenas a largura do objeto
- **`"height"`**: Anima apenas a altura do objeto

##### Efeitos Especiais:
- **`"pulse"`**: Efeito de pulso (cresce e diminui)
- **`"shake"`**: Efeito de tremor
- **`"bounce"`**: Efeito de quicar
- **`"fade_in"`**: Aparece gradualmente
- **`"fade_out"`**: Desaparece gradualmente
- **`"slide_in"`**: Desliza para dentro
- **`"slide_out"`**: Desliza para fora

#### Tipos de Easing (Interpolação):

- **`"linear"`**: Movimento constante (padrão)
- **`"ease_in"`**: Aceleração gradual
- **`"ease_out"`**: Desaceleração gradual
- **`"ease_in_out"`**: Aceleração e desaceleração

#### Exemplos de Uso:

```python
from Graphite import GraphiteInter

# Criar janela e elementos
GraphiteInter.create_window("Teste")
GraphiteInter.create_button("Botão", "btn1", None)
GraphiteInter.buttonposition("btn1", 50, 50)

# Animações básicas
GraphiteInter.animateObject("btn1", "move", 2000, 
                           startpos=(50, 50), endpos=(200, 50), 
                           easing="ease_in_out")

GraphiteInter.animateObject("btn1", "color", 2000, 
                           startcolor="#FF0000", endcolor="#00FF00", 
                           easing="ease_in")

# Animações de tamanho
GraphiteInter.animateObject("btn1", "size", 2000, 
                           startwidth=10, endwidth=20, 
                           startheight=2, endheight=4, 
                           easing="ease_out")

# Efeitos especiais
GraphiteInter.animateObject("btn1", "pulse", 2000, easing="ease_in_out")
GraphiteInter.animateObject("btn1", "shake", 1000)
GraphiteInter.animateObject("btn1", "bounce", 2000, easing="ease_out")
GraphiteInter.animateObject("btn1", "slide_in", 1500, easing="ease_in_out")
GraphiteInter.animateObject("btn1", "fade_out", 2000, easing="ease_in")

# Animações de texto
GraphiteInter.inserttext("texto", "Texto Animado", 16, (100, 100), "black")
GraphiteInter.animateObject("texto", "textcolor", 2000, 
                           startcolor="black", endcolor="#FF0000", 
                           easing="ease_in_out")
```

#### Parâmetros Completos da Função:

```python
GraphiteInter.animateObject(
    objectId,           # ID do objeto a ser animado
    animation,          # Tipo de animação
    duration,           # Duração em milissegundos
    startpos=None,      # Posição inicial (x, y) para "move"
    endpos=None,        # Posição final (x, y) para "move"
    startcolor=None,    # Cor inicial (RGB, Hex ou Nome)
    endcolor=None,      # Cor final (RGB, Hex ou Nome)
    startwidth=None,    # Largura inicial para "size"/"width"
    endwidth=None,      # Largura final para "size"/"width"
    startheight=None,   # Altura inicial para "size"/"height"
    endheight=None,     # Altura final para "size"/"height"
    startopacity=None,  # Opacidade inicial (0-1)
    endopacity=None,    # Opacidade final (0-1)
    startrotation=None, # Rotação inicial (graus)
    endrotation=None,   # Rotação final (graus)
    startscale=None,    # Escala inicial
    endscale=None,      # Escala final
    easing="linear"     # Tipo de interpolação
)
```

### Teste a Funcionalidade

Execute o arquivo `testeanimatecolor.py` para ver exemplos práticos de todas as animações:

```bash
python testeanimatecolor.py
```

### Recursos Principais

- ✅ Suporte a múltiplos formatos de cor
- ✅ 15+ tipos de animação diferentes
- ✅ 4 tipos de easing para interpolação
- ✅ Animações suaves e fluidas
- ✅ Compatibilidade com todos os widgets
- ✅ Validação automática de formatos
- ✅ Conversão automática entre formatos
- ✅ Efeitos especiais prontos para uso

### Casos de Uso Comuns

#### Interface de Login:
```python
# Botão que pulsa quando há erro
GraphiteInter.animateObject("btn_login", "shake", 500)

# Campo que aparece deslizando
GraphiteInter.animateObject("input_password", "slide_in", 1000, easing="ease_out")
```

#### Dashboard Interativo:
```python
# Cards que aparecem com fade in
GraphiteInter.animateObject("card1", "fade_in", 800, easing="ease_in")

# Botões que reagem ao hover
GraphiteInter.animateObject("btn_action", "pulse", 300, easing="ease_in_out")
```

#### Notificações:
```python
# Notificação que aparece deslizando
GraphiteInter.animateObject("notification", "slide_in", 500, easing="ease_out")

# Alerta que treme para chamar atenção
GraphiteInter.animateObject("alert", "shake", 1000)
```

### Instalação

```bash
pip install -e .
```

### Uso Básico

```python
from Graphite import GraphiteInter

# Criar janela
GraphiteInter.create_window("Minha App")
GraphiteInter.setdimensions(800, 600)

# Criar elementos
GraphiteInter.create_button("Clique Aqui", "btn1", lambda: print("Clicado!"))
GraphiteInter.buttonposition("btn1", 100, 100)

# Adicionar animação
GraphiteInter.animateObject("btn1", "pulse", 2000, easing="ease_in_out")

# Executar
GraphiteInter.run()
```

### Licença

Este projeto está sob licença MIT.

## Como Usar

```python
from Graphite import GraphiteInter

# Função para exibir a contagem regressiva e a mensagem final
def start_countdown():
    GraphiteInter._root.after(0,GraphiteInter.removebutton("countdown"))
    GraphiteInter._root.after(1000,GraphiteInter.removebutton("rstrt"))
    # Insere a contagem de 10 a 0
    for i in range(60, -1, -1):  # De 10 até 0
        GraphiteInter._root.after((60 - i) * 1000, lambda i=i: GraphiteInter.inserttext(f"counter{i}", str(i), 50, (400, 250), "red"))
        GraphiteInter._root.after((60 - i) * 1000 + 500, lambda i=i: GraphiteInter.removeText(f"counter{i}"))

    # Insere a mensagem após a contagem regressiva
    GraphiteInter._root.after(61 * 1000, lambda: GraphiteInter.inserttext("EndTrial", "Sua licença expirou, reabra o programa", 30, (50, 250), "red"))
    GraphiteInter._root.after(61*1000,lambda:GraphiteInter.create_button("Reiniciar","rstrt",restart)) 
    GraphiteInter._root.after(61*1000,lambda:GraphiteInter.buttonposition("rstrt",0,0)) 
# Cria a janela
def restart():
 GraphiteInter._root.after(61*1000,lambda:GraphiteInter.removebutton("rstrt"))
 GraphiteInter._root.after(0,lambda:GraphiteInter.removeText("EndTrial"))
 GraphiteInter.create_button("Iniciar Contagem","countdown",start_countdown)
 GraphiteInter.buttonposition("countdown",0,0)
 GraphiteInter.removeBgImage()
#criando a janela
GraphiteInter.create_window("teste")

# Define o fundo da janela e a imagem de fundo
GraphiteInter.setbackground("blue")
GraphiteInter.setbgimage("C:\\Users\\leona\\Desktop\\imagem.jpg")

GraphiteInter.create_button("Iniciar Contagem","countdown",start_countdown)
GraphiteInter.buttonposition("countdown",0,0)

# Exibe a janela
GraphiteInter.run()
