import sys
import pygame
from video_player import CoverManager, resource_path

# Paleta de Cores Sofisticada (Estilo Noir / Tribunal / Glassmorphism)
COLOR_WHITE = (255, 255, 255)
COLOR_GOLD = (235, 190, 80)
COLOR_GOLD_HOVER = (255, 225, 130)
COLOR_CRIMSON = (220, 60, 60)
COLOR_CRIMSON_HOVER = (255, 90, 90)
COLOR_TEXT_MUTED = (200, 205, 220)
COLOR_BG_CARD = (15, 18, 26)
COLOR_ACCENT_GOLD = (195, 155, 60)
COLOR_ACCENT_CRIMSON = (180, 40, 50)


class Button:
    def __init__(self, text, x, y, width, height, action=None, accent_color=COLOR_ACCENT_GOLD, hover_color=COLOR_GOLD_HOVER):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.base_rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.accent_color = accent_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.hover_progress = 0.0

    def set_position(self, x, y, width=None, height=None):
        w = width if width is not None else self.base_rect.width
        h = height if height is not None else self.base_rect.height
        self.base_rect = pygame.Rect(x, y, w, h)
        self.rect = pygame.Rect(x, y, w, h)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target - self.hover_progress) * 0.22

    def draw(self, screen, font):
        # Efeito de elevação sutil no hover
        offset_y = int(self.hover_progress * -3)
        current_rect = self.base_rect.move(0, offset_y)
        self.rect = current_rect

        # Fundo glassmorphism translúcido
        bg_surface = pygame.Surface((current_rect.width, current_rect.height), pygame.SRCALPHA)
        alpha = int(140 + self.hover_progress * 80)
        pygame.draw.rect(bg_surface, (18, 20, 28, alpha), bg_surface.get_rect(), border_radius=8)

        # Borda com brilho adaptativo
        border_r = int(self.accent_color[0] + self.hover_progress * (self.hover_color[0] - self.accent_color[0]))
        border_g = int(self.accent_color[1] + self.hover_progress * (self.hover_color[1] - self.accent_color[1]))
        border_b = int(self.accent_color[2] + self.hover_progress * (self.hover_color[2] - self.accent_color[2]))
        border_alpha = int(150 + self.hover_progress * 105)
        border_color = (border_r, border_g, border_b, border_alpha)

        pygame.draw.rect(bg_surface, border_color, bg_surface.get_rect(), width=2, border_radius=8)
        screen.blit(bg_surface, current_rect.topleft)

        # Texto do botão
        text_color = self.hover_color if self.hover_progress > 0.5 else COLOR_WHITE
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=current_rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                self.action()


class ChoiceCard:
    """Card interativo para o sistema de escolhas da história."""
    def __init__(self, title, description, x, y, width, height, action=None, accent_color=COLOR_ACCENT_GOLD, hover_color=COLOR_GOLD_HOVER):
        self.title = title
        self.description = description
        self.rect = pygame.Rect(x, y, width, height)
        self.base_rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.accent_color = accent_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.hover_progress = 0.0

    def set_position(self, x, y, width=None, height=None):
        w = width if width is not None else self.base_rect.width
        h = height if height is not None else self.base_rect.height
        self.base_rect = pygame.Rect(x, y, w, h)
        self.rect = pygame.Rect(x, y, w, h)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target - self.hover_progress) * 0.2

    def draw(self, screen, font_title, font_desc):
        offset_y = int(self.hover_progress * -4)
        current_rect = self.base_rect.move(0, offset_y)
        self.rect = current_rect

        bg_surface = pygame.Surface((current_rect.width, current_rect.height), pygame.SRCALPHA)
        alpha = int(160 + self.hover_progress * 70)
        pygame.draw.rect(bg_surface, (14, 16, 24, alpha), bg_surface.get_rect(), border_radius=10)

        # Borda com destaque
        border_r = int(self.accent_color[0] + self.hover_progress * (self.hover_color[0] - self.accent_color[0]))
        border_g = int(self.accent_color[1] + self.hover_progress * (self.hover_color[1] - self.accent_color[1]))
        border_b = int(self.accent_color[2] + self.hover_progress * (self.hover_color[2] - self.accent_color[2]))
        border_alpha = int(160 + self.hover_progress * 95)
        border_width = 3 if self.hover_progress > 0.5 else 2

        pygame.draw.rect(bg_surface, (border_r, border_g, border_b, border_alpha), bg_surface.get_rect(), width=border_width, border_radius=10)
        screen.blit(bg_surface, current_rect.topleft)

        # Título da Escolha
        title_color = self.hover_color if self.hover_progress > 0.4 else COLOR_WHITE
        title_surf = font_title.render(self.title, True, title_color)
        screen.blit(title_surf, (current_rect.x + 24, current_rect.y + 18))

        # Descrição / Consequência da Escolha
        desc_color = COLOR_WHITE if self.hover_progress > 0.5 else COLOR_TEXT_MUTED
        desc_surf = font_desc.render(self.description, True, desc_color)
        screen.blit(desc_surf, (current_rect.x + 24, current_rect.y + 52))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                self.action()


