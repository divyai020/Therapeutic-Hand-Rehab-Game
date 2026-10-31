# TheraHand — Physical Therapy & Motor Rehabilitation Assistant

A computer-vision-powered interactive rehabilitation prototype designed to assist individuals recovering from hand, wrist, or finger injuries (such as post-fracture cast removal, tendon repair, or mild stroke recovery) in practicing fine-motor pinch-and-sort coordination exercises from the comfort of their laptop.

---

## 🌟 Key Rehabilitation & Clinical Design Features

1. **Touchless Interaction via Laptop Webcam:**
   - No costly specialized hardware or wearable glove sensors required.
   - Uses standard webcams with Google MediaPipe's pre-trained deep-learning hand landmark models.

2. **Tremor Damping (Exponential Moving Average Filter):**
   - Patients recovering from hand trauma or nerve injuries often experience micro-tremors or shakiness.
   - An integrated EMA smoothing filter stabilizes the virtual cursor and token to prevent patient frustration.

3. **Dual-Threshold Pinch Hysteresis:**
   - Prevents "grab chatter" or accidental dropping mid-air. Grasping activates when thumb and index finger approach each other, and requires an intentional release motion.

4. **Adjustable Range-of-Motion / Sensitivity Presets:**
   - **Gentle (Mild / Stiff Hand):** Large objects and generous grasp distance for patients with limited range of motion.
   - **Standard:** Balanced fine motor training for regular therapy sessions.
   - **Precision:** Tighter pinch threshold and smaller targets to challenge advanced coordination.

5. **Quantitative Performance Tracking & Session Reports:**
   - Tracks total repetitions, grasp accuracy %, movement time, and average hold duration.
   - Automatically exports anonymized session logs to `sessions/rehab_sessions_log.csv` for personal or therapist review.

---

## 🛠️ Architecture & Tech Stack

```text
Therapeutic_Hand_Rehab_Game/
│
├── main.py              # Main application loop, state machine & rendering
├── hand_tracker.py      # OpenCV webcam capture, MediaPipe HandLandmarker, tremor damping
├── game_engine.py       # Virtual therapy tokens, target baskets, particles & metrics
├── ui_components.py     # Clean clinical UI, HUD, grip proximity gauge & summary modals
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

2. Run the application:
   ```powershell
   python main.py
   ```

3. **In-Session Controls:**
   - `Pinch Gesture (Thumb + Index)`: Grab and drag virtual tokens
   - `Separate Fingers`: Release token into target basket
   - `C`: Toggle between live webcam mirror overlay and minimalist dark clinic mode
   - `R`: Reset / restart the current exercise session
   - `M`: Return to main menu
   - `ESC`: Exit application

---

## 💼 Suggested LinkedIn Post Template

Feel free to copy and personalize this for your LinkedIn post or video showcase:

> **Excited to share my latest Computer Vision & HealthTech prototype: TheraHand! 🖐️🩺**
>
> Recovering from a hand injury, surgery, or stroke requires repetitive motor-skill practice—reaching, pinching, holding, and placing objects. Traditional exercises can feel monotonous, and patients often lack objective metrics on their daily progress.
>
> I built **TheraHand**, an interactive desktop application that transforms laptop webcams into touchless physical therapy tools using Python, OpenCV, MediaPipe, and Pygame.
>
> **Key Highlights:**
> 🔹 **Sub-second Hand Tracking:** Tracks 21 anatomical hand landmarks at 60 FPS without requiring physical sensors or gloves.
> 🔹 **Tremor-Damping EMA Filter:** Stabilizes shaky finger movements so patients aren't penalized by micro-tremors.
> 🔹 **Pinch Hysteresis:** Prevents grab-and-drop chatter for a natural grasp experience.
> 🔹 **Adaptive Sensitivity Modes:** Offers Gentle, Standard, and Precision presets tailored to the patient’s range of motion.
> 🔹 **Therapist Analytics:** Automatically logs reps, accuracy %, hold stability, and completion time to local session reports.
>
> *Disclaimer: This is an experimental educational prototype exploring gamified computer vision in assistive technology, not a certified medical device.*
>
> Let me know your thoughts or feedback! #Python #ComputerVision #OpenCV #MediaPipe #HealthTech #PhysicalTherapy #Gamification #Accessibility
