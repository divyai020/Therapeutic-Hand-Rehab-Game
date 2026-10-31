"""
Real-time Hand Tracking & Gesture Detection Module.
Uses MediaPipe Tasks API (HandLandmarker) with OpenCV video capture.
Features:
- Mirror inversion for intuitive self-view
- Exponential Moving Average (EMA) smoothing for hand tremors
- Scale-invariant + pixel-based dual pinch detection
- Grasp persistence buffer (prevents accidental drops during upward motion)
- Release debounce (ensures intentional finger release)
- Full 21-landmark skeleton rendering for visual feedback
"""

import os
import math
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import config

class HandTracker:
    def __init__(self, model_path="hand_landmarker.task", camera_index=0):
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        
        # Verify model exists
        if not os.path.exists(model_path):
            alt_path = os.path.join(os.path.dirname(__file__), model_path)
            if os.path.exists(alt_path):
                model_path = alt_path
            else:
                raise FileNotFoundError(f"MediaPipe hand model not found at {model_path}")
                
        # Initialize MediaPipe Tasks HandLandmarker with forgiving confidence
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.40,  # Forgiving of finger angles
            min_hand_presence_confidence=0.40,
            min_tracking_confidence=0.40
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        self.frame_timestamp_ms = 0
        self.hand_detected = False
        self.raw_landmarks = []
        self.smoothed_landmarks = []
        
        # Pinch state
        self.thumb_pos = (0, 0)
        self.index_pos = (0, 0)
        self.pinch_pos = (0, 0)
        self.pinch_distance = 999.0
        self.hand_span = 100.0
        self.rel_pinch_ratio = 1.0
        self.is_pinched = False
        
        # Grasp stability & debounce buffers
        self.lost_frames = 0
        self.max_lost_grace = 10     # ~300ms persistence grace period
        self.open_finger_frames = 0  # Requires sustained open fingers to drop
        self.min_open_confirm = 4    # 4 consecutive frames (~130ms) to confirm release
        
        # Difficulty configuration
        self.grab_threshold = 75
        self.release_threshold = 105
        self.grab_ratio = 0.52
        self.smoothing_factor = 0.50
        
        self.latest_camera_rgb = None

    def update_difficulty(self, preset_name):
        """Applies rehabilitation difficulty settings."""
        preset = config.DIFFICULTY_PRESETS.get(preset_name)
        if not preset:
            preset = config.DIFFICULTY_PRESETS.get("Medium") or config.DIFFICULTY_PRESETS.get("Standard") or list(config.DIFFICULTY_PRESETS.values())[0]
        self.grab_threshold = preset["pinch_threshold_grab"]
        self.release_threshold = preset["pinch_threshold_release"]
        self.grab_ratio = preset["pinch_ratio_grab"]
        self.smoothing_factor = preset["smoothing_factor"]

    def process_frame(self, screen_w, screen_h):
        """
        Captures camera frame, runs MediaPipe detection, updates smoothed landmarks & pinch state.
        Returns: True if a hand was detected (or kept in persistence), False otherwise.
        """
        if not self.cap.isOpened():
            return False

        ret, frame = self.cap.read()
        if not ret:
            return False

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.latest_camera_rgb = frame_rgb

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        self.frame_timestamp_ms += 33
        
        results = self.detector.detect_for_video(mp_image, self.frame_timestamp_ms)

        if results.hand_landmarks and len(results.hand_landmarks) > 0:
            self.hand_detected = True
            self.lost_frames = 0
            landmarks = results.hand_landmarks[0]
            
            # Map normalized coordinates (0.0 to 1.0) with comfortable reach margin
            margin = 0.08
            current_raw = []
            for lm in landmarks:
                norm_x = (lm.x - margin) / (1.0 - 2 * margin)
                norm_y = (lm.y - margin) / (1.0 - 2 * margin)
                sx = int(norm_x * screen_w)
                sy = int(norm_y * screen_h)
                sx = max(10, min(screen_w - 10, sx))
                sy = max(10, min(screen_h - 10, sy))
                current_raw.append((sx, sy))
                
            self.raw_landmarks = current_raw
            
            # Exponential Moving Average (EMA) tremor filter
            if not self.smoothed_landmarks or len(self.smoothed_landmarks) != len(current_raw):
                self.smoothed_landmarks = current_raw
            else:
                alpha = 1.0 - self.smoothing_factor
                smoothed = []
                for prev, curr in zip(self.smoothed_landmarks, current_raw):
                    sm_x = int(alpha * curr[0] + (1.0 - alpha) * prev[0])
                    sm_y = int(alpha * curr[1] + (1.0 - alpha) * prev[1])
                    smoothed.append((sm_x, sm_y))
                self.smoothed_landmarks = smoothed

            # Extract Thumb Tip (4) and Index Tip (8)
            self.thumb_pos = self.smoothed_landmarks[4]
            self.index_pos = self.smoothed_landmarks[8]
            
            self.pinch_pos = (
                (self.thumb_pos[0] + self.index_pos[0]) // 2,
                (self.thumb_pos[1] + self.index_pos[1]) // 2
            )
            
            dx = self.thumb_pos[0] - self.index_pos[0]
            dy = self.thumb_pos[1] - self.index_pos[1]
            self.pinch_distance = math.hypot(dx, dy)

            # Scale-Invariant Hand Span (Wrist [0] to Middle Knuckle [9])
            wrist = self.smoothed_landmarks[0]
            mcp = self.smoothed_landmarks[9]
            self.hand_span = max(40.0, math.hypot(wrist[0] - mcp[0], wrist[1] - mcp[1]))
            self.rel_pinch_ratio = self.pinch_distance / self.hand_span
            
            # Dual Hysteresis Pinch Detection with Release Debounce
            pinch_condition_enter = (self.pinch_distance <= self.grab_threshold) or (self.rel_pinch_ratio <= self.grab_ratio)
            pinch_condition_exit = (self.pinch_distance > self.release_threshold) and (self.rel_pinch_ratio > (self.grab_ratio + 0.18))

            if not self.is_pinched:
                if pinch_condition_enter:
                    self.is_pinched = True
                    self.open_finger_frames = 0
            else:
                if pinch_condition_exit:
                    self.open_finger_frames += 1
                    # Only release when fingers stay open for multiple consecutive frames (stops accidental drops!)
                    if self.open_finger_frames >= self.min_open_confirm:
                        self.is_pinched = False
                else:
                    self.open_finger_frames = 0
                    
            return True
        else:
            # Temporary frame loss handling (hand persistence grace period)
            self.lost_frames += 1
            if self.lost_frames <= self.max_lost_grace and self.smoothed_landmarks:
                # Keep hand state active during momentary frame drops (e.g. quick upward motion)
                self.hand_detected = True
                return True
            else:
                # Extended loss: release grasp
                self.hand_detected = False
                self.is_pinched = False
                self.open_finger_frames = 0
                return False

    def get_pinch_proximity_ratio(self):
        if not self.hand_detected:
            return 0.0
        open_ratio = self.grab_ratio + 0.50
        clamped = max(self.grab_ratio, min(open_ratio, self.rel_pinch_ratio))
        ratio = 1.0 - ((clamped - self.grab_ratio) / (open_ratio - self.grab_ratio))
        return float(np.clip(ratio, 0.0, 1.0))

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
