import math
import random
import pgzrun
from pygame import Rect

# Constantes do jogo
TAMANHO_GRADE = 32
LARGURA_MUNDO = 20
ALTURA_MUNDO = 15
LARGURA_TELA = LARGURA_MUNDO * TAMANHO_GRADE
ALTURA_TELA = ALTURA_MUNDO * TAMANHO_GRADE + 64

# Estados do jogo
ESTADO_MENU = 0
ESTADO_JOGANDO = 1
ESTADO_FIM_JOGO = 2

teclas_pressionadas = {
    'esquerda': False,
    'direita': False,
    'cima': False,
    'baixo': False
}

class AnimadorSprite:
    def __init__(self, quadros, duracao_quadro=0.2):
        self.quadros = quadros
        self.duracao_quadro = duracao_quadro
        self.quadro_atual = 0
        self.tempo_quadro = 0
        
    def atualizar(self, dt):
        self.tempo_quadro += dt
        if self.tempo_quadro >= self.duracao_quadro:
            self.tempo_quadro = 0
            self.quadro_atual = (self.quadro_atual + 1) % len(self.quadros)
    
    def obter_quadro_atual(self):
        return self.quadros[self.quadro_atual]

class Personagem:
    def __init__(self, x, y, cores_parado, cores_movimento):
        self.grade_x = x
        self.grade_y = y
        self.pixel_x = x * TAMANHO_GRADE
        self.pixel_y = y * TAMANHO_GRADE
        self.alvo_x = self.pixel_x
        self.alvo_y = self.pixel_y
        self.velocidade = 120
        self.movendo = False
        
        self.animador_parado = AnimadorSprite(cores_parado, 0.8)
        self.animador_movimento = AnimadorSprite(cores_movimento, 0.3)
        
    def atualizar(self, dt):
        self.animador_parado.atualizar(dt)
        self.animador_movimento.atualizar(dt)
        
        if self.movendo:
            dx = self.alvo_x - self.pixel_x
            dy = self.alvo_y - self.pixel_y
            distancia = math.sqrt(dx*dx + dy*dy)
            
            if distancia < 2:
                self.pixel_x = self.alvo_x
                self.pixel_y = self.alvo_y
                self.movendo = False
            else:
                distancia_movimento = self.velocidade * dt
                self.pixel_x += (dx / distancia) * distancia_movimento
                self.pixel_y += (dy / distancia) * distancia_movimento
    
    def mover_para(self, grade_x, grade_y):
        if not self.movendo:
            self.grade_x = grade_x
            self.grade_y = grade_y
            self.alvo_x = grade_x * TAMANHO_GRADE
            self.alvo_y = grade_y * TAMANHO_GRADE
            self.movendo = True
    
    def obter_cor_atual(self):
        if self.movendo:
            return self.animador_movimento.obter_quadro_atual()
        else:
            return self.animador_parado.obter_quadro_atual()
    
    def obter_retangulo(self):
        return Rect(self.pixel_x, self.pixel_y, TAMANHO_GRADE, TAMANHO_GRADE)

class Jogador(Personagem):
    def __init__(self, x, y):
        cores_parado = [(0, 255, 0), (0, 200, 0), (0, 255, 50)]
        cores_movimento = [(50, 255, 50), (0, 255, 0), (100, 255, 100), (0, 200, 0)]
        super().__init__(x, y, cores_parado, cores_movimento)
        self.pontuacao = 0
        self.vida = 3

