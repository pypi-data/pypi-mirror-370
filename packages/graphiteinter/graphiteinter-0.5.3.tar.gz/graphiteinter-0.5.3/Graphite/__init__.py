#Graphite version 0.5.3
import threading
import time
import tkinter as tk
from tkinter import  Checkbutton, Entry, Frame, IntVar, Label, OptionMenu, Radiobutton, StringVar, Text, ttk
from PIL import Image, ImageTk
import json
from tkinter import Button
from tkinter import messagebox
from tkinterweb import HtmlFrame  # Importação de tkinterweb sem a verificação
from lxml import etree
from tkinter import PhotoImage
import tempfile
import os
import requests
import re
import configparser
import ctypes
import inspect
import pandas as pd
import tkinter.filedialog as fd

class GraphiteInter:
    created_buttons = set()  # Conjunto para armazenar IDs dos botões criados
    _root = None
    _bg_image_label = None
    _buttons = {}
    _texts = []
    _comboboxes = {}
    _sliders = {}
    _inputs = {} 
    _texts = {}  # Usado para armazenar os textos com seus IDs
    _state = {}  # Variável para armazenar o estado
    _width = 800
    _height = 600
    _bgi = None
    _tabs = {}
    _widgets = {}
    _loading_label = None
    _loading_running = False
    _html_frame = None 
    _Functions={}
    _buttons = {}  # Dicionário para armazenar botões pelo ID
    _icons = {}  # Dicionário para armazenar os ícones dos botões
    _loading_labels = {}  # Dicionário para armazenar labels de loading
    _windows = {}
    _images = {}  # Dicionário para armazenar imagens com seus IDs
    _tables = {}  # Dicionário para armazenar tabelas com seus IDs
    _excel_containers = {}  # Dicionário para armazenar containers Excel
    _window_closed = False  # Variável para rastrear se a janela foi fechada

    @staticmethod
    def create_window(title="GraphiteInter App"):
        """Cria uma janela principal."""
        GraphiteInter._root = tk.Tk()
        GraphiteInter._root.title(title)
        GraphiteInter._root.geometry("800x600")
        GraphiteInter._windows[title] = GraphiteInter._root
        GraphiteInter._window_closed = False  # Reset do estado da janela
        
        # Configurar evento de fechamento da janela
        def on_closing():
            GraphiteInter._window_closed = True
            GraphiteInter._root.destroy()
        
        GraphiteInter._root.protocol("WM_DELETE_WINDOW", on_closing)

    @staticmethod
    def onclosewindow():
        """
        Retorna o estado da janela principal.
        Retorna:
        - 1: Janela foi fechada
        - 0: Janela está ativa/aberta
        """
        if GraphiteInter._root is None:
            return 1  # Se não há janela, considera como fechada
        
        try:
            # Verifica se a janela ainda existe e está ativa
            if GraphiteInter._window_closed or not GraphiteInter._root.winfo_exists():
                return 1
            else:
                return 0
        except tk.TclError:
            # Se ocorrer erro ao verificar a janela, significa que foi fechada
            return 1

    @staticmethod
    def closewindow(windowname):
        """Fecha uma janela específica pelo nome."""
        if windowname in GraphiteInter._windows:
            GraphiteInter._windows[windowname].destroy()
            del GraphiteInter._windows[windowname]
        else:
            print(f"⚠️ A janela '{windowname}' não foi encontrada.")

    @staticmethod
    def setdimensions(width, height):
        """Define as dimensões da janela e armazena nas variáveis de classe."""
        if GraphiteInter._root:
            GraphiteInter._root.geometry(f"{width}x{height}")
            
            # Armazenar as dimensões nas variáveis de classe
            GraphiteInter._width = width
            GraphiteInter._height = height
            
            return width, height
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    @staticmethod
    def animateObject(objectId, animation, duration, startpos=None, endpos=None, startwidth=None, endwidth=None, startheight=None, endheight=None, startcolor=None, endcolor=None, startopacity=None, endopacity=None, startrotation=None, endrotation=None, startscale=None, endscale=None, easing="linear"):
        """
        Anima um objeto (widget ou texto do canvas) identificado por objectId.
        
        Tipos de animação suportados:
        - 'move': Move o objeto de uma posição para outra
        - 'color': Anima a cor de fundo do objeto
        - 'textcolor': Anima a cor do texto do objeto
        - 'size': Anima o tamanho do objeto (largura e altura)
        - 'width': Anima apenas a largura do objeto
        - 'height': Anima apenas a altura do objeto
        - 'opacity': Anima a transparência do objeto (0-1)
        - 'rotation': Anima a rotação do objeto (graus)
        - 'scale': Anima a escala do objeto (fator de escala)
        - 'pulse': Efeito de pulso (cresce e diminui)
        - 'shake': Efeito de tremor
        - 'fade_in': Aparece gradualmente
        - 'fade_out': Desaparece gradualmente
        - 'bounce': Efeito de quicar
        - 'slide_in': Desliza para dentro
        - 'slide_out': Desliza para fora
        
        Parâmetros:
        - duration: duração total em ms
        - startpos/endpos: (x, y) para mover
        - startcolor/endcolor: para cor de fundo ou texto (suporta RGB, Hex e nomes)
        - startwidth/endwidth: largura inicial/final
        - startheight/endheight: altura inicial/final
        - startopacity/endopacity: opacidade inicial/final (0-1)
        - startrotation/endrotation: rotação inicial/final (graus)
        - startscale/endscale: escala inicial/final
        - easing: tipo de interpolação ('linear', 'ease_in', 'ease_out', 'ease_in_out')
        """
        # Funções auxiliares para conversão de cores
        def parse_color(color):
            """Converte cor de qualquer formato para RGB."""
            if color is None:
                return None
            
            # Se já é uma tupla RGB
            if isinstance(color, (tuple, list)) and len(color) == 3:
                return tuple(int(c) for c in color)
            
            # Se é string hexadecimal
            if isinstance(color, str):
                color = color.strip()
                # Remove # se presente
                if color.startswith('#'):
                    color = color[1:]
                
                # Verifica se é hexadecimal válido
                if len(color) == 6 and all(c in '0123456789ABCDEFabcdef' for c in color):
                    return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                
                # Se não é hexadecimal, tenta usar como nome de cor
                try:
                    # Testa se é um nome de cor válido do Tkinter
                    test_widget = tk.Label()
                    test_widget.config(bg=color)
                    # Se chegou aqui, é um nome válido, converte para RGB
                    rgb = test_widget.winfo_rgb(color)
                    test_widget.destroy()
                    return tuple(c // 256 for c in rgb)  # Tkinter usa 0-65535, converte para 0-255
                except:
                    raise ValueError(f"Formato de cor inválido: {color}")
            
            raise ValueError(f"Formato de cor não suportado: {color}")
        
        def rgb_to_hex(rgb):
            """Converte RGB para hexadecimal."""
            return '#%02x%02x%02x' % rgb
        
        def apply_easing(progress, easing_type):
            """Aplica diferentes tipos de easing à animação."""
            if easing_type == "linear":
                return progress
            elif easing_type == "ease_in":
                return progress * progress
            elif easing_type == "ease_out":
                return 1 - (1 - progress) * (1 - progress)
            elif easing_type == "ease_in_out":
                if progress < 0.5:
                    return 2 * progress * progress
                else:
                    return 1 - 2 * (1 - progress) * (1 - progress)
            else:
                return progress
        
        # Descobrir o widget ou item
        widget = None
        for d in [GraphiteInter._buttons, GraphiteInter._texts, GraphiteInter._comboboxes, GraphiteInter._sliders, GraphiteInter._inputs, GraphiteInter._images, GraphiteInter.widgets]:
            if objectId in d:
                widget = d[objectId]
                break
        if widget is None:
            raise ValueError(f"Widget com ID '{objectId}' não encontrado.")

        # Caso especial para imagens
        if objectId in GraphiteInter._images:
            image_data = GraphiteInter._images[objectId]
            widget = image_data['label']  # Usa o label da imagem como widget

        steps = 30  # Número de frames
        interval = max(1, duration // steps)

        # Caso especial: texto do canvas
        if isinstance(widget, tuple) and hasattr(widget[0], 'itemconfig'):
            canvas, item_id = widget
            
            if animation == "move" and startpos and endpos:
                x0, y0 = startpos
                x1, y1 = endpos
                def animate_move(step=0):
                    if step > steps:
                        canvas.coords(item_id, x1, y1)
                        return
                    progress = apply_easing(step / steps, easing)
                    x = x0 + (x1 - x0) * progress
                    y = y0 + (y1 - y0) * progress
                    canvas.coords(item_id, x, y)
                    GraphiteInter._root.after(interval, animate_move, step + 1)
                animate_move()
                
            elif animation == "textcolor" and startcolor and endcolor:
                c0 = parse_color(startcolor)
                c1 = parse_color(endcolor)
                def animate_textcolor(step=0):
                    if step > steps:
                        canvas.itemconfig(item_id, fill=rgb_to_hex(c1))
                        return
                    progress = apply_easing(step / steps, easing)
                    r = int(c0[0] + (c1[0] - c0[0]) * progress)
                    g = int(c0[1] + (c1[1] - c0[1]) * progress)
                    b = int(c0[2] + (c1[2] - c0[2]) * progress)
                    canvas.itemconfig(item_id, fill=rgb_to_hex((r, g, b)))
                    GraphiteInter._root.after(interval, animate_textcolor, step + 1)
                animate_textcolor()
                
            elif animation == "fade_in":
                def animate_fade_in(step=0):
                    if step > steps:
                        return
                    progress = apply_easing(step / steps, easing)
                    # Para canvas, usamos transparência via cor
                    current_color = canvas.itemcget(item_id, "fill")
                    if current_color:
                        # Adiciona transparência simulada
                        canvas.itemconfig(item_id, fill=current_color)
                    GraphiteInter._root.after(interval, animate_fade_in, step + 1)
                animate_fade_in()
                
            elif animation == "fade_out":
                def animate_fade_out(step=0):
                    if step > steps:
                        canvas.itemconfig(item_id, fill="")
                        return
                    progress = apply_easing(step / steps, easing)
                    # Simula fade out
                    GraphiteInter._root.after(interval, animate_fade_out, step + 1)
                animate_fade_out()
                
            else:
                raise ValueError(f"Tipo de animação '{animation}' não suportado para canvas items.")
                
        else:
            # Widgets normais
            if animation == "move" and startpos and endpos:
                x0, y0 = startpos
                x1, y1 = endpos
                def animate_move(step=0):
                    if step > steps:
                        widget.place(x=x1, y=y1)
                        return
                    progress = apply_easing(step / steps, easing)
                    x = x0 + (x1 - x0) * progress
                    y = y0 + (y1 - y0) * progress
                    widget.place(x=int(x), y=int(y))
                    GraphiteInter._root.after(interval, animate_move, step + 1)
                animate_move()
                
            elif animation == "color" and startcolor and endcolor:
                c0 = parse_color(startcolor)
                c1 = parse_color(endcolor)
                def animate_color(step=0):
                    if step > steps:
                        widget.config(bg=rgb_to_hex(c1))
                        return
                    progress = apply_easing(step / steps, easing)
                    r = int(c0[0] + (c1[0] - c0[0]) * progress)
                    g = int(c0[1] + (c1[1] - c0[1]) * progress)
                    b = int(c0[2] + (c1[2] - c0[2]) * progress)
                    widget.config(bg=rgb_to_hex((r, g, b)))
                    GraphiteInter._root.after(interval, animate_color, step + 1)
                animate_color()
                
            elif animation == "textcolor" and startcolor and endcolor:
                c0 = parse_color(startcolor)
                c1 = parse_color(endcolor)
                def animate_textcolor(step=0):
                    if step > steps:
                        widget.config(fg=rgb_to_hex(c1))
                        return
                    progress = apply_easing(step / steps, easing)
                    r = int(c0[0] + (c1[0] - c0[0]) * progress)
                    g = int(c0[1] + (c1[1] - c0[1]) * progress)
                    b = int(c0[2] + (c1[2] - c0[2]) * progress)
                    widget.config(fg=rgb_to_hex((r, g, b)))
                    GraphiteInter._root.after(interval, animate_textcolor, step + 1)
                animate_textcolor()
                
            elif animation == "size" and startwidth and endwidth and startheight and endheight:
                def animate_size(step=0):
                    if step > steps:
                        widget.config(width=endwidth, height=endheight)
                        return
                    progress = apply_easing(step / steps, easing)
                    width = int(startwidth + (endwidth - startwidth) * progress)
                    height = int(startheight + (endheight - startheight) * progress)
                    widget.config(width=width, height=height)
                    GraphiteInter._root.after(interval, animate_size, step + 1)
                animate_size()
                
            elif animation == "width" and startwidth and endwidth:
                def animate_width(step=0):
                    if step > steps:
                        widget.config(width=endwidth)
                        return
                    progress = apply_easing(step / steps, easing)
                    width = int(startwidth + (endwidth - startwidth) * progress)
                    widget.config(width=width)
                    GraphiteInter._root.after(interval, animate_width, step + 1)
                animate_width()
                
            elif animation == "height" and startheight and endheight:
                def animate_height(step=0):
                    if step > steps:
                        widget.config(height=endheight)
                        return
                    progress = apply_easing(step / steps, easing)
                    height = int(startheight + (endheight - startheight) * progress)
                    widget.config(height=height)
                    GraphiteInter._root.after(interval, animate_height, step + 1)
                animate_height()
                
            elif animation == "pulse":
                original_width = widget.winfo_reqwidth()
                original_height = widget.winfo_reqheight()
                def animate_pulse(step=0):
                    if step > steps:
                        widget.config(width=original_width, height=original_height)
                        return
                    progress = apply_easing(step / steps, easing)
                    # Efeito de pulso: cresce até 1.2x e volta ao normal
                    scale = 1 + 0.2 * abs(progress - 0.5) * 2
                    width = int(original_width * scale)
                    height = int(original_height * scale)
                    widget.config(width=width, height=height)
                    GraphiteInter._root.after(interval, animate_pulse, step + 1)
                animate_pulse()
                
            elif animation == "shake":
                original_x = widget.winfo_x()
                original_y = widget.winfo_y()
                def animate_shake(step=0):
                    if step > steps:
                        widget.place(x=original_x, y=original_y)
                        return
                    progress = step / steps
                    # Efeito de tremor: movimento aleatório
                    import random
                    shake_x = original_x + random.randint(-5, 5)
                    shake_y = original_y + random.randint(-5, 5)
                    widget.place(x=shake_x, y=shake_y)
                    GraphiteInter._root.after(interval, animate_shake, step + 1)
                animate_shake()
                
            elif animation == "fade_in":
                def animate_fade_in(step=0):
                    if step > steps:
                        return
                    progress = apply_easing(step / steps, easing)
                    # Simula fade in alterando a cor gradualmente
                    current_bg = widget.cget("bg")
                    if current_bg:
                        # Adiciona transparência simulada
                        pass
                    GraphiteInter._root.after(interval, animate_fade_in, step + 1)
                animate_fade_in()
                
            elif animation == "fade_out":
                def animate_fade_out(step=0):
                    if step > steps:
                        widget.place_forget()  # Esconde o widget
                        return
                    progress = apply_easing(step / steps, easing)
                    # Simula fade out
                    GraphiteInter._root.after(interval, animate_fade_out, step + 1)
                animate_fade_out()
                
            elif animation == "bounce":
                original_y = widget.winfo_y()
                def animate_bounce(step=0):
                    if step > steps:
                        widget.place(y=original_y)
                        return
                    progress = step / steps
                    # Efeito de quicar: movimento parabólico
                    bounce_height = 50
                    y_offset = bounce_height * (1 - (2 * progress - 1) ** 2)
                    widget.place(y=int(original_y - y_offset))
                    GraphiteInter._root.after(interval, animate_bounce, step + 1)
                animate_bounce()
                
            elif animation == "slide_in":
                original_x = widget.winfo_x()
                original_y = widget.winfo_y()
                # Começa fora da tela
                widget.place(x=original_x - 200, y=original_y)
                def animate_slide_in(step=0):
                    if step > steps:
                        widget.place(x=original_x, y=original_y)
                        return
                    progress = apply_easing(step / steps, easing)
                    x = original_x - 200 + 200 * progress
                    widget.place(x=int(x), y=original_y)
                    GraphiteInter._root.after(interval, animate_slide_in, step + 1)
                animate_slide_in()
                
            elif animation == "slide_out":
                original_x = widget.winfo_x()
                original_y = widget.winfo_y()
                def animate_slide_out(step=0):
                    if step > steps:
                        widget.place_forget()
                        return
                    progress = apply_easing(step / steps, easing)
                    x = original_x + 200 * progress
                    widget.place(x=int(x), y=original_y)
                    GraphiteInter._root.after(interval, animate_slide_out, step + 1)
                animate_slide_out()
                
            else:
                raise ValueError(f"Tipo de animação '{animation}' não suportado ou parâmetros inválidos para animateObject.")

    @staticmethod
    def setbackground(color):
        """Define a cor de fundo da janela e do canvas principal, se existir."""
        if GraphiteInter._root:
            GraphiteInter._root.configure(bg=color)
            if hasattr(GraphiteInter, '_main_canvas') and GraphiteInter._main_canvas is not None:
                GraphiteInter._main_canvas.config(bg=color)
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    @staticmethod
    def parseword(from_word, to_word):
     def converter(entrada):
        # Caso 1: substituição simples em string
        if isinstance(entrada, str) and isinstance(from_word, str):
            return entrada.replace(from_word, to_word)

        # Caso 2: substituição por posição em listas
        elif isinstance(entrada, list) and isinstance(from_word, list) and isinstance(to_word, list):
            resultado = entrada[:]
            for i in range(min(len(from_word), len(to_word))):
                for j in range(len(resultado)):
                    if resultado[j] == from_word[i]:
                        resultado[j] = to_word[i]
                        break  # troca só a primeira ocorrência por item
            return resultado

        # Caso 3: substituição de todas as ocorrências na lista
        elif isinstance(entrada, list) and isinstance(from_word, str):
            return [to_word if item == from_word else item for item in entrada]

        else:
            return entrada  # se o tipo não for tratado, retorna original
     return converter


    @staticmethod
    def setbgimage(image_path):
        """Define uma imagem de fundo na janela."""
        
        if GraphiteInter._root:
        
            try:
                image = Image.open(image_path)
                bg_image = ImageTk.PhotoImage(image)
                
                if GraphiteInter._bg_image_label:
                    GraphiteInter._bg_image_label.destroy()  # Remove o antigo label da imagem

                # Criar e posicionar a imagem de fundo
                GraphiteInter._bg_image_label = tk.Label(GraphiteInter._root, image=bg_image)
                GraphiteInter._bg_image_label.image = bg_image  # Mantém uma referência para a imagem
                GraphiteInter._bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)  # Preenche toda a janela
                GraphiteInter._bgi=image_path
            except Exception as e:
                raise RuntimeError(f"Erro ao carregar a imagem: {e}")
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")

    @staticmethod
    def InsertImage(image_id, image_path, position, size=None):
        """
        Insere uma imagem na interface com ID específico.
        
        Parâmetros:
        - image_id: ID único para identificar a imagem
        - image_path: Caminho para o arquivo de imagem
        - position: Tupla (x, y) com a posição da imagem
        - size: Tupla opcional (width, height) para redimensionar a imagem
        """
        if GraphiteInter._root:
            if image_id in GraphiteInter._images:
                raise ValueError(f"Já existe uma imagem com o ID '{image_id}'.")
            
            try:
                # Carregar a imagem usando PIL
                pil_image = Image.open(image_path)
                
                # Redimensionar se o tamanho for especificado
                if size:
                    width, height = size
                    pil_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)
                
                # Converter para PhotoImage do Tkinter
                photo_image = ImageTk.PhotoImage(pil_image)
                
                # Criar um Label para exibir a imagem
                x, y = position
                image_label = tk.Label(GraphiteInter._root, image=photo_image)
                image_label.image = photo_image  # Mantém referência para evitar garbage collection
                image_label.place(x=x, y=y)
                
                # Armazenar a imagem no dicionário
                GraphiteInter._images[image_id] = {
                    'label': image_label,
                    'photo': photo_image,
                    'path': image_path,
                    'position': position,
                    'size': size
                }
                
                print(f"✅ Imagem '{image_id}' inserida com sucesso em {position}")
                
            except Exception as e:
                raise RuntimeError(f"Erro ao carregar a imagem '{image_path}': {e}")
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")

    @staticmethod
    def create_button(text, button_id, command):
     """Cria um botão e adiciona ao estado."""
     if GraphiteInter._root:
        if button_id in GraphiteInter._buttons:
            raise ValueError(f"Já existe um botão com o ID '{button_id}'.")
        
        # Cria o botão
        button = tk.Button(GraphiteInter._root, text=text, command=command)
        GraphiteInter._buttons[button_id] = button
        
        # Inicializa o botão no estado
        GraphiteInter._state.setdefault("buttons", {})
        GraphiteInter._state["buttons"][button_id] = {
            "text": text,
            "bg": button.cget("bg"),
            "fg": button.cget("fg"),
            "position": [0, 0]  # Posição padrão inicial
        }
     else:
        raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")

    @staticmethod
    def buttonposition(button_id, x, y):
     """Define a posição de um botão na interface."""
     if button_id in GraphiteInter._buttons:
        button = GraphiteInter._buttons[button_id]
        button.place(x=x, y=y)  # Altera a posição visual do botão
        GraphiteInter._state["buttons"][button_id]["position"] = [x, y]  # Atualiza a posição no estado interno
     else:
        raise KeyError(f"Botão com ID '{button_id}' não encontrado.")

    @staticmethod
    def inserttext(text_id, text, font_size, position, color):
        """Insere texto em uma posição específica usando Canvas, sem fundo, com ID."""
        if GraphiteInter._root:
            x, y = position
            # Cria um canvas se ainda não existir para textos
            if not hasattr(GraphiteInter, '_main_canvas') or GraphiteInter._main_canvas is None:
                GraphiteInter._main_canvas = tk.Canvas(GraphiteInter._root, width=GraphiteInter._width, height=GraphiteInter._height, highlightthickness=0, bg=GraphiteInter._root.cget("bg"))
                GraphiteInter._main_canvas.place(x=0, y=0, relwidth=1, relheight=1)
            # Adiciona o texto ao canvas
            text_item = GraphiteInter._main_canvas.create_text(x, y, text=text, fill=color, font=("Arial", font_size), anchor="nw")
            # Salva referência ao texto e ao canvas
            GraphiteInter._texts[text_id] = (GraphiteInter._main_canvas, text_item)
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")

    @staticmethod
    def update_text(text_id, new_text):
        """Atualiza o texto de um Label ou item do Canvas, dado o ID."""
        if text_id in GraphiteInter._texts:
            obj = GraphiteInter._texts[text_id]
            if isinstance(obj, tuple) and hasattr(obj[0], 'itemconfig'):
                canvas, item_id = obj
                canvas.itemconfig(item_id, text=new_text)
            else:
                obj.config(text=new_text)
        else:
            raise ValueError(f"O texto com ID '{text_id}' não foi encontrado.")
      
    @staticmethod
    def insertcombo(combo_id, options, position, size=(20, 3)):
     """Cria uma ComboBox (caixa de seleção) e a armazena com seu ID."""
     if GraphiteInter._root:
        if combo_id in GraphiteInter._comboboxes:
            raise ValueError(f"A ComboBox com ID '{combo_id}' já existe.")
        
        # Cria a ComboBox
        combo = ttk.Combobox(GraphiteInter._root, values=options.split(','), width=size[0], height=size[1])
        x, y = position
        combo.place(x=x, y=y)
        
        # Armazena a ComboBox no dicionário com seu ID
        GraphiteInter._comboboxes[combo_id] = combo
     else:
        raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    @staticmethod
    def get_combo_value(combo_id):
     """Retorna o valor selecionado da ComboBox com o ID especificado."""
     if combo_id in GraphiteInter._comboboxes:
        return GraphiteInter._comboboxes[combo_id].get()
     else:
        raise ValueError(f"A ComboBox com ID '{combo_id}' não foi encontrada.")
    @staticmethod
    def update_combo_options(combo_id, new_options):
     """Atualiza as opções de uma ComboBox existente."""
     if combo_id in GraphiteInter._comboboxes:
        combo = GraphiteInter._comboboxes[combo_id]
        combo['values'] = new_options.split(',')
     else:
        raise ValueError(f"A ComboBox com ID '{combo_id}' não foi encontrada.")
    @staticmethod
    def remove_combo(combo_id):
     """Remove uma ComboBox da interface."""
     if combo_id in GraphiteInter._comboboxes:
        GraphiteInter._comboboxes[combo_id].destroy()
        del GraphiteInter._comboboxes[combo_id]
     else:
        raise ValueError(f"A ComboBox com ID '{combo_id}' não foi encontrada.")

    @staticmethod
    def insertslider(slider_id, position, orient="horizontal", sliderlength=20, slider_color="blue", width=10):
        """Cria um slider e o armazena no dicionário com seu ID."""
        if GraphiteInter._root:
            slider = tk.Scale(GraphiteInter._root, orient=orient, sliderlength=sliderlength, length=300, width=width)
            x, y = position
            slider.place(x=x, y=y)
            GraphiteInter._sliders[slider_id] = slider
            # Estilo para o slider (cor)
            slider.config(troughcolor="lightgray", sliderrelief="solid", bg=slider_color)
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    @staticmethod
    def Getslidervalue(slider_id):
        """Obtém o valor atual do slider."""
        if slider_id in GraphiteInter._sliders:
            return GraphiteInter._sliders[slider_id].get()
        else:
            raise ValueError(f"O slider com ID '{slider_id}' não foi encontrado.")
    @staticmethod
    def setmaximum(slider_id, max_value):
        """Define o valor máximo de um slider."""
        if GraphiteInter._root:
            if slider_id in GraphiteInter._sliders:
                GraphiteInter._sliders[slider_id].config(to=max_value)  # Corrigir para 'to' em vez de 'max'
            else:
                raise ValueError(f"O slider com ID '{slider_id}' não foi encontrado.")
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    @staticmethod
    def sliderpos(slider_id, position):
        """Define a posição do slider."""
        if slider_id in GraphiteInter._sliders:
            GraphiteInter._sliders[slider_id].set(position)
        else:
            raise ValueError(f"O slider com ID '{slider_id}' não foi encontrado.")
    @staticmethod
    def removebutton(button_id):
        """Remove um botão da interface."""
        if button_id in GraphiteInter._buttons:
            GraphiteInter._buttons[button_id].destroy()
            del GraphiteInter._buttons[button_id]
    @staticmethod
    def removeslider(Slider_id):
        """Remove um slider da interface."""
        if Slider_id in GraphiteInter._sliders:
            GraphiteInter._sliders[Slider_id].destroy()
            del GraphiteInter._sliders[Slider_id]
    @staticmethod
    def removeText(text_id):
        """Remove um texto da interface (Label ou Canvas)."""
        if text_id in GraphiteInter._texts:
            obj = GraphiteInter._texts[text_id]
            if isinstance(obj, tuple) and hasattr(obj[0], 'delete'):
                canvas, item_id = obj
                canvas.delete(item_id)
            else:
                obj.destroy()
            del GraphiteInter._texts[text_id]
    @staticmethod
    def removeInput(_inputs):
        """Remove um input da interface."""
        if _inputs in GraphiteInter._inputs:
            GraphiteInter._inputs[_inputs].destroy()
            del GraphiteInter._inputs[_inputs]
    @staticmethod
    def removeBgImage():
      """Remove a imagem de fundo da interface."""
      if GraphiteInter._bg_image_label:
          GraphiteInter._bg_image_label.destroy()  # Remove o widget da imagem de fundo
          GraphiteInter._bg_image_label = None
      else:
          raise ValueError("Nenhuma imagem de fundo foi definida.")         
    @staticmethod
    def sliderOrientation(slider_id, orientation):
        """Define a orientação do slider (horizontal ou vertical)."""
        if slider_id in GraphiteInter._sliders:
            GraphiteInter._sliders[slider_id].config(orient=orientation)
        else:
            raise ValueError(f"O slider com ID '{slider_id}' não foi encontrado.")
    @staticmethod
    def sliderthickness(slider_id, thickness):
        """Define a espessura do slider."""
        if GraphiteInter._root:
            if slider_id in GraphiteInter._sliders:
                GraphiteInter._sliders[slider_id].config(width=thickness)  # Corrigir para 'width' em vez de 'thickness'
            else:
                raise ValueError(f"O slider com ID '{slider_id}' não foi encontrado.")
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    @staticmethod
    def slidercolor(slider_id, color):
        """Define a cor do slider."""
        if slider_id in GraphiteInter._sliders:
            GraphiteInter._sliders[slider_id].config(bg=color)
        else:
            raise ValueError(f"O slider com ID '{slider_id}' não foi encontrado.")
    @staticmethod
    def addtextinput(input_id, position, size=(20, 3)):
        """Cria uma caixa de entrada de texto (Text) e a armazena com seu ID."""
        if GraphiteInter._root:
            text = tk.Text(GraphiteInter._root, width=size[0], height=size[1])
            x, y = position
            text.place(x=x, y=y)
            GraphiteInter._inputs[input_id] = text  # Armazena a entrada criada
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    @staticmethod
    def inputposition(input_id, position):
        """Define a posição de um campo de entrada."""
        if input_id in GraphiteInter._inputs:
            entry = GraphiteInter._inputs[input_id]
            x, y = position
            entry.place(x=x, y=y)
        else:
            raise ValueError(f"O campo de entrada com ID '{input_id}' não foi encontrado.")
    @staticmethod
    def inputsize(input_id, size):
        """Define o tamanho do campo de entrada (largura, altura)."""
        if input_id in GraphiteInter._inputs:
            entry = GraphiteInter._inputs[input_id]
            entry.config(width=size[0], height=size[1])
        else:
            raise ValueError(f"O campo de entrada com ID '{input_id}' não foi encontrado.")
    @staticmethod
    def buttonaction(button_id, command):
        """Define a ação de um botão."""
        if GraphiteInter._root:
            if button_id in GraphiteInter._buttons:
                button = GraphiteInter._buttons[button_id]
                button.config(command=command)
            else:
                raise ValueError(f"O botão com ID '{button_id}' não foi encontrado.")
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    
    @staticmethod
    def run():
        """Inicia o loop principal da interface gráfica."""
        if GraphiteInter._root:
            GraphiteInter._root.mainloop()
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
  
    @staticmethod
    def show_notification(message, duration, color, font):
     """
    Exibe uma notificação temporária na janela principal.
    :param message: Texto da notificação.
    :param duration: Duração em milissegundos (default: 3000ms).
    :param color: Cor de fundo da notificação (default: "yellow").
    :param font: Fonte do texto (default: "Arial", 12).
    """
     if GraphiteInter._root:
        notification_label = tk.Label(
            GraphiteInter._root,
            text=message,
            bg=color,
            fg="black",
            font=font,
            relief="solid",
            padx=10,
            pady=5,
        )
        notification_label.place(relx=0.5, rely=0, anchor="n")
        
        # Remove a notificação após o tempo definido
        GraphiteInter._root.after(duration, notification_label.destroy)
     else:
        raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")

    @staticmethod
    def create_tab(tab_id, label):
        """
        Cria uma nova aba com o rótulo especificado.
        :param tab_id: ID único para a aba.
        :param label: Rótulo visível da aba.
        """
        if not hasattr(GraphiteInter, "_notebook"):
            GraphiteInter._notebook = ttk.Notebook(GraphiteInter._root)
            GraphiteInter._notebook.pack(expand=True, fill="both")
            GraphiteInter._tabs = {}
    
        if tab_id in GraphiteInter._tabs:
            raise ValueError(f"Uma aba com o ID '{tab_id}' já existe.")
    
        tab_frame = tk.Frame(GraphiteInter._notebook)
        GraphiteInter._notebook.add(tab_frame, text=label)
        GraphiteInter._tabs[tab_id] = tab_frame
    @staticmethod
    def tabwidget(tab_id, widget):
     """
    Adiciona um widget a uma aba específica.
    :param tab_id: ID da aba onde o widget será adicionado.
    :param widget: Widget a ser adicionado.
    """
     if tab_id in GraphiteInter._tabs:
        widget.pack(in_=GraphiteInter._tabs[tab_id], padx=10, pady=5)
     else:
        raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
    @staticmethod
    def remove_tab(tab_id):
        """
        Remove uma aba existente.
        :param tab_id: ID da aba a ser removida.
        """
        if tab_id in GraphiteInter._tabs:
            tab_frame = GraphiteInter._tabs[tab_id]
            GraphiteInter._notebook.forget(tab_frame)  # Remove a aba do Notebook
            del GraphiteInter._tabs[tab_id]  # Remove a referência
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
    @staticmethod
    def create_tab_button(tab_id, button_id, button_text, buttonposx, buttonposy, action, button_color=None, text_color=None):
        """
        Cria um botão dentro de uma aba específica.
        :param tab_id: ID da aba onde o botão será adicionado.
        :param button_id: ID único para o botão.
        :param button_text: Texto exibido no botão.
        :param buttonposx: Espaçamento horizontal do botão.
        :param buttonposy: Espaçamento vertical do botão.
        :param action: Função que será executada quando o botão for clicado.
        :param button_color: Cor de fundo do botão.
        :param text_color: Cor do texto do botão.
        """
        if tab_id not in GraphiteInter._tabs:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")

        if button_id in GraphiteInter._buttons:
            raise ValueError(f"Já existe um botão com o ID '{button_id}'.")

        # Criar o botão
        button = tk.Button(GraphiteInter._tabs[tab_id], text=button_text, command=action, bg=button_color, fg=text_color)
        button.pack(padx=buttonposx, pady=buttonposy)  # Posiciona o botão dentro da aba

        # Armazenar o botão com seu ID
        GraphiteInter._buttons[button_id] = button

    @staticmethod
    def tabbackground(tab_id, background):
        """
        Define o plano de fundo de uma aba específica.
        :param tab_id: ID da aba onde o plano de fundo será alterado.
        :param background: Cor (ex.: "blue") ou caminho para uma imagem (ex.: "path/to/image.png").
        """
        if tab_id not in GraphiteInter._tabs:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
    
        tab = GraphiteInter._tabs[tab_id]
    
        # Se for uma cor, define como fundo da aba
        if isinstance(background, str) and not background.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            tab.configure(bg=background)
        else:
            # Caso seja uma imagem, carrega e define como fundo
            try:
                image = Image.open(background)
                bg_image = ImageTk.PhotoImage(image)
    
                # Cria um label com a imagem de fundo
                bg_label = tk.Label(tab, image=bg_image)
                bg_label.image = bg_image  # Mantém a referência à imagem
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
                # Coloca o label como fundo da aba
                bg_label.lower()  # Move para trás de outros widgets
            except Exception as e:
                raise RuntimeError(f"Erro ao carregar a imagem: {e}")
            
