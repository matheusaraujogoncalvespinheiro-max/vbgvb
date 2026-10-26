import os
import sys
import time
import cv2
import pygame

def resource_path(relative_path: str) -> str:
    """Retorna o caminho absoluto para recursos, funcionando em dev e no executável compilado."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    path = os.path.join(base_path, relative_path)
    if os.path.exists(path):
        return path

    # Fallbacks para compatibilidade com diferentes versões do PyInstaller
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        for candidate in [
            os.path.join(exe_dir, relative_path),
            os.path.join(exe_dir, "_internal", relative_path)
        ]:
            if os.path.exists(candidate):
                return candidate

    return path


class PingPongVideoBackground:
    """
    Gerenciador de vídeo de fundo em loop ping-pong (frente -> reverso -> frente -> ...).
    Utiliza dois arquivos de vídeo para máxima performance e zero travamentos.
    Suporta controle de velocidade (ex: 0.8x).
    """
    def __init__(self, forward_video_name="parte principal do jogo.mp4", reverse_video_name="background_reverse.mp4", speed: float = 0.8):
        self.forward_name = forward_video_name
        self.reverse_name = reverse_video_name
        self.forward_path = resource_path(forward_video_name)
        self.reverse_path = resource_path(reverse_video_name)
        self.speed = max(0.1, speed)

        # Se o vídeo reverso ainda não existe, cria automaticamente a partir do original
        if not os.path.exists(self.reverse_path) and os.path.exists(self.forward_path):
            print(f"[VideoBackground] Gerando vídeo reverso otimizado: {reverse_video_name}...")
            self._generate_reverse_video(self.forward_path, self.reverse_path)

        self.cap_fwd = cv2.VideoCapture(self.forward_path)
        self.cap_rev = cv2.VideoCapture(self.reverse_path)

        self.base_fps = self.cap_fwd.get(cv2.CAP_PROP_FPS) or 24.0
        self.fps = self.base_fps * self.speed
        self.frame_duration = 1.0 / self.fps

        self.current_direction = "forward"  # "forward" ou "reverse"
        self.current_surface = None
        self.last_frame_time = time.time()

        # Lê o primeiro frame para inicializar
        self._read_next_frame()

    def _generate_reverse_video(self, source_path: str, target_path: str):
        cap = cv2.VideoCapture(source_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(target_path, fourcc, fps, (w, h))
        for f in reversed(frames):
            out.write(f)
        out.release()
        print(f"[VideoBackground] Vídeo reverso gerado com sucesso ({len(frames)} frames).")

    def _read_next_frame(self):
        active_cap = self.cap_fwd if self.current_direction == "forward" else self.cap_rev
        ret, frame = active_cap.read()

        if not ret:
            # Chegou ao fim do vídeo atual: inverte a direção
            if self.current_direction == "forward":
                self.current_direction = "reverse"
                self.cap_fwd.set(cv2.CAP_PROP_POS_FRAMES, 0)
                active_cap = self.cap_rev
                active_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                self.current_direction = "forward"
                self.cap_rev.set(cv2.CAP_PROP_POS_FRAMES, 0)
                active_cap = self.cap_fwd
                active_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            ret, frame = active_cap.read()

        if ret and frame is not None:
            h, w, _ = frame.shape
            self.current_surface = pygame.image.frombuffer(frame.data, (w, h), 'BGR')

    def reset(self):
        self.current_direction = "forward"
        if self.cap_fwd.isOpened():
            self.cap_fwd.set(cv2.CAP_PROP_POS_FRAMES, 0)
        if self.cap_rev.isOpened():
            self.cap_rev.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.last_frame_time = time.time()
        self._read_next_frame()

    def update(self):
        """Atualiza o frame de acordo com o framerate do vídeo ajustado pela velocidade."""
        now = time.time()
        elapsed = now - self.last_frame_time

        if elapsed >= self.frame_duration:
            frames_to_advance = int(elapsed // self.frame_duration)
            for _ in range(frames_to_advance):
                self._read_next_frame()
            self.last_frame_time = now - (elapsed % self.frame_duration)

    def draw(self, screen: pygame.Surface):
        """Desenha o frame atual na tela, ajustando à resolução da janela com alto desempenho."""
        if self.current_surface is None:
            return

        screen_w, screen_h = screen.get_size()
        frame_w, frame_h = self.current_surface.get_size()

        if (screen_w, screen_h) == (frame_w, frame_h):
            screen.blit(self.current_surface, (0, 0))
        else:
            scaled = pygame.transform.scale(self.current_surface, (screen_w, screen_h))
            screen.blit(scaled, (0, 0))

    def get_status_text(self) -> str:
        dir_name = ">> FRENTE" if self.current_direction == "forward" else "<< REVERSO"
        return f"Ping-Pong ({dir_name} a {self.speed:.1f}x)"

    def release(self):
        """Libera recursos do OpenCV ao encerrar o jogo."""
        if self.cap_fwd.isOpened():
            self.cap_fwd.release()
        if self.cap_rev.isOpened():
            self.cap_rev.release()


class SequentialVideoBackground:
    """
    Gerenciador de múltiplos vídeos encadeados em loop infinito contínuo.
    Exemplo: [Parte 1, Parte 2].
    Quando a Parte 1 acaba, exibe uma tela preta de 0.5s e inicia a Parte 2.
    Quando a Parte 2 acaba, retorna à Parte 1 com a mesma transição de tela preta.
    Suporta redução de velocidade das animações (ex: 0.8x).
    """
    def __init__(self, video_names: list[str], speed: float = 0.8, black_screen_duration: float = 0.5, black_screen_on_loop: bool = True):
        self.video_names = video_names
        self.speed = max(0.1, speed)
        self.black_screen_duration = black_screen_duration
        self.black_screen_on_loop = black_screen_on_loop

        self.paths = [resource_path(name) for name in video_names]
        self.caps = [cv2.VideoCapture(p) for p in self.paths]

        # Configura framerate base e framerate com velocidade reduzida (0.8x)
        self.base_fps = 24.0
        for cap in self.caps:
            cap_fps = cap.get(cv2.CAP_PROP_FPS)
            if cap_fps and cap_fps > 0:
                self.base_fps = cap_fps
                break
        
        # A 0.8x, fps = 24.0 * 0.8 = 19.2 fps (10s de vídeo para cada parte de 192 frames)
        self.fps = self.base_fps * self.speed
        self.frame_duration = 1.0 / self.fps

        self.current_index = 0
        self.current_surface = None
        self.last_frame_time = time.time()

        # Estado de tela preta entre animações
        self.is_in_black_screen = False
        self.black_screen_end_time = 0.0

        # Lê o primeiro frame da sequência
        self._read_next_frame()

    def _read_next_frame(self):
        if not self.caps:
            return

        active_cap = self.caps[self.current_index]
        ret, frame = active_cap.read()

        if not ret:
            # Vídeo atual chegou ao fim: reseta para o frame 0
            active_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            # Verifica se esta transição terá a tela preta de 0.5 segundos
            is_loop_transition = (self.current_index == len(self.caps) - 1)
            should_apply_black = (
                (self.current_index == 0 and self.black_screen_duration > 0) or
                (is_loop_transition and self.black_screen_on_loop and self.black_screen_duration > 0)
            )

            next_index = (self.current_index + 1) % len(self.caps)

            if should_apply_black:
                self.is_in_black_screen = True
                self.black_screen_end_time = time.time() + self.black_screen_duration
                self.current_index = next_index
                print(f"[SequentialBackground] Transição para animação {self.current_index + 1}: Tela preta de {self.black_screen_duration}s...")
                return
            else:
                self.current_index = next_index
                active_cap = self.caps[self.current_index]
                ret, frame = active_cap.read()

        if ret and frame is not None:
            h, w, _ = frame.shape
            self.current_surface = pygame.image.frombuffer(frame.data, (w, h), 'BGR')

    def reset(self):
        self.is_in_black_screen = False
        self.black_screen_end_time = 0.0
        self.current_index = 0
        for cap in self.caps:
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.last_frame_time = time.time()
        self._read_next_frame()

    def update(self):
        """Atualiza os frames respeitando o framerate desacelerado (0.8x) e o tempo de tela preta (0.5s)."""
        now = time.time()

        # Se estiver no momento da tela preta de transição
        if self.is_in_black_screen:
            if now >= self.black_screen_end_time:
                # Fim da tela preta de 0.5s: inicia a próxima animação
                self.is_in_black_screen = False
                self.last_frame_time = now
                active_cap = self.caps[self.current_index]
                ret, frame = active_cap.read()
                if ret and frame is not None:
                    h, w, _ = frame.shape
                    self.current_surface = pygame.image.frombuffer(frame.data, (w, h), 'BGR')
            return

        elapsed = now - self.last_frame_time
        if elapsed >= self.frame_duration:
            frames_to_advance = int(elapsed // self.frame_duration)
            for _ in range(frames_to_advance):
                if self.is_in_black_screen:
                    break
                self._read_next_frame()
            self.last_frame_time = now - (elapsed % self.frame_duration)

    def draw(self, screen: pygame.Surface):
        """Renderiza o frame redimensionado ou preenche com preto durante a transição."""
        if self.is_in_black_screen:
            screen.fill((0, 0, 0))
            return

        if self.current_surface is None:
            return

        screen_w, screen_h = screen.get_size()
        frame_w, frame_h = self.current_surface.get_size()

        if (screen_w, screen_h) == (frame_w, frame_h):
            screen.blit(self.current_surface, (0, 0))
        else:
            scaled = pygame.transform.scale(self.current_surface, (screen_w, screen_h))
            screen.blit(scaled, (0, 0))

    def get_status_text(self) -> str:
        if self.is_in_black_screen:
            rem = max(0.0, self.black_screen_end_time - time.time())
            return f"Transição [Tela Preta: {rem:.1f}s]"
        part_num = self.current_index + 1
        total = len(self.caps)
        return f"Sequência Estendida (Parte {part_num}/{total} a {self.speed:.1f}x)"

    def release(self):
        """Libera todos os vídeos ao fechar o jogo."""
        for cap in self.caps:
            if cap.isOpened():
                cap.release()


class AudioManager:
    """
    Gerenciador de reprodução de música com suporte a repetição contínua
    e intervalo configurável (ex: reiniciar 2 segundos após o término).
    """
    def __init__(self):
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"[AudioManager] Falha ao inicializar mixer: {e}")

        self.current_file = None
        self.is_active = False
        self.music_waiting = False
        self.restart_time = 0.0
        self.restart_delay = 2.0  # 2 segundos de pausa após o término
        self.MUSIC_END_EVENT = pygame.USEREVENT + 1

        try:
            pygame.mixer.music.set_endevent(self.MUSIC_END_EVENT)
        except Exception:
            pass

    def play(self, relative_path: str, loop_delay: float = 2.0):
        full_path = resource_path(relative_path)
        if not os.path.exists(full_path):
            print(f"[AudioManager] Arquivo de música não encontrado: {full_path}")
            return

        # Se já estiver tocando a mesma faixa, mantém contínua sem reiniciar
        if self.is_active and self.current_file == full_path and pygame.mixer.music.get_busy():
            return

        self.current_file = full_path
        self.restart_delay = loop_delay
        self.is_active = True
        self.music_waiting = False
        self.restart_time = 0.0

        try:
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.play(loops=0)  # Toca uma vez para disparar evento ao fim
            print(f"[AudioManager] Reproduzindo música: {relative_path} (Pausa de {loop_delay}s ao terminar)")
        except Exception as e:
            print(f"[AudioManager] Erro ao reproduzir música: {e}")

    def stop(self, fadeout_ms: int = 400):
        self.is_active = False
        self.music_waiting = False
        self.current_file = None
        try:
            if fadeout_ms > 0:
                pygame.mixer.music.fadeout(fadeout_ms)
            else:
                pygame.mixer.music.stop()
        except Exception as e:
            print(f"[AudioManager] Erro ao parar música: {e}")

    def handle_event(self, event):
        if event.type == self.MUSIC_END_EVENT and self.is_active:
            if not self.music_waiting:
                self.music_waiting = True
                self.restart_time = time.time() + self.restart_delay
                print(f"[AudioManager] Música finalizada. Reiniciando em {self.restart_delay}s...")

    def update(self):
        if not self.is_active or self.current_file is None:
            return

        # Detecção de contingência caso o evento USEREVENT seja consumido
        if not self.music_waiting and not pygame.mixer.music.get_busy():
            self.music_waiting = True
            self.restart_time = time.time() + self.restart_delay
            print(f"[AudioManager] Fim da música detectado. Reiniciando em {self.restart_delay}s...")

        # Reinicia a música após 2 segundos
        if self.music_waiting and time.time() >= self.restart_time:
            self.music_waiting = False
            try:
                pygame.mixer.music.load(self.current_file)
                pygame.mixer.music.play(loops=0)
                print("[AudioManager] Música reiniciada com sucesso após intervalo de 2s!")
            except Exception as e:
                print(f"[AudioManager] Erro ao reiniciar música: {e}")

    def fast_forward_near_end(self):
        """Atalho de teste para avançar a música perto do fim e verificar o intervalo de 2 segundos."""
        if self.is_active and self.current_file:
            try:
                # msc final ruim 1 tem ~177s. Pula para 175.5s
                pygame.mixer.music.play(start=175.5)
                print("[AudioManager] Música adiantada para perto do fim para teste do loop de 2s.")
            except Exception as e:
                print(f"[AudioManager] Não foi possível adiantar a música: {e}")

    def get_status_text(self) -> str:
        if not self.is_active:
            return "Música: Nenhuma"
        if self.music_waiting:
            rem = max(0.0, self.restart_time - time.time())
            return f"Música: Intervalo ({rem:.1f}s p/ reiniciar)"
        return "Música: Tocando (Contínua)"


class CoverManager:
    """
    Gerenciador Central de Capas/Planos de Fundo Dinâmicos.
    Permite alternar entre a Capa Principal e a Animação Estendida de Final Ruim,
    sincronizando vídeo (a 0.8x de velocidade com tela preta de 0.5s na transição)
    e música temática automaticamente.
    """
    COVER_PRINCIPAL = "principal"
    COVER_FINAL_RUIM_1 = "final_ruim_1"

    def __init__(self):
        self.audio = AudioManager()

        # 1. Capa Principal: Ping-Pong a 0.8x
        self.cover_principal = PingPongVideoBackground(
            forward_video_name="parte principal do jogo.mp4",
            reverse_video_name="background_reverse.mp4",
            speed=0.8
        )

        # 2. Capa Final Ruim 1: Sequência Estendida (Parte 1 -> Parte 2 em loop a 0.8x com 0.5s de tela preta)
        self.cover_final_ruim_1 = SequentialVideoBackground(
            video_names=[
                "animação final ruim 1 , parte 1.mp4",
                "animação final ruim 1, parte 2.mp4"
            ],
            speed=0.8,
            black_screen_duration=0.5,
            black_screen_on_loop=True
        )

        self.current_cover_id = self.COVER_PRINCIPAL
        self.active_background = self.cover_principal

    @property
    def is_in_black_screen(self) -> bool:
        """Indica se a animação está atualmente no intervalo de tela preta de 0.5s."""
        if self.active_background and hasattr(self.active_background, 'is_in_black_screen'):
            return self.active_background.is_in_black_screen
        return False

    def set_cover(self, cover_id: str):
        """Muda a capa atual conforme as escolhas do jogador."""
        if cover_id == self.current_cover_id:
            return

        print(f"[CoverManager] Trocando capa para: '{cover_id}'")
        self.current_cover_id = cover_id

        if cover_id == self.COVER_FINAL_RUIM_1:
            self.active_background = self.cover_final_ruim_1
            self.cover_final_ruim_1.reset()
            # Toca a música 'msc final ruim 1.mp3' e reinicia após 2 segundos
            self.audio.play("msc final ruim 1.mp3", loop_delay=2.0)
        else:
            self.active_background = self.cover_principal
            self.cover_principal.reset()
            # Para a música do final ruim ao voltar à capa normal
            self.audio.stop(fadeout_ms=400)

    def toggle_cover(self):
        """Alterna rapidamente entre a Capa Principal e o Final Ruim 1."""
        if self.current_cover_id == self.COVER_PRINCIPAL:
            self.set_cover(self.COVER_FINAL_RUIM_1)
        else:
            self.set_cover(self.COVER_PRINCIPAL)

    def handle_event(self, event):
        self.audio.handle_event(event)

    def update(self):
        if self.active_background:
            self.active_background.update()
        self.audio.update()

    def draw(self, screen: pygame.Surface):
        if self.active_background:
            self.active_background.draw(screen)

    def get_status_text(self) -> str:
        cover_name = "Capa Principal" if self.current_cover_id == self.COVER_PRINCIPAL else "Final Ruim 1"
        bg_status = self.active_background.get_status_text() if self.active_background else ""
        audio_status = self.audio.get_status_text()
        return f"Capa: {cover_name} [{bg_status}]  |  {audio_status}"

    def release(self):
        """Encerra com segurança todos os recursos de vídeo e áudio."""
        self.audio.stop(fadeout_ms=0)
        self.cover_principal.release()
        self.cover_final_ruim_1.release()
