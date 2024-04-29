#include <ESP32Servo.h>

Servo myservoX;  // Create a servo object for X-axis
Servo myservoY;  // Create a servo object for Y-axis

int posX = 90;   // Initial position for X-axis servo
int posY = 90;   // Initial position for Y-axis servo

void setup() {
  Serial.begin(9600);   // Initialize serial communication
  myservoX.attach(5);  // Attach X-axis servo to pin 12
  myservoY.attach(4);  // Attach Y-axis servo to pin 13
}

void loop() {
  if (Serial.available() > 0) {  // Check if data is available to read
    String data = Serial.readStringUntil('\n');  // Read the incoming data until newline character
    int commaIndex = data.indexOf(',');  // Find the index of comma
    if (commaIndex != -1) {  // If comma is found
      // Extract X and Y coordinates from the received data
      posX = data.substring(0, commaIndex).toInt();
      posY = data.substring(commaIndex + 1).toInt();
      // Map the received values (0-320 for X, 0-240 for Y) to servo angles (0-180)
      posX = map(posX, 0, 320, 0, 180);
      posY = map(posY, 0, 240, 0, 180);
      // Control the servos
      myservoX.write(posX);
      myservoY.write(posY);
    }
  }
}