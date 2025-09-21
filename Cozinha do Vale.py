import pyxel

#tamanho da janela do jogo
WINDOW_WIDTH = 160
WINDOW_HEIGHT = 120

#classe principal do jogo
class CozinhaGame:
    def __init__(self):
        
        #define o titulo
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT, title="Cozinha do Vale")
        
        #ligar o mouse pra usar ele no jogo
        pyxel.mouse(True)

        
        #imagens do jogo
        pyxel.image(0).load(0, 0, "cozinha final boss.png") 
        pyxel.image(1).load(0, 0, "ovo.png")
        pyxel.image(1).load(32, 0, "leite.png")
        pyxel.image(1).load(48, 0, "farinha.png")
        pyxel.image(1).load(64, 0, "açucar.png")
        pyxel.image(1).load(80, 0, "panela.png") 

        
        # dados dos ingredientes tipo onde eles ficam e se estao sendo arrastados
        self.ingredientes_data = {
            "ovo":      {"name": "ovo",   "x": 9, "y": 37, "x_orig": 9, "y_orig": 37,  "img_u": 0, "img_v": 0,   "dragging": False, "in_area": False},
            "leite":    {"name": "leite",   "x": 20, "y": 37, "x_orig": 20, "y_orig": 37, "img_u": 32, "img_v": 0, "dragging": False, "in_area": False},
            "farinha":  {"name": "farinha", "x": 9, "y": 48, "x_orig": 9, "y_orig": 48, "img_u": 48, "img_v": 0, "dragging": False, "in_area": False},
            "açucar":   {"name": "açucar",  "x": 20, "y": 48, "x_orig": 20, "y_orig": 48, "img_u": 64, "img_v": 0, "dragging": False, "in_area": False},
        }
        
        # panela, que e a area de combinacao
        self.panela_rect = {"x": WINDOW_WIDTH // 2 - 18, "y": WINDOW_HEIGHT // 2 - 10, "w": 32, "h": 32}

        
        self.combination_rect = {"x": self.panela_rect["x"] + 8, "y": self.panela_rect["y"] + 8, "w": 16, "h": 16}

        
        self.combination_slots = [
            {"x": self.combination_rect["x"] - 6, "y": self.combination_rect["y"]},
            {"x": self.combination_rect["x"] + 10, "y": self.combination_rect["y"]}
        ]
        
        # as posicoes e tamanhos dos botoes
        self.confirm_button_rect = {"x": WINDOW_WIDTH // 2 - 35, "y": 71, "w": 50, "h": 15}

        self.another_recipe_button_rect = {"x": WINDOW_WIDTH // 2 - 40, "y": WINDOW_HEIGHT // 2 + 20, "w": 80, "h": 15}
        self.show_list_button_rect = {"x": WINDOW_WIDTH // 2 - 40, "y": WINDOW_HEIGHT // 2 + 40, "w": 80, "h": 15}
        
        self.back_button_rect = {"x": WINDOW_WIDTH // 2 - 40, "y": WINDOW_HEIGHT - 25, "w": 80, "h": 15}
        
        # botao pra comecar o jogo
        self.start_button_rect = {"x": WINDOW_WIDTH // 2 - 40, "y": WINDOW_HEIGHT // 2, "w": 80, "h": 15}


        self.ingredientes_na_area = []

        # as receitas que da pra fazer
        self.receitas_possiveis = {
            frozenset(["ovo", "leite"]): "Bolo Simples",
            frozenset(["farinha", "leite"]): "Bolo de Cenoura",
            frozenset(["farinha", "açucar"]): "Bolo de Chocolate",
        }

        # lista das receitas que ja foram feitas
        self.receitas_concluidas = []

        # comeca o jogo na tela de inicio
        self.game_state = "start_screen" 
        self.message = ""
        
        # pra saber se ja tem algum ingrediente sendo arrastado
        self.dragging_ingredient = None

        # comeca o jogo
        pyxel.run(self.update, self.draw)

    # isso aqui roda toda hora, e a logica do jogo
    def update(self):
        # se for a tela de inicio, ve se o botao de comecar foi clicado
        if self.game_state == "start_screen":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and \
               self.start_button_rect["x"] < pyxel.mouse_x < self.start_button_rect["x"] + self.start_button_rect["w"] and \
               self.start_button_rect["y"] < pyxel.mouse_y < self.start_button_rect["y"] + self.start_button_rect["h"]:
                self.game_state = "playing"
                
        # se o jogo estiver rodando, faz as coisas de drag and drop
        elif self.game_state == "playing":
            # se clicou e nao tem nada sendo arrastado ainda
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.dragging_ingredient is None:
                # checa se o mouse ta em cima de um ingrediente
                for key in list(self.ingredientes_data.keys()):
                    ingrediente = self.ingredientes_data[key]
                    if ingrediente["x_orig"] < pyxel.mouse_x < ingrediente["x_orig"] + 16 and \
                       ingrediente["y_orig"] < pyxel.mouse_y < ingrediente["y_orig"] + 16 and \
                       not ingrediente["in_area"]:
                        self.dragging_ingredient = key
                        ingrediente["dragging"] = True
                        break # para de checar, ja pegou um
            
            # se tem um ingrediente sendo arrastado
            if self.dragging_ingredient:
                ingrediente = self.ingredientes_data[self.dragging_ingredient]
                ingrediente["x"] = pyxel.mouse_x - 8
                ingrediente["y"] = pyxel.mouse_y - 8

                # se soltou o mouse
                if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                    ingrediente["dragging"] = False
                    
                    # se soltou na panela
                    if self.panela_rect["x"] < pyxel.mouse_x < self.panela_rect["x"] + self.panela_rect["w"] and \
                       self.panela_rect["y"] < pyxel.mouse_y < self.panela_rect["y"] + self.panela_rect["h"]:
                        
                        # se o ingrediente nao ta na panela e tem espaco
                        if self.dragging_ingredient not in self.ingredientes_na_area and len(self.ingredientes_na_area) < 2:
                            self.ingredientes_na_area.append(self.dragging_ingredient)
                            self.message = f"{ingrediente['name'].capitalize()} adicionado!"
                            ingrediente["in_area"] = True
                            
                    else:
                        # se soltou fora da panela, volta pro lugar
                        ingrediente["x"] = ingrediente["x_orig"]
                        ingrediente["y"] = ingrediente["y_orig"]
                        ingrediente["in_area"] = False
                    
                    self.dragging_ingredient = None


            # logica do botao de confirmar
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and \
               self.confirm_button_rect["x"] < pyxel.mouse_x < self.confirm_button_rect["x"] + self.confirm_button_rect["w"] and \
               self.confirm_button_rect["y"] < pyxel.mouse_y < self.confirm_button_rect["y"] + self.confirm_button_rect["h"]:
                
                # se tiver dois ingredientes, checa a receita
                if len(self.ingredientes_na_area) == 2:
                    self.check_recipe()
                else:
                    self.message = "Precisa de 2 ingredientes!"
            
            
            # se apertar C, limpa a panela
            if pyxel.btnp(pyxel.KEY_C):
                self.clear_area()

        # se a receita foi feita
        elif self.game_state == "recipe_done":
        
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):

                # ve se o botao de fazer outra receita foi clicado
                if self.another_recipe_button_rect["x"] < pyxel.mouse_x < self.another_recipe_button_rect["x"] + self.another_recipe_button_rect["w"] and \
                   self.another_recipe_button_rect["y"] < pyxel.mouse_y < self.another_recipe_button_rect["y"] + self.another_recipe_button_rect["h"]:
                    self.clear_area() 
                
                # ve se o botao de ver a lista foi clicado
                elif self.show_list_button_rect["x"] < pyxel.mouse_x < self.show_list_button_rect["x"] + self.show_list_button_rect["w"] and \
                        self.show_list_button_rect["y"] < pyxel.mouse_y < self.show_list_button_rect["y"] + self.show_list_button_rect["h"]:
                    self.game_state = "show_list"
        
        # se for a tela da lista de receitas
        elif self.game_state == "show_list":
            # se apertar r, reinicia o jogo todo
            if pyxel.btnp(pyxel.KEY_R):
                self.__init__() 
            
            # ve se o botao de voltar foi clicado
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and \
               self.back_button_rect["x"] < pyxel.mouse_x < self.back_button_rect["x"] + self.back_button_rect["w"] and \
               self.back_button_rect["y"] < pyxel.mouse_y < self.back_button_rect["y"] + self.back_button_rect["h"]:
                self.game_state = "playing" # volta pra cozinha
                self.clear_area() # faz os ingredientes voltarem pra estante

        # se todas as receitas foram feitas, e fim de jogo
        if len(self.receitas_concluidas) == len(self.receitas_possiveis) and self.game_state != "game_over":
            self.game_state = "game_over"
            self.message = "Parabens! Voce fez todas as receitas!"

        # se o jogo acabou e apertou qualquer tecla sai do jogo
        if self.game_state == "game_over" and pyxel.btnp(pyxel.KEY_ANY):
            pyxel.quit()

    # checa a combinacao de ingredientes na panela
    def check_recipe(self):
        ingredientes_atuais = frozenset(self.ingredientes_na_area)
        receita_encontrada = False
        
        # compara o que ta na panela com as receitas que existem
        for receita_ingredientes, nome_receita in self.receitas_possiveis.items():
            if ingredientes_atuais == receita_ingredientes:
                if nome_receita not in self.receitas_concluidas:
                    self.receitas_concluidas.append(nome_receita)
                    self.message = f"Voce fez: {nome_receita}!"
                else:
                    self.message = "Voce ja fez essa receita!"
                
                receita_encontrada = True
                break
        
        # se nao achou a receita, manda uma mensagem
        if not receita_encontrada:
            self.message = "Essa combinacao nao faz nada!"
        
        # muda o estado do jogo pra tela de receita feita
        self.game_state = "recipe_done" 

    # faz os ingredientes voltarem pro lugar
    def clear_area(self):
        for ingrediente_key in self.ingredientes_na_area:
            ingrediente = self.ingredientes_data.get(ingrediente_key)
            if ingrediente:
                ingrediente["x"] = ingrediente["x_orig"]
                ingrediente["y"] = ingrediente["y_orig"]
                ingrediente["in_area"] = False
                ingrediente["dragging"] = False
            
        self.ingredientes_na_area.clear()
        self.message = "" 
        self.game_state = "playing" 

    def draw(self):
        pyxel.cls(0) # limpa a tela
        
        # desenha a tela de inicio
        if self.game_state == "start_screen":
            pyxel.cls(14) # fundo rosa
            title_text = "Cozinha do Vale"
            title_width = len(title_text) * 4
            pyxel.text(WINDOW_WIDTH // 2 - title_width // 2, WINDOW_HEIGHT // 2 - 20, title_text, 7)
            
            # desenha o botao de comecar
            pyxel.rectb(self.start_button_rect["x"], self.start_button_rect["y"], 
                        self.start_button_rect["w"], self.start_button_rect["h"], 7)
            
            button_text = "Iniciar Jogo"
            text_width = len(button_text) * 4
            text_x = self.start_button_rect["x"] + (self.start_button_rect["w"] - text_width) // 2
            pyxel.text(text_x, self.start_button_rect["y"] + 4, button_text, 7)

        # desenha a tela do jogo
        elif self.game_state == "playing":
            # desenha o fundo da cozinha
            pyxel.blt(0, 0, 0, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, colkey = 11)
            # desenha a panela
            pyxel.blt(self.panela_rect["x"], self.panela_rect["y"], 1, 80, 0, 32, 32, colkey=0)

            # desenha os ingredientes na prateleira
            for key, ingrediente in self.ingredientes_data.items():
                if not ingrediente["in_area"]:
                    pyxel.blt(ingrediente["x"], ingrediente["y"], 1, 
                              ingrediente["img_u"], ingrediente["img_v"], 
                              16, 16, 0)
            
            # desenha o botao de confirmar
            pyxel.rectb(self.confirm_button_rect["x"], self.confirm_button_rect["y"], 
                        self.confirm_button_rect["w"], self.confirm_button_rect["h"], 7)
            
            # texto do botao
            text_width = len("Confirmar") * 4
            text_x = self.confirm_button_rect["x"] + (self.confirm_button_rect["w"] - text_width) // 2
            pyxel.text(text_x, self.confirm_button_rect["y"] + 4, "Confirmar", 7)
            
            # desenha a mensagem na tela
            if self.message:
                message_width = len(self.message) * 4
                pyxel.text(WINDOW_WIDTH // 2 - message_width // 2, WINDOW_HEIGHT - 10, self.message, 7)

        # desenha a tela de receita feita
        elif self.game_state == "recipe_done":
            pyxel.cls(0) # tela preta
            
            message_width = len(self.message) * 4 
            pyxel.text(WINDOW_WIDTH // 2 - message_width // 2, WINDOW_HEIGHT // 2 - 10, self.message, 7)

            # desenha os botoes
            pyxel.rectb(self.another_recipe_button_rect["x"], self.another_recipe_button_rect["y"],
                        self.another_recipe_button_rect["w"], self.another_recipe_button_rect["h"], 7)
            pyxel.text(self.another_recipe_button_rect["x"] + 5, self.another_recipe_button_rect["y"] + 4, "Fazer outra?", 7)

            pyxel.rectb(self.show_list_button_rect["x"], self.show_list_button_rect["y"],
                        self.show_list_button_rect["w"], self.show_list_button_rect["h"], 7)
            pyxel.text(self.show_list_button_rect["x"] + 10, self.show_list_button_rect["y"] + 4, "Ver lista", 7)

        # desenha a tela da lista de receitas
        elif self.game_state == "show_list":
            pyxel.cls(0) # tela preta
            
            pyxel.text(WINDOW_WIDTH // 2 - 20, 20, "Receitas Feitas:", 7)
            y_offset = 0
            for receita in self.receitas_concluidas:
                text_width = len(receita) * 4
                x_pos = (WINDOW_WIDTH - text_width) // 2
                pyxel.text(x_pos, 40 + y_offset, receita, 10)
                y_offset += 10
            
            # desenha o botao de voltar
            pyxel.rectb(self.back_button_rect["x"], self.back_button_rect["y"], 
                        self.back_button_rect["w"], self.back_button_rect["h"], 7)
            pyxel.text(self.back_button_rect["x"] + 10, self.back_button_rect["y"] + 4, "Voltar", 7)

        # desenha a tela de fim de jogo
        elif self.game_state == "game_over":
            pyxel.cls(14) # tela final rosa
            
            pyxel.text(WINDOW_WIDTH // 2 - len(self.message) * 2, WINDOW_HEIGHT // 2 - 10, self.message, 7)
            # mensagem pra sair do jogo
            pyxel.text(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 + 10, "Pressione qualquer tecla para sair.", 7)


CozinhaGame()
