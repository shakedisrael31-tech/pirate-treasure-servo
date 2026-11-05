// servo_look.ino - Arduino Leonardo + MG995
// Receives over Serial:
//   '1' = someone is looking   -> servo moves 25 degrees
//   '0' = nobody is looking    -> servo returns to rest
// The servo moves gradually (one degree at a time) to reduce current spikes.

#include <Servo.h>

const int SERVO_PIN  = 9;    // servo signal pin on the shield
const int REST_ANGLE = 90;   // rest angle
const int MOVE_ANGLE = 25;   // how many degrees to move when looked at
const int STEP_DELAY = 4;    // ms between each degree (higher = slower, gentler on power)

Servo servo;
int current = REST_ANGLE;
int target  = REST_ANGLE;
unsigned long lastStep = 0;

void setup() {
  Serial.begin(9600);
  servo.attach(SERVO_PIN);
  servo.write(current);
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '1') target = REST_ANGLE + MOVE_ANGLE;
    else if (c == '0') target = REST_ANGLE;
  }

  if (current != target && millis() - lastStep >= STEP_DELAY) {
    lastStep = millis();
    current += (target > current) ? 1 : -1;
    servo.write(current);
  }
}
