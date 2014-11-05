// Name: Hillel Chaitoff
// Date: OCT 15 2014
// Note: Rocket Code

// Imports

// Variables
char ID[] = "000001";
boolean poweredOn = false;
char powerOn[] = "{\"" + ID + "_rocket" + "\":{\"powerOn\":\"True\"}}"; // Launcher Powered On
char received[] = ""; // Message Received Over Serial (from RaspberryPi)
boolean initialized = false;
char initializeOn[] = "{\"" + ID + "_rocket" + "\":{\"initialized\":\"True\"}}"; // Launcher Initialized (Prepping for Launch)
char initCommand[] = "{\"" + ID + "_rocket" + "\":{\"initCommand\":\"True\"}}"; // RaspberryPi Sent Initialization Command
boolean launched = false;
char launchCommand[] = "{\"" + ID + "_rocket" + "\":{\"launchCommand\":\"True\"}}"; // RaspberryPi Sent Launch Command
char dataStr[] = "";	// Sensor Data

// @TODO: Sensor PINs

// Setup Loop
void setup(){
  Serial.begin(9600); //Set Serial BaudeRate
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
  // If "LaunchCommand" is received and "isInitialized":
  if(!launched){
  	// Check if Launch Command Received
  	if(received == launchCommand){
  		launched = true;
  	}
  }
  if(launched){
  	// Get Sensor Data
  	dataStr = collectData();
  	// Start Sending
  	Serial.write("{\"" + ID + "_rocket" + "\":{\"data\":" + dataStr + "}}");
  }
}

// Collect and Package Data from Sensors
char collectData(){
	// Get Data from Sensors
	// @TODO: Need Sensor Setup To Obtain Data
	// Compile into JSON-Formatted String
	// @TODO: Data to Strings, then Format
}