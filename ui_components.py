"""
UI Components & Rendering for Therapeutic Hand Coordination Game.
Includes full 21-landmark hand skeleton visualization, real-time grip meter,
clean session summary modal, and human-designed welcome screens.
"""

import math
import pygame
import config

class UIButton:
    def __init__(self, rect, text, bg_color=config.COLOR_CARD, hover_color=(40, 52, 75), text_color=config.COLOR_TEXT_PRIMARY, border_color=config.COLOR_PANEL_BORDER):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface, font):
        col = self.hover_color if self.is_hovered else self.bg_color
        # Shadow
        pygame.draw.rect(surface, (0, 0, 0, 50), self.rect.move(0, 2), border_radius=12)
        # Body
        pygame.draw.rect(surface, col, self.rect, border_radius=12)
        # Border
        b_col = self.border_color if not self.is_hovered else config.COLOR_ACCENT_TEAL
        pygame.draw.rect(surface, b_col, self.rect, width=2, border_radius=12)
        
        txt_surf = font.render(self.text, True, self.text_color)
        t_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, t_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class UIRenderer:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        
        pygame.font.init()
        self.font_large = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 34, bold=True)
        self.font_mid = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 20, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 16)
        self.font_tiny = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13)

    def draw_top_hud(self, surface, current_reps, target_reps, elapsed_sec, difficulty_name, instruction_text):
        """Top exercise HUD banner."""
        hud_rect = pygame.Rect(0, 0, self.w, 75)
        pygame.draw.rect(surface, config.COLOR_PANEL, hud_rect)
        pygame.draw.line(surface, config.COLOR_PANEL_BORDER, (0, 75), (self.w, 75), 2)

        # App Title
        title = self.font_mid.render("Hand Rehab Game", True, config.COLOR_ACCENT_TEAL)
        surface.blit(title, (24, 15))
        sub = self.font_tiny.render("Physical Therapy & Coordination", True, config.COLOR_TEXT_MUTED)
        surface.blit(sub, (24, 42))

        # Active Difficulty Badge
        diff_badge = f"Mode: {difficulty_name}"
        diff_surf = self.font_tiny.render(diff_badge, True, config.COLOR_TEXT_PRIMARY)
        d_bg = pygame.Rect(self.w - 180, 15, 155, 26)
        pygame.draw.rect(surface, config.COLOR_CARD, d_bg, border_radius=6)
        pygame.draw.rect(surface, config.COLOR_PANEL_BORDER, d_bg, width=1, border_radius=6)
        surface.blit(diff_surf, (self.w - 170, 19))

        # Timer
        mins = elapsed_sec // 60
        secs = elapsed_sec % 60
        timer_str = f"Time: {mins:02d}:{secs:02d}"
        t_surf = self.font_tiny.render(timer_str, True, config.COLOR_TEXT_MUTED)
        surface.blit(t_surf, (self.w - 170, 46))

        # Progress bar (center)
        center_x = self.w // 2
        bar_w = 320
        bar_h = 14
        bar_rect = pygame.Rect(center_x - bar_w // 2, 45, bar_w, bar_h)
        pygame.draw.rect(surface, config.COLOR_CARD, bar_rect, border_radius=7)
        
        progress = (current_reps / max(1, target_reps))
        fill_w = int(bar_w * max(0.0, min(1.0, progress)))
        if fill_w > 0:
            fill_rect = pygame.Rect(center_x - bar_w // 2, 45, fill_w, bar_h)
            pygame.draw.rect(surface, config.COLOR_ACCENT_EMERALD, fill_rect, border_radius=7)
        pygame.draw.rect(surface, config.COLOR_PANEL_BORDER, bar_rect, width=1, border_radius=7)

        # Instruction Text
        inst_surf = self.font_mid.render(instruction_text, True, config.COLOR_TEXT_PRIMARY)
        i_rect = inst_surf.get_rect(center=(center_x, 24))
        surface.blit(inst_surf, i_rect)

        # Reps counter text
        reps_str = f"{current_reps} / {target_reps} Sorted"
        r_surf = self.font_tiny.render(reps_str, True, config.COLOR_TEXT_MUTED)
        surface.blit(r_surf, (center_x + bar_w // 2 + 12, 44))

    def draw_pinch_meter(self, surface, pinch_ratio, is_pinched, hand_detected, pinch_dist_px):
        """Bottom-left grip gauge."""
        meter_x = 30
        meter_y = self.h - 105
        meter_w = 230
        meter_h = 75

        c_rect = pygame.Rect(meter_x, meter_y, meter_w, meter_h)
        pygame.draw.rect(surface, config.COLOR_PANEL, c_rect, border_radius=10)
        border_col = config.COLOR_ACCENT_EMERALD if is_pinched else config.COLOR_PANEL_BORDER
        pygame.draw.rect(surface, border_col, c_rect, width=2, border_radius=10)

        pct = int(pinch_ratio * 100)
        if not hand_detected:
            lbl_text = "Hand Not Detected"
            lbl_col = (244, 90, 90)
            status_text = "Place hand in view"
            status_col = config.COLOR_TEXT_MUTED
        elif is_pinched:
            lbl_text = f"Pinch Grip: {pct}%"
            lbl_col = config.COLOR_ACCENT_EMERALD
            status_text = "PINCH GRASPED!"
            status_col = config.COLOR_ACCENT_EMERALD
        else:
            lbl_text = f"Finger Distance: {int(pinch_dist_px)}px"
            lbl_col = config.COLOR_TEXT_MUTED
            status_text = f"Pinching ({pct}%)" if pct > 40 else "Ready / Open Hand"
            status_col = (80, 180, 255) if pct > 40 else config.COLOR_TEXT_PRIMARY

        surface.blit(self.font_tiny.render(lbl_text, True, lbl_col), (meter_x + 14, meter_y + 10))
        surface.blit(self.font_mid.render(status_text, True, status_col), (meter_x + 14, meter_y + 30))

        pb_rect = pygame.Rect(meter_x + 14, meter_y + 56, meter_w - 28, 8)
        pygame.draw.rect(surface, config.COLOR_CARD, pb_rect, border_radius=4)
        if hand_detected and pinch_ratio > 0:
            fill_w = int((meter_w - 28) * pinch_ratio)
            col = config.COLOR_ACCENT_EMERALD if is_pinched else (80, 180, 255)
            pygame.draw.rect(surface, col, (meter_x + 14, meter_y + 56, fill_w, 8), border_radius=4)

    def draw_skeleton(self, surface, landmarks, is_pinched):
        """Full hand skeleton with joints, finger rings, and pinch cursor."""
        if not landmarks or len(landmarks) < 21:
            return

        # 1. Draw bones
        for p1_idx, p2_idx in config.HAND_CONNECTIONS:
            p1 = landmarks[p1_idx]
            p2 = landmarks[p2_idx]
            pygame.draw.line(surface, config.COLOR_PANEL_BORDER, p1, p2, 3)

        # 2. Draw joints
        for idx, (px, py) in enumerate(landmarks):
            if idx in (4, 8):
                # Thumb tip & Index tip
                ring_col = config.COLOR_ACCENT_EMERALD if is_pinched else (80, 180, 255)
                pygame.draw.circle(surface, ring_col, (px, py), 10, 2)
                pygame.draw.circle(surface, (255, 255, 255), (px, py), 4)
            else:
                pygame.draw.circle(surface, config.COLOR_TEXT_MUTED, (px, py), 3)

        # 3. Midpoint grasp cursor
        t = landmarks[4]
        i = landmarks[8]
        mx = (t[0] + i[0]) // 2
        my = (t[1] + i[1]) // 2

        if is_pinched:
            pygame.draw.line(surface, config.COLOR_ACCENT_EMERALD, t, i, 4)
            pygame.draw.circle(surface, config.COLOR_ACCENT_EMERALD, (mx, my), 16, 3)
            pygame.draw.circle(surface, (255, 255, 255), (mx, my), 6)
        else:
            pygame.draw.line(surface, (255, 255, 255, 110), t, i, 1)
            pygame.draw.circle(surface, (80, 180, 255), (mx, my), 14, 2)
            pygame.draw.circle(surface, (255, 255, 255), (mx, my), 3)

    def draw_session_summary_modal(self, surface, stats):
        """Clinical summary card."""
        modal_w = 540
        modal_h = 390
        modal_x = (self.w - modal_w) // 2
        modal_y = (self.h - modal_h) // 2

        dim_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 160))
        surface.blit(dim_surf, (0, 0))

        card_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
        pygame.draw.rect(surface, config.COLOR_PANEL, card_rect, border_radius=14)
        pygame.draw.rect(surface, config.COLOR_ACCENT_TEAL, card_rect, width=2, border_radius=14)

        head = self.font_large.render("Session Completed!", True, config.COLOR_ACCENT_EMERALD)
        h_rect = head.get_rect(center=(self.w // 2, modal_y + 40))
        surface.blit(head, h_rect)

        subhead = self.font_small.render("Physical Therapy Motor Coordination Summary", True, config.COLOR_TEXT_MUTED)
        s_rect = subhead.get_rect(center=(self.w // 2, modal_y + 75))
        surface.blit(subhead, s_rect)

        metrics = [
            ("Reps Completed", f"{stats.correct_placements} / {stats.reps_target}"),
            ("Grasp Accuracy", f"{stats.get_accuracy_pct()}%"),
            ("Session Duration", f"{stats.get_elapsed_seconds()} seconds"),
            ("Avg Hold Stability", f"{stats.get_avg_hold_time()}s per rep"),
            ("Difficulty Level", f"{stats.difficulty_name}"),
        ]

        y_offset = modal_y + 115
        for label, val in metrics:
            pygame.draw.line(surface, config.COLOR_PANEL_BORDER, (modal_x + 30, y_offset + 24), (modal_x + modal_w - 30, y_offset + 24), 1)
            l_surf = self.font_small.render(label, True, config.COLOR_TEXT_MUTED)
            surface.blit(l_surf, (modal_x + 35, y_offset))
            v_surf = self.font_mid.render(val, True, config.COLOR_TEXT_PRIMARY)
            v_rect = v_surf.get_rect(right=modal_x + modal_w - 35, top=y_offset)
            surface.blit(v_surf, v_rect)
            y_offset += 36

        note = self.font_tiny.render("Regular low-strain repetition supports neural-motor recovery.", True, config.COLOR_ACCENT_TEAL)
        n_rect = note.get_rect(center=(self.w // 2, modal_y + 310))
        surface.blit(note, n_rect)
