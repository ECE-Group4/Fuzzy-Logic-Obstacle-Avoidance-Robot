# Hardware Wiring & Schematic Guide

This document provides complete, pin-by-pin hardware connection specifications for building the **Fuzzy Logic Obstacle Avoidance & Speed Regulating Robot** using an **Arduino Uno R3**.

---

## 1. System Components & Specifications

| Component | Part / Model | Operating Voltage | Function |
|---|---|---|---|
| **Microcontroller** | Arduino Uno R3 / Nano (ATmega328P) | 5V Logic (7–12V via VIN / DC Jack) | 8-bit MCU running Fuzzy Logic Controller |
| **Distance Sensor** | HC-SR04 Ultrasonic Module | 5V DC | Emits 40kHz ultrasound; measures 2 cm – 400 cm |
| **Motor Driver** | L298N Dual H-Bridge | 5V Logic, 7.4–12V Motor VIN | Independent direction & PWM speed regulation |
| **Drive Motors** | 2x TT Geared DC Motors (1:48) | 3V – 9V DC | Differential steering & forward propulsion |
| **Power Source** | 2S (7.4V) Li-ion or 6x AA Pack | 7.4V – 9.0V | High-current power for motors and logic |
| **Optional Bluetooth** | Keyes / Keyestudio HC-05 / HC-06 | 3.6V – 6V DC | Wireless remote control & telemetry |

---

## 2. Arduino Uno / Nano Connection Pinout

> [!IMPORTANT]
> **Remove the two black jumper caps** from `ENA` and `ENB` on the L298N module before connecting Arduino pins 5 and 6! Leaving the jumpers on ties `ENA`/`ENB` permanently to 5V (100% speed), preventing PWM speed regulation.

| Arduino Uno Pin | L298N Motor Driver Pin | HC-SR04 Sensor Pin | Function / Description |
|---|---|---|---|
| **Pin 9** | — | `TRIG` | Ultrasonic trigger pulse (10 µs) |
| **Pin 10** | — | `ECHO` | Ultrasonic pulse return time input |
| **Pin 5** (PWM Timer0) | `ENA` (Jumper removed) | — | Left Motor PWM Speed Control |
| **Pin 7** | `IN1` | — | Left Motor Direction Bit 1 |
| **Pin 8** | `IN2` | — | Left Motor Direction Bit 2 |
| **Pin 6** (PWM Timer0) | `ENB` (Jumper removed) | — | Right Motor PWM Speed Control |
| **Pin 4** | `IN3` | — | Right Motor Direction Bit 1 |
| **Pin 2** | `IN4` | — | Right Motor Direction Bit 2 |
| **5V** | `5V` (Logic Supply) | `VCC` | 5V Power for sensor and L298N logic |
| **GND** | `GND` | `GND` | **Common Ground** (Must connect to battery (-)) |

---

## 3. Power Architecture & Grounding Rules

```
                      +-------------------+
                      | 7.4V - 9.0V Pack  |
                      +---------+---------+
                                |
                   +------------+------------+
                   |                         |
               (+) |                     (-) |
                   v                         v
         +-------------------+     +-------------------+
         | L298N Motor VIN   |     | COMMON GROUND BUS | <---+
         +-------------------+     +---------+---------+     |
                   |                         |               |
             Internal 7805                   |               |
                   |                         |               |
                   v (5V Logic)              |               |
       +-----------+-----------+             |               |
       |                       |             |               |
       v                       v             v               |
+--------------+       +--------------+  +-------+           |
| HC-SR04 VCC  |       | Arduino 5V   |  | Logic |           |
|              |       | (Pin 5V)     |  | GND   | ----------+
+--------------+       +--------------+  +-------+
```

1. **Common Ground:** The negative terminal (-) of the battery pack, the GND of the L298N, the GND of the microcontroller, and the GND of the HC-SR04 **MUST** all be connected together. Without a common ground reference, the PWM signals float, causing jittery or unresponsive motors.
2. **L298N 5V Regulator Jumper:**
   - Keep the on-board 5V regulator jumper **ON** the L298N. Connect the L298N `5V` screw terminal directly to the Arduino's **`5V` pin** (NOT the `VIN` pin).
3. **Soft-Start Power Delay:**
   - The Arduino firmware incorporates a 2-second boot delay during which the motors stay completely OFF (`PWM = 0`). This prevents startup inrush current from causing an under-voltage brownout when operating on battery power.

---

## 4. Keyes Bluetooth Module Wiring

The **Keyes Bluetooth module** (HC-05 / HC-06) enables wireless remote steering and telemetry:

```
       Arduino Uno R3                   Keyes Bluetooth Module
+--------------------------+          +------------------------+
|                      5V  | -------> | VCC (3.6V - 6V DC)     |
|                      GND | -------> | GND                    |
|             Pin 3 (RX)   | <------- | TXD (Transmit data)    |
|             Pin 11 (TX)  | --[1kΩ]--+ RXD (Receive data)     |
|                          |          |   |                    |
|                          |          |  [2kΩ]                 |
|                          |          |   |                    |
|                          |          +--GND (Level divider)   |
+--------------------------+          +------------------------+
```

### Pin-to-Pin Connection Table:

| Keyes Module Pin | Arduino Uno Pin | Description |
|---|---|---|
| **VCC** | **5V** | Power (Keyes breakout has onboard 3.3V LDO regulator) |
| **GND** | **GND** | Common ground reference |
| **TXD** | **Pin 3** | Keyes transmit $\rightarrow$ Arduino `SoftwareSerial` receive |
| **RXD** | **Pin 11** | Arduino transmit $\rightarrow$ Keyes receive (via 1k/2k voltage divider) |

* **Default Baud Rate:** `9600 bps`
* **Default Pairing PIN:** `1234` or `0000`
