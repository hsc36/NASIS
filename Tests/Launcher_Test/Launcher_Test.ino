int led13 = 13;
int led12 = 12;
//int relay5 = 5;
int blinkRate = 1000;
boolean relayLaunch = false;
#define RELAY 5

void setup() {
  Serial.begin(9600);
  pinMode(RELAY, OUTPUT);
}

void loop() {
  char ctrl = 'N';
  if (Serial.available()) {
    ctrl = ((char) Serial.read());
    delay(10);
    if(ctrl == 'N'){
      relayLaunch = true;
    }else if(ctrl == 'M'){
      relayLaunch = false;
    }
  }
  if(relayLaunch){
    digitalWrite(led13, LOW);    // turn the LED off
    digitalWrite(led12, HIGH);
    digitalWrite(RELAY, LOW);
    delay(blinkRate);               // wait
  }else{
    digitalWrite(led13, HIGH);   // turn the LED on
    digitalWrite(led12, LOW);
    digitalWrite(RELAY, HIGH);
    delay(blinkRate);               // wait
  }
}
