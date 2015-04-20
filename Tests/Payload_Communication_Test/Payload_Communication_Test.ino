float count = 0;
void setup() {
  Serial.begin(9600);
}

void loop() {
  Serial.println(count);
  count += 0.5;
  delay(500);
}
