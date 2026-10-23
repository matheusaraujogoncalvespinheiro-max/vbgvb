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
    """
    def __init__(self, forward_video_name="parte principal do jogo.mp4", reverse_video_name="background_reverse.mp4"):
        self.forward_path = resource_path(forward_video_name)
        self.reverse_path = resource_path(reverse_video_name)

        # Se o vídeo reverso ainda não existe, cria automaticamente
        if not os.path.exists(self.reverse_path):
            print(f"[VideoBackground] Gerando vídeo reverso otimizado: {reverse_video_name}...")
            self._generate_reverse_video(self.forward_path, self.reverse_path)

        self.cap_fwd = cv2.VideoCapture(self.forward_path)
        self.cap_rev = cv2.VideoCapture(self.reverse_path)

        self.fps = self.cap_fwd.get(cv2.CAP_PROP_FPS) or 24.0
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
            # pygame.image.frombuffer com formato 'BGR' é ultra rápido (sem conversão de cores na CPU)
            self.current_surface = pygame.image.frombuffer(frame.data, (w, h), 'BGR')

    def update(self):
        """Atualiza o frame de acordo com o framerate do vídeo (24 fps)."""
        now = time.time()
        elapsed = now - self.last_frame_time

        if elapsed >= self.frame_duration:
            # Avança o número de frames decorridos caso ocorra algum atraso
            frames_to_advance = int(elapsed // self.frame_duration)
            for _ in range(frames_to_advance):
                self._read_next_frame()
            self.last_frame_time = now - (elapsed % self.frame_duration)

    def draw(self, screen: pygame.Surface):
        """Desenha o frame atual na tela, ajustando à resolução da janela mantendo o preenchimento."""
        if self.current_surface is None:
            return

        screen_w, screen_h = screen.get_size()
        frame_w, frame_h = self.current_surface.get_size()

        if (screen_w, screen_h) == (frame_w, frame_h):
            screen.blit(self.current_surface, (0, 0))
        else:
            # Redimensionamento suave para telas com resolução diferente
            scaled = pygame.transform.smoothscale(self.current_surface, (screen_w, screen_h))
            screen.blit(scaled, (0, 0))

    def release(self):
        """Libera recursos do OpenCV ao encerrar o jogo."""
        if self.cap_fwd.isOpened():
            self.cap_fwd.release()
        if self.cap_rev.isOpened():
            self.cap_rev.release()
