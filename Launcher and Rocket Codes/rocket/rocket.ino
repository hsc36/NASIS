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
// SDA -> A4 :: 2
// SCL -> A5 :: 3

#define GEIGER_COUNTER 2  // Geiger Counter Data PIN
#define L2R_RIP_CHORD 6   // Launcher Signal to Rocket - Rip Chord PIN (External Launcher-Box Wire: Blue)
#define R2L_RIP_CHORD 7   // Rocket Signal to Launcher - Rip Chord PIN (External Launcher-Box Wire: Green)

// Using microseconds
#define LOG_PERIOD 1000000  // 1s

L3G gyro;
LSM303 accel;
LPS barom;

SoftwareSerial GPS_Soft_Serial(9, 8); // TX, RX
Adafruit_GPS GPS(&GPS_Soft_Serial);

// Variables
char gpsChar;

unsigned long geigerCount;  // GM Tube events
unsigned long geigerCpm;    // CPM
unsigned long prevMicros;   // Process Time
boolean maySendData = false;   // Only True when GeigerCount is Available

// GPS Specific
#define GPSECHO  false
boolean usingInterrupt = false;
void useInterrupt(boolean); // Func prototype keeps Arduino 0023 happy

//String gps_str = "";

//String ID = "000001";
boolean poweredOn = false;
String received = ""; // Message Received Over Serial (from RaspberryPi)
boolean launched = false;
String dataStr = "";	// Sensor Data

// Geiger Counter Specific
void geigerTubeTimeImpulse(){
  delay(1);
  geigerCount += 1;;
}

// Setup Loop
void setup(){
  Serial.begin(9600); // Set Serial BaudeRate (Needs to be faster in order to compensate for GPS)
  // GPS Module
  GPS.begin(9600);    // Set GPS Serial BaudeRate
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);  // Get recommended minimum and GGA data
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);     // GPS update rate (1, 5, or 10 Hz)
  //GPS.sendCommand(PGCMD_ANTENNA);                // Antenna status updates
  // IMU Sensors
  Wire.begin();
  accel.init();
  gyro.init();
  accel.enableDefault();
  barom.enableDefault();
  gyro.enableDefault();
  // Geiger Counter
  pinMode(GEIGER_COUNTER, INPUT);                     // set pin INT0 input for capturing GM Tube events
  digitalWrite(GEIGER_COUNTER, HIGH);                 // turn on internal pullup resistors, solder C-INT on the PCB
  attachInterrupt(0, geigerTubeTimeImpulse, FALLING); // define external interrupts
  // Rip Chords
  pinMode(R2L_RIP_CHORD, OUTPUT);
  digitalWrite(R2L_RIP_CHORD, HIGH);
  pinMode(L2R_RIP_CHORD, INPUT);
  // @TODO: Remove
  //Serial.println(digitalRead(R2L_RIP_CHORD));
  //Serial.println(digitalRead(L2R_RIP_CHORD));
}

//***** Taken from Adafruit GPS Parsing Example *****//
// Interrupt is called once a microsecond, looks for any new GPS data, and stores it
SIGNAL(TIMER0_COMPA_vect) {
  char gpsChar = GPS.read();
  // if you want to debug, this is a good time to do it!
#ifdef UDR0
  if(GPSECHO)
    if(gpsChar) UDR0 = gpsChar;  
    // writing direct to UDR0 is much much faster than Serial.print 
    // but only one character can be written at a time. 
#endif
}
void useInterrupt(boolean v) {
  if(v) {
    // Timer0 is already used for micros() - we'll just interrupt somewhere
    // in the middle and call the "Compare A" function above
    OCR0A = 0xAF;
    TIMSK0 |= _BV(OCIE0A);
    usingInterrupt = true;
  } else {
    // do not call the interrupt function COMPA anymore
    TIMSK0 &= ~_BV(OCIE0A);
    usingInterrupt = false;
  }
}
//***************************************************//

uint32_t timer = micros();

