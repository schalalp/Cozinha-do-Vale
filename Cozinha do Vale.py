import pyxel

# Caminhos para as imagens
BACKGROUND_IMAGE = "cozinhafoda.png"
MESA_IMAGE = "mesa.png"

class Jogo:
    def __init__(self):
        # Inicializa a tela
        pyxel.init(160, 120)

        # Título da janela
        try:
            pyxel.window_caption = "Cozinha do Vale"
        except AttributeError:
            pass

        # Carregar o fundo no banco 0
        pyxel.image(0).load(0, 0, BACKGROUND_IMAGE)

        # Carregar a mesa no banco 1
        pyxel.image(1).load(0, 0, MESA_IMAGE)

        pyxel.run(self.update, self.draw)

    def update(self):
        pass

    def draw(self):
        pyxel.cls(0)  # limpa a tela

        # Desenha o fundo
        pyxel.blt(0, 0, 0, 0, 0, 160, 120)

        # Desenha a mesa centralizada embaixo (no chão)
        pyxel.blt(56, 72, 1, 0, 0, 48, 48, 0)

Jogo()
