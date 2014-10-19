//  Name: Hillel Chaitoff
//  Date: OCT 15 2014
//  Note: Launcher Code

// Imports
#include <dht11.h>

// Definitions
dht11 DHT;
#define DHT11_PIN 6  // Humidity & Temperature PIN
#define LAUNCH_RELAY 5  // Relay PIN

// Variables
char ID[] = "000001";
boolean powerOn = false;
char poweredOn[] = "{\"" + ID + "\":{\"poweredOn\":\"True\"}}";
char received[] = "";
boolean initialized = false;
char initCommand[] = "";
boolean launched = false;
char launchCommand[] = "";


int IR_PIN = 3;  // IR Distance Sensor on A3
int SOUND_PIN = 4;  // Sound Sensor on A4
int FLAME_PIN = 5;  // Flame Sensor on A5
int sensorValue = 0;

// Setup Loop
void setup(){
  Serial.begin(9600); //Set Serial BaudeRate
  // Rocket Launch Signal (Relay PIN)
  pinMode(LAUNCH_RELAY, OUTPUT);  // Mode
  digitalWrite(LAUNCH_RELAY, LOW)  // Initial Value
  
}

// Process Loop
void loop(){
  // If First Power-On:
  if(powerOn == false){
    //  Send "PoweredOn" over Serial
    Serial.write(poweredOn);
    powerOn = true;
  }
  
  // Read from the Serial for a Command
  received = Serial.read()
  // If "InitializeCommand" is received:
  if(received == initCommand){
    //  Go from STANDBY to FULL_POWER mode
    initialized = true;
    //  Send Confirmations of Initialization over Serial
  }
  
  // If "LaunchCommand" is received and "isInitialized":
  if((received == launchCommand) && initialized){
    //  Launch Rocket
    digitalWrite(LAUNCH_RELAY, HIGH);
    //  Confirm Launch by Reading the IR Data
    // If Confirmed:
    if(launchConfirmed){
      launched = true;
    }else{
      //  Report Launch Failure
    }
  }
  
  // If Launched:
  if(launched){
    //  Send Data over Serial
    digitalWrite(LAUNCH_RELAY, LOW);
  }
  
}

