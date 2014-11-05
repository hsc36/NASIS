// Name: Hillel Chaitoff
// Date: OCT 15 2014
// Note: Launcher Code

// Definitions
#define LAUNCH_RELAY 5  // Relay PIN

// Variables
char ID[] = "000001";
boolean poweredOn = false;
char powerOn[] = "{\"" + ID + "_launcher" + "\":{\"powerOn\":\"True\"}}"; // Launcher Powered On
char received[] = ""; // Message Received Over Serial (from RaspberryPi)
boolean initialized = false;
char initializeOn[] = "{\"" + ID + "_launcher" + "\":{\"initialized\":\"True\"}}"; // Launcher Initialized (Prepping for Launch)
char initCommand[] = "{\"" + ID + "_launcher" + "\":{\"initCommand\":\"True\"}}"; // RaspberryPi Sent Initialization Command
boolean confirmIR = false;
boolean confirmSound = false;
boolean confirmFlame = false;
boolean launchConfirmed = false;
boolean launched = false;
char launchConfirmOn[] = "{\"" + ID + "_launcher" + "\":{\"launched\":\"True\"}}"; // Rocket Launch Confirmed
char launchConfirmOff[] = "{\"" + ID + "_launcher" + "\":{\"launched\":\"False\"}}"; // Rocket Launch Not Confirmed
char launchCommand[] = "{\"" + ID + "_launcher" + "\":{\"launchCommand\":\"True\"}}"; // RaspberryPi Sent Launch Command

int IR_PIN = 3;  // IR Distance Sensor on A3
int SOUND_PIN = 4;  // Sound Sensor on A4
int FLAME_PIN = 5;  // Flame Sensor on A5

// Setup Loop
void setup(){
  Serial.begin(9600); //Set Serial BaudeRate
  // Rocket Launch Signal (Relay PIN)
  pinMode(LAUNCH_RELAY, OUTPUT);  // Mode
  digitalWrite(LAUNCH_RELAY, LOW)  // Initial Value
}

// Process Loop
void loop(){

  // If Power-On:
  if(!poweredOn){
    // Send "PoweredOn" over Serial
    Serial.write(powerOn);
    poweredOn = true;
  }
  if(!initialized){
    // Read from the Serial for a Command
    received = Serial.read()
    // If "InitializeCommand" is received:
    if(received == initCommand){
      // Go from STANDBY to FULL_POWER mode
      initialized = true;
      // Send Confirmations of Initialization over Serial
      Serial.write(initializeOn);
    }
  }
  if(!launched){
    // If "LaunchCommand" is received and "isInitialized":
    if((received == launchCommand) && initialized){
      // Launch Rocket
      digitalWrite(LAUNCH_RELAY, HIGH);
      // @NOTE: Options  1. WAIT, then get data from all 3 sensors before reporting successful launch
      //                *2. WHILE NO confirmation for each of 3 keep checking for confirmation
      // Confirm Launch by Reading the IR, Sound, and Flame Data
      int sensorCount = 0;
      while(!(confirmFlame && confirmSound && confirmIR) || (sensorCount > 299)){ // 30 Seconds
        // 1: Check for Flame
        if((!confirmFlame)){
          confirmFlame = checkFlame();
          delay(33.333333333);  // Delay One-Thirtieth of a Second
        }
        // 2: Check for Sound
        if((!confirmSound)){
          confirmSound = checkSound();
          delay(33.333333333);  // Delay One-Thirtieth of a Second
        }
        // 3: Check IR (if Rocket Present)
        if((!confirmIR)){
          confirmIR = checkIR();
          delay(33.333333333);  // Delay One-Thirtieth of a Second
        }
        // If Confirmed:
        if(confirmFlame && confirmSound && confirmIR){
          // Launch Confirmation
          launchConfirmed = true;
        }else{
          // No Launch Confirmation
          launchConfirmed = false;
        }
        sensorCount = sensorCount + 1;
      }
      // Launch Action Performed
      launched = true;
    }
    // If Launched:
    if(launched){
      // Switch off the Relay
      digitalWrite(LAUNCH_RELAY, LOW);
      // Send Data over Serial
      if(launchConfirmed){
        Serial.write(launchConfirmOn);
      }else{
        Serial.write(launchConfirmOff);
      }
    }
  }
}

// Check if Rocket Launch Made Expected Flame
boolean checkFlame(){
  if(analogRead(FLAME_PIN) < 201){  // Resolution = 0-1023
    return true;
  }else{
    return false;
  }
}
// Check if Rocket Launch Made Expected Sound
boolean checkSound(){
  if(analogRead(SOUND_PIN) > 509){  // Resolution = 0-1023
    return true;
  }else{
    return false;
  }
}
// Check if Rocket Left the Launcher
boolean checkIR(){
  if(((analogRead(IRpin) * 0.0048828125) > 5.0){ // Distance (cm) = IR_PIN * (5/1024)
    return true;
  }else{
    return false;
  }
}