class Inimigo(Personagem):
    def __init__(self, x, y, tipo_inimigo):
        if tipo_inimigo == 'goblin':
            cores_parado = [(255, 0, 0), (200, 0, 0), (255, 50, 50)]
            cores_movimento = [(255, 0, 0), (200, 0, 0), (255, 100, 100), (150, 0, 0)]
        else:  # orc
            cores_parado = [(150, 0, 0), (100, 0, 0), (180, 0, 0)]
            cores_movimento = [(150, 0, 0), (100, 0, 0), (120, 0, 0), (180, 20, 20)]
        
        super().__init__(x, y, cores_parado, cores_movimento)
        self.tipo_inimigo = tipo_inimigo
        self.cronometro_movimento = 0
        self.intervalo_movimento = random.uniform(1.5, 3.5)
        self.centro_territorio_x = x
        self.centro_territorio_y = y
        self.raio_territorio = 4
    
    def atualizar(self, dt):
        super().atualizar(dt)
        
        if not self.movendo:
            self.cronometro_movimento += dt
            if self.cronometro_movimento >= self.intervalo_movimento:
                self.cronometro_movimento = 0
                self.intervalo_movimento = random.uniform(1.5, 3.5)
                self.mover_aleatoriamente()
    
    def mover_aleatoriamente(self):
        direcoes = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(direcoes)
        
        for dx, dy in direcoes:
            novo_x = self.grade_x + dx
            novo_y = self.grade_y + dy
            
            if (0 <= novo_x < LARGURA_MUNDO and 0 <= novo_y < ALTURA_MUNDO):
                distancia_do_centro = math.sqrt(
                    (novo_x - self.centro_territorio_x)**2 + 
                    (novo_y - self.centro_territorio_y)**2
                )
                if distancia_do_centro <= self.raio_territorio:
                    if not jogo.posicao_bloqueada(novo_x, novo_y):
                        self.mover_para(novo_x, novo_y)
                        break

