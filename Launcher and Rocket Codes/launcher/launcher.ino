// Name: Hillel Chaitoff
// Date: OCT 15 2014
// Note: Launcher Code

// Definitions
#define LAUNCH_RELAY 5  // Relay PIN

// Variables
String ID = "000001";
boolean poweredOn = false;
String powerOn = "{\"000001_launcher\":{\"powerOn\":\"True\"}}"; // Launcher Powered On
String received = ""; // Message Received Over Serial (from RaspberryPi)
boolean initialized = false;
String initializeOn = "\n{\"000001_launcher\":{\"initialized\":\"True\"}}"; // Launcher Initialized (Prepping for Launch)
String initCommand = "{\"000001_launcher\":{\"initCommand\":\"True\"}}"; // RaspberryPi Sent Initialization Command
boolean confirmIR = false;
boolean confirmSound = false;
boolean confirmFlame = false;
boolean launchConfirmed = false;
boolean launched = false;
String launchConfirmOn = "\n{\"000001_launcher\":{\"launched\":\"True\"}}"; // Rocket Launch Confirmed
String launchConfirmOff = "\n{\"000001_launcher\":{\"launched\":\"False\"}}"; // Rocket Launch Not Confirmed
String launchCommand = "{\"000001_launcher\":{\"launchCommand\":\"True\"}}"; // RaspberryPi Sent Launch Command

int IR_PIN = 3;  // IR Distance Sensor on A3
int SOUND_PIN = 4;  // Sound Sensor on A4

// Setup //
void setup(){
  Serial.begin(9600); //Set Serial BaudeRate
  // Rocket Launch Signal (Relay PIN)
  pinMode(LAUNCH_RELAY, OUTPUT);  // Mode
  digitalWrite(LAUNCH_RELAY, HIGH);  // Initial Value
}

// Process //
void loop(){

  // If Power-On:
  if(!poweredOn){
    // Send "PoweredOn" over Serial
    Serial.println(powerOn);
    Serial.flush();
    poweredOn = true;
  }
  if(!initialized && (Serial.available() > 0)){
    // Read from the Serial for a Command
    received = Serial.readStringUntil('\n');
    // If "InitializeCommand" is received:
    if(initCommand.equals(received)){
      // Go from STANDBY to FULL_POWER mode
      initialized = true;
      // Send Confirmations of Initialization over Serial
      Serial.println(initializeOn);
      Serial.flush();
    }
  }
  if(initialized && !launched && (Serial.available() > 0)){
    // Read from the Serial for a Command
    received = Serial.readStringUntil('\n');
    // If "LaunchCommand" is received and "isInitialized":
    if(launchCommand.equals(received)){
      // Launch Rocket
      digitalWrite(LAUNCH_RELAY, LOW);
      // @NOTE: Options  1. WAIT, then get data from all 3 sensors before reporting successful launch
      //                *2. WHILE NO confirmation for each of 3 keep checking for confirmation
      // Confirm Launch by Reading the IR, Sound, and Flame Data
      int sensorCount = 0;
      // 1: Check for Sound - In "Real-time"
      while(sensorCount < 1000){ // 3 Seconds
        if((!confirmSound)){
          confirmSound = checkSound();
        }
        delay(3.0);  // Delay Three Milliseconds
        sensorCount = sensorCount + 1;
      }
      // 2: Check IR (if Rocket Present) - After it is expected to be gone
      confirmIR = checkIR();
      // If Launch is confirmed by Sound and Distance sensors:
      if(confirmSound && confirmIR){
        // Launch Confirmed
        launchConfirmed = true;
      }else{
        // Launch NOT Confirmation
        launchConfirmed = false;
      }
      // Launch Action Performed - Regardless, the launch action was performed
      launched = true;
    }
    // If Launched was performed:
    if(launched){
      // Switch off the Relay
      digitalWrite(LAUNCH_RELAY, HIGH);
      // Send Data over Serial
      if(launchConfirmed){
        Serial.println(launchConfirmOn);
      }else{
        Serial.println(launchConfirmOff);
      }
      Serial.flush();
    }
  }
}

// Other Functions //
// Check if Rocket Launch Made Expected Sound
boolean checkSound(){
  if(analogRead(SOUND_PIN) > 1000){  // Resolution = 0-1023
    //Serial.println("Sound = True");
    return true;
  }else{
    //Serial.println("Sound = False");
    return false;
  }
}

// Check if Rocket Left the Launcher
boolean checkIR(){
  float voltage = (analogRead(IR_PIN) * 0.0048828125); //Resolution: IR_PIN * (5/1024)
  float distance = 65 * pow(voltage, -1.1); // Volts to Distance (See: http://luckylarry.co.uk/arduino-projects/arduino-using-a-sharp-ir-sensor-for-distance-calculation/)
  //Serial.println(voltage, DEC);
  //Serial.println(distance, DEC);
  Serial.flush();
  if(distance > 5.0){ // Distance (cm)
    Serial.print("\nIR = True\n");
    return true;
  }else{
    Serial.print("\nIR = False\n");
    return false;
  }
  Serial.flush();
}