#acabei de criar abaixo

    @staticmethod
    def insert_text_in_tab(tab_id, text_id, text, font_size, position, color):
     """Insere um texto em uma aba específica com um ID.""" 
     if tab_id in GraphiteInter._tabs:
        x, y = position
        try:
            # Forçar conversão correta de cor hexadecimal
            if color.startswith("#") and len(color) == 7:
                tk_color = color.upper()  # Algumas versões do Tkinter podem exigir maiúsculas
            else:
                tk_color = color.lower()  # Garantir que cores por nome sejam minúsculas
                
            label = tk.Label(GraphiteInter._tabs[tab_id], text=text, fg=tk_color, font=("Arial", font_size))
            label.place(x=x, y=y)
            GraphiteInter._texts[text_id] = label
        except tk.TclError:
            raise ValueError(f"Cor '{color}' inválida. Use um nome de cor válido ou um código hexadecimal no formato #RRGGBB.")
     else:
        raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")

    @staticmethod
    def update_text_in_tab(tab_id, text_id, new_text):
        """Atualiza o texto de um Label dentro de uma aba específica, dado o ID."""
        if tab_id in GraphiteInter._tabs:
            if text_id in GraphiteInter._texts:
                GraphiteInter._texts[text_id].config(text=new_text)
            else:
                raise ValueError(f"O texto com ID '{text_id}' não foi encontrado.")
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
  
    @staticmethod
    def remove_text_from_tab(tab_id, text_id):
        """Remove um texto de uma aba específica."""
        if tab_id in GraphiteInter._tabs:
            if text_id in GraphiteInter._texts:
                GraphiteInter._texts[text_id].destroy()
                del GraphiteInter._texts[text_id]
            else:
                raise ValueError(f"O texto com ID '{text_id}' não foi encontrado na aba '{tab_id}'.")
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
  
    @staticmethod
    def insert_slider_in_tab(tab_id, slider_id, position, orient="horizontal", sliderlength=20, slider_color="blue", width=10):
        """Insere um slider em uma aba específica."""
        if tab_id in GraphiteInter._tabs:
            slider = tk.Scale(GraphiteInter._tabs[tab_id], orient=orient, sliderlength=sliderlength, length=300, width=width)
            x, y = position
            slider.place(x=x, y=y)
            GraphiteInter._sliders[slider_id] = slider
            slider.config(troughcolor="lightgray", sliderrelief="solid", bg=slider_color)
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
  
    @staticmethod
    def remove_slider_from_tab(tab_id, slider_id):
        """Remove um slider de uma aba específica."""
        if tab_id in GraphiteInter._tabs:
            if slider_id in GraphiteInter._sliders:
                GraphiteInter._sliders[slider_id].destroy()
                del GraphiteInter._sliders[slider_id]
            else:
                raise ValueError(f"O slider com ID '{slider_id}' não foi encontrado na aba '{tab_id}'.")
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
  
    @staticmethod
    def insert_combo_in_tab(tab_id, combo_id, options, position, size=(20, 3)):
        """Insere uma ComboBox em uma aba específica."""
        if tab_id in GraphiteInter._tabs:
            if combo_id in GraphiteInter._comboboxes:
                raise ValueError(f"A ComboBox com ID '{combo_id}' já existe.")
            combo = ttk.Combobox(GraphiteInter._tabs[tab_id], values=options.split(','), width=size[0], height=size[1])
            x, y = position
            combo.place(x=x, y=y)
            GraphiteInter._comboboxes[combo_id] = combo
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
  
    @staticmethod
    def remove_combo_from_tab(tab_id, combo_id):
        """Remove uma ComboBox de uma aba específica."""
        if tab_id in GraphiteInter._tabs:
            if combo_id in GraphiteInter._comboboxes:
                GraphiteInter._comboboxes[combo_id].destroy()
                del GraphiteInter._comboboxes[combo_id]
            else:
                raise ValueError(f"A ComboBox com ID '{combo_id}' não foi encontrada na aba '{tab_id}'.")
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
  
    @staticmethod
    def insert_input_in_tab(tab_id, input_id, position, size=(20, 3)):
        """Insere uma caixa de entrada de texto (Input) em uma aba específica."""
        if tab_id in GraphiteInter._tabs:
            input_field = tk.Text(GraphiteInter._tabs[tab_id], width=size[0], height=size[1])
            x, y = position
            input_field.place(x=x, y=y)
            GraphiteInter._inputs[input_id] = input_field  # Armazena o input com o ID especificado
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
  
    @staticmethod
    def remove_input_from_tab(tab_id, input_id):
        """Remove uma caixa de entrada de texto de uma aba específica."""
        if tab_id in GraphiteInter._tabs:
            if input_id in GraphiteInter._inputs:
                GraphiteInter._inputs[input_id].destroy()
                del GraphiteInter._inputs[input_id]
            else:
                raise ValueError(f"O input com ID '{input_id}' não foi encontrado na aba '{tab_id}'.")
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
    widgets = {}
    scheduled_events = {}

    @staticmethod
    def schedule_event(event_id, action, delay_ms):
        """Agenda a execução de uma função após um tempo definido."""
        def delayed_execution():
            time.sleep(delay_ms / 1000)
            action()
        
        thread = threading.Thread(target=delayed_execution)
        thread.start()
        GraphiteInter.scheduled_events[event_id] = thread
    
    
    
    @staticmethod
    def create_form(form_id, fields, x=0, y=0, buttonaction=None, width=None, height=None):
     """Cria um formulário com base em um dicionário de campos e permite definir a posição e dimensões."""
     form_frame = Frame()
 
     if width or height:
         form_frame.config(width=width, height=height)
 
     GraphiteInter.widgets[form_id] = form_frame
 
     for i, (label_text, field_type) in enumerate(fields.items()):
         label = Label(form_frame, text=label_text)
         label.grid(row=i, column=0, padx=5, pady=5)
 
         entry = None
 
         if field_type == "text":
             entry = Entry(form_frame)
         elif field_type == "password":
             entry = Entry(form_frame, show="*")
         elif field_type == "email":
             entry = Entry(form_frame)
         elif field_type == "number":
             entry = Entry(
                 form_frame,
                 validate="key",
                 validatecommand=(form_frame.register(lambda char: char.isdigit()), "%P"),
             )
         elif field_type == "date":
             entry = Entry(form_frame)
         elif field_type == "checkbox":
             var = IntVar()
             entry = Checkbutton(form_frame, text=label_text, variable=var)
             GraphiteInter.widgets[f"{form_id}_{label_text}_var"] = var
         elif field_type == "radio":
             var = IntVar()
             entry = Frame(form_frame)
             options = ["Option 1", "Option 2", "Option 3"]
             for j, option in enumerate(options):
                 radio = Radiobutton(entry, text=option, variable=var, value=j)
                 radio.grid(row=j, column=0)
             GraphiteInter.widgets[f"{form_id}_{label_text}_var"] = var
         elif field_type == "textarea":
             entry = Text(form_frame, height=4, width=30)
         elif field_type == "file":
             entry = Entry(form_frame)
         elif field_type == "hidden":
             entry = Entry(form_frame, show="")
         elif field_type.lower() == "button":
             entry = Button(form_frame, text=label_text, command=buttonaction or (lambda: print("Botão pressionado!")))
 
         if entry:
             entry.grid(row=i, column=1, padx=5, pady=5)
             GraphiteInter.widgets[f"{form_id}_{label_text}"] = entry
 
     form_frame.place(x=x, y=y)

    @staticmethod
    def get_form_data(form_id):
        """Obtém os dados preenchidos no formulário com base no form_id."""
        form_data = {}
        
        for widget_key, widget in GraphiteInter.widgets.items():
            if widget_key.startswith(f"{form_id}_"):
                label_text = widget_key.replace(f"{form_id}_", "")
                if isinstance(widget, Entry):
                    form_data[label_text] = widget.get()
                elif isinstance(widget, Text):
                    form_data[label_text] = widget.get("1.0", "end-1c")
                elif isinstance(widget, Checkbutton):
                    var = GraphiteInter.widgets.get(f"{form_id}_{label_text}_var")
                    form_data[label_text] = var.get() if var else None
                elif isinstance(widget, Frame):
                    var = GraphiteInter.widgets.get(f"{form_id}_{label_text}_var")
                    form_data[label_text] = var.get() if var else None
        
        return form_data
    @staticmethod
    def save_in_file(file_name, form_data):
        """Salva os dados do formulário em um arquivo, adicionando ao final do arquivo."""
        try:
            with open(file_name, 'a') as file:  # Modo 'a' para adicionar ao final do arquivo
                file.write(",")  # Linha de separação entre formulários
                for key, value in form_data.items():
                    file.write(f"{key}: {value}\n")
                file.write("\n")  # Adiciona uma linha em branco ao final
            print(f"Dados salvos no arquivo: {file_name}")
        except Exception as e:
            print(f"Erro ao salvar dados no arquivo: {e}")

    @staticmethod
    def read_file(file_name):
     """Lê o conteúdo de um arquivo e retorna como uma string."""
     try:
        with open(file_name, 'r') as file:
            content = file.read()  # Lê todo o conteúdo do arquivo
        return content
     except FileNotFoundError:
        return f"Arquivo '{file_name}' não encontrado."
     except Exception as e:
        return f"Erro ao ler o arquivo: {e}"
     

    @staticmethod
    def compare(item1, item2):
     """Compara dois valores e retorna o resultado da comparação."""
     if item1 == item2:
        return True  # Os valores são iguais
     else:
        return False  # Os valores são diferentes

    @staticmethod
    def load_addon(json_path):
     """Carrega um addon em formato JSON e cria elementos dinamicamente."""
     try:
         with open(json_path, "r", encoding="utf-8") as f:
             addon_data = json.load(f)
 
         elements = addon_data.get("elements", [])
         actions = addon_data.get("actions", [])
 
         # Criar um dicionário de ações baseadas em arquivos de código
         action_functions = {action['name']: action for action in actions}
 
         # Função para criar ação de execução
         def create_action(action_name):
             def action():
                 # Se for uma função declarada no JSON como type: Function
                 if action_name in GraphiteInter._Functions:
                     for act in GraphiteInter._Functions[action_name]:
                         tipo = act.get("action_type")
                         if tipo == "create_window":
                             GraphiteInter.create_window(act["name"])
                         elif tipo == "setbackground":
                             GraphiteInter.setbackground(act["color"])
                         # (adicione aqui outros tipos de ações conforme precisar)
                 # Se for uma função associada a um script Python externo
                 elif action_name in action_functions:
                     action_func = action_functions[action_name]
                     code_file = action_func['parameters'][0].get('code_file')
                     function_name = action_func['parameters'][0].get('functionname')
                     if code_file:
                         try:
                             with open(code_file, 'r', encoding='utf-8') as f:
                                 code = f.read()  # Lê o código do arquivo
                             exec(code, globals())  # Executa o código lido
 
                             # Chama a função especificada, se encontrada
                             if function_name:
                                 if function_name in globals():
                                     func = globals()[function_name]
                                     if callable(func):
                                         func()  # Chama a função específica
                                     else:
                                         print(f"Erro: '{function_name}' não é uma função válida.")
                                 else:
                                     print(f"Erro: Função '{function_name}' não encontrada no arquivo.")
                         except FileNotFoundError:
                             print(f"Erro: Arquivo '{code_file}' não encontrado.")
                         except Exception as e:
                             print(f"Erro ao executar o código do arquivo '{code_file}': {e}")
                     else:
                         print(f"Ação {action_name} não possui um arquivo de código válido.")
                 else:
                     print(f"Ação {action_name} não encontrada.")
             return action
 
         # Processar os elementos
         for element in elements:
             element_type = element.get("type")
 
             if element_type == "Function":
                 function_name = element.get("name")
                 action_list = element.get("actions", [])
                 GraphiteInter._Functions[function_name] = action_list
 
             elif element_type == "button":
                 button_id = element.get("id")
                 button_text = element.get("text", "Botão")
                 position = element.get("position", [0, 0])
                 action_names = element.get("action", [])
 
                 if button_id in GraphiteInter.created_buttons:
                     print(f"Erro: Já existe um botão com o ID '{button_id}'.")
                     continue
 
                 for action_name in action_names:
                     action_func = create_action(action_name)
                     GraphiteInter.create_button(button_text, button_id, action_func)
                     GraphiteInter.buttonposition(button_id, position[0], position[1])
 
             elif element_type == "text":
                 text_id = element.get("id")
                 text_content = element.get("text", "Texto Padrão")
                 font_size = element.get("font_size", 12)
                 color = element.get("color", "black")
                 position = element.get("position", [0, 0])
                 GraphiteInter.inserttext(text_id, text_content, font_size, position, color)
 
             elif element_type == "combobox":
                 combo_id = element.get("id")
                 options = element.get("options", "").split(",")
                 position = element.get("position", [0, 0])
                 GraphiteInter.insertcombo(combo_id, ",".join(options), position)
 
             elif element_type == "slider":
                 slider_id = element.get("id")
                 position = element.get("position", [0, 0])
                 max_value = element.get("max", 100)
                 GraphiteInter.insertslider(slider_id, position)
                 GraphiteInter.setmaximum(slider_id, max_value)
 
             elif element_type == "input":
                 input_id = element.get("id")
                 position = element.get("position", [0, 0])
                 GraphiteInter.addtextinput(input_id, position)
 
             elif element_type == "background":
                 color = element.get("color")
                 image = element.get("image")
                 if image:
                     GraphiteInter.setbgimage(image)
                 elif color:
                     GraphiteInter.setbackground(color)
 
             elif element_type == "tab":
                 Tab_id = element.get("id")
                 Tab_Text = element.get("text")
                 GraphiteInter.create_tab(Tab_id, Tab_Text)
 
             elif element_type == "xmlcontainer":
                 XML = element.get("XMLFile")
                 XSLT = element.get("XSLTFile")
                 if XML and XSLT:
                     if os.path.exists(XML) and os.path.exists(XSLT):
                         GraphiteInter.CreateXMLBasedContainer(XML, XSLT)
                     else:
                         print("Erro: Um ou ambos os arquivos XML/XSLT não foram encontrados.")
                 else:
                     print("Erro: Caminho do arquivo XML ou XSLT não fornecido.")
 
             elif element_type == "container":
                 HTML = element.get("HTMLFile")
                 if HTML:
                     if os.path.exists(HTML):
                         GraphiteInter.createHtmlContainer(HTML)
                     else:
                         print("Erro: HTML não foi encontrado.")
                 else:
                     print("Erro: Caminho do HTML não fornecido.")
 
             elif element_type == "tbutton":
                 Tid = element.get("tabid")
                 BID = element.get("bid")
                 BTEXT = element.get("btext")
                 XPOS = element.get("posx")
                 YPOS = element.get("posy")
                 ACTION = element.get("action")
                 BCOLOR = element.get("bcolor")
                 BTEXTCOLOR = element.get("btextcolor")
                 GraphiteInter.create_tab_button(Tid, BID, BTEXT, XPOS, YPOS, ACTION, BCOLOR, BTEXTCOLOR)
 
             elif element_type == "ttext":
                 TABID = element.get("tabid")
                 TEXTID = element.get("textid")
                 TEXT = element.get("text")
                 FONTSIZE = element.get("fontsize")
                 POSITION = element.get("position")
                 COLOR = element.get("color")
                 GraphiteInter.insert_text_in_tab(TABID, TEXTID, TEXT, FONTSIZE, POSITION, COLOR)
 
             elif element_type == "tbackground":
                 TAB = element.get("tabid")
                 BG = element.get("tabbackground")
                 GraphiteInter.tabbackground(tab_id=TAB, background=BG)
 
             elif element_type == "ComboTab":
                 TABID = element.get("tabid")
                 COMBOID = element.get("comboid")
                 OPTIONS = element.get("options")
                 POSITION = element.get("position")
                 SIZE = element.get("size")
                 GraphiteInter.insert_combo_in_tab(TABID, COMBOID, OPTIONS, POSITION, SIZE)
 
             elif element_type == "InputTab":
                 TABID = element.get("tabid")
                 INPUTID = element.get("inputid")
                 POSITION = element.get("position")
                 SIZE = element.get("size")
                 GraphiteInter.insert_input_in_tab(TABID, INPUTID, POSITION, SIZE)
 
             elif element_type == "SliderTab":
                 TABID = element.get("tabid")
                 SLIDERID = element.get("sliderid")
                 POSITION = element.get("position")
                 ORIENTATION = element.get("orientation")
                 LENGTH = element.get("length")
                 COLOR = element.get("color")
                 WIDTH = element.get("width")
                 GraphiteInter.insert_slider_in_tab(TABID, SLIDERID, POSITION, ORIENTATION, LENGTH, COLOR, WIDTH)
 
         print(f"✅ Addon '{json_path}' carregado com sucesso!")
 
     except Exception as e:
         print(f"❌ Erro ao carregar o addon: {e}")



    @staticmethod
    def execute_function(function_name):
        """Executa uma função carregada do JSON."""
        if function_name in GraphiteInter._Functions:
            actions = GraphiteInter._Functions[function_name]
            for action in actions:
                if isinstance(action, dict):
                    action_type = action.get("action_type")

                    if action_type == "print":
                        print(action.get("message", "[Mensagem Vazia]"))
                    elif action_type == "show_message":
                        messagebox.showinfo(action.get("title", "Info"), action.get("message", "[Mensagem Vazia]"))
                    elif action_type =="compare":
                        COMPARATOR1=action.get("comparator1")
                        COMPARATOR2=action.get("comparator2")
                        GraphiteInter.compare(COMPARATOR1,COMPARATOR2)
                    elif action_type =="remove_form":
                     FID=action.get("FormId")
                     GraphiteInter.remove_form(FID)

                    elif action_type =="separate_graphite":
                     ITEM=action.get("Separate")
                     SEPARATOR=action.get("Separator")
                     GraphiteInter.separate_graphite(ITEM,SEPARATOR)

                    elif action_type =="create_menu":
                     MENUITEMS=action.get("items")
                     GraphiteInter.create_menu(MENUITEMS)

                    elif action_type =="Show_External_Notification":
                     TITLE=action.get("Title")
                     MESSAGE=action.get("Message")
                     TYPE=action.get("Type")
                     GraphiteInter.Show_External_Notification(TITLE,MESSAGE,TYPE)

                    elif action_type =="enable_drag":
                     ITEMID=action.get("id")
                     GraphiteInter.enable_drag(ITEMID)

                    elif action_type=="CreateXMLBasedContainer":
                     XML=action.get("xml_path")
                     XSLT=action.get("xslt_path")
                     GraphiteInter.CreateXMLBasedContainer(XML,XSLT)

                    elif action_type=="createHtmlContainer":
                     HTMLFILE=action.get("html_file")
                     GraphiteInter.createHtmlContainer(HTMLFILE)
                     
                    elif action_type=="removeHtmlContainer":
                     GraphiteInter.removeHtmlContainer()

                    elif action_type=="load_webpage":
                     URL=action.get("url")
                     GraphiteInter.load_webpage(URL)

                    elif action_type=="create_tab_button":
                     TID=action.get("tab_id")
                     BID=action.get("button_id")
                     BTEXT=action.get("text")
                     BPOSX=action.get("posx")
                     BPOSY=action.get("posy")
                     BCOLOR=action.get("button_color")
                     TEXTCOLOR=action.get("text_color")
                     GraphiteInter.create_tab_button(TID,BID,BTEXT,BPOSX,BPOSY,None,BCOLOR,TEXTCOLOR)
                   
                    elif action_type=="read_file":
                     FNAME=action.get("fileName")
                     GraphiteInter.read_file(FNAME)

                    elif action_type=="create_form":
                     ID=action.get("id")
                     FIELDS=action.get("fields")
                     BACTION=action.get("button action")
                     X=action.get("posx")
                     Y=action.get("posy")
                     GraphiteInter.create_form(ID,FIELDS,X,Y,BACTION)

                    elif action_type=="schedule_event":
                     ACTION=action.get("action")
                     EVEID=action.get("event_id")
                     DELAY=action.get("Delay")
                     GraphiteInter.schedule_event(EVEID,ACTION,DELAY)
                    elif action_type=="remove_input_from_tab":
                     TABID=action.get("tab_id")
                     INPUTID=action.get("input_id")
                     GraphiteInter.remove_input_from_tab(TABID,INPUTID)
                    elif action_type=="insert_input_in_tab":
                     TABID=action.get("tab_id")
                     INPUTID=action.get("input_id")
                     POSITION=action.get("position")
                     SIZE=action.get("size")
                     GraphiteInter.insert_input_in_tab(TABID,INPUTID,POSITION,SIZE)
                    elif action_type=="remove_combo_from_tab":
                     TABID=action.get("tab_id")
                     COMBOID=action.get("combo_id")
                     GraphiteInter.remove_combo_from_tab(TABID,COMBOID)
                    elif action_type=="insert_combo_in_tab":
                     TABID=action.get("tab_id")
                     COMBOID=action.get("combo_id")
                     OPTIONS=action.get("options")
                     GraphiteInter.insert_combo_in_tab(TABID,COMBOID,OPTIONS)
                    elif action_type=="remove_slider_from_tab":
                     TABID=action.get("tab_id")
                     SLIDERID=action.get("slider_id")
                     GraphiteInter.remove_slider_from_tab(TABID,SLIDERID)

                    elif action_type=="insert_slider_in_tab":
                        FONTSIZE=action.get("fontsize")
                        POSITION=action.get("position")
                        TEXTID=action.get("text_id")
                        TABID=action.get("tab_id")
                        COLOR=action.get("color")
                        TEXT=action.get("text")
                        GraphiteInter.insert_text_in_tab(TABID,TEXTID,TEXT,FONTSIZE,POSITION,COLOR)

                    elif action_type=="insert_text_in_tab":
                      TABID=action.get("id")
                      TEXTID=action.get("text id")
                      TEXT=action.get("text")
                      FONTSIZE=action.get("fontsize")
                      POSITION=action.get("position")
                      COLOR=action.get("color")
                      GraphiteInter.insert_text_in_tab(TABID,TEXTID,TEXT,FONTSIZE,POSITION,COLOR)

                    elif action_type=="tabbackground":
                     TAB=action.get("id")
                     BG=action.get("color")
                     GraphiteInter.tabbackground(tab_id=TAB , background=BG)

                    elif action_type=="remove_tab":
                     TABID=action.get("id")
                     GraphiteInter.remove_tab(TABID)
                     
                    elif action_type == "show_notification":
                         GraphiteInter.show_notification(action.get("message", "Notificação"))

                    elif action_type == "addtextinput":
                        GraphiteInter.addtextinput(action.get("input_id"), (action.get("x", 50), action.get("y", 50)))

                    elif action_type == "slidercolor":
                        GraphiteInter.slidercolor(action.get("slider_id"), action.get("color", "blue"))

                    elif action_type == "sliderthickness":
                        GraphiteInter.sliderthickness(action.get("slider_id"), action.get("thickness", 10))

                    elif action_type == "sliderOrientation":
                        GraphiteInter.sliderOrientation(action.get("slider_id"), action.get("orientation"))

                    elif action_type == "removeBgImage":
                        GraphiteInter.removeBgImage()

                    elif action_type == "removeInput":
                        GraphiteInter.removeInput(action.get("input_id"))

                    elif action_type == "removeText":
                        GraphiteInter.removeText(action.get("text_id"))

                    elif action_type == "removeslider":
                        GraphiteInter.removeslider(action.get("slider_id"))
                        
                    elif action_type == "removebutton":
                        GraphiteInter.removebutton(action.get("button_id"))

                    elif action_type == "setmaximum":
                        GraphiteInter.setmaximum(action.get("slider_id"), action.get("max_value", 100))

                    elif action_type == "Getslidervalue":
                        GraphiteInter.Getslidervalue(action.get("slider_id"))

                    elif action_type == "insertslider":
                        GraphiteInter.insertslider(action.get("slider_id"), (action.get("x", 50), action.get("y", 50)))

                    elif action_type == "remove_combo":
                        GraphiteInter.remove_combo(action.get("combo_id"))

                    elif action_type == "get_combo_value":
                        GraphiteInter.get_combo_value(action.get("id"))
                    elif action_type == "insertcombo":
                        GraphiteInter.insertcombo(action.get("combo_id"), action.get("options", ""), (action.get("x", 50), action.get("y", 50)))

                    elif action_type=="inserttext":
                     TID=action.get("id")
                     TEXT=action.get("text")
                     FONTSIZE=action.get("fontsize")
                     POS=action.get("position")
                     COLOR=action.get("color")
                     GraphiteInter.inserttext(TID,TEXT,FONTSIZE,POS,COLOR)

                    elif action_type=="buttonposition":
                     BID=action.get("id")
                     X=action.get("posx")
                     Y=action.get("posy")
                     GraphiteInter.buttonposition(BID,X,Y)

                    elif action_type=="create_button":
                     TEXT=action.get("text") 
                     BID=action.get("id")
                     GraphiteInter.create_button(TEXT,BID,None)

                    elif action_type=="setbgimage":
                     PATH=action.get("path")
                     GraphiteInter.setbgimage(PATH)

                    elif action_type=="setbackground":
                     COLOR=action.get("color")
                     GraphiteInter.setbackground(COLOR)

                    elif action_type=="setdimensions":
                     WIDTH=action.get("width")
                     HEIGHT=action.get("height")
                     GraphiteInter.setdimensions(WIDTH,HEIGHT)

                    elif action_type=="create_window":
                     TITLE=action.get("title")
                     GraphiteInter.create_window(TITLE)
                    else:
                        print(f"⚠️ Tipo de ação desconhecido: {action_type}")
        else:
            print(f"⚠️ Função '{function_name}' não encontrada.")

    @staticmethod
    def remove_form(form_id):
     """Remove um formulário da interface gráfica."""
     form_frame = GraphiteInter.widgets.get(form_id)
     if form_frame:
        form_frame.destroy()  # Remove o frame do formulário
        del GraphiteInter.widgets[form_id]  # Remove da lista de widgets
        print(f"✅ Formulário '{form_id}' removido com sucesso!")
     else:
        print(f"⚠️ Formulário '{form_id}' não encontrado.")
    @staticmethod
    # Função para separar uma string ou lista com base em um separador
    def separate_graphite(Separate, separador):
    # Verifica se o 'o_que' é uma string e usa o método split para separar
     if isinstance(Separate, str):
        return Separate.split(separador)
    
    # Se for uma lista, tenta separar com base no separador fornecido
     elif isinstance(Separate, list):
        separated_list = []
        current_group = []
        for item in Separate:
            if item == separador:
                # Quando encontrar o separador, salva o grupo atual
                if current_group:
                    separated_list.append(current_group)
                    current_group = []
            else:
                current_group.append(item)
        
        # Adiciona o último grupo se houver algum
        if current_group:
            separated_list.append(current_group)
        
        return separated_list

     else:
        raise ValueError("O parâmetro 'o_que' deve ser uma string ou lista.")
     
    @staticmethod
    def create_menu(menu_items):
        """Cria um menu suspenso."""
        if not GraphiteInter._root:
            raise RuntimeError("A janela principal ainda não foi criada.")
        menu_bar = tk.Menu(GraphiteInter._root)
        for menu_name, commands in menu_items.items():
            menu = tk.Menu(menu_bar, tearoff=0)
            for item, action in commands.items():
                menu.add_command(label=item, command=action)
            menu_bar.add_cascade(label=menu_name, menu=menu)
        GraphiteInter._root.config(menu=menu_bar)

    @staticmethod
    def Show_External_Notification(title, message, alert_type="info"):
        """Exibe um pop-up de alerta."""
        if alert_type == "info":
            messagebox.showinfo(title, message)
        elif alert_type == "warn":
            messagebox.showwarning(title, message)
        elif alert_type == "err":
            messagebox.showerror(title, message)

    @staticmethod
    def enable_drag(itemid):
        """Permite arrastar e soltar qualquer widget baseado no itemid."""
        widget = None
        
        # Verifica se o itemid corresponde a algum tipo de widget
        if itemid in GraphiteInter._buttons:
            widget = GraphiteInter._buttons[itemid]
        elif itemid in GraphiteInter._texts:
            widget = GraphiteInter._texts[itemid]
        elif itemid in GraphiteInter._comboboxes:
            widget = GraphiteInter._comboboxes[itemid]
        elif itemid in GraphiteInter._sliders:
            widget = GraphiteInter._sliders[itemid]
        elif itemid in GraphiteInter._inputs:
            widget = GraphiteInter._inputs[itemid]

        if widget is None:
            raise ValueError(f"Widget com ID '{itemid}' não encontrado.")
        
        # Função de arrasto
        def on_drag(event):
            widget.place(x=event.x_root - GraphiteInter._root.winfo_x(), 
                         y=event.y_root - GraphiteInter._root.winfo_y())

        # Liga o evento de arrastar
        widget.bind("<B1-Motion>", on_drag)


    @staticmethod
    def CreateXMLBasedContainer(xml, xslt):
        """
        Função que cria um container HTML dentro de um programa Tkinter,
        aplicando uma transformação XSLT no XML e exibindo o resultado.
        
        Parâmetros:
        xml (str): Caminho para o arquivo XML.
        xslt (str): Caminho para o arquivo XSLT.
        """
        # Carregar XML e XSLT
        try:
            xml_tree = etree.parse(xml)
            xslt_tree = etree.parse(xslt)

            # Aplicar a transformação XSLT
            transform = etree.XSLT(xslt_tree)
            result = transform(xml_tree)  # O resultado da transformação é o HTML gerado

            # Converter o resultado para string
            result_html = etree.tostring(result, pretty_print=True, encoding="UTF-8").decode()

            # Criar um arquivo temporário para armazenar o HTML
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_html:
                temp_html.write(result_html.encode("utf-8"))
                temp_html_path = temp_html.name  # Caminho do arquivo temporário

            # Criar o container HTML dentro da janela principal
            GraphiteInter.createHtmlContainer(temp_html_path)
            print(f"XML baseado no HTML carregado a partir de {temp_html_path}.")
        except Exception as e:
            print(f"Erro ao tentar criar o container XML baseado: {e}")

    @staticmethod
    def createHtmlContainer(HTMLFile):
        """
        Cria um container HTML dentro da janela principal criada com create_window.
        
        Parâmetro:
        HTMLFile (str): Caminho do arquivo HTML a ser carregado.
        """
        if GraphiteInter._root is None:
            print("Erro: A janela principal não foi criada. Chame 'create_window' primeiro.")
            return
        
        try:
            # Se já existir um frame HTML, remova-o primeiro
            if GraphiteInter._html_frame is not None:
                GraphiteInter._html_frame.destroy()
                print("Container HTML existente removido.")

            # Criar um novo frame HTML usando tkinterweb
            GraphiteInter._html_frame = HtmlFrame(GraphiteInter._root, horizontal_scrollbar=True)
            GraphiteInter._html_frame.pack(fill="both", expand=True)

            # Carregar o conteúdo do arquivo HTML no frame
            GraphiteInter._html_frame.load_file(HTMLFile)

            # Atualizar a janela para exibir o conteúdo HTML
            GraphiteInter._root.update_idletasks()
            print(f"Container HTML carregado a partir de {HTMLFile}.")
        except Exception as e:
            print(f"Erro ao tentar criar o container HTML: {e}")

    @staticmethod
    def removeHtmlContainer():
        """
        Remove o container HTML (HtmlFrame) da janela principal.
        """
        if GraphiteInter._html_frame is not None:
            try:
                # Destrói o HtmlFrame (remover o container da interface)
                GraphiteInter._html_frame.destroy()
                GraphiteInter._html_frame = None  # Limpa a variável
                GraphiteInter._root.update_idletasks()  # Atualiza a interface
                print("Container HTML removido com sucesso.")
            except Exception as e:
                print(f"Erro ao tentar remover o container HTML: {e}")
        else:
            print("Nenhum container HTML encontrado para remover.")

    @staticmethod
    def load_webpage(url):
        """Exibe um site e processa JS externamente."""
        if GraphiteInter._root is None:
            print("Erro: A janela principal não foi criada. Chame 'create_window' primeiro.")
            return
        
        try:
            if GraphiteInter._html_frame is not None:
                GraphiteInter._html_frame.destroy()
                print("Container HTML existente removido.")

            GraphiteInter._html_frame = HtmlFrame(GraphiteInter._root, horizontal_scrollbar=True)
            GraphiteInter._html_frame.pack(fill="both", expand=True)

            # Capturar HTML da página para buscar scripts JS
            response = requests.get(url)
            response.raise_for_status()
            html_content = response.text

            # Buscar scripts externos no HTML
            js_files = re.findall(r'<script src="(.*?)"', html_content)
            for js_file in js_files:
                js_url = url + "/" + js_file if not js_file.startswith("http") else js_file
                print(f"Processando JavaScript externo: {js_url}")
                GraphiteInter.fetch_and_execute_js(js_url)

            # Carregar a página no frame
            GraphiteInter._html_frame.load_url(url)
            GraphiteInter._root.update_idletasks()
            print(f"Site carregado: {url}")

        except Exception as e:
            print(f"Erro ao tentar carregar o site: {e}")
    @staticmethod
    def icon_dimensions(button_id, x, y):
        """
        Redimensiona o ícone de um botão.
        :param button_id: ID do botão que terá o ícone redimensionado.
        :param x: Largura desejada.
        :param y: Altura desejada.
        """
        if button_id in GraphiteInter._buttons and button_id in GraphiteInter._icons:
            button = GraphiteInter._buttons[button_id]
            icon = GraphiteInter._icons[button_id].subsample(
                GraphiteInter._icons[button_id].width() // x,
                GraphiteInter._icons[button_id].height() // y
            )
            button.config(image=icon)
            button.image = icon  # Mantém referência para evitar garbage collection
        else:
            raise ValueError(f"Botão ou ícone não encontrado para o ID '{button_id}'.")
    @staticmethod
    def add_icon_to_button(button_id, icon_path):
        """
        Adiciona um ícone a um botão pelo seu ID.
        :param button_id: ID do botão ao qual o ícone será adicionado.
        :param icon_path: Caminho do arquivo da imagem do ícone.
        """
        if button_id in GraphiteInter._buttons:
            button = GraphiteInter._buttons[button_id]
            icon = PhotoImage(file=icon_path)
            GraphiteInter._icons[button_id] = icon  # Salva o ícone original
            button.config(image=icon, compound="left")  # Ícone à esquerda do texto
            button.image = icon  # Mantém referência para evitar garbage collection
        else:
            raise ValueError(f"O botão com ID '{button_id}' não foi encontrado.")
        
    _loadings = {}

    @staticmethod
    def _get_root():
        """Obtém a referência da janela principal automaticamente."""
        if GraphiteInter._root is None:
            GraphiteInter._root = tk._default_root
            if GraphiteInter._root is None:
                GraphiteInter._root = tk.Tk()  # Cria root se não existir
        return GraphiteInter._root

    @staticmethod
    def _get_root():
        """Obtém a referência da janela principal automaticamente."""
        if GraphiteInter._root is None:
            GraphiteInter._root = tk._default_root
            if GraphiteInter._root is None:
                GraphiteInter._root = tk.Tk()  # Cria root se não existir
        return GraphiteInter._root

    @staticmethod
    def insertLoading(loadingId, pathtogif, speed=100, position=(0, 0)):
        """
        Insere um GIF animado de loading na tela.
        :param loadingId: ID do loading.
        :param pathtogif: Caminho do GIF.
        :param speed: Velocidade da animação (quanto menor, mais lento).
        :param position: Posição (x, y) do GIF na tela.
        """
        root = GraphiteInter._get_root()

        try:
            # Abrindo o GIF usando PIL
            gif = Image.open(pathtogif)
            frames = []
            
            try:
                while True:
                    frame = gif.copy()
                    frames.append(ImageTk.PhotoImage(frame))
                    gif.seek(len(frames))  # Avança para o próximo frame
            except EOFError:
                pass  # Quando chega ao fim dos frames

            if not frames:
                raise ValueError("Falha ao carregar frames do GIF.")

            # Criando Label para exibir o GIF
            label = Label(root)
            label.place(x=position[0], y=position[1])  # Define a posição

            # Armazena os dados do loading
            GraphiteInter._loadings[loadingId] = {
                "label": label,
                "frames": frames,
                "current_frame": 0,
                "speed": speed  # Armazena a velocidade
            }

            # Função para animar o GIF
            def update_frame():
                if loadingId in GraphiteInter._loadings:
                    data = GraphiteInter._loadings[loadingId]
                    frame_index = data["current_frame"]
                    data["label"].config(image=data["frames"][frame_index])
                    data["current_frame"] = (frame_index + 1) % len(data["frames"])

                    # Inverte a lógica: valores menores de speed resultam em mais lentidão
                    delay = 1000 // (data["speed"])  # Ajuste para que valores menores de speed sejam mais lentos
                    root.after(delay, update_frame)  # Atualiza conforme a nova velocidade

            update_frame()  # Inicia a animação
        except Exception as e:
            print(f"Erro ao carregar GIF: {e}")

    @staticmethod
    def removeLoading(loadingId):
        """
        Remove um loading animado.
        :param loadingId: ID do loading a ser removido.
        """
        if loadingId in GraphiteInter._loadings:
            GraphiteInter._loadings[loadingId]["label"].destroy()
            del GraphiteInter._loadings[loadingId]
        else:
            print(f"Loading '{loadingId}' não encontrado.")

    @staticmethod
    def changetodefault(json_path):
        """Destrói todos os elementos da interface e recria a partir do JSON."""
        if not GraphiteInter._root:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                default_state = json.load(f)

            # Remover todos os elementos atuais
            for widget_dict in [GraphiteInter._buttons, GraphiteInter._texts, GraphiteInter._comboboxes, 
                                GraphiteInter._sliders, GraphiteInter._inputs, GraphiteInter._tabs]:
                for widget_id in list(widget_dict.keys()):
                    widget_dict[widget_id].destroy()
                widget_dict.clear()

            if GraphiteInter._bg_image_label:
                GraphiteInter._bg_image_label.destroy()
                GraphiteInter._bg_image_label = None

            # Restaurar estado default
            GraphiteInter.setdimensions(default_state.get("width", 800), default_state.get("height", 600))

            if "background" in default_state:
                GraphiteInter.setbackground(default_state["background"])

            if "bg_image" in default_state:
                GraphiteInter.setbgimage(default_state["bg_image"])

            for button in default_state.get("buttons", []):
                GraphiteInter.create_button(button["text"], button["id"], None)
                GraphiteInter.buttonposition(button["id"], *button["position"])

            for text in default_state.get("texts", []):
                GraphiteInter.inserttext(text["id"], text["text"], text["font_size"], text["position"], text["color"])

            for combo in default_state.get("comboboxes", []):
                GraphiteInter.insertcombo(combo["id"], ",".join(combo["options"]), combo["position"])

            for slider in default_state.get("sliders", []):
                GraphiteInter.insertslider(slider["id"], slider["position"])
                GraphiteInter.setmaximum(slider["id"], slider["max_value"])

            for input_field in default_state.get("inputs", []):
                GraphiteInter.addtextinput(input_field["id"], input_field["position"])

            for tab in default_state.get("tabs", []):
                GraphiteInter.create_tab(tab["id"], tab["label"])

            print(f"✅ Interface restaurada com sucesso a partir de '{json_path}'.")

        except Exception as e:
            print(f"Erro ao restaurar a interface: {e}")

    _config = configparser.ConfigParser()

    @staticmethod
    def ReadIniFile(ini_file, part_to_read, variable_to_read):
        """Lê um valor específico de um arquivo INI"""
        if not os.path.isfile(ini_file):
            raise FileNotFoundError(f"O arquivo '{ini_file}' não foi encontrado.")
        
        config = configparser.ConfigParser()
        config.read(ini_file, encoding="utf-8")

        if config.has_section(part_to_read) and config.has_option(part_to_read, variable_to_read):
            return config.get(part_to_read, variable_to_read)
        else:
            raise ValueError(f"A variável '{variable_to_read}' não foi encontrada na seção '{part_to_read}'.")

    @staticmethod
    def Change_ini(iniPath, part_to_change, variable, change_to):
     """Altera o valor de uma variável dentro de uma seção específica."""
     GraphiteInter.ReadIniFile(iniPath, part_to_change, variable)
 
     if not GraphiteInter._config.has_section(part_to_change):
         GraphiteInter._config.add_section(part_to_change)
 
     GraphiteInter._config.set(part_to_change, variable, change_to)
     
     # Correção aqui: passando os argumentos necessários
     GraphiteInter.Save_to_ini(iniPath, part_to_change, variable, change_to)

    @staticmethod
    def Save_to_ini(iniPath, Part_to_save, new_variable, value):
     """Adiciona ou atualiza uma variável em uma seção do INI e salva no disco."""
     # Lê o arquivo existente, se houver
     if os.path.isfile(iniPath):
         GraphiteInter._config.read(iniPath, encoding="utf-8")
 
     # Garante que a seção existe
     if not GraphiteInter._config.has_section(Part_to_save):
         GraphiteInter._config.add_section(Part_to_save)
 
     # Define a variável
     GraphiteInter._config.set(Part_to_save, new_variable, str(value))
 
     # Salva no disco
     with open(iniPath, 'w', encoding="utf-8") as configfile:
         GraphiteInter._config.write(configfile)

    @staticmethod
    def removeBgImage():
      """Remove a imagem de fundo da interface."""
      if GraphiteInter._bg_image_label:
          GraphiteInter._bg_image_label.destroy()  # Remove o widget da imagem de fundo
          GraphiteInter._bg_image_label = None
      else:
          raise ValueError("Nenhuma imagem de fundo foi definida.")         

    @staticmethod
    def removeImage(image_id):
        """Remove uma imagem da interface pelo seu ID."""
        if image_id in GraphiteInter._images:
            # Destrói o label da imagem
            GraphiteInter._images[image_id]['label'].destroy()
            # Remove do dicionário
            del GraphiteInter._images[image_id]
            print(f"✅ Imagem '{image_id}' removida com sucesso!")
        else:
            raise ValueError(f"Imagem com ID '{image_id}' não foi encontrada.")

    @staticmethod
    def imagePosition(image_id, position):
        """Define a posição de uma imagem na interface."""
        if image_id in GraphiteInter._images:
            x, y = position
            GraphiteInter._images[image_id]['label'].place(x=x, y=y)
            # Atualiza a posição no dicionário
            GraphiteInter._images[image_id]['position'] = position
        else:
            raise ValueError(f"Imagem com ID '{image_id}' não foi encontrada.")

    @staticmethod
    def imageSize(image_id, size):
        """Redimensiona uma imagem na interface."""
        if image_id in GraphiteInter._images:
            try:
                # Recarrega a imagem original
                pil_image = Image.open(GraphiteInter._images[image_id]['path'])
                
                # Redimensiona
                width, height = size
                pil_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)
                
                # Cria nova PhotoImage
                new_photo = ImageTk.PhotoImage(pil_image)
                
                # Atualiza o label
                image_label = GraphiteInter._images[image_id]['label']
                image_label.config(image=new_photo)
                image_label.image = new_photo  # Mantém referência
                
                # Atualiza o dicionário
                GraphiteInter._images[image_id]['photo'] = new_photo
                GraphiteInter._images[image_id]['size'] = size
                
                print(f"✅ Imagem '{image_id}' redimensionada para {size}")
                
            except Exception as e:
                raise RuntimeError(f"Erro ao redimensionar a imagem: {e}")
        else:
            raise ValueError(f"Imagem com ID '{image_id}' não foi encontrada.")

    @staticmethod
    def createtable(TableId, rows, columns, posx, posy, sizex, sizey, color):
        """
        Cria uma tabela na interface.
        Parâmetros:
        - TableId: ID único para identificar a tabela
        - rows: Número de linhas
        - columns: Número de colunas
        - posx, posy: Posição da tabela (x, y)
        - sizex, sizey: Tamanho da tabela (largura, altura)
        - color: Cor de fundo da tabela
        """
        if GraphiteInter._root:
            if TableId in GraphiteInter._tables:
                raise ValueError(f"Já existe uma tabela com o ID '{TableId}'.")
            # Criar frame principal da tabela
            table_frame = tk.Frame(GraphiteInter._root, bg=color, width=sizex, height=sizey)
            table_frame.place(x=posx, y=posy)
            # Criar Treeview (tabela)
            tree = ttk.Treeview(table_frame, columns=tuple(f"#{i}" for i in range(1, columns + 1)), show="headings", height=rows)
            # Configurar colunas
            for i in range(1, columns + 1):
                tree.heading(f"#{i}", text=f"Coluna {i}")
                tree.column(f"#{i}", width=sizex//columns, anchor="center")
            # Inicializar linhas vazias
            for i in range(rows):
                tree.insert("", "end", values=[""] * columns)
            # Configurar scrollbar se necessário
            if rows > 10:
                scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)
                scrollbar.pack(side="right", fill="y")
            tree.pack(fill="both", expand=True)
            # Armazenar a tabela no dicionário
            GraphiteInter._tables[TableId] = {
                'frame': table_frame,
                'tree': tree,
                'rows': rows,
                'columns': columns,
                'data': [[""] * columns for _ in range(rows)]
            }
            print(f"✅ Tabela '{TableId}' criada com sucesso ({rows}x{columns})")
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")

    @staticmethod
    def tableRow(tableId, rowNumber, content):
        """
        Define o conteúdo de uma linha inteira da tabela.
        Agora aceita callbacks por célula usando dicionário ou tupla e permite edição se 'editable' for True.
        Parâmetros:
        - tableId: ID da tabela
        - rowNumber: Número da linha (começando em 0)
        - content: Lista com os valores para cada coluna da linha
          Cada item pode ser:
            - string/valor simples
            - dict: {"value": valor, "on_click": funcao, "editable": True/False}
            - tuple: (valor, funcao)
        """
        if tableId in GraphiteInter._tables:
            table_data = GraphiteInter._tables[tableId]
            if rowNumber < 0 or rowNumber >= table_data['rows']:
                raise ValueError(f"Número de linha '{rowNumber}' inválido. Deve estar entre 0 e {table_data['rows']-1}")

            # Inicializa estrutura para callbacks e editáveis se não existir
            if 'callbacks' not in table_data:
                table_data['callbacks'] = {}
            if 'editables' not in table_data:
                table_data['editables'] = {}

            # Prepara os valores, callbacks e editáveis
            values = []
            row_callbacks = {}
            row_editables = {}
            for col, item in enumerate(content):
                if isinstance(item, dict):
                    values.append(item.get('value', ''))
                    if 'on_click' in item and callable(item['on_click']):
                        row_callbacks[col] = item['on_click']
                    if item.get('editable', False):
                        row_editables[col] = True
                elif isinstance(item, tuple) and len(item) == 2 and callable(item[1]):
                    values.append(item[0])
                    row_callbacks[col] = item[1]
                else:
                    values.append(item)
            # Ajusta tamanho
            while len(values) < table_data['columns']:
                values.append("")
            values = values[:table_data['columns']]

            # Salva callbacks e editáveis
            if row_callbacks:
                table_data['callbacks'][rowNumber] = row_callbacks
            else:
                table_data['callbacks'].pop(rowNumber, None)
            if row_editables:
                table_data['editables'][rowNumber] = row_editables
            else:
                table_data['editables'].pop(rowNumber, None)

            table_data['data'][rowNumber] = values

            # Atualizar a visualização da tabela
            tree = table_data['tree']
            items = tree.get_children()
            if rowNumber < len(items):
                tree.item(items[rowNumber], values=values)

            # Adiciona o bind de evento apenas uma vez
            if not hasattr(tree, '_graphite_row_bind'):
                def on_row_click(event, table_id=tableId):
                    tree = GraphiteInter._tables[table_id]['tree']
                    region = tree.identify('region', event.x, event.y)
                    if region == 'cell':
                        row_id = tree.identify_row(event.y)
                        col_id = tree.identify_column(event.x)
                        if row_id and col_id:
                            items = tree.get_children()
                            row_idx = items.index(row_id)
                            col_idx = int(col_id.replace('#','')) - 1
                            table_data = GraphiteInter._tables[table_id]
                            callbacks = table_data.get('callbacks', {})
                            editables = table_data.get('editables', {})
                            # Prioridade: callback, depois editable
                            if row_idx in callbacks and col_idx in callbacks[row_idx]:
                                callbacks[row_idx][col_idx]()
                            elif row_idx in editables and col_idx in editables[row_idx]:
                                # Torna a célula editável
                                def save_edit(event, row=row_idx, col=col_idx, entry_widget=None):
                                    new_value = entry_widget.get()
                                    table_data['data'][row][col] = new_value
                                    tree.item(items[row], values=table_data['data'][row])
                                    entry_widget.destroy()
                                # Pega posição da célula
                                bbox = tree.bbox(row_id, col_id)
                                if bbox:
                                    x, y, width, height = bbox
                                    entry = tk.Entry(tree)
                                    entry.place(x=x, y=y, width=width, height=height)
                                    entry.insert(0, tree.set(row_id, col_id))
                                    entry.focus()
                                    entry.bind('<Return>', lambda e, entry_widget=entry: save_edit(e, entry_widget=entry_widget))
                                    entry.bind('<FocusOut>', lambda e, entry_widget=entry: entry_widget.destroy())
                tree.bind('<Double-1>', on_row_click)
                tree._graphite_row_bind = True

            print(f"✅ Linha {rowNumber} da tabela '{tableId}' atualizada (com métodos/editável se fornecidos)")
        else:
            raise ValueError(f"Tabela com ID '{tableId}' não foi encontrada.")

    @staticmethod
    def tableColumn(tableId, colNumber, content):
        """
        Define o conteúdo de uma coluna inteira da tabela.
        
        Parâmetros:
        - tableId: ID da tabela
        - colNumber: Número da coluna (começando em 0)
        - content: Lista com os valores para cada linha da coluna
        """
        if tableId in GraphiteInter._tables:
            table_data = GraphiteInter._tables[tableId]
            
            if colNumber < 0 or colNumber >= table_data['columns']:
                raise ValueError(f"Número de coluna '{colNumber}' inválido. Deve estar entre 0 e {table_data['columns']-1}")
            
            # Atualizar dados na matriz
            if isinstance(content, list):
                # Garantir que o conteúdo tenha o tamanho correto
                while len(content) < table_data['rows']:
                    content.append("")
                content = content[:table_data['rows']]  # Truncar se for muito grande
            else:
                # Se não for lista, preencher toda a coluna com o mesmo valor
                content = [str(content)] * table_data['rows']
            
            # Atualizar cada linha da coluna
            for row in range(table_data['rows']):
                if row < len(content):
                    table_data['data'][row][colNumber] = content[row]
            
            # Atualizar a visualização da tabela
            tree = table_data['tree']
            items = tree.get_children()
            for row in range(min(len(items), table_data['rows'])):
                tree.item(items[row], values=table_data['data'][row])
            
            print(f"✅ Coluna {colNumber} da tabela '{tableId}' atualizada")
            
        else:
            raise ValueError(f"Tabela com ID '{tableId}' não foi encontrada.")

    @staticmethod
    def cellvalue(tableId, rowNumber, colNumber):
        """
        Obtém o valor de uma célula específica da tabela.
        
        Parâmetros:
        - tableId: ID da tabela
        - rowNumber: Número da linha (começando em 0)
        - colNumber: Número da coluna (começando em 0)
        
        Retorna:
        - Valor da célula
        """
        if tableId in GraphiteInter._tables:
            table_data = GraphiteInter._tables[tableId]
            
            if rowNumber < 0 or rowNumber >= table_data['rows']:
                raise ValueError(f"Número de linha '{rowNumber}' inválido. Deve estar entre 0 e {table_data['rows']-1}")
            
            if colNumber < 0 or colNumber >= table_data['columns']:
                raise ValueError(f"Número de coluna '{colNumber}' inválido. Deve estar entre 0 e {table_data['columns']-1}")
            
            return table_data['data'][rowNumber][colNumber]
            
        else:
            raise ValueError(f"Tabela com ID '{tableId}' não foi encontrada.")

    @staticmethod
    def setCellValue(tableId, rowNumber, colNumber, value):
        """
        Define o valor de uma célula específica da tabela.
        
        Parâmetros:
        - tableId: ID da tabela
        - rowNumber: Número da linha (começando em 0)
        - colNumber: Número da coluna (começando em 0)
        - value: Valor a ser definido na célula
        """
        if tableId in GraphiteInter._tables:
            table_data = GraphiteInter._tables[tableId]
            
            if rowNumber < 0 or rowNumber >= table_data['rows']:
                raise ValueError(f"Número de linha '{rowNumber}' inválido. Deve estar entre 0 e {table_data['rows']-1}")
            
            if colNumber < 0 or colNumber >= table_data['columns']:
                raise ValueError(f"Número de coluna '{colNumber}' inválido. Deve estar entre 0 e {table_data['columns']-1}")
            
            # Atualizar dados na matriz
            table_data['data'][rowNumber][colNumber] = str(value)
            
            # Atualizar a visualização da tabela
            tree = table_data['tree']
            items = tree.get_children()
            if rowNumber < len(items):
                tree.item(items[rowNumber], values=table_data['data'][rowNumber])
            
            print(f"✅ Célula ({rowNumber},{colNumber}) da tabela '{tableId}' atualizada")
            
        else:
            raise ValueError(f"Tabela com ID '{tableId}' não foi encontrada.")

    @staticmethod
    def removeTable(tableId):
        """
        Remove uma tabela da interface.
        
        Parâmetros:
        - tableId: ID da tabela a ser removida
        """
        if tableId in GraphiteInter._tables:
            table_data = GraphiteInter._tables[tableId]
            table_data['frame'].destroy()
            del GraphiteInter._tables[tableId]
            print(f"✅ Tabela '{tableId}' removida com sucesso!")
        else:
            raise ValueError(f"Tabela com ID '{tableId}' não foi encontrada.")

    @staticmethod
    def modifytable(tableid, line, column, newcontent):
        """
        Modifica o valor de uma célula específica da tabela.
        Parâmetros:
        - tableid: ID da tabela
        - line: Número da linha (começando em 0)
        - column: Número da coluna (começando em 0)
        - newcontent: Novo valor para a célula
        """
        if tableid in GraphiteInter._tables:
            table_data = GraphiteInter._tables[tableid]
            if line < 0 or line >= table_data['rows']:
                raise ValueError(f"Número de linha '{line}' inválido. Deve estar entre 0 e {table_data['rows']-1}")
            if column < 0 or column >= table_data['columns']:
                raise ValueError(f"Número de coluna '{column}' inválido. Deve estar entre 0 e {table_data['columns']-1}")
            # Atualizar dados na matriz
            table_data['data'][line][column] = str(newcontent)
            # Atualizar a visualização da tabela
            tree = table_data['tree']
            items = tree.get_children()
            if line < len(items):
                tree.item(items[line], values=table_data['data'][line])
            print(f"✅ Célula ({line},{column}) da tabela '{tableid}' modificada para '{newcontent}'")
        else:
            raise ValueError(f"Tabela com ID '{tableid}' não foi encontrada.")

    @staticmethod
    def tabletitle(tableid, col_number, title):
        """
        Altera o título (header) de uma coluna específica da tabela.
        Parâmetros:
        - tableid: ID da tabela
        - col_number: Número da coluna (começando em 0)
        - title: Novo título para a coluna
        """
        if tableid in GraphiteInter._tables:
            table_data = GraphiteInter._tables[tableid]
            if col_number < 0 or col_number >= table_data['columns']:
                raise ValueError(f"Número de coluna '{col_number}' inválido. Deve estar entre 0 e {table_data['columns']-1}")
            tree = table_data['tree']
            tree.heading(f"#{col_number+1}", text=title)
            print(f"✅ Título da coluna {col_number} da tabela '{tableid}' alterado para '{title}'")
        else:
            raise ValueError(f"Tabela com ID '{tableid}' não foi encontrada.")

    @staticmethod
    def tablestyle(tableid, fontcolor, fontstyle, tamanhofonte, corborda, cordefundo, header_fontcolor=None, header_fontstyle=None, header_tamanhofonte=None, header_cordefundo=None):
        """
        Altera o estilo visual da tabela (corpo e cabeçalho).
        Parâmetros:
        - tableid: ID da tabela
        - fontcolor: Cor do texto do corpo
        - fontstyle: Fonte do corpo
        - tamanhofonte: Tamanho da fonte do corpo
        - corborda: Cor da borda
        - cordefundo: Cor de fundo do corpo
        - header_fontcolor: Cor do texto do cabeçalho (opcional)
        - header_fontstyle: Fonte do cabeçalho (opcional)
        - header_tamanhofonte: Tamanho da fonte do cabeçalho (opcional)
        - header_cordefundo: Cor de fundo do cabeçalho (opcional)
        Agora aceita cores em formato nome, hexadecimal ou tupla RGB.
        """
        if tableid in GraphiteInter._tables:
            table_data = GraphiteInter._tables[tableid]
            tree = table_data['tree']
            frame = table_data['frame']
            style = ttk.Style()
            style.theme_use('clam')  # Permite customização do cabeçalho
            style_name = f"Custom.Treeview.{tableid}"

            # Sempre tenta definir o layout copiando do Treeview padrão
            try:
                style.layout(style_name)
            except Exception:
                style.layout(style_name, style.layout("Treeview"))

            # Converte todas as cores para formato aceito
            fontcolor_hex = _parse_color(fontcolor)
            cordefundo_hex = _parse_color(cordefundo)
            corborda_hex = _parse_color(corborda)
            header_fontcolor_hex = _parse_color(header_fontcolor) if header_fontcolor is not None else fontcolor_hex
            header_cordefundo_hex = _parse_color(header_cordefundo) if header_cordefundo is not None else cordefundo_hex

            # Estilo do corpo da tabela
            style.configure(
                style_name,
                foreground=fontcolor_hex,
                background=cordefundo_hex,
                fieldbackground=cordefundo_hex,
                font=(fontstyle, tamanhofonte)
            )
            # Salva o estilo do corpo para restauração posterior
            table_data['last_body_style'] = {
                'foreground': fontcolor_hex,
                'background': cordefundo_hex,
                'fieldbackground': cordefundo_hex,
                'font': (fontstyle, tamanhofonte)
            }
            # Estilo do cabeçalho (se fornecido, senão usa do corpo)
            style.configure(
                style_name + ".Heading",
                foreground=header_fontcolor_hex,
                background=header_cordefundo_hex,
                font=(header_fontstyle if header_fontstyle is not None else fontstyle,
                      header_tamanhofonte if header_tamanhofonte is not None else tamanhofonte,
                      "bold")
            )
            tree.configure(style=style_name)
            frame.config(bg=cordefundo_hex, highlightbackground=corborda_hex, highlightcolor=corborda_hex, highlightthickness=2)
            print(f"✅ Estilo da tabela '{tableid}' atualizado (corpo e cabeçalho).")
        else:
            raise ValueError(f"Tabela com ID '{tableid}' não foi encontrada.")

    @staticmethod
    def exporttable(tableid, path):
        """
        Exporta a tabela para um arquivo Excel (.xlsx).
        Parâmetros:
        - tableid: ID da tabela
        - path: Caminho do arquivo Excel a ser salvo
        """
        if tableid in GraphiteInter._tables:
            table_data = GraphiteInter._tables[tableid]
            df = pd.DataFrame(table_data['data'])
            df.to_excel(path, index=False, header=False)
            print(f"✅ Tabela '{tableid}' exportada para {path}")
        else:
            raise ValueError(f"Tabela com ID '{tableid}' não foi encontrada.")

    @staticmethod
    def importtable(tableid, path, posx=0, posy=0):
        """
        Importa uma tabela de um arquivo Excel (.xlsx) e cria uma nova tabela na interface.
        Parâmetros:
        - tableid: ID da nova tabela
        - path: Caminho do arquivo Excel
        - posx, posy: Posição da tabela
        """
        df = pd.read_excel(path, header=None)
        rows, columns = df.shape
        sizex, sizey = 300, 50 + 25 * rows  # Tamanho padrão ajustado
        color = "white"
        GraphiteInter.createtable(tableid, rows, columns, posx, posy, sizex, sizey, color)
        for i in range(rows):
            GraphiteInter.tableRow(tableid, i, list(df.iloc[i]))
        GraphiteInter.make_table_fully_editable(tableid)
        print(f"✅ Tabela '{tableid}' importada de {path}")

    @staticmethod
    def selectcell(tableid, row, col, metodo):
        """
        Define um método (editable ou on_click) para uma célula específica da tabela.
        Parâmetros:
        - tableid: ID da tabela
        - row: número da linha (começando em 0)
        - col: número da coluna (começando em 0)
        - metodo: dict com 'on_click' e/ou 'editable', ou apenas uma função/callback
        """
        if tableid in GraphiteInter._tables:
            table_data = GraphiteInter._tables[tableid]
            # Garante que as estruturas existem
            if 'callbacks' not in table_data:
                table_data['callbacks'] = {}
            if 'editables' not in table_data:
                table_data['editables'] = {}
            # Callback
            if isinstance(metodo, dict):
                if 'on_click' in metodo and callable(metodo['on_click']):
                    if row not in table_data['callbacks']:
                        table_data['callbacks'][row] = {}
                    table_data['callbacks'][row][col] = metodo['on_click']
                if metodo.get('editable', False):
                    if row not in table_data['editables']:
                        table_data['editables'][row] = {}
                    table_data['editables'][row][col] = True
            elif callable(metodo):
                if row not in table_data['callbacks']:
                    table_data['callbacks'][row] = {}
                table_data['callbacks'][row][col] = metodo
            elif metodo == 'editable':
                if row not in table_data['editables']:
                    table_data['editables'][row] = {}
                table_data['editables'][row][col] = True
            else:
                raise ValueError("metodo deve ser um dict, função ou 'editable'")
            print(f"✅ Método definido para célula ({row},{col}) da tabela '{tableid}'")
        else:
            raise ValueError(f"Tabela com ID '{tableid}' não foi encontrada.")

    @staticmethod
    def filedialog(extensionfilter=None):
        """
        Abre um explorador de arquivos para selecionar um arquivo.
        Parâmetros:
        - extensionfilter: string como '*.xlsx' ou '*.txt'. Se None ou vazio, mostra todos os arquivos.
        Retorna o caminho do arquivo selecionado ou None se cancelado.
        """
        root = GraphiteInter._get_root()
        filetypes = [('Todos os arquivos', '*.*')]
        if extensionfilter:
            filetypes = [(f'Filtro ({extensionfilter})', extensionfilter)]
        path = fd.askopenfilename(parent=root, filetypes=filetypes)
        return path if path else None

    @staticmethod
    def make_table_fully_editable(tableid):
        """
        Torna todas as células da tabela editáveis, detectando automaticamente as dimensões.
        Parâmetros:
        - tableid: ID da tabela
        """
        if tableid in GraphiteInter._tables:
            table_data = GraphiteInter._tables[tableid]
            rows = table_data['rows']
            columns = table_data['columns']
            for row in range(rows):
                for col in range(columns):
                    GraphiteInter.selectcell(tableid, row, col, 'editable')
            print(f"✅ Todas as células da tabela '{tableid}' agora são editáveis.")
        else:
            raise ValueError(f"Tabela com ID '{tableid}' não foi encontrada.")

    @staticmethod
    def create_excel_container(container_id="excel_container", posx=0, posy=0, sizex=800, sizey=500):
        """
        Cria um container visual tipo Excel (com botão de importar, exportar, edição, copiar/colar e abas) na janela principal.
        Parâmetros:
        - container_id: ID do container (padrão: 'excel_container')
        - posx, posy: posição do container
        - sizex, sizey: tamanho do container
        """
        import pandas as pd
        if not hasattr(GraphiteInter, '_excel_containers'):
            GraphiteInter._excel_containers = {}
        if container_id in GraphiteInter._excel_containers:
            GraphiteInter._excel_containers[container_id].destroy()
        frame = tk.Frame(GraphiteInter._root, bg="#f8f8f8", width=sizex, height=sizey, highlightbackground="#222", highlightthickness=1)
        frame.place(x=posx, y=posy, width=sizex, height=sizey)
        # Notebook para abas
        notebook = ttk.Notebook(frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=(40,10))
        # Botões de importar/exportar/remover aba
        btn_frame = tk.Frame(frame, bg="#f8f8f8")
        btn_frame.place(x=0, y=0, width=sizex, height=40)
        def import_excel():
            file_path = fd.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
            if not file_path:
                return
            df = pd.read_excel(file_path)
            add_tab(df, os.path.basename(file_path))
        def export_excel():
            current = notebook.index(notebook.select())
            if current < 0 or current >= len(tabs):
                messagebox.showwarning("Exportar Excel", "Nenhuma aba selecionada.")
                return
            df = tabs[current]['df']
            file_path = fd.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if not file_path:
                return
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Exportar Excel", f"Arquivo exportado para {file_path}")
        def remove_tab():
            current = notebook.index(notebook.select())
            if current < 0 or current >= len(tabs):
                messagebox.showwarning("Remover Aba", "Nenhuma aba selecionada.")
                return
            notebook.forget(current)
            del tabs[current]
        import_btn = tk.Button(btn_frame, text="Importar Excel", command=import_excel)
        import_btn.pack(side="left", padx=8, pady=5)
        export_btn = tk.Button(btn_frame, text="Exportar Excel", command=export_excel)
        export_btn.pack(side="left", padx=8, pady=5)
        remove_btn = tk.Button(btn_frame, text="Remover Aba", command=remove_tab)
        remove_btn.pack(side="left", padx=8, pady=5)
        # Lista de abas/tabelas
        tabs = []
        # Variável para copiar/colar
        clipboard = {'value': None}
        def add_tab(df, tab_name):
            tab_frame = tk.Frame(notebook)
            notebook.add(tab_frame, text=tab_name)
            table_frame = tk.Frame(tab_frame)
            table_frame.pack(fill="both", expand=True)
            columns = list(df.columns)
            tree = ttk.Treeview(table_frame, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120, anchor="center")
            for idx, row in df.iterrows():
                tree.insert("", "end", values=list(row))
            vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")
            # Edição de células
            def on_double_click(event, tree=tree, df=df):
                region = tree.identify('region', event.x, event.y)
                if region == 'cell':
                    row_id = tree.identify_row(event.y)
                    col_id = tree.identify_column(event.x)
                    if row_id and col_id:
                        items = tree.get_children()
                        row_idx = items.index(row_id)
                        col_idx = int(col_id.replace('#','')) - 1
                        col_name = columns[col_idx]
                        bbox = tree.bbox(row_id, col_id)
                        if bbox:
                            x, y, width, height = bbox
                            entry = tk.Entry(tree)
                            entry.place(x=x, y=y, width=width, height=height)
                            entry.insert(0, tree.set(row_id, col_id))
                            entry.focus_set()
                            def save_edit(event, row=row_idx, col=col_idx, entry_widget=entry):
                                new_value = entry_widget.get()
                                tree.set(row_id, col_id, new_value)
                                df.iat[row, col] = new_value
                                entry_widget.destroy()
                            entry.bind('<Return>', save_edit)
                            entry.bind('<FocusOut>', lambda e: entry.destroy())
            tree.bind('<Double-1>', on_double_click)
            # Copiar célula selecionada (Ctrl+C)
            def on_copy(event, tree=tree):
                selected = tree.focus()
                if not selected:
                    return
                col = tree.identify_column(tree.winfo_pointerx() - tree.winfo_rootx())
                if not col:
                    return
                value = tree.set(selected, col)
                clipboard['value'] = value
                tree.clipboard_clear()
                tree.clipboard_append(value)
            tree.bind('<Control-c>', on_copy)
            tree.bind('<Control-C>', on_copy)
            # Colar na célula selecionada (Ctrl+V)
            def on_paste(event, tree=tree, df=df):
                selected = tree.focus()
                if not selected:
                    return
                col = tree.identify_column(tree.winfo_pointerx() - tree.winfo_rootx())
                if not col:
                    return
                value = clipboard['value']
                if value is None:
                    try:
                        value = tree.clipboard_get()
                    except Exception:
                        return
                col_idx = int(col.replace('#','')) - 1
                tree.set(selected, col, value)
                row_idx = tree.get_children().index(selected)
                df.iat[row_idx, col_idx] = value
            tree.bind('<Control-v>', on_paste)
            tree.bind('<Control-V>', on_paste)
            tabs.append({'df': df, 'tree': tree, 'tab_frame': tab_frame})
        GraphiteInter._excel_containers[container_id] = frame
        print(f"✅ Container Excel '{container_id}' com edição, exportação, abas, copiar e colar criado.")