class Jogo:
    def __init__(self):
        self.estado = ESTADO_MENU
        self.musica_ativada = True
        self.som_ativado = True
        self.cronometro_movimento = 0
        self.velocidade_movimento = 0.15 
        self.fase_atual = 1  
        self.reiniciar_jogo()
        
    def reiniciar_jogo(self):
        self.fase_atual = 1
        self.jogador = Jogador(1, 1)
        self.inimigos = []
        self.tesouros = []
        self.paredes = set()
        self.gerar_nivel()
        
    def gerar_nivel(self):
        # Gerar paredes
        for x in range(LARGURA_MUNDO):
            for y in range(ALTURA_MUNDO):
                if x == 0 or x == LARGURA_MUNDO-1 or y == 0 or y == ALTURA_MUNDO-1:
                    self.paredes.add((x, y))
                elif random.random() < 0.12:
                    self.paredes.add((x, y))
        
        # Garantir que área inicial do jogador está livre
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                self.paredes.discard((1 + dx, 1 + dy))
        
        # Gerar inimigos
        contador_inimigos = 0
        tentativas = 0
        while contador_inimigos < 6 and tentativas < 100:
            x = random.randint(4, LARGURA_MUNDO-2)
            y = random.randint(4, ALTURA_MUNDO-2)
            if not self.posicao_bloqueada_apenas_paredes(x, y):
                if math.sqrt((x - 1)**2 + (y - 1)**2) > 3:
                    tipo_inimigo = random.choice(['goblin', 'orc'])
                    # Ajustar velocidade baseado na fase
                    velocidade_inimigo = 1.0 if self.fase_atual == 1 else 0.5  # Fase 2 é mais rápida
                    inimigo = Inimigo(x, y, tipo_inimigo)
                    inimigo.intervalo_movimento = random.uniform(1.5, 3.5) * velocidade_inimigo
                    self.inimigos.append(inimigo)
                    contador_inimigos += 1
            tentativas += 1
        
        # Gerar tesouros em posições acessíveis
        contador_tesouros = 0
        tentativas = 0
        while contador_tesouros < 8 and tentativas < 200:
            x = random.randint(1, LARGURA_MUNDO-2)
            y = random.randint(1, ALTURA_MUNDO-2)
            if (not self.posicao_bloqueada_apenas_paredes(x, y) and 
                math.sqrt((x - 1)**2 + (y - 1)**2) > 1 and
                self.posicao_acessivel(x, y)):
                self.tesouros.append((x, y))
                contador_tesouros += 1
            tentativas += 1
    
    def posicao_acessivel(self, alvo_x, alvo_y):
        """Verifica se é possível chegar até uma posição a partir do spawn do jogador"""
        if (alvo_x, alvo_y) in self.paredes:
            return False
        
        visitados = set()
        fila = [(1, 1)]  # Posição inicial do jogador
        
        while fila:
            x, y = fila.pop(0)
            if (x, y) in visitados:
                continue
            visitados.add((x, y))
            
            if x == alvo_x and y == alvo_y:
                return True
            
            # Verificar todas as 4 direções
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                novo_x, novo_y = x + dx, y + dy
                if (0 <= novo_x < LARGURA_MUNDO and 
                    0 <= novo_y < ALTURA_MUNDO and
                    (novo_x, novo_y) not in self.paredes and
                    (novo_x, novo_y) not in visitados):
                    fila.append((novo_x, novo_y))
        
        return False

    def posicao_bloqueada_apenas_paredes(self, x, y):
        """Verifica apenas paredes e limites, não inimigos"""
        if x < 0 or x >= LARGURA_MUNDO or y < 0 or y >= ALTURA_MUNDO:
            return True
        
        if (x, y) in self.paredes:
            return True
        
        return False

    def avancar_fase(self):
        """Avança para a próxima fase"""
        self.fase_atual += 1
        self.jogador.grade_x = 1
        self.jogador.grade_y = 1
        self.jogador.pixel_x = TAMANHO_GRADE
        self.jogador.pixel_y = TAMANHO_GRADE
        self.jogador.alvo_x = self.jogador.pixel_x
        self.jogador.alvo_y = self.jogador.pixel_y
        self.jogador.movendo = False
        self.inimigos = []
        self.tesouros = []
        self.paredes = set()
        self.gerar_nivel()
    
    def posicao_bloqueada(self, x, y):
            # Verifica limites do mundo
            if x < 0 or x >= LARGURA_MUNDO or y < 0 or y >= ALTURA_MUNDO:
                return True
            
            # Verifica paredes
            if (x, y) in self.paredes:
                return True
            
            # Verifica se há outro inimigo na posição (mas permite movimento do jogador)
            for inimigo in self.inimigos:
                if inimigo.grade_x == x and inimigo.grade_y == y:
                    return True
            
            # NÃO bloqueia se o jogador estiver na posição - permite colisão
            return False
        
    def atualizar(self, dt):
        if self.estado == ESTADO_JOGANDO:
            self.jogador.atualizar(dt)
            
            # Verificar movimento contínuo
            if not self.jogador.movendo:
                self.cronometro_movimento += dt
                if self.cronometro_movimento >= self.velocidade_movimento:
                    self.cronometro_movimento = 0
                    self.processar_movimento_continuo()
            
            for inimigo in self.inimigos:
                inimigo.atualizar(dt)
            
            self.verificar_colisoes()
            self.verificar_tesouros()
            
            # Verificar se todos os tesouros foram coletados
            if len(self.tesouros) == 0:
                if self.fase_atual == 1:
                    self.avancar_fase()
                else:
                    self.estado = ESTADO_FIM_JOGO
    
    def processar_movimento_continuo(self):
        novo_x, novo_y = self.jogador.grade_x, self.jogador.grade_y
        
        if teclas_pressionadas['esquerda'] and novo_x > 0:
            novo_x -= 1
        elif teclas_pressionadas['direita'] and novo_x < LARGURA_MUNDO - 1:
            novo_x += 1
        elif teclas_pressionadas['cima'] and novo_y > 0:
            novo_y -= 1
        elif teclas_pressionadas['baixo'] and novo_y < ALTURA_MUNDO - 1:
            novo_y += 1
        
        if (novo_x, novo_y) != (self.jogador.grade_x, self.jogador.grade_y):
            # Verifica apenas paredes e limites, não inimigos
            if not self.posicao_bloqueada_apenas_paredes(novo_x, novo_y):
                self.jogador.mover_para(novo_x, novo_y)

    def verificar_colisoes(self):
        for inimigo in self.inimigos:
            if (self.jogador.grade_x == inimigo.grade_x and 
                self.jogador.grade_y == inimigo.grade_y):
                # Game Over imediato após colisão
                self.estado = ESTADO_FIM_JOGO
                # Zerar as teclas pressionadas para evitar movimento no game over
                global teclas_pressionadas
                teclas_pressionadas = {
                    'esquerda': False,
                    'direita': False,
                    'cima': False,
                    'baixo': False
                }
                break
    
    def verificar_tesouros(self):
        posicao_jogador = (self.jogador.grade_x, self.jogador.grade_y)
        if posicao_jogador in self.tesouros:
            self.tesouros.remove(posicao_jogador)
            self.jogador.pontuacao += 10

jogo = Jogo()

def update(dt):
    jogo.atualizar(dt)

def draw():
    screen.clear()
    
    if jogo.estado == ESTADO_MENU:
        desenhar_menu()
    elif jogo.estado == ESTADO_JOGANDO:
        desenhar_jogo()
    elif jogo.estado == ESTADO_FIM_JOGO:
        desenhar_fim_jogo()

