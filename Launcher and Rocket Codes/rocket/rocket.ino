// Name: Hillel Chaitoff
// Date: OCT 15 2014
// Note: Rocket Code

// Imports
#include <SPI.h>
#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <L3G.h>
#include <LSM303.h>
#include <LPS.h>

// IMU PIN Setup (UNO :: Micro)
// SDA -> A4 :: 3
// SCL -> A5 :: 2

#define GEIGER_COUNTER 5  // Geiger Counter Data PIN
#define L2R_RIP_CHORD 6   // Launcher Signal to Rocket - Rip Chord PIN
#define R2L_RIP_CHORD 7   // Rocket Signal to Launcher - Rip Chord PIN

// Using microseconds
#define LOG_PERIOD 5000000  // 15000ms => 15000000us
#define MAX_PERIOD 60000000

L3G gyro;
LSM303 accel;
LPS barom;

SoftwareSerial GPS_Soft_Serial(9, 8); // TX, RX
Adafruit_GPS GPS(&GPS_Soft_Serial);

// Variables
char gpsChar;

unsigned long geigerCount;  // GM Tube events
unsigned long geigerCpm;    // CPM
unsigned int geigerMulti;   // CPM Multiplier
unsigned long prevMicros;   // Process Time
boolean maySendData = false;   // Only True when GeigerCount is Available

//String gps_str = "";

//String ID = "000001";
boolean poweredOn = false;
String powerOn = "{\"node_id\":\"000001R\",\"powerOn\":\"True\"}"; // Launcher Powered On
String received = ""; // Message Received Over Serial (from RaspberryPi)
// boolean initialized = false;
// char initializeOn[] = "{\"" + ID + "_rocket" + "\":{\"initialized\":\"True\"}}"; // Launcher Initialized (Prepping for Launch)
// char initCommand[] = "{\"" + ID + "_rocket" + "\":{\"initCommand\":\"True\"}}"; // RaspberryPi Sent Initialization Command
boolean launched = false;
// String launchCommand = "{\"" + ID + "_rocket" + "\":{\"launchCommand\":\"True\"}}"; // RaspberryPi Sent Launch Command
String dataStr = "";	// Sensor Data

// Setup Loop
void setup(){
  Wire.begin();
  Serial.begin(9600); // Set Serial BaudeRate
  // GPS Module
  GPS.begin(9600);    // Set GPS Serial BaudeRate
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA); // Get recommended minimum and GGA data
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);    // GPS update rate
  // IMU Sensors
  accel.init();
  accel.enableDefault();
  barom.enableDefault();
  gyro.enableDefault();
  // Geiger Counter
  pinMode(GEIGER_COUNTER, INPUT);                     // set pin INT0 input for capturing GM Tube events
  digitalWrite(GEIGER_COUNTER, HIGH);                 // turn on internal pullup resistors, solder C-INT on the PCB
  attachInterrupt(0, geigerTubeTimeImpulse, FALLING); // define external interrupts
}

// Process Loop
void loop(){
  // If Power-On:
  if(!poweredOn){
  // Send "PoweredOn" over Serial
    Serial.println(powerOn);
    poweredOn = true;
  }
  // If Rocket is Launched
  if(launched){
  	// Get Sensor Data
  	dataStr = collectData();
  	// Start Sending
  	Serial.println("{\"node_id\":\"000001R\",\"data\":" + dataStr + "}");
  }else{
    if(digitalRead(L2R_RIP_CHORD) == LOW){
      launched = true;
    }
  }
  Serial.println(digitalRead(L2R_RIP_CHORD));
  // Reset Data Sending Permission 
  maySendData = false;
}

// Collect and Package Data from Sensors
String collectData(){
  // Serial.println("collectData"); // @TESTING
  // Get GPS Location
  String gpsData = getGPS();
  // Get Accelerometer Data
  String accelData = getAccel();
  // Get Gyroscope Data
  String gyroData = getGyro();
  // Get Barometer Data
  String baromData = getBarom();
  // Get Geiger Counter Data
  String geigData = "";
  // Get current time in microseconds
  unsigned long currMicros = micros();
  // Serial.println("currMicros: " + currMicros);
  // Serial.println("prevMicros: " + prevMicros);
  // Serial.println("LOG_PERIOD: " + LOG_PERIOD);
  if(currMicros - prevMicros > LOG_PERIOD){
    geigData = getGeig(currMicros);
    maySendData = true;
  }
	// Compile into JSON-Formatted String
	String collectedData = "";
  collectedData += "{\"gps\":";
  collectedData += gpsData;
  collectedData += ",\"accelerometer\":";
  collectedData += accelData;
  collectedData += ",\"gyroscope\":";
  collectedData += gyroData;
  collectedData += ",\"barometer\":";
  collectedData += baromData;
  collectedData += ",\"geigerCounter\":";
  collectedData += geigData;
  collectedData += "}";
  return collectedData;
}

String getGPS(){
  // Serial.println("getGPS"); // @TESTING
  while(!GPS.newNMEAreceived()){
    gpsChar = GPS.read();
    break;  // @TESTING
  }
  GPS.parse(GPS.lastNMEA());
  String nmeaStr = GPS.lastNMEA();
  return nmeaStr;
}

String getAccel(){
  // Serial.println("getAccel"); // @TESTING
  //float accelX = accel.a.x;
  //float accelY = accel.a.y;
  //float accelZ = accel.a.z;
  // Append the values in JSON format
  String gyroStr = "";
  gyroStr += "{\"x\":\"";
  gyroStr += accel.a.x;
  gyroStr += "\",\"y\":\"";
  gyroStr += accel.a.y;
  gyroStr += "\",\"z\":\"";
  gyroStr += accel.a.z;
  gyroStr += "\"}";
  return gyroStr;
}

String getGyro(){
  // Serial.println("getGyro"); // @TESTING
  //float gyroX = gyro.g.x;
  //float gyroY = gyro.g.y;
  //float gyroZ = gyro.g.z;
  // Append the values in JSON format
  String gyroStr = "";
  gyroStr += "{\"x\":\"";
  gyroStr += gyro.g.x;
  gyroStr += "\",\"y\":\"";
  gyroStr += gyro.g.y;
  gyroStr += "\",\"z\":\"";
  gyroStr += gyro.g.z;
  gyroStr += "\"}";
  return gyroStr;
}

String getBarom(){
  // Serial.println("getBarom"); // @TESTING
  //float baromPres = barom.readPressureMillibars();
  //float baromAlti = barom.pressureToAltitudeMeters(baromPres);
  //float baromTemp = barom.readTemperatureC();
  // Append the values in JSON format
  String baromStr = "";
  baromStr += "{\"x\":\"";
  baromStr += barom.readPressureMillibars();
  baromStr += "\",\"y\":\"";
  baromStr += barom.pressureToAltitudeMeters(barom.readPressureMillibars());
  baromStr += "\",\"z\":\"";
  baromStr += barom.readTemperatureC();
  baromStr += "\"}";
  return baromStr;
}

String getGeig(long currMicros){
  // Serial.println("getGeig"); // @TESTING
  prevMicros = currMicros;
  geigerCpm = geigerCount * geigerMulti;
  geigerCount = 0;
  String geigerStr = "";
  geigerStr += "{\"count\":";
  geigerStr += geigerCpm;
  geigerStr += "}";
  return geigerStr;
}

void geigerTubeTimeImpulse(){
  Serial.println("geigerTubeTimeImpulse");
  geigerCount += 1;
}
