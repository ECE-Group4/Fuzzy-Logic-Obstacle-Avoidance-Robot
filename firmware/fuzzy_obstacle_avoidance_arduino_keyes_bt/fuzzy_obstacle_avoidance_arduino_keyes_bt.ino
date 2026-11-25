/*
 * Fuzzy Logic Obstacle Avoidance Robot with Keyes Bluetooth Remote
 * Course: Artificial Intelligence and Logic
 *
 * Hardware:
 *   - Arduino Uno R3
 *   - Keyes Bluetooth Module (HC-05 / HC-06) on Pin 3 (RX) and Pin 11 (TX)
 *   - HC-SR04 Ultrasonic Distance Sensor
 *   - L298N Dual H-Bridge Motor Driver
 *
 * Modes:
 *   - 'A' : Autonomous Fuzzy Logic Obstacle Avoidance
 *   - 'M' : Manual Bluetooth Remote Control
 *   - 'F', 'B', 'L', 'R', 'S' : Manual Steering
 */

#include <SoftwareSerial.h>

// Bluetooth Module Serial on Pins 3 (RX) and 11 (TX)
SoftwareSerial bluetooth(3, 11);

// Ultrasonic Sensor Pins
const int TRIG_PIN = 9;
const int ECHO_PIN = 10;

// L298N Motor Driver Pins
const int ENA = 5;  // Left Motor PWM
const int IN1 = 7;
const int IN2 = 8;
const int ENB = 6;  // Right Motor PWM
const int IN3 = 4;
const int IN4 = 2;

// Distance Parameters
const float STOP_DISTANCE_CM = 20.0;  // Stop when closer than 20 cm
const float MAX_DISTANCE_CM  = 200.0; // 2 meters max range

// Operation Modes
enum DriveMode { AUTONOMOUS, MANUAL };
DriveMode currentMode = MANUAL;
char currentCommand = 'S';

// Membership Functions
float trimf(float x, float a, float b, float c) {
  if (x <= a || x >= c) return 0.0;
  if (x == b) return 1.0;
  if (x > a && x < b) return (x - a) / (b - a);
  return (c - x) / (c - b);
}

float trimfLeft(float x, float b, float c) {
  if (x <= b) return 1.0;
  if (x >= c) return 0.0;
  return (c - x) / (c - b);
}

float trimfRight(float x, float a, float b) {
  if (x <= a) return 0.0;
  if (x >= b) return 1.0;
  return (x - a) / (b - a);
}

float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duration == 0) return MAX_DISTANCE_CM;
  return constrain((duration * 0.0343) / 2.0, 0.0, MAX_DISTANCE_CM);
}

void drive(int leftSpeed, int rightSpeed, bool leftFwd, bool rightFwd) {
  digitalWrite(IN1, leftFwd ? HIGH : LOW);
  digitalWrite(IN2, leftFwd ? LOW : HIGH);
  digitalWrite(IN3, rightFwd ? HIGH : LOW);
  digitalWrite(IN4, rightFwd ? LOW : HIGH);
  analogWrite(ENA, constrain(abs(leftSpeed), 0, 255));
  analogWrite(ENB, constrain(abs(rightSpeed), 0, 255));
}

void stopMotors() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  analogWrite(ENA, 0);   analogWrite(ENB, 0);
}

void setup() {
  Serial.begin(115200);
  bluetooth.begin(9600);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);

  // Soft-start delay to stabilize battery voltage
  stopMotors();
  delay(2000);

  Serial.println("Robot Ready. Bluetooth listening on 9600 baud.");
}

void loop() {
  // Check for Bluetooth input
  if (bluetooth.available()) {
    char cmd = bluetooth.read();
    if (cmd == 'A' || cmd == 'a') {
      currentMode = AUTONOMOUS;
      bluetooth.println("Switched to Autonomous Mode");
    } else if (cmd == 'M' || cmd == 'm') {
      currentMode = MANUAL;
      currentCommand = 'S';
      stopMotors();
      bluetooth.println("Switched to Manual Mode");
    } else if (currentMode == MANUAL) {
      currentCommand = cmd;
    }
  }

  float distance = readDistanceCm();

  // Fuzzification
  float muNear   = trimfLeft(distance, 0.0, 60.0);
  float muMedium = trimf(distance, 40.0, 100.0, 160.0);
  float muFar    = trimfRight(distance, 140.0, 200.0);

  // Defuzzification (Weighted Average)
  float num = (muNear * 20.0) + (muMedium * 60.0) + (muFar * 100.0);
  float den = muNear + muMedium + muFar;
  float speedPercent = (den > 0.0) ? (num / den) : 0.0;
  int fuzzyPwm = (int)round((speedPercent / 100.0) * 255.0);

  if (distance <= STOP_DISTANCE_CM) {
    fuzzyPwm = 0;
  }

  // Autonomous or Manual Behavior
  if (currentMode == AUTONOMOUS) {
    if (distance <= STOP_DISTANCE_CM) {
      // Evasive turn when obstacle is close
      stopMotors();
      delay(150);
      drive(130, 130, false, false); delay(350); // reverse
      drive(140, 140, false, true);  delay(300); // turn
      stopMotors();
    } else {
      drive(fuzzyPwm, fuzzyPwm, true, true);
    }
  } else {
    // Manual steering with safety braking
    switch (currentCommand) {
      case 'F': case 'f':
        if (distance <= STOP_DISTANCE_CM) {
          stopMotors();
          bluetooth.println("Obstacle ahead! Auto-brake engaged.");
        } else {
          drive(fuzzyPwm, fuzzyPwm, true, true);
        }
        break;
      case 'B': case 'b': drive(180, 180, false, false); break;
      case 'L': case 'l': drive(160, 160, false, true);  break;
      case 'R': case 'r': drive(160, 160, true, false);  break;
      case 'S': case 's':
      default:
        stopMotors();
        break;
    }
  }

  delay(60);
}
