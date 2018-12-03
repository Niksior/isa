/*
This code is based on the examples at http://forum.arduino.cc/index.php?topic=396450
*/


// Example 5 - parsing text and numbers with start and end markers in the stream
#include "ISAMobile.h"
//#include <DueTimer.h>/
#include <math.h>
#include "helper.h"

const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

dataPacket packet;


boolean newData = false;

//=========nasze
void SetPowerLevel(PowerSideEnum side, int level)
{
  level = constrain(level, -255, 255);
  
  if (side == PowerSideEnum::Right) {
    if (level > 0) {
      // do przodu
      digitalWrite(A_PHASE, 1);
      analogWrite(A_ENABLE, level);
    } else if (level < 0) {
      // do tyłu
      digitalWrite(A_PHASE, 0);
      analogWrite(A_ENABLE, -level);
    } else {
      // stop
      digitalWrite(A_PHASE, 0);
      analogWrite(A_ENABLE, 0);
    }
  }
  
  if (side == PowerSideEnum::Left) {
    if (level > 0) {
      // do przodu
      digitalWrite(B_PHASE, 1);
      analogWrite(B_ENABLE, level);
    } else if (level < 0) {
      // do tyłu
      digitalWrite(B_PHASE, 0);
      analogWrite(B_ENABLE, -level);
    } else {
      // stop
      digitalWrite(B_PHASE, 0);
      analogWrite(B_ENABLE, 0);
    }
  } 
}


int measureSoundSpeed(int trigger_pin, int echo_pin)
{
  digitalWrite(trigger_pin, false);
  delayMicroseconds(2);

  digitalWrite(trigger_pin, true);
  delayMicroseconds(10);
  digitalWrite(trigger_pin, false);

  // zmierz czas przelotu fali dźwiękowej
  int duration = pulseIn(echo_pin, true, 50 * 1000);
  

  // przelicz czas na odległość (1/2 Vsound(t=20st.C))
  int distance = (int)((float)duration * 0.03438f * 0.5f);
  return distance;
}

int distanceFront() {
  UltraSoundSensor sensor = UltraSoundSensor::Front;
  char buffer[64];
  int d[5] = {};
  int sum = 0;
  int id = 0;
  int dist = measureSoundSpeed(
      ultrasound_trigger_pin[(int)sensor],
      ultrasound_echo_pin[(int)sensor]);

  // średnia krocząca
  sum -= d[id];
  sum += d[id] = dist;
  id = (id + 1) % 5;
  dist = sum / 5;
  return dist;
}

void stopuj(){
  while(distanceFront() < 7 && distanceFront() != 0){
    SetPowerLevel(PowerSideEnum::Left, 0);
    SetPowerLevel(PowerSideEnum::Right, 0);
  }
}


//============

void setup() {
  // Czujniki ultradźwiekowe
  for (int i = (int)UltraSoundSensor::__first; i <= (int)UltraSoundSensor::__last; i++)
  {
    pinMode(ultrasound_trigger_pin[i], OUTPUT);
    pinMode(ultrasound_echo_pin[i], INPUT);
    
    digitalWrite(ultrasound_trigger_pin[i], 0);
  }
  
  // Silniki
  pinMode(A_PHASE, OUTPUT);
  pinMode(A_ENABLE, OUTPUT);
  pinMode(B_PHASE, OUTPUT);
  pinMode(B_ENABLE, OUTPUT);
  pinMode(MODE, OUTPUT);

  digitalWrite(MODE, true);
  SetPowerLevel(PowerSideEnum::Left, 0);
  SetPowerLevel(PowerSideEnum::Right, 0);

//  Timer4.attachInterrupt(stopuj);
//  Timer4.setFrequency(4);
//  Timer4.start();
  
  Serial.begin(9600);
  //Serial.println("This demo expects 3 pieces of data - text, an integer and a floating point value");
  //Serial.println("Enter data in this style <HelloWorld, 12, 24.7>  ");
  //Serial.println();
}

///double N = -400;
double k = 0.4;
double d = 0.4;
double i = 0.05;
double torSum = 0;
double lastDeviation = 0;
double sumDeviation = 0;

void pid(dataPacket packet) {
  Serial.print("Integer ");
  Serial.println(packet.packet_int);
  double deviation = (double)packet.packet_int;
  double proportionalTor = k * deviation;
  double differentialTor = d * (deviation - lastDeviation);

  sumDeviation += deviation;
  double integralTor = i * sumDeviation;

  torSum = proportionalTor + differentialTor + integralTor;

  int power = (int)torSum;
  if(power > 100) power = 100;
  if(power < -100) power = -100;
  if(torSum > 100) torSum = 100;
  if(torSum < -100) torSum = -100;

  if(integralTor > 25) {
    integralTor = 25;
    sumDeviation = integralTor / i;
  }
  if(integralTor < -25) {
    integralTor = -25;
    sumDeviation = integralTor / i;
  }
  SetPowerLevel(PowerSideEnum::Right, power + 100);
  SetPowerLevel(PowerSideEnum::Left, -power + 100);
}

/*void pid(dataPacket packet) {
  int value = packet.packet_int;
  SetPowerLevel(PowerSideEnum::Right, 100);
  SetPowerLevel(PowerSideEnum::Left, 100);
}*/

//============

void loop() {
    recvWithStartEndMarkers();
    if (newData == true) {
        strcpy(tempChars, receivedChars);
            // this temporary copy is necessary to protect the original data
            //   because strtok() used in parseData() replaces the commas with \0
        packet = parseData();
        showParsedData(packet);
        pid(packet);
        newData = false;
    }
}

//============

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

//============

dataPacket parseData() {      // split the data into its parts

    dataPacket tmpPacket;

    char * strtokIndx; // this is used by strtok() as an index

    strtokIndx = strtok(tempChars,",");      // get the first part - the string
    strcpy(tmpPacket.message, strtokIndx); // copy it to messageFromPC
 
    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    tmpPacket.packet_int = atoi(strtokIndx);     // convert this part to an integer

    strtokIndx = strtok(NULL, ",");
    tmpPacket.packet_float = atof(strtokIndx);     // convert this part to a float

    return tmpPacket;
}


void showParsedData(dataPacket packet) {
    Serial.print("Message ");
    Serial.println(packet.message);
    Serial.print("Integer ");
    Serial.println(packet.packet_int);
    Serial.print("Float ");
    Serial.println(packet.packet_float);
}