class DllManager:
    dll = None
    default_parameters = []
    loaded_funcname = None

    @staticmethod
    def ReadDll(dll_path):
        try:
            DllManager.dll = ctypes.WinDLL(dll_path)
            print(f"✅ DLL carregada: {dll_path}")
        except Exception as e:
            print(f"❌ Erro ao carregar DLL: {e}")

    @staticmethod
    def SetParametersAuto(funcname, *args):
        if DllManager.dll is None:
            print("❌ Nenhuma DLL carregada.")
            return

        try:
            func = getattr(DllManager.dll, funcname)
            DllManager.loaded_funcname = funcname

            # Tentativa de dedução (caso argtypes não esteja definido)
            if not hasattr(func, 'argtypes') or func.argtypes is None:
                # Suponha todos como ponteiro genérico se não houver argtypes
                func.argtypes = [ctypes.c_void_p] * len(args)

            converted_args = []
            for i, argtype in enumerate(func.argtypes):
                raw_value = args[i]

                # Conversão automática básica
                if argtype == ctypes.c_void_p:
                    if raw_value == "None":
                        converted_args.append(ctypes.c_void_p(None))
                    else:
                        converted_args.append(ctypes.c_void_p(int(raw_value)))
                elif argtype == ctypes.c_char_p:
                    converted_args.append(ctypes.c_char_p(str(raw_value).encode('utf-8')))
                elif argtype == ctypes.c_wchar_p:
                    converted_args.append(ctypes.c_wchar_p(str(raw_value)))
                elif argtype == ctypes.c_int:
                    converted_args.append(ctypes.c_int(int(raw_value)))
                elif argtype == ctypes.c_uint:
                    converted_args.append(ctypes.c_uint(int(raw_value)))
                elif argtype == ctypes.c_bool:
                    converted_args.append(ctypes.c_bool(bool(raw_value)))
                else:
                    # fallback seguro
                    converted_args.append(argtype(raw_value))

            DllManager.default_parameters = converted_args
            print("✅ Parâmetros definidos com sucesso.")

        except Exception as e:
            print(f"❌ Erro ao definir parâmetros automaticamente: {e}")

    @staticmethod
    def UseDllFunction(funcname=None, parameters=None):
        if DllManager.dll is None:
            print("❌ Nenhuma DLL carregada.")
            return

        try:
            funcname = funcname or DllManager.loaded_funcname
            func = getattr(DllManager.dll, funcname)
            func.restype = ctypes.c_int  # Valor padrão de retorno

            args = parameters if parameters else DllManager.default_parameters
            result = func(*args)
            print(f"✅ Função '{funcname}' chamada. Resultado: {result}")
            return result

        except Exception as e:
            print(f"❌ Erro ao chamar função: {e}")
            
