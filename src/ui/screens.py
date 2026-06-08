from typing import List, Dict, Union
import numpy as np
from src.config import WIDTH, HEIGHT
from src.ui.renderer import Renderer

class Screens:
    def __init__(self, renderer: Renderer) -> None:
        self.renderer: Renderer = renderer

    def draw_menu(self, canvas: np.ndarray, player_name: str, selected_mode: str, screen_mode: str, typing: bool = False) -> None:
        # Designated panel width is 1040, using max_width=960 for safety padding
        max_w = 960
        self.renderer.draw_panel(canvas, WIDTH // 2 - 520, HEIGHT // 2 - 320, 1040, 640, alpha=0.7)
        
        self.renderer.draw_text(canvas, "FLAPPY HEAD", (WIDTH // 2, HEIGHT // 2 - 200),
                                 scale=4.2, thickness=8, centered=True, color=(120, 240, 255), max_width=max_w)
        
        self.renderer.draw_text(canvas, "Seu Nome (TAB para editar):", (WIDTH // 2, HEIGHT // 2 - 70),
                                 scale=1.4, thickness=3, centered=True, color=(200, 200, 200), max_width=max_w)
                                      
        import cv2
        cursor = "_" if typing and (cv2.getTickCount() / cv2.getTickFrequency()) % 1.0 > 0.5 else ""
        name_color = (120, 255, 120) if typing else (255, 255, 255)
        self.renderer.draw_text(canvas, player_name + cursor, (WIDTH // 2, HEIGHT // 2 - 20),
                                 scale=2.0, thickness=4, centered=True, color=name_color, max_width=max_w)

        # Portuguese Translations for Modes and Screens
        mode_pt = "BOCA" if selected_mode == "mouth" else "CABEÇA"
        
        if screen_mode == "fullscreen":
            screen_pt = "TELA CHEIA"
        elif screen_mode == "windowed":
            screen_pt = "JANELA"
        else:
            screen_pt = "SEM BORDAS"

        self.renderer.draw_text(canvas, f"Controle [M]: {mode_pt}  |  Tela [F]: {screen_pt}", (WIDTH // 2, HEIGHT // 2 + 70),
                                 scale=1.5, thickness=4, centered=True, color=(180, 255, 180), max_width=max_w)
        
        self.renderer.draw_text(canvas, "ESPAÇO = Jogar  |  L = Placar", (WIDTH // 2, HEIGHT // 2 + 180),
                                 scale=1.4, thickness=3, centered=True, color=(255, 230, 120), max_width=max_w)
        self.renderer.draw_text(canvas, "ESC = Sair", (WIDTH // 2, HEIGHT // 2 + 250),
                                 scale=1.0, thickness=2, centered=True, color=(220, 220, 220), max_width=max_w)

    def draw_hud(self, canvas: np.ndarray, survival_time: float) -> None:
        self.renderer.draw_panel(canvas, 0, 0, WIDTH, 100, alpha=0.35)
        self.renderer.draw_text(canvas, f"TEMPO: {survival_time:.1f}s",
                                 (WIDTH // 2, 65), scale=2.0, thickness=4,
                                 centered=True, color=(255, 255, 255))

    def draw_game_over(self, canvas: np.ndarray, time_val: float) -> None:
        max_w = 800
        self.renderer.draw_panel(canvas, WIDTH // 2 - 440, HEIGHT // 2 - 200, 880, 400, alpha=0.75)
        self.renderer.draw_text(canvas, "FIM DE JOGO", (WIDTH // 2, HEIGHT // 2 - 70),
                                 scale=3.8, thickness=8, centered=True, color=(80, 80, 255), max_width=max_w)
        self.renderer.draw_text(canvas, f"Seu Tempo: {time_val:.1f}s", (WIDTH // 2, HEIGHT // 2 + 30),
                                 scale=2.0, thickness=4, centered=True, max_width=max_w)
        self.renderer.draw_text(canvas, "Aperte ESPAÇO para voltar", (WIDTH // 2, HEIGHT // 2 + 130),
                                 scale=1.4, thickness=3, centered=True, color=(255, 230, 120), max_width=max_w)

    def draw_leaderboard(
        self,
        canvas: np.ndarray,
        records: List[Dict[str, Union[str, float]]],
        scroll_offset: int,
        search_text: str,
        search_active: bool
    ) -> None:
        max_w = 900
        self.renderer.draw_panel(canvas, WIDTH // 2 - 500, HEIGHT // 2 - 400, 1000, 800, alpha=0.85)
        self.renderer.draw_text(canvas, "CLASSIFICAÇÃO", (WIDTH // 2, HEIGHT // 2 - 320),
                                 scale=2.5, thickness=5, centered=True, color=(255, 215, 0), max_width=max_w)
        
        # Desenha caixa de busca
        import cv2
        cursor = "_" if search_active and (cv2.getTickCount() / cv2.getTickFrequency()) % 1.0 > 0.5 else ""
        search_color = (120, 255, 120) if search_active else (200, 200, 200)
        self.renderer.draw_text(canvas, f"Buscar Jogador [TAB]: {search_text}{cursor}", (WIDTH // 2, HEIGHT // 2 - 260),
                                 scale=1.2, thickness=3, centered=True, color=search_color, max_width=max_w)

        y_base = HEIGHT // 2 - 180
        self.renderer.draw_text(canvas, "NOME", (WIDTH // 2 - 350, y_base), scale=1.2, thickness=2)
        self.renderer.draw_text(canvas, "MODO", (WIDTH // 2, y_base), scale=1.2, thickness=2, centered=True)
        self.renderer.draw_text(canvas, "TEMPO", (WIDTH // 2 + 250, y_base), scale=1.2, thickness=2)

        # Exibe no máximo 10 registros a partir do scroll_offset
        visible_records = records[scroll_offset : scroll_offset + 10]
        for i, reg in enumerate(visible_records):
            y_line = y_base + 50 + (i * 45)
            mode_pt = "Boca" if reg['mode'] == "mouth" else "Cabeça"
            self.renderer.draw_text(canvas, f"{scroll_offset + i + 1}. {reg['name'][:15]}", (WIDTH // 2 - 350, y_line), scale=1.1, thickness=2, color=(200, 255, 200))
            self.renderer.draw_text(canvas, mode_pt, (WIDTH // 2, y_line), scale=1.1, thickness=2, centered=True, color=(200, 200, 255))
            self.renderer.draw_text(canvas, f"{reg['time']:.1f}s", (WIDTH // 2 + 250, y_line), scale=1.1, thickness=2, color=(255, 200, 200))

        # Informações do scroll
        scroll_info = f"Registros {scroll_offset + 1}-{scroll_offset + len(visible_records)} de {len(records)}" if records else "Nenhum registro encontrado"
        self.renderer.draw_text(canvas, scroll_info, (WIDTH // 2, HEIGHT // 2 + 270),
                                 scale=1.0, thickness=2, centered=True, color=(180, 180, 180), max_width=max_w)

        self.renderer.draw_text(canvas, "W/S: Rolar  |  R: Limpar Placar  |  ESPAÇO: Voltar", (WIDTH // 2, HEIGHT // 2 + 330),
                                 scale=1.2, thickness=3, centered=True, color=(255, 230, 120), max_width=max_w)