// Process Loop
void loop(){
  // If Power-On:
  if(!poweredOn){
    //Send "PoweredOn" over Serial
    Serial.println("{\"node_id\":\"000001R\",\"power\":\"True\"}");
    Serial.flush();
    poweredOn = true;
  }
  // If Rocket is Launched
  if(launched){
    //Serial.println("Collecting Data!");
    if(!usingInterrupt) {
    char gpsChar = GPS.read();
    if(GPSECHO)
      if(gpsChar){
        Serial.print(gpsChar);
      }
    }
    if(GPS.newNMEAreceived()){
      if(!GPS.parse(GPS.lastNMEA())){
        return;
      }
    }
    if(timer > micros()){
      timer = micros();
    }
    if(micros() - timer > 1000000) {
      timer = micros(); // reset the timer
      //Serial.println(timer);
      // Get Sensor Data
      dataStr = "{\"node_id\":\"000001R\"";
      if(GPS.fix){
        dataStr+= ",";
        collectData(String(GPS.latitudeDegrees, 4), String(GPS.longitudeDegrees, 4));
      }else{
        collectData("NO GPS LAT","NO GPS LON");
      }
      dataStr += "}";
      Serial.println(dataStr);
    }
    // Start Sending
    //Serial.println("{\"node_id\":\"000001R\",\"data\":" + dataStr + "}");
  }else{
    if(digitalRead(L2R_RIP_CHORD) == LOW){
      launched = true;
      //Serial.println("LAUNCHED!");
    }
  }
  // Reset Data Sending Permission 
  maySendData = false;
}

// Collect and Package Data from Sensors
void collectData(String lat, String lon){
  //Serial.println("collectData");
  dataStr += "{\"gps\":";
  dataStr += "{\"lat\":" + lat +",\"lon\":" + lon +"}";
  dataStr += ",\"accelerometer\":";
  // Get Accelerometer Data
  dataStr += getAccel();
  dataStr += ",\"gyroscope\":";
  // Get Gyroscope Data
  dataStr += getGyro();
  dataStr += ",\"barometer\":";
  // Get Barometer Data
  dataStr += "{\"pressure\":";
  dataStr += barom.readPressureMillibars();
  dataStr += ",\"altitude\":";
  dataStr += barom.pressureToAltitudeMeters(barom.readPressureMillibars());
  dataStr += ",\"temp\":";
  dataStr += barom.readTemperatureC();
  dataStr += "}";
  // Get current time in microseconds
  dataStr += ",\"microseconds\":";
  unsigned long currMicros = micros();
  dataStr += currMicros; 
  dataStr += "}";
  // Get Geiger Counter Data
  dataStr += ",\"geigerCounter\":";
  dataStr += getGeig(currMicros);
  maySendData = true;
  dataStr += "}";
}

String getAccel(){  // Convert to binary, drop the lowest 4 bits, convert to float and multiply by 1000 to get number of "g"s 
  accel.read();
  //Serial.println("getAccel");
  // Append the values in JSON format
  String accelStr = "";
  accelStr += "{\"x\":";
  accelStr += accel.a.x;
  accelStr += ",\"y\":";
  accelStr += accel.a.y;
  accelStr += ",\"z\":";
  accelStr += accel.a.z;
  accelStr += "}";
  return accelStr;
}

String getGyro(){ // Multiply by 0.00875 to get dps (degrees-per-second)
  gyro.read();
  //Serial.println("getGyro");
  // Append the values in JSON format
  String gyroStr = "";
  gyroStr += "{\"x\":";
  gyroStr += gyro.g.x;
  gyroStr += ",\"y\":";
  gyroStr += gyro.g.y;
  gyroStr += ",\"z\":";
  gyroStr += gyro.g.z;
  gyroStr += "}";
  return gyroStr;
}

String getGeig(float currMicros){
  //Serial.println("getGeig");
  // Append the values in JSON format
  String geigerStr = "";
  prevMicros = currMicros;
  if(currMicros - prevMicros < LOG_PERIOD){
    geigerStr += "{\"count\":";
    geigerStr += geigerCount;
    geigerStr += "}";
  }
  geigerCount = 0;
  return geigerStr;
}