class Locator:
    @staticmethod
    def Locate_File(diskletter, fileName):
        search_root = f"{diskletter.upper()}:\\"
        fileNameLower = fileName.lower()

        for root, dirs, files in os.walk(search_root):
            for f in files:
                if f.lower() == fileNameLower:
                    return os.path.join(root, f)
        
        return ""
    
    @staticmethod
    def Locate_multiple(dependencies_source, section=None, numberoffiles=None):
        """
        Localiza múltiplos arquivos definidos em um arquivo INI ou dicionário.

        Args:
            dependencies_source (str/dict): Caminho para o arquivo INI ou um dicionário com as dependências.
            section (str, opcional): Seção do arquivo INI que contém as dependências, caso seja passado um arquivo INI.
            numberoffiles (int, opcional): Número total de arquivos a procurar, caso seja passado um arquivo INI, deve ser passado um a mais (6 arquivos -> 7).
        
        Returns:
            list: Lista com os caminhos encontrados ou "Não encontrado".
        """
        dependencias_encontradas = []

        # Caso o parâmetro seja um arquivo INI
        if isinstance(dependencies_source, str):
            import configparser
            config = configparser.ConfigParser()
            config.read(dependencies_source)

            for i in range(1, numberoffiles + 1):  # Inclui o último número
                chave = str(i)
                valor = config.get(section, chave)

                caminho = Locator.Locate_File("C", valor)

                dependencias_encontradas.append(caminho if caminho else "Não encontrado")
        
        # Caso o parâmetro seja um dicionário
        elif isinstance(dependencies_source, dict):
            for chave, valor in dependencies_source.items():
                caminho = Locator.Locate_File("C", valor)

                dependencias_encontradas.append(caminho if caminho else "Não encontrado")

        return dependencias_encontradas
    

    

