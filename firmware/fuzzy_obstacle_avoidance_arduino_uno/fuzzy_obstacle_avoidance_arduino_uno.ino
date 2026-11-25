/*
 * Fuzzy Logic Obstacle Avoidance Robot
 * Course: Artificial Intelligence and Logic
 * 
 * Hardware:
 *   - Arduino Uno R3
 *   - HC-SR04 Ultrasonic Distance Sensor
 *   - L298N Dual H-Bridge Motor Driver
 *   - 2WD DC Motor Chassis
 * 
 * Behavior:
 *   - Uses triangular membership functions (Near, Medium, Far)
 *   - Smoothly adjusts speed based on obstacle distance (0 to 200 cm)
 *   - Automatically stops when an obstacle is within 20 cm
 */

// Ultrasonic Sensor Pins
const int TRIG_PIN = 9;
const int ECHO_PIN = 10;

// L298N Motor Driver Pins
const int ENA = 5;  // PWM Left
const int IN1 = 7;
const int IN2 = 8;
const int ENB = 6;  // PWM Right
const int IN3 = 4;
const int IN4 = 2;

// Distance Parameters
const float STOP_DISTANCE_CM = 20.0;  // Stop when closer than 20 cm
const float MAX_DISTANCE_CM  = 200.0; // 2 meters max range (Far)

// Standard triangular membership function
float trimf(float x, float a, float b, float c) {
  if (x <= a || x >= c) return 0.0;
  if (x == b) return 1.0;
  if (x > a && x < b) return (x - a) / (b - a);
  return (c - x) / (c - b);
}

// Left shoulder function for "Near"
float trimfLeft(float x, float b, float c) {
  if (x <= b) return 1.0;
  if (x >= c) return 0.0;
  return (c - x) / (c - b);
}

// Right shoulder function for "Far"
float trimfRight(float x, float a, float b) {
  if (x <= a) return 0.0;
  if (x >= b) return 1.0;
  return (x - a) / (b - a);
}

// Read obstacle distance in centimeters using HC-SR04
float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // 30ms timeout (~5m)
  if (duration == 0) {
    return MAX_DISTANCE_CM; // No echo, assume clear pathway
  }
  float dist = (duration * 0.0343) / 2.0;
  return constrain(dist, 0.0, MAX_DISTANCE_CM);
}

// Drive forward with PWM speed (0 to 255)
void setMotorSpeed(int pwmVal) {
  pwmVal = constrain(pwmVal, 0, 255);

  if (pwmVal == 0) {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
    analogWrite(ENA, 0);
    analogWrite(ENB, 0);
    return;
  }

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, pwmVal);
  analogWrite(ENB, pwmVal);
}

// Evasive maneuver if obstacle is dangerously close (< 12 cm)
void evadeObstacle() {
  setMotorSpeed(0);
  delay(150);

  // Reverse briefly
  digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH);
  analogWrite(ENA, 130);   analogWrite(ENB, 130);
  delay(350);

  // Pivot turn to find a clear path
  digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  analogWrite(ENA, 140);   analogWrite(ENB, 140);
  delay(300);

  setMotorSpeed(0);
}

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);

  // Soft-start: Keep motors completely off for 2 seconds
  // This allows the battery and microcontroller power rails to stabilize
  setMotorSpeed(0);
  delay(2000);

  Serial.println("Fuzzy Logic Obstacle Avoidance Robot Initialized");
  Serial.println("Dist(cm)\tNear\tMed\tFar\tSpeed%\tPWM\tStatus");
}

void loop() {
  float distance = readDistanceCm();

  // Safety: Stop if obstacle is within 20 cm
  if (distance <= STOP_DISTANCE_CM) {
    setMotorSpeed(0);

    if (distance < 12.0) {
      Serial.print("Dist: "); Serial.print(distance, 1);
      Serial.println(" cm | Danger Close -> Turning Away");
      evadeObstacle();
    } else {
      Serial.print("Dist: "); Serial.print(distance, 1);
      Serial.println(" cm | Stopped (Within 20 cm)");
      delay(100);
    }
    return;
  }

  // 1. Fuzzification
  // Near: peak at 0, 0 at 60 cm
  // Medium: (40, 100, 160) cm - peak at 1m
  // Far: 0 at 140, peak at 200 cm (2m)
  float muNear   = trimfLeft(distance, 0.0, 60.0);
  float muMedium = trimf(distance, 40.0, 100.0, 160.0);
  float muFar    = trimfRight(distance, 140.0, 200.0);

  // 2. Rule Evaluation & Defuzzification (Weighted Average)
  // Consequents: Slow = 20%, Medium = 60%, Fast = 100%
  float numerator   = (muNear * 20.0) + (muMedium * 60.0) + (muFar * 100.0);
  float denominator = muNear + muMedium + muFar;
  float speedPercent = (denominator > 0.0) ? (numerator / denominator) : 0.0;

  int pwm = (int)round((speedPercent / 100.0) * 255.0);
  pwm = constrain(pwm, 0, 255);

  setMotorSpeed(pwm);

  // Serial Monitor Output
  Serial.print("Dist: "); Serial.print(distance, 1);
  Serial.print(" cm | Near: "); Serial.print(muNear, 2);
  Serial.print(" Med: "); Serial.print(muMedium, 2);
  Serial.print(" Far: "); Serial.print(muFar, 2);
  Serial.print(" | Speed: "); Serial.print(speedPercent, 1);
  Serial.print("% (PWM: "); Serial.print(pwm); Serial.println(")");

  delay(100);
}
