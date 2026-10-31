"""
Game Engine & Mechanics for Therapeutic Hand Game.
Manages colored balls, target containers, collision detection,
particle effects, and session statistics.
"""

import math
import random
import time
import os
import csv
import pygame
import config

class Particle:
    """Celebratory particle when a ball is placed correctly."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2.5, 6.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 1.5
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.04)
        self.size = random.uniform(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= self.decay

    def draw(self, surface):
        if self.life > 0:
            alpha = int(self.life * 255)
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            col = (*self.color, alpha)
            pygame.draw.circle(s, col, (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class TargetContainer:
    """Matching colored target container where balls are placed."""
    def __init__(self, color_info, center_x, center_y, radius):
        self.color_info = color_info
        self.x = center_x
        self.y = center_y
        self.radius = radius
        self.is_hovered = False
        self.items_received = 0
        self.pulse = 0.0

    def update(self):
        self.pulse += 0.05

    def contains_point(self, px, py):
        dist = math.hypot(px - self.x, py - self.y)
        return dist <= self.radius * 1.55

    def draw(self, surface, font):
        r = self.radius
        
        # Soft outer glow if hovered
        if self.is_hovered:
            glow_rad = r + 12 + int(math.sin(self.pulse * 2) * 3)
            glow_surf = pygame.Surface((glow_rad * 2 + 10, glow_rad * 2 + 10), pygame.SRCALPHA)
            col = (*self.color_info["glow"], 80)
            pygame.draw.circle(glow_surf, col, (glow_rad + 5, glow_rad + 5), glow_rad)
            surface.blit(glow_surf, (self.x - glow_rad - 5, self.y - glow_rad - 5))

        # Container body
        pygame.draw.circle(surface, config.COLOR_CARD, (self.x, self.y), r)
        
        # Inner colored base
        inner_r = max(10, r - 10)
        pygame.draw.circle(surface, self.color_info["target_color"], (self.x, self.y), inner_r)
        
        # Colored rim
        rim_col = self.color_info["color"] if not self.is_hovered else (255, 255, 255)
        rim_w = 5 if self.is_hovered else 3
        pygame.draw.circle(surface, rim_col, (self.x, self.y), r, rim_w)

        # Label: Simple name (e.g. RED, BLUE, GREEN, YELLOW)
        name_text = font.render(self.color_info["name"].upper(), True, config.COLOR_TEXT_PRIMARY)
        n_rect = name_text.get_rect(center=(self.x, self.y))
        surface.blit(name_text, n_rect)


class TherapyBall:
    """Interactive colored ball that the user pinches and moves."""
    def __init__(self, color_info, home_x, home_y, radius):
        self.color_info = color_info
        self.home_x = home_x
        self.home_y = home_y
        self.x = home_x
        self.y = home_y
        self.radius = radius
        
        self.state = 'IDLE'  # 'IDLE', 'GRABBED', 'SORTED', 'RETURNING'
        self.is_hovered = False
        self.grab_start_time = 0.0
        self.total_hold_duration = 0.0
        self.pulse = random.uniform(0, 3.14)

    def contains_point(self, px, py):
        dist = math.hypot(px - self.x, py - self.y)
        # Generous grab zone (95 px) for effortless physical therapy selection
        return dist <= max(95.0, self.radius * 2.4)

    def grab(self):
        self.state = 'GRABBED'
        self.grab_start_time = time.time()

    def update(self, cursor_x, cursor_y):
        self.pulse += 0.06
        
        if self.state == 'GRABBED':
            # Smooth follow (eliminates jitter and stops snap-drops)
            self.x += (cursor_x - self.x) * 0.55
            self.y += (cursor_y - self.y) * 0.55
        elif self.state == 'RETURNING':
            dx = self.home_x - self.x
            dy = self.home_y - self.y
            dist = math.hypot(dx, dy)
            if dist < 6.0:
                self.x = self.home_x
                self.y = self.home_y
                self.state = 'IDLE'
            else:
                self.x += dx * 0.22
                self.y += dy * 0.22

    def release(self, target_container):
        if self.grab_start_time > 0:
            self.total_hold_duration = time.time() - self.grab_start_time

        if target_container.contains_point(self.x, self.y):
            if target_container.color_info["name"] == self.color_info["name"]:
                self.state = 'SORTED'
                self.x = target_container.x
                self.y = target_container.y
                target_container.items_received += 1
                return True
        
        self.state = 'RETURNING'
        return False

    def reset(self):
        self.x = self.home_x
        self.y = self.home_y
        self.state = 'IDLE'

    def draw(self, surface, font):
        if self.state == 'SORTED':
            return

        rad = self.radius
        if self.state == 'IDLE':
            rad = self.radius + int(math.sin(self.pulse) * 2)
        elif self.state == 'GRABBED':
            rad = self.radius + 3

        # Visual indicator when hand is hovering over this ball
        if self.is_hovered and self.state == 'IDLE':
            hover_rad = rad + 14 + int(math.sin(self.pulse * 2) * 3)
            pygame.draw.circle(surface, (255, 255, 255, 180), (int(self.x), int(self.y)), hover_rad, 2)
            
            prompt_surf = font.render("PINCH TO GRAB", True, config.COLOR_ACCENT_EMERALD)
            p_rect = prompt_surf.get_rect(center=(int(self.x), int(self.y - rad - 20)))
            pill = p_rect.inflate(14, 6)
            pygame.draw.rect(surface, config.COLOR_PANEL, pill, border_radius=4)
            pygame.draw.rect(surface, config.COLOR_ACCENT_EMERALD, pill, width=1, border_radius=4)
            surface.blit(prompt_surf, p_rect)

        # Soft drop shadow
        shadow_surf = pygame.Surface((rad * 2 + 16, rad * 2 + 16), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 80), (rad + 8, rad + 8), rad)
        surface.blit(shadow_surf, (self.x - rad - 8, self.y - rad + 4))

        # Main sphere body
        pygame.draw.circle(surface, self.color_info["color"], (int(self.x), int(self.y)), rad)
        
        # 3D Highlight sheen
        highlight_x = int(self.x - rad * 0.3)
        highlight_y = int(self.y - rad * 0.3)
        highlight_rad = max(4, int(rad * 0.35))
        pygame.draw.circle(surface, (255, 255, 255, 170), (highlight_x, highlight_y), highlight_rad)

        # Border
        border_col = (255, 255, 255) if (self.state == 'GRABBED' or self.is_hovered) else (255, 255, 255, 140)
        border_w = 4 if self.state == 'GRABBED' else (3 if self.is_hovered else 2)
        pygame.draw.circle(surface, border_col, (int(self.x), int(self.y)), rad, border_w)


class TherapySessionStats:
    """Records quantitative performance for physiotherapy session feedback."""
    def __init__(self, difficulty_name):
        self.difficulty_name = difficulty_name
        self.start_time = time.time()
        self.end_time = None
        self.reps_target = 0
        self.correct_placements = 0
        self.accidental_drops = 0
        self.token_hold_times = []
        self.is_completed = False
        self.has_exported = False

    def record_success(self, hold_time):
        self.correct_placements += 1
        self.token_hold_times.append(hold_time)

    def record_drop(self):
        self.accidental_drops += 1

    def finish(self):
        self.end_time = time.time()
        self.is_completed = True

    def get_elapsed_seconds(self):
        if self.end_time:
            return int(self.end_time - self.start_time)
        return int(time.time() - self.start_time)

    def get_accuracy_pct(self):
        total_attempts = self.correct_placements + self.accidental_drops
        if total_attempts == 0:
            return 100.0
        return round((self.correct_placements / total_attempts) * 100.0, 1)

    def get_avg_hold_time(self):
        if not self.token_hold_times:
            return 0.0
        return round(sum(self.token_hold_times) / len(self.token_hold_times), 2)

    def export_csv(self, output_dir="sessions"):
        """Saves session record to local CSV without collecting sensitive personal data."""
        if self.has_exported:
            return os.path.join(output_dir, "rehab_sessions_log.csv")
        self.has_exported = True

        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "rehab_sessions_log.csv")
        file_exists = os.path.exists(file_path)

        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.start_time))
        row = [
            timestamp_str,
            self.difficulty_name,
            self.reps_target,
            self.correct_placements,
            self.accidental_drops,
            self.get_accuracy_pct(),
            self.get_elapsed_seconds(),
            self.get_avg_hold_time()
        ]

        with open(file_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "Timestamp", "Difficulty", "RepsTarget", "CorrectPlacements",
                    "AccidentalDrops", "AccuracyPct", "DurationSec", "AvgHoldSec"
                ])
            writer.writerow(row)
        return file_path
