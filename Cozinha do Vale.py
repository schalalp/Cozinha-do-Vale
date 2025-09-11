import pyxel

# Dimensões da janela
WINDOW_WIDTH = 160
WINDOW_HEIGHT = 120

# A classe principal do jogo
class CozinhaGame:
    def __init__(self):
        # Inicializa a janela do Pyxel
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT, title="Jogo da Cozinha")
        
        # Habilita a exibição do cursor do mouse
        pyxel.mouse(True)

        # Carrega a imagem do fundo (Cozinha.png) e outras imagens
        # Certifique-se de que Cozinha.png, Ovo.png, Leite.png, Queijo.png, Panela.png, Bolo.png
        # estejam na mesma pasta do seu script Python.
        pyxel.image(0).load(0, 0, "Cozinha.png") # Fundo no image bank 0
        pyxel.image(1).load(0, 0, "Ovo.png")
        pyxel.image(1).load(32, 0, "Leite.png")
        pyxel.image(1).load(48, 0, "Queijo.png")
        pyxel.image(1).load(64, 0, "Panela.png")
        pyxel.image(1).load(80, 0, "Bolo.png") # Imagem do Bolo

        # Posições e estados dos ingredientes na prateleira
        self.ingredientes_data = {
            "ovo":      {"name": "Ovo",     "x": 20, "y": 20, "x_orig": 20, "y_orig": 20,  "img_u": 0, "img_v": 0,  "dragging": False, "in_pan": False},
            "leite":    {"name": "Leite",   "x": 20, "y": 50, "x_orig": 20, "y_orig": 50, "img_u": 32, "img_v": 0, "dragging": False, "in_pan": False},
            "queijo":   {"name": "Queijo",  "x": 20, "y": 80, "x_orig": 20, "y_orig": 80, "img_u": 48, "img_v": 0, "dragging": False, "in_pan": False},
        }
        
        # Posição da panela
        self.panela_rect = {"x": WINDOW_WIDTH // 2 - 8, "y": WINDOW_HEIGHT - 30, "w": 16, "h": 16, "img_u": 64, "img_v": 0}

        # Posições fixas para os ingredientes (slots)
        self.pan_slots = [
            {"x": self.panela_rect["x"] - 20, "y": self.panela_rect["y"]},
            {"x": self.panela_rect["x"] + 20, "y": self.panela_rect["y"]}
        ]
        
        # Posição e dimensões do botão de confirmar
        self.confirm_button_rect = {"x": WINDOW_WIDTH // 2 - 25, "y": 10, "w": 50, "h": 15}

        # Posições dos novos botões (ajustadas para ficarem abaixo do bolo)
        # O espaçamento y foi ajustado para melhor visualização
        self.another_recipe_button_rect = {"x": WINDOW_WIDTH // 2 - 40, "y": WINDOW_HEIGHT // 2 + 20, "w": 80, "h": 15}
        self.show_list_button_rect = {"x": WINDOW_WIDTH // 2 - 40, "y": WINDOW_HEIGHT // 2 + 40, "w": 80, "h": 15}

        self.show_bolo = False # Flag para mostrar o bolo na tela de receita pronta
        self.ingredientes_na_panela = []

        # Definição das receitas (ingredientes necessários)
        self.receitas_possiveis = {
            frozenset(["ovo", "leite"]): "Bolo",
            frozenset(["queijo", "leite"]): "Creme de Queijo",
        }

        # Lista para armazenar as receitas concluídas
        self.receitas_concluidas = []

        # Variáveis de estado do jogo
        self.game_state = "playing" # 'playing', 'recipe_done', 'show_list', 'game_over'
        self.message = ""

        # Inicia o loop do jogo
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.game_state == "playing":
            # Lógica de arrastar e soltar
            for key, ingrediente in self.ingredientes_data.items():
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and \
                   ingrediente["x"] < pyxel.mouse_x < ingrediente["x"] + 16 and \
                   ingrediente["y"] < pyxel.mouse_y < ingrediente["y"] + 16 and \
                   not ingrediente["in_pan"]:
                    ingrediente["dragging"] = True
                
                if ingrediente["dragging"]:
                    ingrediente["x"] = pyxel.mouse_x - 8
                    ingrediente["y"] = pyxel.mouse_y - 8

                if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT) and ingrediente["dragging"]:
                    ingrediente["dragging"] = False
                    
                    slot_colidiu = False
                    for i, slot in enumerate(self.pan_slots):
                        if slot["x"] < pyxel.mouse_x < slot["x"] + 16 and \
                           slot["y"] < pyxel.mouse_y < slot["y"] + 16:
                            if key not in self.ingredientes_na_panela and len(self.ingredientes_na_panela) <= i:
                                ingrediente["in_pan"] = True
                                ingrediente["x"] = slot["x"]
                                ingrediente["y"] = slot["y"]
                                self.ingredientes_na_panela.insert(i, key)
                                slot_colidiu = True
                                break
                            elif key in self.ingredientes_na_panela:
                                # Se já está na panela e arrastou para outro slot, move
                                self.ingredientes_na_panela.remove(key)
                                self.ingredientes_na_panela.insert(i, key)
                                ingrediente["x"] = slot["x"]
                                ingrediente["y"] = slot["y"]
                                slot_colidiu = True
                                break
                    
                    if not slot_colidiu:
                        # Se não colidiu com slot, retorna à posição original
                        ingrediente["x"] = ingrediente["x_orig"]
                        ingrediente["y"] = ingrediente["y_orig"]
                        ingrediente["in_pan"] = False
                        if key in self.ingredientes_na_panela:
                            self.ingredientes_na_panela.remove(key)

            # Lógica para o botão de confirmar a receita
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and \
               self.confirm_button_rect["x"] < pyxel.mouse_x < self.confirm_button_rect["x"] + self.confirm_button_rect["w"] and \
               self.confirm_button_rect["y"] < pyxel.mouse_y < self.confirm_button_rect["y"] + self.confirm_button_rect["h"]:
                
                if len(self.ingredientes_na_panela) == 2:
                    self.check_recipe()
                else:
                    self.message = "Precisa de 2 ingredientes!"
            
            # Botão de limpar (C)
            if pyxel.btnp(pyxel.KEY_C):
                self.clear_pan()

        elif self.game_state == "recipe_done":
            # Lógica dos novos botões
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                # Botão "Fazer outra?"
                if self.another_recipe_button_rect["x"] < pyxel.mouse_x < self.another_recipe_button_rect["x"] + self.another_recipe_button_rect["w"] and \
                   self.another_recipe_button_rect["y"] < pyxel.mouse_y < self.another_recipe_button_rect["y"] + self.another_recipe_button_rect["h"]:
                    self.clear_pan() # Limpa e retorna ao estado 'playing'
                
                # Botão "Ver lista"
                elif self.show_list_button_rect["x"] < pyxel.mouse_x < self.show_list_button_rect["x"] + self.show_list_button_rect["w"] and \
                     self.show_list_button_rect["y"] < pyxel.mouse_y < self.show_list_button_rect["y"] + self.show_list_button_rect["h"]:
                    self.game_state = "show_list"
        
        elif self.game_state == "show_list":
            # Pressionar 'R' reinicia o jogo
            if pyxel.btnp(pyxel.KEY_R):
                self.__init__() # Reseta completamente o jogo

        # Verificar condição de vitória (todas as receitas feitas)
        if len(self.receitas_concluidas) == len(self.receitas_possiveis) and self.game_state != "game_over":
            self.game_state = "game_over"
            self.message = "Parabens! Voce fez todas as receitas!\nPressione 'R' para reiniciar."

        # Pressionar 'R' na tela de Game Over também reinicia
        if self.game_state == "game_over" and pyxel.btnp(pyxel.KEY_R):
            self.__init__()

    def check_recipe(self):
        ingredientes_atuais = frozenset(self.ingredientes_na_panela)
        receita_encontrada = False
        
        for receita_ingredientes, nome_receita in self.receitas_possiveis.items():
            if ingredientes_atuais == receita_ingredientes:
                if nome_receita not in self.receitas_concluidas:
                    self.receitas_concluidas.append(nome_receita)
                    self.message = f"Voce fez: {nome_receita}!"
                else:
                    self.message = "Voce ja fez essa receita. Vejo que aprendeu bem!"
                
                # Verifica se a receita é de Bolo para exibir a imagem
                if nome_receita == "Bolo":
                    self.show_bolo = True
                else:
                    self.show_bolo = False # Nao mostra imagem para outras receitas

                receita_encontrada = True
                break
        
        if not receita_encontrada:
            self.message = "Essa combinacao nao faz nada!"
            self.show_bolo = False # Nao mostra imagem se a receita for invalida
        
        self.game_state = "recipe_done" # Transiciona para a tela de receita pronta

    def clear_pan(self):
        # Retorna todos os ingredientes às suas posições originais na prateleira
        for ing_key in self.ingredientes_data: # Itera sobre TODOS os ingredientes, nao apenas os na panela
            self.ingredientes_data[ing_key]["in_pan"] = False
            self.ingredientes_data[ing_key]["x"] = self.ingredientes_data[ing_key]["x_orig"]
            self.ingredientes_data[ing_key]["y"] = self.ingredientes_data[ing_key]["y_orig"]
            
        self.ingredientes_na_panela.clear()
        self.show_bolo = False # Garante que o bolo suma ao limpar a panela
        self.message = "" # Limpa qualquer mensagem anterior
        self.game_state = "playing" # Retorna ao estado de jogo principal

    def draw(self):
        pyxel.cls(0)
        # Desenha o fundo da cozinha em TODAS as telas
        pyxel.blt(0, 0, 0, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        if self.game_state == "playing":
            # Desenha a panela
            pyxel.blt(self.panela_rect["x"], self.panela_rect["y"], 1, 
                      self.panela_rect["img_u"], self.panela_rect["img_v"], 
                      self.panela_rect["w"], self.panela_rect["h"], 0)

            # Desenha os quadrados dos slots
            pyxel.rect(self.pan_slots[0]["x"], self.pan_slots[0]["y"], 16, 16, 13)
            pyxel.rect(self.pan_slots[1]["x"], self.pan_slots[1]["y"], 16, 16, 13)

            # Desenha o botão de Confirmar
            pyxel.rectb(self.confirm_button_rect["x"], self.confirm_button_rect["y"], 
                        self.confirm_button_rect["w"], self.confirm_button_rect["h"], 7)
            pyxel.text(self.confirm_button_rect["x"] + 5, self.confirm_button_rect["y"] + 4, "Confirmar", 7)
            
            # Desenha os ingredientes (sempre visíveis no modo playing)
            for key, ingrediente in self.ingredientes_data.items():
                pyxel.blt(ingrediente["x"], ingrediente["y"], 1, 
                          ingrediente["img_u"], ingrediente["img_v"], 
                          16, 16, 0)
            
            # A lista de receitas e o título foram movidos para a direita
            pyxel.text(WINDOW_WIDTH - 60, 50, "Receitas:", 7)
            y_offset = 0
            for receita in self.receitas_concluidas:
                pyxel.text(WINDOW_WIDTH - 60, 60 + y_offset, receita, 10)
                y_offset += 10
            
            # Desenha a mensagem de feedback
            if self.message:
                message_width = len(self.message) * 4
                pyxel.text(WINDOW_WIDTH // 2 - message_width // 2, WINDOW_HEIGHT - 10, self.message, 7)

        elif self.game_state == "recipe_done":
            # Neste estado, a panela e os slots nao sao desenhados
            
            # Se a receita de bolo foi feita, desenha o bolo
            if self.show_bolo:
                # Mensagem "Voce fez: Bolo!" acima do bolo
                message_width = len(self.message) * 4 
                pyxel.text(WINDOW_WIDTH // 2 - message_width // 2, WINDOW_HEIGHT // 2 - 25, self.message, 7)

                # Desenha o bolo bem centralizado
                pyxel.blt(WINDOW_WIDTH // 2 - 8, WINDOW_HEIGHT // 2 - 8, 1, 
                          80, 0, 16, 16, 0)

            # Botões "Fazer outra?" e "Ver lista" abaixo do bolo
            pyxel.rectb(self.another_recipe_button_rect["x"], self.another_recipe_button_rect["y"],
                        self.another_recipe_button_rect["w"], self.another_recipe_button_rect["h"], 7)
            pyxel.text(self.another_recipe_button_rect["x"] + 5, self.another_recipe_button_rect["y"] + 4, "Fazer outra?", 7)

            pyxel.rectb(self.show_list_button_rect["x"], self.show_list_button_rect["y"],
                        self.show_list_button_rect["w"], self.show_list_button_rect["h"], 7)
            pyxel.text(self.show_list_button_rect["x"] + 10, self.show_list_button_rect["y"] + 4, "Ver lista", 7)

        elif self.game_state == "show_list":
            # Tela com a lista de receitas feitas
            pyxel.text(WINDOW_WIDTH // 2 - 20, 20, "Receitas Feitas:", 7)
            y_offset = 0
            for receita in self.receitas_concluidas:
                text_width = len(receita) * 4
                x_pos = (WINDOW_WIDTH - text_width) // 2
                pyxel.text(x_pos, 40 + y_offset, receita, 10)
                y_offset += 10
            
            pyxel.text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT - 20, "Pressione 'R' para recomecar.", 7)

        elif self.game_state == "game_over":
            # Tela de Game Over
            pyxel.rect(0, WINDOW_HEIGHT // 2 - 20, WINDOW_WIDTH, 40, 0)
            pyxel.text(WINDOW_WIDTH // 2 - len(self.message) * 2, WINDOW_HEIGHT // 2 - 10, self.message, 7)
            pyxel.text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 + 10, "Pressione 'R' para reiniciar.", 7)

# Executa a classe principal do jogo
CozinhaGame()