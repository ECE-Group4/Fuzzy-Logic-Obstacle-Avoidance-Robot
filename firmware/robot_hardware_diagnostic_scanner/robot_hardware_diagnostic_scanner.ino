/**
 * =========================================================================================
 * Robot Hardware Pin Auto-Scanner & Diagnostic Tool
 * Course: Artificial Intelligence and Logic
 * 
 * Purpose:
 *   Automatically discovers which pins your HC-SR04 ultrasonic sensor and motors
 *   are physically connected to WITHOUT needing to trace crowded wires!
 * 
 * How to use:
 *   1. Upload this sketch to your Arduino Uno via USB.
 *   2. Open the Serial Monitor at 115200 baud.
 *   3. Wave your hand in front of the ultrasonic sensor (~20 cm away).
 *   4. The tool scans all digital/analog pins and prints the EXACT pin numbers!
 * =========================================================================================
 */

// Candidate pins to test
const int candidatePins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, A0, A1, A2, A3};
const int numPins = sizeof(candidatePins) / sizeof(candidatePins[0]);

int detectedTrig = -1;
int detectedEcho = -1;

void testUltrasonic() {
  Serial.println("\n-----------------------------------------------------------");
  Serial.println("  SCANNING FOR HC-SR04 ULTRASONIC SENSOR PINS...");
  Serial.println("  (Please place your hand ~20 cm in front of the sensor)   ");
  Serial.println("-----------------------------------------------------------");

  bool found = false;

  for (int t = 0; t < numPins; t++) {
    int trig = candidatePins[t];

    for (int e = 0; e < numPins; e++) {
      if (t == e) continue;
      int echo = candidatePins[e];

      // Configure test pins
      pinMode(trig, OUTPUT);
      pinMode(echo, INPUT);

      // Send 10us ultrasonic trigger pulse
      digitalWrite(trig, LOW);
      delayMicroseconds(2);
      digitalWrite(trig, HIGH);
      delayMicroseconds(10);
      digitalWrite(trig, LOW);

      // Listen for echo (timeout 25ms corresponds to ~4 meters)
      long duration = pulseIn(echo, HIGH, 25000);

      if (duration > 150 && duration < 24000) {
        float distance = (duration * 0.0343f) / 2.0f;
        // Verify reading is plausible (2 cm - 300 cm)
        if (distance >= 2.0f && distance <= 300.0f) {
          Serial.print(">>> [MATCH FOUND!] Ultrasonic Sensor Detected on: ");
          Serial.print("TRIG = Pin "); Serial.print(trig);
          Serial.print(" | ECHO = Pin "); Serial.print(echo);
          Serial.print(" (Reading: "); Serial.print(distance, 1);
          Serial.println(" cm) <<<");

          detectedTrig = trig;
          detectedEcho = echo;
          found = true;
          break;
        }
      }

      // Reset pin states
      pinMode(trig, INPUT);
      pinMode(echo, INPUT);
    }
    if (found) break;
  }

  if (!found) {
    Serial.println("No ultrasonic echo detected on candidate pins.");
    Serial.println("Tip: Ensure the sensor's VCC has 5V, GND is grounded, and your hand is in front.");
  }
}

void testMotors() {
  Serial.println("\n-----------------------------------------------------------");
  Serial.println("  TESTING MOTOR DRIVER PINS ONE BY ONE...");
  Serial.println("  Watch your wheels and note which pin makes a wheel move: ");
  Serial.println("-----------------------------------------------------------");

  // Candidate PWM / directional pins
  int motorPins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11};
  int count = sizeof(motorPins) / sizeof(motorPins[0]);

  for (int i = 0; i < count; i++) {
    int p = motorPins[i];
    Serial.print("Testing Pin "); Serial.print(p);
    Serial.println(" HIGH for 0.5 seconds...");

    pinMode(p, OUTPUT);
    digitalWrite(p, HIGH);
    delay(500);
    digitalWrite(p, LOW);
    pinMode(p, INPUT);
    delay(300);
  }
  Serial.println("Motor pin test completed.");
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("===========================================================");
  Serial.println("     ROBOT HARDWARE AUTO-SCANNER & PIN DETECTOR TOOL       ");
  Serial.println("===========================================================");

  testUltrasonic();
  delay(1000);
  testMotors();

  Serial.println("\nScan complete. Send 'R' to re-scan, or 'U' to test ultrasonic only.");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'R' || c == 'r') {
      testUltrasonic();
      testMotors();
    } else if (c == 'U' || c == 'u') {
      testUltrasonic();
    }
  }
  delay(100);
}
