# You will never find out what the treasure is

A pirate-themed camera installation: a servo motor sits at 150° while nobody is looking, and swings 60° to 90° when someone looks straight at the camera.

Gaze detection runs in the browser with [MediaPipe Face Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker) (head direction + iris position), and commands are sent to the Arduino over USB using the Web Serial API.

## Hardware

- Arduino Leonardo (ATmega32U4)
- DFRduino Nano Expansion v1.1 shield
- MG995 servo (180°)
- External 5–6 V / 2 A+ supply for the servo (recommended)

### Wiring

| Servo wire | Connect to |
|---|---|
| Orange (signal) | D9 |
| Red (+) | External supply + |
| Brown (−) | External supply − **and** Arduino GND |

The MG995 can draw 1–2.5 A when it starts moving. Powered from USB alone, the board browns out and resets, so the servo works a couple of times and then stops. A 470–1000 µF capacitor across the servo supply also helps.

## Files

```
index.html                         Chrome page: camera + gaze detection + Web Serial
arduino/servo_look/servo_look.ino  Arduino sketch
python/look_detector.py            Alternative: same detection as a Python script
```

## How to run

1. Open `arduino/servo_look/servo_look.ino` in Arduino IDE, select **Arduino Leonardo** and the port under Tools → Port, and upload.
2. Close the Serial Monitor in Arduino IDE.
3. Open `index.html` in **Chrome** or **Edge** on a computer (needs an internet connection to load MediaPipe).
4. Click the **camera coin**, then the **plug coin** and pick the Arduino.
5. Look at the camera.

Other coins: two test coins to move/return the servo manually, and a compass coin that opens the sensitivity settings.

### Python alternative

```
pip install mediapipe==0.10.14 opencv-python pyserial
python python/look_detector.py --port COM5
```

## Serial protocol

9600 baud. `'1'` = someone is looking → 90°, `'0'` = nobody is looking → 150°. The sketch moves one degree every 20 ms and releases the servo when idle, to keep current spikes low enough for USB power. With an external supply you can lower STEP_DELAY for faster motion.
