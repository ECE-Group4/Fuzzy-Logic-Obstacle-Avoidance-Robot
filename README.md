# Fuzzy Logic Obstacle Avoidance Robot

A mobile robot project implementing a **Fuzzy Logic Controller (FLC)** for smooth obstacle avoidance and speed regulation using triangular membership functions.

Unlike crisp bang-bang control (*"if distance < 20 cm, stop; else full speed"*), fuzzy control continuously computes motor speed based on obstacle distance, producing smooth acceleration, deceleration, and collision avoidance.

---

## Project Structure

```
.
├── Makefile                                                    # Build and simulation targets
├── run_all.sh                                                  # Full verification script
├── docs/
│   ├── LAB_REPORT.md                                           # Complete practical lab report
│   ├── SYSTEM_BLOCK_DIAGRAM.md                                 # Block diagram and control pipeline
│   └── WIRING_AND_SCHEMATICS.md                                # Circuit diagrams and pinout tables
├── firmware/
│   ├── include/
│   │   └── FuzzyLogicController.h                              # C++ Fuzzy Logic Controller class
│   ├── fuzzy_obstacle_avoidance_arduino_uno/
│   │   └── fuzzy_obstacle_avoidance_arduino_uno.ino            # Arduino Uno autonomous FLC firmware
│   └── fuzzy_obstacle_avoidance_arduino_keyes_bt/
│       └── fuzzy_obstacle_avoidance_arduino_keyes_bt.ino       # Arduino Uno + Keyes Bluetooth firmware
├── simulation/
│   ├── fuzzy_controller.py                                     # Python FLC model
│   ├── generate_plots.py                                       # Membership function & curve plot generator
│   └── robot_simulation.py                                     # Terminal simulation & results table
└── images/
    ├── membership_functions.png                                # Triangular membership functions plot
    ├── flc_speed_response_curve.png                            # Control surface (fuzzy vs crisp)
    └── system_block_diagram.png                                # System block diagram
```

---

## Hardware Requirements

* **Microcontroller:** Arduino Uno R3 (ATmega328P)
* **Distance Sensor:** HC-SR04 Ultrasonic Sensor (measures 2 cm – 400 cm)
* **Motor Driver:** L298N Dual H-Bridge
* **Chassis:** 2WD robot chassis with DC geared motors
* **Power Supply:** 7.4V – 12V Li-ion battery pack
* **Optional:** Keyes Bluetooth Module (HC-05 / HC-06) for wireless control

---

## Fuzzy Controller Design

### 1. Triangular Membership Function Formula
$$\mu(x; a, b, c) = \max\left(0, \min\left(\frac{x - a}{b - a}, \frac{c - x}{c - b}\right)\right)$$

### 2. Distance Input ($d \in [0, 100]\text{ cm}$)
* **Near:** Left-shoulder triangle $(0, 0, 30)$ cm
* **Medium:** Symmetric triangle $(15, 45, 75)$ cm
* **Far:** Right-shoulder triangle $(60, 100, 100)$ cm

### 3. Output Motor Speed ($v \in [0, 100]\%$)
* **Slow:** Centroid $20\%$ (PWM 51)
* **Medium:** Centroid $60\%$ (PWM 153)
* **Fast:** Centroid $100\%$ (PWM 255)
* *(Safety Barrier: if $d \le 20\text{ cm}$, motors stop moving completely).*

### 4. Defuzzification (Weighted Average)
$$v_{\text{out}} = \frac{\mu_{\text{Near}} \cdot 20 + \mu_{\text{Medium}} \cdot 60 + \mu_{\text{Far}} \cdot 100}{\mu_{\text{Near}} + \mu_{\text{Medium}} + \mu_{\text{Far}}}$$

### 5. Worked Example ($d = 25\text{ cm}$)
* $\mu_{\text{Near}}(25) = \frac{30 - 25}{30} = 0.167$
* $\mu_{\text{Medium}}(25) = \frac{25 - 15}{30} = 0.333$
* $\mu_{\text{Far}}(25) = 0.0$
* $v_{\text{out}} = \frac{(0.167 \times 20) + (0.333 \times 60)}{0.167 + 0.333} = \frac{23.33}{0.50} = \mathbf{46.7\%}$
* $\text{PWM Output} = 0.467 \times 255 \approx \mathbf{119}$

---

## How to Run

### 1. Run Verification & Generate Plots
```bash
chmod +x run_all.sh
./run_all.sh
```

### 2. Run Python Simulation
```bash
python3 simulation/robot_simulation.py --demo
```

### 3. Upload Code to Arduino Uno
Using Arduino CLI:
```bash
arduino-cli compile --fqbn arduino:avr:uno firmware/fuzzy_obstacle_avoidance_arduino_uno
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno firmware/fuzzy_obstacle_avoidance_arduino_uno
```
*(Or open the `.ino` files directly in the official Arduino IDE).*
