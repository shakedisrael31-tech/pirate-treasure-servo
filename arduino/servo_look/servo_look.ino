// servo_look.ino - Arduino Leonardo + MG995
// Receives over Serial:
//   '1' = someone is looking   -> servo goes to LOOK_ANGLE
//   '0' = nobody is looking    -> servo goes to AWAY_ANGLE (60 degrees further)
// Power-friendly: moves slowly, and switches the servo off (detach) once it
// arrives, so it doesn't keep drawing current while standing still.

#include <Servo.h>

const int SERVO_PIN  = 9;     // servo signal pin on the shield
const int LOOK_ANGLE = 90;    // position while someone is looking
const int AWAY_ANGLE = 150;   // position while nobody is looking (LOOK_ANGLE + 60)
const int STEP_DELAY = 20;    // ms between each degree (higher = slower, less current)
const int HOLD_MS    = 300;   // keep powered this long after arriving, then release

Servo servo;
int current = AWAY_ANGLE;
int target  = AWAY_ANGLE;
unsigned long lastStep = 0;
unsigned long arrivedAt = 0;

void setup() {
  Serial.begin(9600);
  servo.write(current);       // set the position before attaching
  servo.attach(SERVO_PIN);
  arrivedAt = millis();
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '1') target = LOOK_ANGLE;
    else if (c == '0') target = AWAY_ANGLE;
  }

  if (current != target) {
    if (!servo.attached()) servo.attach(SERVO_PIN);
    if (millis() - lastStep >= STEP_DELAY) {
      lastStep = millis();
      current += (target > current) ? 1 : -1;
      servo.write(current);
      if (current == target) arrivedAt = millis();
    }
  } else if (servo.attached() && millis() - arrivedAt >= HOLD_MS) {
    servo.detach();           // stop driving the motor while idle
  }
}
