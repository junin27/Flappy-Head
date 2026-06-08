import cv2
import numpy as np
import random
import math
from typing import List, Dict, Union, Tuple, Any, Optional

from src.config import (
    HEIGHT, WIDTH, GROUND_HEIGHT, COLOR_SKY_TOP, COLOR_SKY_BASE,
    COLOR_GROUND, COLOR_GROUND_DETAIL, COLOR_GROUND_LINE, COLOR_CLOUD,
    COLOR_PIPE_BODY, COLOR_PIPE_BORDER, COLOR_PIPE_TOP, COLOR_TEXT,
    COLOR_SHADOW, COLOR_PANEL
)
from src.models.player import Player
from src.models.pipe import Pipe

class Renderer:
    def __init__(self) -> None:
        self.sky_base: np.ndarray = self._create_sky()
        self.clouds: List[Dict[str, float]] = self._generate_clouds()
        
        # Pillow Font Configuration
        from PIL import Image, ImageDraw
        import os
        self.font_path: Optional[str] = None
        win_font = "C:\\Windows\\Fonts\\arial.ttf"
        if os.path.exists(win_font):
            self.font_path = win_font
            
        self.dummy_img: Image.Image = Image.new("RGB", (1, 1))
        self.dummy_draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.dummy_img)

    def _create_sky(self) -> np.ndarray:
        sky = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        for y in range(HEIGHT):
            t = y / max(1, HEIGHT - 1)
            b = int(COLOR_SKY_TOP[0] * (1 - t) + COLOR_SKY_BASE[0] * t)
            g = int(COLOR_SKY_TOP[1] * (1 - t) + COLOR_SKY_BASE[1] * t)
            r = int(COLOR_SKY_TOP[2] * (1 - t) + COLOR_SKY_BASE[2] * t)
            sky[y, :] = (b, g, r)
        return sky

    def _generate_clouds(self, count: int = 9) -> List[Dict[str, float]]:
        clouds: List[Dict[str, float]] = []
        for _ in range(count):
            clouds.append({
                "x": float(random.randint(0, WIDTH)),
                "y": float(random.randint(60, HEIGHT // 2)),
                "scale": random.uniform(1.2, 2.4),
                "speed": random.uniform(0.4, 1.2),
            })
        return clouds

    def update_clouds(self) -> None:
        for c in self.clouds:
            c["x"] -= c["speed"]
            if c["x"] < -60:
                c["x"] = float(WIDTH + random.randint(20, 200))
                c["y"] = float(random.randint(40, HEIGHT // 2))
                c["scale"] = random.uniform(0.7, 1.4)
                c["speed"] = random.uniform(0.3, 0.9)

    def create_base_canvas(self) -> np.ndarray:
        return self.sky_base.copy()

    def draw_scenario(self, canvas: np.ndarray, ground_offset: float) -> None:
        # Clouds
        for c in self.clouds:
            x, y = int(c["x"]), int(c["y"])
            r = int(22 * c["scale"])
            cv2.circle(canvas, (x, y), r, COLOR_CLOUD, -1)
            cv2.circle(canvas, (x + r, y + r // 3), int(r * 0.9), COLOR_CLOUD, -1)
            cv2.circle(canvas, (x - r, y + r // 3), int(r * 0.9), COLOR_CLOUD, -1)
            cv2.circle(canvas, (x + r // 2, y - r // 2), int(r * 0.8), COLOR_CLOUD, -1)
            cv2.circle(canvas, (x - r // 2, y - r // 2), int(r * 0.8), COLOR_CLOUD, -1)

        # Ground
        y_ground = HEIGHT - GROUND_HEIGHT
        cv2.rectangle(canvas, (0, y_ground), (WIDTH, HEIGHT), COLOR_GROUND, -1)
        cv2.rectangle(canvas, (0, y_ground), (WIDTH, y_ground + 14), COLOR_GROUND_DETAIL, -1)
        
        stripe_width = 56
        for x in range(-stripe_width, WIDTH + stripe_width, stripe_width):
            x_real = x - int(ground_offset)
            pts = np.array([
                [x_real, HEIGHT],
                [x_real + stripe_width // 2, y_ground + 18],
                [x_real + stripe_width, HEIGHT],
            ], dtype=np.int32)
            cv2.fillPoly(canvas, [pts], COLOR_GROUND_DETAIL)
            
        cv2.line(canvas, (0, y_ground), (WIDTH, y_ground), COLOR_GROUND_LINE, 3)

    def draw_pipes(self, canvas: np.ndarray, pipes: List[Pipe]) -> None:
        y_ground = HEIGHT - GROUND_HEIGHT
        mouth_thickness = 36
        overlap = 10
        border = 5
        
        for pipe in pipes:
            x = int(pipe.x)
            gap_y = pipe.gap_y
            
            # Top Pipe
            cv2.rectangle(canvas, (x, 0), (x + pipe.width, gap_y), COLOR_PIPE_BODY, -1)
            cv2.rectangle(canvas, (x, 0), (x + pipe.width, gap_y), COLOR_PIPE_BORDER, border)
            cv2.rectangle(canvas, (x - overlap, gap_y - mouth_thickness), (x + pipe.width + overlap, gap_y), COLOR_PIPE_BODY, -1)
            cv2.rectangle(canvas, (x - overlap, gap_y - mouth_thickness), (x + pipe.width + overlap, gap_y), COLOR_PIPE_BORDER, border)
            cv2.line(canvas, (x + 22, 0), (x + 22, gap_y - mouth_thickness), COLOR_PIPE_TOP, 6)

            # Bottom Pipe
            y_start = gap_y + pipe.gap
            cv2.rectangle(canvas, (x, y_start), (x + pipe.width, y_ground), COLOR_PIPE_BODY, -1)
            cv2.rectangle(canvas, (x, y_start), (x + pipe.width, y_ground), COLOR_PIPE_BORDER, border)
            cv2.rectangle(canvas, (x - overlap, y_start), (x + pipe.width + overlap, y_start + mouth_thickness), COLOR_PIPE_BODY, -1)
            cv2.rectangle(canvas, (x - overlap, y_start), (x + pipe.width + overlap, y_start + mouth_thickness), COLOR_PIPE_BORDER, border)
            cv2.line(canvas, (x + 22, y_start + mouth_thickness), (x + 22, y_ground), COLOR_PIPE_TOP, 6)

    def draw_face(self, canvas: np.ndarray, player: Player) -> None:
        face = player.face_img
        x, y, radius, angle = int(player.x), int(player.y), player.radius, player.angle
        
        h_canvas, w_canvas = canvas.shape[:2]

        if face is None:
            if not player.webcam_available:
                cv2.circle(canvas, (x, y), radius, (90, 220, 255), -1, cv2.LINE_AA)
                cv2.circle(canvas, (x, y), radius, COLOR_SHADOW, 3, cv2.LINE_AA)
                self.draw_text(canvas, "CÂMERA", (x, y - 12), scale=0.6, color=(255, 255, 255), thickness=2, centered=True, max_width=radius * 2 - 10)
                self.draw_text(canvas, "NÃO DETECTADA", (x, y + 12), scale=0.45, color=(255, 255, 255), thickness=1, centered=True, max_width=radius * 2 - 10)
            else:
                cv2.circle(canvas, (x, y), radius, (90, 220, 255), -1, cv2.LINE_AA)
                cv2.circle(canvas, (x, y), radius, COLOR_SHADOW, 3, cv2.LINE_AA)
                self.draw_text(canvas, "ROSTO", (x, y - 12), scale=0.6, color=(255, 255, 255), thickness=2, centered=True, max_width=radius * 2 - 10)
                self.draw_text(canvas, "NÃO DETECTADO", (x, y + 12), scale=0.45, color=(255, 255, 255), thickness=1, centered=True, max_width=radius * 2 - 10)
            return

        M = cv2.getRotationMatrix2D((radius, radius), -angle, 1.0)
        face_rot = cv2.warpAffine(face, M, (radius * 2, radius * 2), borderMode=cv2.BORDER_REFLECT)
        mask = np.zeros((radius * 2, radius * 2), dtype=np.uint8)
        cv2.circle(mask, (radius, radius), radius - 2, 255, -1, cv2.LINE_AA)

        x1, y1 = x - radius, y - radius
        x2, y2 = x + radius, y + radius

        if x2 <= 0 or y2 <= 0 or x1 >= w_canvas or y1 >= h_canvas:
            return

        cx1, cy1 = max(0, x1), max(0, y1)
        cx2, cy2 = min(w_canvas, x2), min(h_canvas, y2)
        rx1, ry1 = cx1 - x1, cy1 - y1
        rx2, ry2 = rx1 + (cx2 - cx1), ry1 + (cy2 - cy1)

        sub_face = face_rot[ry1:ry2, rx1:rx2]
        sub_mask = mask[ry1:ry2, rx1:rx2]
        sub_mask_inv = cv2.bitwise_not(sub_mask)

        background = cv2.bitwise_and(canvas[cy1:cy2, cx1:cx2], canvas[cy1:cy2, cx1:cx2], mask=sub_mask_inv)
        foreground = cv2.bitwise_and(sub_face, sub_face, mask=sub_mask)
        canvas[cy1:cy2, cx1:cx2] = cv2.add(background, foreground)

        cv2.circle(canvas, (x, y), radius, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.circle(canvas, (x, y), radius + 1, COLOR_SHADOW, 1, cv2.LINE_AA)

    def draw_text(
        self,
        canvas: np.ndarray,
        text: str,
        pos: Tuple[int, int],
        scale: float = 1.0,
        color: Tuple[int, int, int] = COLOR_TEXT,
        thickness: int = 2,
        centered: bool = False,
        with_shadow: bool = True,
        max_width: Optional[int] = None
    ) -> Tuple[int, int]:
        from PIL import Image, ImageDraw, ImageFont
        
        font_size = int(scale * 24)
        if self.font_path:
            font = ImageFont.truetype(self.font_path, font_size)
        else:
            font = ImageFont.load_default()
            
        if max_width is not None:
            bbox = self.dummy_draw.textbbox((0, 0), text, font=font)
            w = bbox[2] - bbox[0]
            if w > max_width:
                font_size = max(8, int(font_size * (max_width / w)))
                if self.font_path:
                    font = ImageFont.truetype(self.font_path, font_size)
                    
        bbox = self.dummy_draw.textbbox((0, 0), text, font=font)
        w_text = bbox[2] - bbox[0]
        h_text = bbox[3] - bbox[1]
        
        x, y = pos
        if centered:
            x = x - w_text // 2
            
        x_min = max(0, x - 10)
        y_min = max(0, y - h_text - 15)
        x_max = min(canvas.shape[1], x + w_text + 15)
        y_max = min(canvas.shape[0], y + 15)
        
        if x_max <= x_min or y_max <= y_min:
            return w_text, h_text
            
        sub_cv = canvas[y_min:y_max, x_min:x_max]
        sub_rgb = cv2.cvtColor(sub_cv, cv2.COLOR_BGR2RGB)
        sub_pil = Image.fromarray(sub_rgb)
        
        draw = ImageDraw.Draw(sub_pil)
        color_rgb = (color[2], color[1], color[0])
        shadow_rgb = (COLOR_SHADOW[2], COLOR_SHADOW[1], COLOR_SHADOW[0])
        
        draw_x = x - x_min
        draw_y = y - y_min
        
        if with_shadow:
            draw.text((draw_x + 2, draw_y + 2), text, font=font, fill=shadow_rgb, anchor="ls")
        draw.text((draw_x, draw_y), text, font=font, fill=color_rgb, anchor="ls")
        
        res_cv = cv2.cvtColor(np.array(sub_pil), cv2.COLOR_RGB2BGR)
        canvas[y_min:y_max, x_min:x_max] = res_cv
        
        return w_text, h_text

    def draw_panel(self, canvas: np.ndarray, x: int, y: int, w: int, h: int, alpha: float = 0.55) -> None:
        h_canvas, w_canvas = canvas.shape[:2]
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(w_canvas, x + w), min(h_canvas, y + h)
        if x2 <= x1 or y2 <= y1:
            return
        sub = canvas[y1:y2, x1:x2]
        overlay = np.full_like(sub, COLOR_PANEL)
        cv2.addWeighted(overlay, alpha, sub, 1 - alpha, 0, sub)
        cv2.rectangle(canvas, (x1, y1), (x2 - 1, y2 - 1), (255, 255, 255), 2)
