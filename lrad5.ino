// LRAD for Arduino MKR Zero
// Roni Bandini Jan 2023

// Install AudioZero library
// Audio output DAC and GND
// Pot to A1, VCC and GND
// WAV 44100 mono

#include <SPI.h>
#include <SD.h>
#include <AudioZero.h>

Sd2Card card;
SdVolume volume;
SdFile root;
int potValue=0;

const int chipSelect = SDCARD_SS_PIN;
int track;

void setup() {

  pinMode(LED_BUILTIN, OUTPUT);
    
  Serial.begin(9600);
  delay(1000);

  Serial.println("LRAD Started");
  Serial.println("Roni Bandini 1/2023");

 if (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present");
    // don't do anything more:
    while (1);
  }
  Serial.println("SD card initialized.");
  
  AudioZero.begin(44100);
}

void loop()
{

  potValue = analogRead(A1);    
  Serial.println("Analog read");      
  Serial.println(potValue);      
  
  potValue = map(potValue, 0, 1023, 0, 3);

  
   Serial.println("WAV Selection: ");
   Serial.println(potValue);
  
   File myFile = SD.open("lrad"+String(potValue)+".wav");    
   
   if (!myFile) {
    // if the file didn't open, print an error and stop
    Serial.println("Error opening WAV");
    while (true);
    }

  digitalWrite(LED_BUILTIN, HIGH);        
    
  Serial.println("Playing WAV");   
  AudioZero.play(myFile);

  Serial.println("WAV finished.");  
  
  digitalWrite(LED_BUILTIN, LOW);
    

  delay(500);
  
}