# Lista persistente para savetolist
_savetolist_global = []

def savetolist(valor=None):
    """
    Adiciona um valor à lista global persistente e retorna a lista acumulada.
    Exemplo:
        a = savetolist(1)  # a = [1]
        a = savetolist(2)  # a = [1, 2]
        a = savetolist()   # a = [1, 2]
    """
    global _savetolist_global
    if valor is not None:
        _savetolist_global.append(valor)
    return _savetolist_global

def clearlist():
    """
    Limpa a lista global usada por savetolist.
    """
    global _savetolist_global
    _savetolist_global.clear()

# Funções auxiliares para conversão de cores (reutilizáveis)
def _parse_color(color):
    """Converte cor de qualquer formato para hexadecimal aceito pelo Tkinter."""
    if color is None:
        return None
    # Se já é uma tupla RGB
    if isinstance(color, (tuple, list)) and len(color) == 3:
        return '#%02x%02x%02x' % tuple(int(c) for c in color)
    # Se é string hexadecimal
    if isinstance(color, str):
        color = color.strip()
        if color.startswith('#'):
            color = color[1:]
        if len(color) == 6 and all(c in '0123456789ABCDEFabcdef' for c in color):
            return '#' + color.lower()
        # Se não é hexadecimal, tenta usar como nome de cor
        try:
            test_widget = tk.Label()
            test_widget.config(bg=color)
            test_widget.destroy()
            return color.lower()
        except:
            raise ValueError(f"Formato de cor inválido: {color}")
    raise ValueError(f"Formato de cor não suportado: {color}")

class ExcelContainer(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill="both", expand=True)
        self.tree = None
        self.create_widgets()

    def create_widgets(self):
        btn = tk.Button(self, text="Importar Excel", command=self.import_excel)
        btn.pack(pady=5)
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill="both", expand=True)

    def import_excel(self):
        file_path = fd.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        df = pd.read_excel(file_path)
        self.show_table(df)

    def show_table(self, df):
        # Remove tabela anterior
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        columns = list(df.columns)
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")