def desenhar_menu():
    screen.fill((20, 20, 40))
    
    cor_titulo = (255, 255, 255)
    screen.draw.text("EXPLORADOR DE MASMORRAS", center=(LARGURA_TELA//2, 80), 
                    fontsize=36, color=cor_titulo)
    
    botao_iniciar = Rect(LARGURA_TELA//2 - 100, 180, 200, 50)
    botao_musica = Rect(LARGURA_TELA//2 - 100, 250, 200, 50)
    botao_sair = Rect(LARGURA_TELA//2 - 100, 320, 200, 50)
    
    cor_botao = (60, 60, 80)
    screen.draw.filled_rect(botao_iniciar, cor_botao)
    screen.draw.filled_rect(botao_musica, cor_botao)
    screen.draw.filled_rect(botao_sair, cor_botao)
    
    screen.draw.rect(botao_iniciar, (100, 100, 120))
    screen.draw.rect(botao_musica, (100, 100, 120))
    screen.draw.rect(botao_sair, (100, 100, 120))
    
    screen.draw.text("INICIAR JOGO", center=botao_iniciar.center, 
                    fontsize=20, color="white")
    
    texto_musica = f"MÚSICA: {'LIGADA' if jogo.musica_ativada else 'DESLIGADA'}"
    screen.draw.text(texto_musica, center=botao_musica.center, 
                    fontsize=20, color="white")
    
    screen.draw.text("SAIR", center=botao_sair.center, 
                    fontsize=20, color="white")
    
    screen.draw.text("Use as setas para se mover", center=(LARGURA_TELA//2, 400), 
                    fontsize=16, color=(150, 150, 150))
    screen.draw.text("Colete todos os tesouros para vencer!", center=(LARGURA_TELA//2, 420), 
                    fontsize=16, color=(150, 150, 150))

def desenhar_jogo():
    # Fundos diferentes por fase
    if jogo.fase_atual == 1:
        screen.fill((15, 15, 25))  # Azul escuro
    else:
        screen.fill((25, 10, 10))  # Vermelho escuro
    
    # Cor das paredes muda por fase
    cor_parede = (80, 80, 80) if jogo.fase_atual == 1 else (100, 60, 60)
    cor_borda_parede = (60, 60, 60) if jogo.fase_atual == 1 else (80, 40, 40)
    
    for x, y in jogo.paredes:
        ret_parede = Rect(x * TAMANHO_GRADE, y * TAMANHO_GRADE, TAMANHO_GRADE, TAMANHO_GRADE)
        screen.draw.filled_rect(ret_parede, cor_parede)
        screen.draw.rect(ret_parede, cor_borda_parede)
    
    # Resto do código de desenho permanece igual...
    for x, y in jogo.tesouros:
        ret_tesouro = Rect(x * TAMANHO_GRADE + 6, y * TAMANHO_GRADE + 6, 
                          TAMANHO_GRADE - 12, TAMANHO_GRADE - 12)
        screen.draw.filled_rect(ret_tesouro, (255, 215, 0))
        ret_interno = Rect(x * TAMANHO_GRADE + 10, y * TAMANHO_GRADE + 10, 
                          TAMANHO_GRADE - 20, TAMANHO_GRADE - 20)
        screen.draw.filled_rect(ret_interno, (255, 255, 150))
    
    for inimigo in jogo.inimigos:
        ret_inimigo = Rect(inimigo.pixel_x + 2, inimigo.pixel_y + 2, 
                          TAMANHO_GRADE - 4, TAMANHO_GRADE - 4)
        cor = inimigo.obter_cor_atual()
        screen.draw.filled_rect(ret_inimigo, cor)
        tamanho_olho = 4
        olho_esquerdo = Rect(inimigo.pixel_x + 8, inimigo.pixel_y + 8, tamanho_olho, tamanho_olho)
        olho_direito = Rect(inimigo.pixel_x + 20, inimigo.pixel_y + 8, tamanho_olho, tamanho_olho)
        screen.draw.filled_rect(olho_esquerdo, (255, 255, 255))
        screen.draw.filled_rect(olho_direito, (255, 255, 255))
    
    ret_jogador = Rect(jogo.jogador.pixel_x + 1, jogo.jogador.pixel_y + 1, 
                      TAMANHO_GRADE - 2, TAMANHO_GRADE - 2)
    cor = jogo.jogador.obter_cor_atual()
    screen.draw.filled_rect(ret_jogador, cor)
    tamanho_olho = 3
    olho_esquerdo = Rect(jogo.jogador.pixel_x + 8, jogo.jogador.pixel_y + 8, tamanho_olho, tamanho_olho)
    olho_direito = Rect(jogo.jogador.pixel_x + 21, jogo.jogador.pixel_y + 8, tamanho_olho, tamanho_olho)
    screen.draw.filled_rect(olho_esquerdo, (0, 0, 0))
    screen.draw.filled_rect(olho_direito, (0, 0, 0))
    
    ui_y = ALTURA_TELA - 55
    screen.draw.filled_rect(Rect(0, ui_y, LARGURA_TELA, 64), (40, 40, 40))
    
    screen.draw.text(f"Pontuação: {jogo.jogador.pontuacao}", (10, ui_y + 10), 
                    fontsize=20, color="white")
    screen.draw.text(f"Vida: {jogo.jogador.vida}", (10, ui_y + 35), 
                    fontsize=20, color="white")
    screen.draw.text(f"Tesouros: {len(jogo.tesouros)}", (200, ui_y + 10), 
                    fontsize=20, color="white")
    screen.draw.text(f"Fase: {jogo.fase_atual}", (350, ui_y + 10), 
                    fontsize=20, color="white")
    
def desenhar_fim_jogo():
    screen.fill((0, 0, 0))
    
    if jogo.jogador.vida <= 0:
        screen.draw.text("FIM DE JOGO", center=(LARGURA_TELA//2, ALTURA_TELA//2 - 60), 
                        fontsize=42, color=(255, 100, 100))
    else:
        screen.draw.text("VITÓRIA!", center=(LARGURA_TELA//2, ALTURA_TELA//2 - 60), 
                        fontsize=42, color=(100, 255, 100))
    
    screen.draw.text(f"Pontuação Final: {jogo.jogador.pontuacao}", 
                    center=(LARGURA_TELA//2, ALTURA_TELA//2 - 10), 
                    fontsize=28, color="white")
    
    screen.draw.text("Pressione ESPAÇO para voltar ao menu", 
                    center=(LARGURA_TELA//2, ALTURA_TELA//2 + 40), 
                    fontsize=20, color=(200, 200, 200))

def on_mouse_down(pos):
    if jogo.estado == ESTADO_MENU:
        botao_iniciar = Rect(LARGURA_TELA//2 - 100, 180, 200, 50)
        botao_musica = Rect(LARGURA_TELA//2 - 100, 250, 200, 50)
        botao_sair = Rect(LARGURA_TELA//2 - 100, 320, 200, 50)
        
        if botao_iniciar.collidepoint(pos):
            jogo.estado = ESTADO_JOGANDO
            jogo.reiniciar_jogo()
        elif botao_musica.collidepoint(pos):
            jogo.musica_ativada = not jogo.musica_ativada
            jogo.som_ativado = jogo.musica_ativada
        elif botao_sair.collidepoint(pos):
            quit()

def on_key_down(key):
    if jogo.estado == ESTADO_FIM_JOGO and key == keys.SPACE:
        jogo.estado = ESTADO_MENU
    elif jogo.estado == ESTADO_JOGANDO:
        if key == keys.LEFT:
            teclas_pressionadas['esquerda'] = True
        elif key == keys.RIGHT:
            teclas_pressionadas['direita'] = True
        elif key == keys.UP:
            teclas_pressionadas['cima'] = True
        elif key == keys.DOWN:
            teclas_pressionadas['baixo'] = True

def on_key_up(key):
    if jogo.estado == ESTADO_JOGANDO:
        if key == keys.LEFT:
            teclas_pressionadas['esquerda'] = False
        elif key == keys.RIGHT:
            teclas_pressionadas['direita'] = False
        elif key == keys.UP:
            teclas_pressionadas['cima'] = False
        elif key == keys.DOWN:
            teclas_pressionadas['baixo'] = False

# Configuração do pgzero
WIDTH = LARGURA_TELA
HEIGHT = ALTURA_TELA

# Iniciar o jogo
if __name__ == "__main__":
    pgzrun.go()
