import sys
import pygame
from video_player import PingPongVideoBackground, resource_path

# Cores e Estilos do Menu
COLOR_WHITE = (255, 255, 255)
COLOR_GOLD = (235, 190, 80)
COLOR_GOLD_HOVER = (255, 220, 120)
COLOR_BG_DARK = (15, 18, 25, 180)
COLOR_ACCENT = (195, 155, 60)

class Button:
    def __init__(self, text, x, y, width, height, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.base_rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.is_hovered = False
        self.hover_progress = 0.0  # Para animação suave

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        # Suavização da transição de hover
        target = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target - self.hover_progress) * 0.2

    def draw(self, screen, font):
        # Efeito de elevação sutil no hover
        offset_y = int(self.hover_progress * -3)
        current_rect = self.base_rect.move(0, offset_y)
        self.rect = current_rect

        # Superfície com transparência para estilo glassmorphism
        bg_surface = pygame.Surface((current_rect.width, current_rect.height), pygame.SRCALPHA)
        alpha = int(140 + self.hover_progress * 70)
        
        # Cor de fundo do botão
        pygame.draw.rect(bg_surface, (18, 20, 28, alpha), bg_surface.get_rect(), border_radius=8)
        
        # Borda com brilho dourado
        border_color = (
            int(COLOR_ACCENT[0] + self.hover_progress * (COLOR_GOLD_HOVER[0] - COLOR_ACCENT[0])),
            int(COLOR_ACCENT[1] + self.hover_progress * (COLOR_GOLD_HOVER[1] - COLOR_ACCENT[1])),
            int(COLOR_ACCENT[2] + self.hover_progress * (COLOR_GOLD_HOVER[2] - COLOR_ACCENT[2])),
            int(160 + self.hover_progress * 95)
        )
        pygame.draw.rect(bg_surface, border_color, bg_surface.get_rect(), width=2, border_radius=8)
        screen.blit(bg_surface, current_rect.topleft)

        # Renderização do texto
        text_color = COLOR_GOLD_HOVER if self.hover_progress > 0.5 else COLOR_WHITE
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=current_rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                self.action()

class MainMenu:
    def __init__(self, screen_width=1280, screen_height=720):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Menu Principal")

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        # Inicializa o vídeo em loop ping-pong
        self.video_bg = PingPongVideoBackground(
            forward_video_name="parte principal do jogo.mp4",
            reverse_video_name="background_reverse.mp4"
        )

        # Fontes
        self.font_title = pygame.font.SysFont("georgia", 52, bold=True)
        self.font_subtitle = pygame.font.SysFont("arial", 18, italic=True)
        self.font_btn = pygame.font.SysFont("arial", 22, bold=True)
        self.font_small = pygame.font.SysFont("consolas", 14)

        # Estado do Menu
        self.running = True
        self.show_ui = True  # Pressione 'H' para ocultar/mostrar os botões e ver apenas o vídeo

        # Botões do Menu
        btn_w, btn_h = 260, 50
        start_x = 90
        start_y = 340
        gap = 65

        self.buttons = [
            Button("NOVO JOGO", start_x, start_y, btn_w, btn_h, action=self.on_new_game),
            Button("CONTINUAR", start_x, start_y + gap, btn_w, btn_h, action=self.on_continue),
            Button("OPÇÕES", start_x, start_y + gap * 2, btn_w, btn_h, action=self.on_options),
            Button("SAIR", start_x, start_y + gap * 3, btn_w, btn_h, action=self.quit_game),
        ]

    def on_new_game(self):
        print("[Menu] 'NOVO JOGO' selecionado!")

    def on_continue(self):
        print("[Menu] 'CONTINUAR' selecionado!")

    def on_options(self):
        print("[Menu] 'OPÇÕES' selecionado!")

    def quit_game(self):
        self.running = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_h:
                    self.show_ui = not self.show_ui  # Alterna visibilidade da interface
            elif event.type == pygame.VIDEORESIZE:
                self.screen_width, self.screen_height = event.w, event.h
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)

            if self.show_ui:
                for btn in self.buttons:
                    btn.handle_event(event)

    def update(self):
        # Atualiza os frames do vídeo (controlado pelo framerate natural de 24fps)
        self.video_bg.update()

        # Atualiza botões
        if self.show_ui:
            mouse_pos = pygame.mouse.get_pos()
            for btn in self.buttons:
                btn.update(mouse_pos)

    def draw(self):
        # 1. Desenha o vídeo de fundo (ping-pong)
        self.video_bg.draw(self.screen)

        # 2. Se a interface estiver visível, desenha o painel e os botões
        if self.show_ui:
            # Painel com efeito degradê lateral sutil para destacar os botões
            panel = pygame.Surface((440, self.screen_height), pygame.SRCALPHA)
            for x in range(440):
                alpha = int(180 * (1.0 - (x / 440) ** 1.3))
                pygame.draw.line(panel, (10, 12, 18, alpha), (x, 0), (x, self.screen_height))
            self.screen.blit(panel, (0, 0))

            # Título do Jogo
            title_shadow = self.font_title.render("VEREDITO", True, (0, 0, 0))
            title_surf = self.font_title.render("VEREDITO", True, COLOR_GOLD)
            self.screen.blit(title_shadow, (92, 162))
            self.screen.blit(title_surf, (90, 160))

            # Subtítulo
            sub_surf = self.font_subtitle.render("A Balança do Poder", True, (210, 215, 230))
            self.screen.blit(sub_surf, (94, 225))

            # Linha divisória dourada estilizada
            pygame.draw.line(self.screen, COLOR_ACCENT, (90, 260), (320, 260), 2)

            # Botões
            for btn in self.buttons:
                btn.draw(self.screen, self.font_btn)

            # Informações no rodapé
            direction_label = ">> FRENTE" if self.video_bg.current_direction == "forward" else "<< REVERSO"
            status_text = self.font_small.render(
                f"Vídeo: {direction_label}  |  Loop Ping-Pong Ativo  |  Pressione 'H' para ocultar menu  |  ESC p/ Sair",
                True,
                (200, 200, 200)
            )
            self.screen.blit(status_text, (20, self.screen_height - 30))

        pygame.display.flip()

    def run(self):
        print("[Menu] Jogo iniciado. Pressione ESC para sair.")
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            # 60 FPS no loop de jogo para interface responsiva
            self.clock.tick(60)

        self.cleanup()

    def cleanup(self):
        print("[Menu] Encerrando recursos...")
        self.video_bg.release()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
