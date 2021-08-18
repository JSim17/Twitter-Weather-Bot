// Listens for data over serial connection 
// and plays a beep on the buzzer
// and flashes the LED

#ifndef SERIAL_RATE
#define SERIAL_RATE     9600
#endif

#ifndef SERIAL_TIMEOUT
#define SERIAL_TIMEOUT  5
#endif

// Set variables for the code
const int buzzer_pin = 13;
const int led_pin = 7;
int incomingByte;
int frequency = 200;
int duration = 100;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(SERIAL_RATE);
  Serial.setTimeout(SERIAL_TIMEOUT);
  pinMode(led_pin, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  while (Serial.available() > 0) {
    switch(Serial.parseInt()){
      case 1:
        while (Serial.parseInt() != 2) {
          digitalWrite(led_pin, HIGH);
          tone(buzzer_pin, frequency, duration);
          delay(2000);
        }
        digitalWrite(led_pin, LOW);
        noTone(buzzer_pin);
      case 99:
        // do nothing, to stop any previous operation
        break;  
    }
  }
}
