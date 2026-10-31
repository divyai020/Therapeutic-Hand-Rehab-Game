# 🖐️ Hand Rehab Game — Touchless Hand Physical Therapy

A computer-vision-powered interactive rehabilitation game designed to assist individuals recovering from hand, wrist, or finger injuries (such as post-fracture cast removal, tendon repair, or mild stroke recovery) in practicing fine-motor pinch-and-sort coordination exercises from the comfort of their laptop.

---

## 🌟 Key Features

1. **Touchless Interaction via Laptop Webcam:**
   - No costly specialized hardware or wearable glove sensors required.
   - Uses standard laptop webcams with Google MediaPipe's pre-trained deep-learning hand landmark models.

2. **Tremor Damping (Exponential Moving Average Filter):**
   - Patients recovering from hand trauma or nerve injuries often experience micro-tremors or shakiness.
   - An integrated EMA smoothing filter stabilizes the virtual cursor and ball to prevent frustration.

3. **Intentional Pinch-to-Grab & Persistence Buffer:**
   - Dual-threshold hysteresis prevents the ball from dropping mid-air if your grip slightly sways while lifting.
   - Requires an intentional opening motion to release.

4. **3 Adaptive Therapy Levels:**
   - **Easy (Gentle):** 3 large balls (Red, Green, Blue) with a generous pinch zone for stiff joints or early post-cast recovery.
   - **Medium (Standard):** 4 balls (Red, Green, Blue, Yellow) for active physical therapy.
   - **Hard (Precision):** 6 smaller balls (adds Orange and Purple) requiring fine finger opposition and endurance.

5. **Quantitative Performance Tracking & Session Reports:**
   - Tracks total repetitions, grasp accuracy %, movement time, and average hold duration.
   - Automatically exports anonymized session logs to `sessions/rehab_sessions_log.csv` for personal or therapist review.

---

## 🛠️ Architecture & Tech Stack

```text
Therapeutic_Hand_Rehab_Game/
│
├── main.py              # Main application loop, state machine & camera preview
├── hand_tracker.py      # OpenCV webcam capture, MediaPipe HandLandmarker, tremor damping
├── game_engine.py       # Colored balls, target containers, particles & metrics
├── ui_components.py     # Hand skeleton visualization, grip meter, HUD & summary modals
├── sound_effects.py     # Procedural audio chime synthesis (zero external audio files needed!)
├── config.py            # Color palettes, difficulty settings & geometry
├── requirements.txt     # Dependency specifications
└── hand_landmarker.task # MediaPipe Tasks vision model file
```

---

## 🚀 How to Run

1. Open your terminal in this directory:
   ```powershell
   cd C:\Users\Divya\Downloads\Therapeutic_Hand_Rehab_Game
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Run the application:
   ```powershell
   python main.py
   ```

### In-Game Controls:
| Key / Gesture | Action |
| :---: | :--- |
| **Thumb + Index** | Pinch to pick up and drag a ball |
| **Open Fingers** | Release ball into matching container |
| **`C`** | Toggle between live camera mirror view and dark mode |
| **`R`** | Restart / reset current exercise |
| **`M`** | Return to main menu |
| **`ESC`** | Exit |

