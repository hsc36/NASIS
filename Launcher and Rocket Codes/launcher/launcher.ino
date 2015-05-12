// Name: Hillel Chaitoff
// Date: OCT 15 2014
// Note: Launcher Code

// Definitions
#define ALARM_RELAY 4   // Launcher Warning Alarm Relay PIN
#define LAUNCH_RELAY 5  // Launcher Relay PIN
#define R2L_RIP_CHORD 6 // Rocket Signal to Launcher - Rip Chord PIN - H2
#define L2R_RIP_CHORD 7 // Launcher Signal to Rocket - Rip Chord PIN - H1

// Variables
int SOUND_PIN = A0; // Sound Sensor on A0 - F1
int IR_PIN = A1;    // IR Distance Sensor on A1 - G1
boolean poweredOn = false;
// node_id = "000001L";
String powerOn = "{\"node_id\":\"000001L\",\"powerOn\":\"True\"}"; // Launcher Powered On
String received = ""; // Message Received Over Serial (from RaspberryPi)
String checkCommand = "{\"node_id\":\"000001L\", \"command\":\"check\"}";
String checked = "{\"node_id\":\"000001L\", \"message\":\"checked\", \"package\":{";
boolean initialized = false;
String initializeOn = "{\"node_id\":\"000001L\", \"message\":\"initialized\"}"; // Launcher Initialized (Prepping for Launch)
String initCommand = "{\"node_id\":\"000001L\", \"command\":\"init\"}"; // RaspberryPi Sent Initialization Command
boolean confirmIR = false;
boolean confirmSound = false;
boolean launchConfirmed = false;
boolean launched = false;
String launchConfirm = "{\"node_id\":\"000001L\", \"message\":\"launched\", \"package\":{";
String launchCommand = "{\"node_id\":\"000001L\", \"command\":\"launch\"}"; // RaspberryPi Sent Launch Command

// Setup //
void setup(){
  Serial.begin(9600); //Set Serial BaudeRate
  // Rocket Launch Signal (Relay PIN)
  pinMode(LAUNCH_RELAY, OUTPUT);  // Mode
  digitalWrite(LAUNCH_RELAY, HIGH);  // Initial Value
  // Rocket Signal to Launcher - Rip Chord (Audio Plug)
  pinMode(R2L_RIP_CHORD, INPUT);
  // Launcher Signal to Rocket - Rip Chord (Independent Wire)
  pinMode(L2R_RIP_CHORD, OUTPUT);
  digitalWrite(L2R_RIP_CHORD, HIGH);
  // Alarm Warning
  pinMode(ALARM_RELAY, OUTPUT);
  digitalWrite(ALARM_RELAY, HIGH);
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
    else if(checkCommand.equals(received)){
      // Check the Sensors and Append the Data
      String temp = "";
      temp += "\"sound\":\"";
      temp += checkSound();
      temp += "\", \"distance\":\"";
      temp += checkIR();
      temp += "\", \"chord\":\"";
      temp += digitalRead(R2L_RIP_CHORD);
      temp += "\"}}";  // Close the JSON Package
      // Send the Data
      Serial.println(checked + temp);
      Serial.flush();
    }
  }
  if(initialized && !launched && (Serial.available() > 0)){
    // Read from the Serial for a Command
    received = Serial.readStringUntil('\n');
    // If "LaunchCommand" is received and "isInitialized":
    if(launchCommand.equals(received)){
      // Warning Alarm On
      digitalWrite(ALARM_RELAY, LOW);
      // Wait 3 Seconds
      delay(3000.0);
      digitalWrite(ALARM_RELAY, HIGH);
      // Set the L2R to LOW, to ensure data is sent right after the launch occurs
      digitalWrite(L2R_RIP_CHORD, LOW);
      delay(100);
      // Launch Rocket
      digitalWrite(LAUNCH_RELAY, LOW);
      // WAIT, then get data from both sensors before reporting successful launch
      // Confirm Launch by Reading the IR and Sound Sensors
      int sensorCount = 0;
      // 1: Check for Sound - In "Real-time"
      while(sensorCount < 1000){ // ~2 Seconds Max (1000 rounds * 2ms delay)
        if((!confirmSound)){
          confirmSound = checkSound();
        }
        delay(2.0);  // Delay Two Milliseconds
        sensorCount = sensorCount + 1;
      }
      // 2: Check IR (if Rocket Present) - After it is expected to be gone
      delay(500);  // Delay half-a-second
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
      // Check the Sensors and Append the Data
      String temp = "";
      temp += "\"sound\":\"";
      temp += confirmSound;
      temp += "\", \"distance\":\"";
      temp += confirmIR;
      temp += "\", \"chord\":\"";
      temp += digitalRead(R2L_RIP_CHORD);
      temp += "\"}}";  // Close the JSON Package
      // Send the Data
      Serial.println(launchConfirm + temp);
      Serial.flush();
    }
  }
}

// Other Functions //
// Check if Rocket Launch Made Expected Sound
boolean checkSound(){
  boolean read_out = (analogRead(SOUND_PIN) > 800);  // Resolution = 0-1023
  return read_out;
}

// Check if Rocket Left the Launcher
boolean checkIR(){  // Distance Calculation From: http://www.udoo.org/ProjectsAndTutorials/android-and-arduino-on-udoo-bidirectional-communication/
  float read_out = analogRead(IR_PIN);
  if(read_out < 100){  // Low bound
    read_out = 100;  
  }
  else if(read_out > 900){  // High Bound
    read_out = 900;
  }
  // Calculate Distance
  //float distance = (2076.0/(read_out - 11) + 4);
  //return read_out; // distance
  if (read_out < 200){
    return true;  // Rocket is Gone
  }else{
    return false; // Rocket is Present
  }
  // Serial.flush();
}
