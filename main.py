"""
Therapeutic Hand Coordination & Rehabilitation Game
Interactive computer-vision physical therapy game.
Simple colors: Red, Green, Blue, Yellow.
Full hand skeleton tracking + clean, human-designed interface.
"""

import sys
import os
import math
import time
import pygame
import cv2
import numpy as np

import config
from sound_effects import SoundManager
from hand_tracker import HandTracker
from game_engine import TherapyBall, TargetContainer, Particle, TherapySessionStats
from ui_components import UIButton, UIRenderer

STATE_MENU = "MENU"
STATE_EXERCISE = "EXERCISE"
STATE_SUMMARY = "SUMMARY"

class TheraHandApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Therapeutic Hand Coordination & Rehabilitation")
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Core Engines
        self.ui = UIRenderer(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.sound = SoundManager()
        
        # Hand Tracker
        model_path = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")
        self.tracker = HandTracker(model_path=model_path, camera_index=0)
        
        # State & Configuration
        self.state = STATE_MENU
        self.selected_difficulty = "Medium"
        self.show_camera_background = True
        self.status_toast = ""
        self.toast_timer = 0.0

        # Mouse interaction fallback
        self.mouse_dragging = False

        # Exercise Entities
        self.tokens = []
        self.containers = []
        self.particles = []
        self.active_drag_token = None
        self.stats = None

        self._init_buttons()

    def _init_buttons(self):
        center_x = config.WINDOW_WIDTH // 2
        
        # Menu Start Button
        self.btn_start = UIButton((center_x - 130, 605, 260, 52), "START EXERCISE", 
                                  bg_color=(20, 160, 120), hover_color=(25, 185, 140),
                                  border_color=config.COLOR_ACCENT_EMERALD)
        
        # Difficulty Toggles (Easy, Medium, Hard)
        btn_y = 540
        self.diff_buttons = {
            "Easy": UIButton((center_x - 240, btn_y, 145, 42), "Easy (Gentle)"),
            "Medium": UIButton((center_x - 72, btn_y, 145, 42), "Medium"),
            "Hard": UIButton((center_x + 95, btn_y, 145, 42), "Hard")
        }

        # Summary Buttons
        self.btn_restart = UIButton((center_x - 210, 560, 130, 42), "Try Again")
        self.btn_menu = UIButton((center_x - 65, 560, 130, 42), "Main Menu")
        self.btn_save_csv = UIButton((center_x + 80, 560, 130, 42), "Save Report")

    def _setup_exercise(self):
        """Prepares colored balls and target containers."""
        self.tracker.update_difficulty(self.selected_difficulty)
        preset = config.DIFFICULTY_PRESETS[self.selected_difficulty]
        num_items = preset["token_count"]
        
        self.tokens.clear()
        self.containers.clear()
        self.particles.clear()
        self.active_drag_token = None
        self.mouse_dragging = False
        
        w = config.WINDOW_WIDTH
        h = config.WINDOW_HEIGHT
        
        # Create Target Containers on the right side
        container_radius = preset["target_radius"]
        container_x = w - 165
        container_y_start = 135
        container_y_spacing = (h - 220) // max(1, num_items - 1)
        
        for i in range(num_items):
            pal = config.TOKEN_PALETTE[i % len(config.TOKEN_PALETTE)]
            by = container_y_start + i * container_y_spacing
            container = TargetContainer(pal, container_x, by, container_radius)
            self.containers.append(container)

        # Create Colored Balls at bottom-left
        token_radius = preset["token_radius"]
        
        if num_items <= 4:
            token_x_start = 220
            token_spacing = 150
            for i in range(num_items):
                pal = config.TOKEN_PALETTE[i % len(config.TOKEN_PALETTE)]
                tx = token_x_start + i * token_spacing
                ty = h - 160
                ball = TherapyBall(pal, tx, ty, token_radius)
                self.tokens.append(ball)
        else:
            # 6 precision balls arranged in 2 clean rows of 3
            token_x_start = 200
            token_spacing = 135
            for i in range(num_items):
                pal = config.TOKEN_PALETTE[i % len(config.TOKEN_PALETTE)]
                col_idx = i % 3
                row_idx = i // 3
                tx = token_x_start + col_idx * token_spacing
                ty = h - 210 + row_idx * 90
                ball = TherapyBall(pal, tx, ty, token_radius)
                self.tokens.append(ball)

        # Initialize Session Statistics
        self.stats = TherapySessionStats(self.selected_difficulty)
        self.stats.reps_target = num_items
        self.state = STATE_EXERCISE

    def show_toast(self, message, duration=2.5):
        self.status_toast = message
        self.toast_timer = time.time() + duration

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_EXERCISE:
                        self.state = STATE_MENU
                    else:
                        self.running = False
                elif event.key == pygame.K_r:
                    if self.state in (STATE_EXERCISE, STATE_SUMMARY):
                        self._setup_exercise()
                elif event.key == pygame.K_c:
                    self.show_camera_background = not self.show_camera_background
                    mode_name = "Camera View" if self.show_camera_background else "Dark Focus Mode"
                    self.show_toast(f"Display: {mode_name}")
                elif event.key == pygame.K_m:
                    self.state = STATE_MENU

            # Mouse / trackpad fallback
            if self.state == STATE_EXERCISE:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for token in self.tokens:
                        if token.state == 'IDLE' and token.contains_point(mouse_pos[0], mouse_pos[1]):
                            token.grab()
                            self.active_drag_token = token
                            self.mouse_dragging = True
                            self.sound.play('grab')
                            break
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.mouse_dragging and self.active_drag_token:
                        self._release_token()
                        self.mouse_dragging = False

            # Button clicks
            if self.state == STATE_MENU:
                if self.btn_start.is_clicked(event):
                    self._setup_exercise()
                for name, btn in self.diff_buttons.items():
                    if btn.is_clicked(event):
                        self.selected_difficulty = name
            
            elif self.state == STATE_SUMMARY:
                if self.btn_restart.is_clicked(event):
                    self._setup_exercise()
                elif self.btn_menu.is_clicked(event):
                    self.state = STATE_MENU
                elif self.btn_save_csv.is_clicked(event):
                    if self.stats:
                        path = self.stats.export_csv()
                        self.show_toast(f"Session saved to {path}")

    def _release_token(self):
        """Validates placement when pinch or mouse is released."""
        if self.active_drag_token is None:
            return
        
        token = self.active_drag_token
        matching_box = next((c for c in self.containers if c.color_info["name"] == token.color_info["name"]), None)
        
        if matching_box and token.release(matching_box):
            # Placement success!
            self.sound.play('success')
            self.stats.record_success(token.total_hold_duration)
            
            for _ in range(24):
                self.particles.append(Particle(token.x, token.y, token.color_info["color"]))
                
            # Check if all tokens sorted
            if self.stats.correct_placements >= self.stats.reps_target:
                self.stats.finish()
                self.stats.export_csv()
                self.sound.play('complete')
                self.state = STATE_SUMMARY
        else:
            # Dropped outside
            self.sound.play('reset')
            self.stats.record_drop()

        self.active_drag_token = None

    def update(self):
        self.tracker.process_frame(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        mouse_pos = pygame.mouse.get_pos()

        if self.state == STATE_MENU:
            self.btn_start.update(mouse_pos)
            for name, btn in self.diff_buttons.items():
                btn.update(mouse_pos)
                if name == self.selected_difficulty:
                    btn.border_color = config.COLOR_ACCENT_TEAL
                    btn.bg_color = (35, 48, 70)
                else:
                    btn.border_color = config.COLOR_PANEL_BORDER
                    btn.bg_color = config.COLOR_PANEL

        elif self.state == STATE_EXERCISE:
            if self.tracker.hand_detected:
                cx, cy = self.tracker.pinch_pos
                is_pinched = self.tracker.is_pinched
            elif self.mouse_dragging:
                cx, cy = mouse_pos
                is_pinched = True
            else:
                cx, cy = mouse_pos
                is_pinched = False

            # Update hover states
            for token in self.tokens:
                token.is_hovered = (token.state == 'IDLE' and token.contains_point(cx, cy))

            for container in self.containers:
                container.update()
                if self.active_drag_token:
                    container.is_hovered = container.contains_point(cx, cy) and (container.color_info["name"] == self.active_drag_token.color_info["name"])
                else:
                    container.is_hovered = False

            # Update particles
            for p in self.particles[:]:
                p.update()
                if p.life <= 0:
                    self.particles.remove(p)

            # Hand pinch grasp logic
            if not self.mouse_dragging and self.tracker.hand_detected:
                if is_pinched:
                    if self.active_drag_token is None:
                        closest_token = None
                        min_dist = 9999.0
                        for token in self.tokens:
                            if token.state == 'IDLE' and token.contains_point(cx, cy):
                                d = math.hypot(cx - token.x, cy - token.y)
                                if d < min_dist:
                                    min_dist = d
                                    closest_token = token
                        if closest_token:
                            closest_token.grab()
                            self.active_drag_token = closest_token
                            self.sound.play('grab')
                else:
                    if self.active_drag_token is not None:
                        self._release_token()

            for token in self.tokens:
                token.update(cx, cy)

        elif self.state == STATE_SUMMARY:
            self.btn_restart.update(mouse_pos)
            self.btn_menu.update(mouse_pos)
            self.btn_save_csv.update(mouse_pos)

    def render(self):
        # 1. Base Background Rendering
        if self.show_camera_background and self.tracker.latest_camera_rgb is not None:
            cam_frame = self.tracker.latest_camera_rgb
            cam_h, cam_w, _ = cam_frame.shape
            
            cam_surf = pygame.image.frombuffer(cam_frame.tobytes(), (cam_w, cam_h), "RGB")
            cam_surf = pygame.transform.smoothscale(cam_surf, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
            
            tint_surf = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
            tint_surf.fill((16, 22, 34, 205))
            
            self.screen.blit(cam_surf, (0, 0))
            self.screen.blit(tint_surf, (0, 0))
        else:
            self.screen.fill(config.COLOR_BG)

        # 2. State-specific drawing
        if self.state == STATE_MENU:
            self._render_menu()
        elif self.state == STATE_EXERCISE:
            self._render_exercise()
        elif self.state == STATE_SUMMARY:
            self._render_exercise()
            self.ui.draw_session_summary_modal(self.screen, self.stats)
            self.btn_restart.draw(self.screen, self.ui.font_small)
            self.btn_menu.draw(self.screen, self.ui.font_small)
            self.btn_save_csv.draw(self.screen, self.ui.font_small)

        # 3. Always render hand skeleton & finger rings if detected
        if self.tracker.hand_detected:
            self.ui.draw_skeleton(self.screen, self.tracker.smoothed_landmarks, self.tracker.is_pinched)

        # 4. Status Toast
        if time.time() < self.toast_timer:
            t_surf = self.ui.font_small.render(self.status_toast, True, config.COLOR_TEXT_PRIMARY)
            t_rect = t_surf.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - 35))
            pad_rect = t_rect.inflate(28, 12)
            pygame.draw.rect(self.screen, config.COLOR_PANEL, pad_rect, border_radius=8)
            pygame.draw.rect(self.screen, config.COLOR_ACCENT_TEAL, pad_rect, width=1, border_radius=8)
            self.screen.blit(t_surf, t_rect)

        pygame.display.flip()

    def _render_menu(self):
        """A clean, human-designed opening page with live camera preview and intuitive controls."""
        w = config.WINDOW_WIDTH
        center_x = w // 2

        # 1. Title & Subtitle
        title_surf = self.ui.font_large.render("Therapeutic Hand Coordination", True, config.COLOR_TEXT_PRIMARY)
        self.screen.blit(title_surf, title_surf.get_rect(center=(center_x, 50)))

        sub_surf = self.ui.font_mid.render("Physical Rehabilitation & Motor Skill Exercise", True, config.COLOR_ACCENT_TEAL)
        self.screen.blit(sub_surf, sub_surf.get_rect(center=(center_x, 88)))

        # 2. Live Camera Preview Box (520 x 290)
        # Allows user to see their hand tracking working right on the welcome screen!
        cam_box_w = 520
        cam_box_h = 290
        cam_box_x = center_x - cam_box_w // 2
        cam_box_y = 115

        # Card shadow & border
        box_rect = pygame.Rect(cam_box_x, cam_box_y, cam_box_w, cam_box_h)
        pygame.draw.rect(self.screen, (0, 0, 0, 70), box_rect.move(0, 3), border_radius=16)
        pygame.draw.rect(self.screen, config.COLOR_CARD, box_rect, border_radius=16)

        if self.tracker.latest_camera_rgb is not None:
            cam_frame = self.tracker.latest_camera_rgb
            ch, cw, _ = cam_frame.shape
            preview_surf = pygame.image.frombuffer(cam_frame.tobytes(), (cw, ch), "RGB")
            preview_surf = pygame.transform.smoothscale(preview_surf, (cam_box_w - 8, cam_box_h - 8))
            self.screen.blit(preview_surf, (cam_box_x + 4, cam_box_y + 4))
        
        pygame.draw.rect(self.screen, config.COLOR_PANEL_BORDER, box_rect, width=2, border_radius=16)

        # Camera Status Pill inside Preview Box
        if self.tracker.hand_detected:
            status_txt = " Hand Tracking Active"
            status_col = config.COLOR_ACCENT_EMERALD
        else:
            status_txt = " Wave hand in camera to test"
            status_col = config.COLOR_TEXT_MUTED

        pill_rect = pygame.Rect(cam_box_x + 16, cam_box_y + 16, 240, 28)
        pygame.draw.rect(self.screen, (15, 23, 42, 220), pill_rect, border_radius=14)
        dot_col = config.COLOR_ACCENT_EMERALD if self.tracker.hand_detected else (240, 160, 40)
        pygame.draw.circle(self.screen, dot_col, (cam_box_x + 30, cam_box_y + 30), 4)
        surface_txt = self.ui.font_tiny.render(status_txt, True, status_col)
        self.screen.blit(surface_txt, (cam_box_x + 40, cam_box_y + 22))

        # 3. Quick 3-Step Guide Badges (Clean, friendly, human)
        steps = [
            ("1. Move Hand", "Hover near any ball"),
            ("2. Pinch Fingers", "Thumb & index to pick up"),
            ("3. Match Color", "Drop in matching box")
        ]
        step_w = 200
        total_w = len(steps) * step_w + 30
        start_x = center_x - total_w // 2
        step_y = 425

        for i, (title_step, desc_step) in enumerate(steps):
            sx = start_x + i * (step_w + 15)
            s_rect = pygame.Rect(sx, step_y, step_w, 54)
            pygame.draw.rect(self.screen, config.COLOR_PANEL, s_rect, border_radius=10)
            pygame.draw.rect(self.screen, config.COLOR_PANEL_BORDER, s_rect, width=1, border_radius=10)
            
            t_s = self.ui.font_small.render(title_step, True, config.COLOR_TEXT_PRIMARY)
            d_s = self.ui.font_tiny.render(desc_step, True, config.COLOR_TEXT_MUTED)
            self.screen.blit(t_s, (sx + 14, step_y + 9))
            self.screen.blit(d_s, (sx + 14, step_y + 31))

        # 4. Difficulty Selector Heading & Buttons
        d_lbl = self.ui.font_tiny.render("SELECT DIFFICULTY / RANGE OF MOTION", True, config.COLOR_TEXT_MUTED)
        self.screen.blit(d_lbl, d_lbl.get_rect(center=(center_x, 520)))

        for btn in self.diff_buttons.values():
            btn.draw(self.screen, self.ui.font_small)

        # 4b. Dynamic Level Description Preview
        desc_text = config.DIFFICULTY_PRESETS[self.selected_difficulty]["description"]
        desc_surf = self.ui.font_tiny.render(desc_text, True, (80, 205, 255))
        self.screen.blit(desc_surf, desc_surf.get_rect(center=(center_x, 584)))

        # 5. Start Button
        self.btn_start.draw(self.screen, self.ui.font_mid)

        # Shortcut hint
        hint = self.ui.font_tiny.render("Press 'C' anytime during exercise to toggle camera view. Press 'ESC' to exit.", True, config.COLOR_TEXT_MUTED)
        self.screen.blit(hint, hint.get_rect(center=(center_x, config.WINDOW_HEIGHT - 25)))

    def _render_exercise(self):
        # Draw Target Containers (Right side: RED, GREEN, BLUE, YELLOW)
        for container in self.containers:
            container.draw(self.screen, self.ui.font_small)

        # Draw Colored Balls (Bottom: RED, GREEN, BLUE, YELLOW)
        for token in self.tokens:
            token.draw(self.screen, self.ui.font_small)

        # Draw Celebratory Particles
        for p in self.particles:
            p.draw(self.screen)

        # Draw Top HUD
        current_reps = self.stats.correct_placements if self.stats else 0
        target_reps = self.stats.reps_target if self.stats else 4
        elapsed_sec = self.stats.get_elapsed_seconds() if self.stats else 0
        
        if self.active_drag_token:
            instruction = f"Holding {self.active_drag_token.color_info['name']} Ball -> Drop into matching box"
        elif not self.tracker.hand_detected:
            instruction = "Place hand in camera view (or click & drag with mouse)"
        else:
            instruction = "Hover over a ball & pinch fingers to pick it up"

        self.ui.draw_top_hud(self.screen, current_reps, target_reps, elapsed_sec, self.selected_difficulty, instruction)

        # Draw Bottom-Left Grip Meter
        ratio = self.tracker.get_pinch_proximity_ratio()
        self.ui.draw_pinch_meter(self.screen, ratio, self.tracker.is_pinched, self.tracker.hand_detected, self.tracker.pinch_distance)

    def run(self):
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                self.clock.tick(config.FPS)
        finally:
            self.tracker.release()
            pygame.quit()


if __name__ == "__main__":
    app = TheraHandApp()
    app.run()