class MainMenu:
    STATE_MAIN_MENU = "menu"
    STATE_STORY_CHOICES = "story"
    STATE_BAD_ENDING_1 = "bad_ending_1"
    STATE_COVERS_GALLERY = "covers"

    def __init__(self, screen_width=1280, screen_height=720):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("VEREDITO: A Balança do Poder")

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        # Gerenciador de Capas e Áudio
        self.cover_manager = CoverManager()

        # Fontes do Jogo
        self.font_title = pygame.font.SysFont("georgia", 50, bold=True)
        self.font_subtitle = pygame.font.SysFont("arial", 18, italic=True)
        self.font_story_title = pygame.font.SysFont("georgia", 28, bold=True)
        self.font_story_body = pygame.font.SysFont("arial", 17)
        self.font_btn = pygame.font.SysFont("arial", 20, bold=True)
        self.font_choice_title = pygame.font.SysFont("arial", 20, bold=True)
        self.font_choice_desc = pygame.font.SysFont("arial", 15)
        self.font_small = pygame.font.SysFont("consolas", 13)

        # Estado da Aplicação
        self.current_state = self.STATE_MAIN_MENU
        self.running = True
        self.show_ui = True  # Pressione 'H' para ocultar/mostrar a interface e ver o vídeo completo

        self._setup_ui()

    def _setup_ui(self):
        """Inicializa todos os botões e cards de escolhas."""
        # --- Botões do Menu Principal ---
        btn_w, btn_h = 280, 50
        start_x = 90
        start_y = 300
        gap = 62

        self.menu_buttons = [
            Button("NOVO JOGO (HISTÓRIA)", start_x, start_y, btn_w, btn_h, action=self.open_story_mode),
            Button("CAPAS / FINAIS", start_x, start_y + gap, btn_w, btn_h, action=self.open_covers_gallery),
            Button("ALTERNAR CAPA [C]", start_x, start_y + gap * 2, btn_w, btn_h, action=self.cover_manager.toggle_cover),
            Button("SAIR", start_x, start_y + gap * 3, btn_w, btn_h, action=self.quit_game),
        ]

        # --- Cards de Escolha da História ---
        choice_w = 780
        choice_h = 85
        choice_x = 90
        choice_y = 350
        choice_gap = 100

        self.choice_cards = [
            ChoiceCard(
                title="1. RECUSAR O SUBORNO",
                description="Manter a integridade judicial, rejeitar o dinheiro e ordenar a investigação do réu.",
                x=choice_x, y=choice_y, width=choice_w, height=choice_h,
                action=self.on_choice_justice,
                accent_color=COLOR_ACCENT_GOLD,
                hover_color=COLOR_GOLD_HOVER
            ),
            ChoiceCard(
                title="2. ACEITAR A PROPOSTA ILÍCITA",
                description="Receber a fortuna, ocultar os documentos e decretar a absolvição imediata.",
                x=choice_x, y=choice_y + choice_gap, width=choice_w, height=choice_h,
                action=self.on_choice_bad_ending_1,
                accent_color=COLOR_ACCENT_CRIMSON,
                hover_color=COLOR_CRIMSON_HOVER
            )
        ]

        self.btn_back_story = Button("VOLTAR AO MENU", choice_x, choice_y + choice_gap * 2 + 10, 240, 48, action=self.open_main_menu)

        # --- Botões da Tela de Final Ruim 1 ---
        self.btn_retry_bad = Button("TENTAR NOVAMENTE", choice_x, 500, 260, 50, action=self.open_story_mode)
        self.btn_menu_bad = Button("MENU PRINCIPAL", choice_x + 280, 500, 260, 50, action=self.open_main_menu)

        # --- Botões da Galeria de Capas ---
        gal_x = 90
        gal_y = 280
        gal_w = 480
        gal_h = 70
        gal_gap = 85

        self.gallery_buttons = [
            ChoiceCard(
                title="CAPA PRINCIPAL (Padrão)",
                description="Vídeo em loop Ping-Pong contínuo de alta fluidez.",
                x=gal_x, y=gal_y, width=gal_w, height=gal_h,
                action=lambda: self.cover_manager.set_cover(CoverManager.COVER_PRINCIPAL),
                accent_color=COLOR_ACCENT_GOLD,
                hover_color=COLOR_GOLD_HOVER
            ),
            ChoiceCard(
                title="FINAL RUIM 1 (Animação Estendida)",
                description="Loop sequencial Parte 1 + Parte 2 com trilha sonora e pausa de 2s.",
                x=gal_x, y=gal_y + gal_gap, width=gal_w, height=gal_h,
                action=lambda: self.cover_manager.set_cover(CoverManager.COVER_FINAL_RUIM_1),
                accent_color=COLOR_ACCENT_CRIMSON,
                hover_color=COLOR_CRIMSON_HOVER
            ),
        ]
        self.btn_back_gallery = Button("VOLTAR AO MENU", gal_x, gal_y + gal_gap * 2 + 20, 240, 48, action=self.open_main_menu)

    # Navegação de Estados
    def open_main_menu(self):
        self.current_state = self.STATE_MAIN_MENU

    def open_story_mode(self):
        # Ao reiniciar o caso, restaura a capa principal para o julgamento
        self.cover_manager.set_cover(CoverManager.COVER_PRINCIPAL)
        self.current_state = self.STATE_STORY_CHOICES

    def open_covers_gallery(self):
        self.current_state = self.STATE_COVERS_GALLERY

    def on_choice_justice(self):
        print("[História] O jogador escolheu o Caminho da Justiça.")
        # Mantém a capa principal ou avança
        self.cover_manager.set_cover(CoverManager.COVER_PRINCIPAL)

    def on_choice_bad_ending_1(self):
        print("[História] Escolha fatal! Desencadeando FINAL RUIM 1...")
        # Ativa a animação de final ruim estendida (Parte 1 -> Parte 2 em loop) + Trilha Sonora com pausa de 2s
        self.cover_manager.set_cover(CoverManager.COVER_FINAL_RUIM_1)
        self.current_state = self.STATE_BAD_ENDING_1

    def quit_game(self):
        self.running = False

    def handle_events(self):
        for event in pygame.event.get():
            # Encaminha eventos para o gerenciador de capa e áudio
            self.cover_manager.handle_event(event)

            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_state != self.STATE_MAIN_MENU:
                        self.current_state = self.STATE_MAIN_MENU
                    else:
                        self.running = False
                elif event.key == pygame.K_h:
                    self.show_ui = not self.show_ui  # Alterna visibilidade da interface
                elif event.key == pygame.K_c:
                    self.cover_manager.toggle_cover()  # Atalho para trocar de capa rapidamente
                elif event.key == pygame.K_1:
                    self.cover_manager.set_cover(CoverManager.COVER_PRINCIPAL)
                elif event.key == pygame.K_2:
                    self.cover_manager.set_cover(CoverManager.COVER_FINAL_RUIM_1)
                    if self.current_state == self.STATE_STORY_CHOICES:
                        self.current_state = self.STATE_BAD_ENDING_1
                elif event.key == pygame.K_m:
                    # Atalho de teste para adiantar a música perto do fim e verificar o loop de 2s
                    self.cover_manager.audio.fast_forward_near_end()

            elif event.type == pygame.VIDEORESIZE:
                self.screen_width, self.screen_height = event.w, event.h
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)

            # Processamento de clique dos botões e cards de acordo com o estado
            if self.show_ui:
                if self.current_state == self.STATE_MAIN_MENU:
                    for btn in self.menu_buttons:
                        btn.handle_event(event)
                elif self.current_state == self.STATE_STORY_CHOICES:
                    for card in self.choice_cards:
                        card.handle_event(event)
                    self.btn_back_story.handle_event(event)
                elif self.current_state == self.STATE_BAD_ENDING_1:
                    self.btn_retry_bad.handle_event(event)
                    self.btn_menu_bad.handle_event(event)
                elif self.current_state == self.STATE_COVERS_GALLERY:
                    for card in self.gallery_buttons:
                        card.handle_event(event)
                    self.btn_back_gallery.handle_event(event)

    def update(self):
        # Atualiza frames do vídeo e controle de música (com intervalo de 2s)
        self.cover_manager.update()

        # Atualiza animações de hover da interface
        if self.show_ui:
            mouse_pos = pygame.mouse.get_pos()
            if self.current_state == self.STATE_MAIN_MENU:
                for btn in self.menu_buttons:
                    btn.update(mouse_pos)
            elif self.current_state == self.STATE_STORY_CHOICES:
                for card in self.choice_cards:
                    card.update(mouse_pos)
                self.btn_back_story.update(mouse_pos)
            elif self.current_state == self.STATE_BAD_ENDING_1:
                self.btn_retry_bad.update(mouse_pos)
                self.btn_menu_bad.update(mouse_pos)
            elif self.current_state == self.STATE_COVERS_GALLERY:
                for card in self.gallery_buttons:
                    card.update(mouse_pos)
                self.btn_back_gallery.update(mouse_pos)

    def draw(self):
        # 1. Renderiza o Plano de Fundo Dinâmico (Capa Principal ou Final Ruim 1)
        # Durante a transição de 0.5s entre vídeos, apenas o plano de fundo fica preto
        self.cover_manager.draw(self.screen)

        # 2. Desenha a interface por cima do fundo (mantendo o jogo interativo e visível)
        if self.show_ui:
            if self.current_state == self.STATE_MAIN_MENU:
                self._draw_main_menu()
            elif self.current_state == self.STATE_STORY_CHOICES:
                self._draw_story_choices()
            elif self.current_state == self.STATE_BAD_ENDING_1:
                self._draw_bad_ending()
            elif self.current_state == self.STATE_COVERS_GALLERY:
                self._draw_covers_gallery()

            # Rodapé informativo com status de vídeo, capa e música
            self._draw_footer()

        pygame.display.flip()

    def _draw_main_menu(self):
        # Painel lateral degradê com estilo glassmorphism
        panel = pygame.Surface((460, self.screen_height), pygame.SRCALPHA)
        for x in range(460):
            alpha = int(185 * (1.0 - (x / 460) ** 1.3))
            pygame.draw.line(panel, (10, 12, 18, alpha), (x, 0), (x, self.screen_height))
        self.screen.blit(panel, (0, 0))

        # Título
        title_shadow = self.font_title.render("VEREDITO", True, (0, 0, 0))
        title_surf = self.font_title.render("VEREDITO", True, COLOR_GOLD)
        self.screen.blit(title_shadow, (92, 122))
        self.screen.blit(title_surf, (90, 120))

        # Subtítulo
        sub_surf = self.font_subtitle.render("A Balança do Poder", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub_surf, (94, 182))

        # Linha divisória dourada estilizada
        pygame.draw.line(self.screen, COLOR_ACCENT_GOLD, (90, 220), (340, 220), 2)

        # Botões
        for btn in self.menu_buttons:
            btn.draw(self.screen, self.font_btn)

    def _draw_story_choices(self):
        # Caixa de narrativa central com glassmorphism
        panel = pygame.Surface((880, 560), pygame.SRCALPHA)
        pygame.draw.rect(panel, (12, 14, 22, 215), panel.get_rect(), border_radius=12)
        pygame.draw.rect(panel, (*COLOR_ACCENT_GOLD, 160), panel.get_rect(), width=2, border_radius=12)
        self.screen.blit(panel, (70, 70))

        # Cabeçalho da História
        title_surf = self.font_story_title.render("CASO 01: O JULGAMENTO DA CÚPULA", True, COLOR_GOLD)
        self.screen.blit(title_surf, (95, 95))

        sub_surf = self.font_subtitle.render("Sessão Extraordinária do Tribunal | A sua decisão alterará as capas e o destino do jogo", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub_surf, (95, 140))

        pygame.draw.line(self.screen, COLOR_ACCENT_GOLD, (95, 175), (880, 175), 1)

        # Contexto Narrativo
        lines = [
            "Você é o magistrado encarregado de julgar os poderosos magnatas acusados de subverter o Estado.",
            "Antes de entrar em plenário, um intermediário deixou em sua mesa uma mala com milhões de dólares,",
            "acompanhada de dossiês adulterados para declarar a inocência dos réus.",
            "Qual será o seu veredito?",
        ]
        for i, line in enumerate(lines):
            line_surf = self.font_story_body.render(line, True, COLOR_WHITE)
            self.screen.blit(line_surf, (95, 195 + i * 28))

        # Cards de Escolha
        for card in self.choice_cards:
            card.draw(self.screen, self.font_choice_title, self.font_choice_desc)

        self.btn_back_story.draw(self.screen, self.font_btn)

    def _draw_bad_ending(self):
        # Painel dramático avermelhado para o Final Ruim
        panel = pygame.Surface((880, 540), pygame.SRCALPHA)
        pygame.draw.rect(panel, (24, 10, 14, 225), panel.get_rect(), border_radius=12)
        pygame.draw.rect(panel, (*COLOR_CRIMSON, 200), panel.get_rect(), width=3, border_radius=12)
        self.screen.blit(panel, (70, 70))

        # Título Dramático
        title_shadow = self.font_story_title.render("FINAL RUIM 1: A BALANÇA CORROMPIDA", True, (0, 0, 0))
        title_surf = self.font_story_title.render("FINAL RUIM 1: A BALANÇA CORROMPIDA", True, COLOR_CRIMSON_HOVER)
        self.screen.blit(title_shadow, (97, 102))
        self.screen.blit(title_surf, (95, 100))

        sub_surf = self.font_subtitle.render("A justiça pereceu sob o peso da ganância.", True, (250, 190, 190))
        self.screen.blit(sub_surf, (95, 145))

        pygame.draw.line(self.screen, COLOR_CRIMSON, (95, 180), (880, 180), 2)

        # Texto do Desfecho
        lines = [
            "Você aceitou o suborno e queimou os autos verdadeiros do processo.",
            "A capa foi consumida pela ruína: a animação estendida (Partes 1 e 2) agora roda em loop contínuo,",
            "ao som da marcha fúnebre da justiça ('msc final ruim 1').",
            "A música toca continuamente durante as animações e reinicia após 2 segundos de silêncio.",
            "Sua autoridade foi desmantelada e seu legado agora pertence às sombras."
        ]
        for i, line in enumerate(lines):
            line_surf = self.font_story_body.render(line, True, COLOR_WHITE)
            self.screen.blit(line_surf, (95, 205 + i * 32))

        # Botões de Ação
        self.btn_retry_bad.draw(self.screen, self.font_btn)
        self.btn_menu_bad.draw(self.screen, self.font_btn)

    def _draw_covers_gallery(self):
        # Painel da Galeria de Capas
        panel = pygame.Surface((640, 520), pygame.SRCALPHA)
        pygame.draw.rect(panel, (12, 14, 22, 215), panel.get_rect(), border_radius=12)
        pygame.draw.rect(panel, (*COLOR_ACCENT_GOLD, 160), panel.get_rect(), width=2, border_radius=12)
        self.screen.blit(panel, (70, 70))

        title_surf = self.font_story_title.render("GALERIA DE CAPAS & FINAIS", True, COLOR_GOLD)
        self.screen.blit(title_surf, (95, 95))

        sub_surf = self.font_subtitle.render("Selecione qual plano de fundo deseja ativar em tempo real:", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub_surf, (95, 140))

        pygame.draw.line(self.screen, COLOR_ACCENT_GOLD, (95, 175), (660, 175), 1)

        # Cards da Galeria
        for card in self.gallery_buttons:
            card.draw(self.screen, self.font_choice_title, self.font_choice_desc)

        self.btn_back_gallery.draw(self.screen, self.font_btn)

    def _draw_footer(self):
        """Rodapé exibindo status atual da capa, vídeo, áudio e atalhos rápidos."""
        status_info = self.cover_manager.get_status_text()
        footer_text = f"{status_info}  |  [1] Capa Normal  |  [2] Final Ruim  |  [C] Trocar  |  [H] Ocultar UI  |  [ESC] Menu"
        status_surf = self.font_small.render(footer_text, True, (215, 220, 235))

        # Faixa escura suave no rodapé para máxima legibilidade
        footer_bg = pygame.Surface((self.screen_width, 28), pygame.SRCALPHA)
        footer_bg.fill((8, 10, 15, 200))
        self.screen.blit(footer_bg, (0, self.screen_height - 28))

        self.screen.blit(status_surf, (15, self.screen_height - 23))

    def run(self):
        print("[Menu] Jogo iniciado com sucesso. Pressione ESC para sair.")
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            # 60 FPS garantem interface ágil e suave
            self.clock.tick(60)

        self.cleanup()

    def cleanup(self):
        print("[Menu] Encerrando o jogo e liberando recursos...")
        self.cover_manager.release()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
