"""Generate commonly used arduino scripts used for gathering data in lab"""

import os

SIMPLE_ANALOG_READER_SCRIPT = """void setup() {
  Serial.begin(9600); // Baud rate
  // pinMode(A1);
  pinMode(A0, INPUT);
}

void loop() {
  int sensorValue = analogRead(A0);
  delay(10);
  float voltage = sensorValue * (5.0 / 1023.0);
  // Use time module to print voltage as well as the time it was printed.
  Serial.println(voltage);
  delay(10);
}
"""

PCB_ANALOG_READER_SCRIPT = """
// Pin assignments
const int CPin1 = 2;  // Connect transistor 1 to digital pin 2
const int CPin2 = 3;  // Connect transistor 2 to digital pin 3
//const int CPin12 = 12;

// Variables
const unsigned long interval = 100;  // Time interval for the square wave (5ms = 0.005s, 100 Hz)
int currentState = LOW;        // Current state of the square wave
unsigned long previousMillis = 0;  // Time of the last state change


void setup() {
  Serial.begin(115200); // Initialize serial communication at 9600 baud rate
  pinMode(CPin1, OUTPUT);  // Set transistor pin 1 as output
  pinMode(CPin2, OUTPUT);  // Set transistor pin 2 as output
  //pinMode(CPin12, OUTPUT);
  
}

void loop() {
  //digitalWrite(CPin12, HIGH);
  unsigned long currentMillis = millis();  // Get the current time

  // Check if the time interval has passed
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    if (currentState == LOW) {
      currentState = HIGH;
    } else {
      currentState = LOW;
    } 
  }

  if (currentState ==HIGH) {
    digitalWrite(CPin1, HIGH);  //
    digitalWrite(CPin2, HIGH);
  }
  if (currentState == LOW) {
    digitalWrite(CPin1, LOW);  //
    digitalWrite(CPin2, LOW); // 
  }
  delay(25);

  int sensorValue = analogRead(A0); // read analog value from pin A0
  float voltage = sensorValue * (5.0 / 1023.0);
  Serial.print(voltage);
  Serial.print(",");

  delay(10);

  sensorValue = analogRead(A2);
  float v2 = sensorValue * (5/1023.0);
  Serial.print(v2);
  Serial.print(",");

  delay(10);

  sensorValue = analogRead(A5);
  float v3 = sensorValue * (5/1023.0);
  Serial.print(v3);

    if (currentState == HIGH){
    Serial.println(",B");
  }else {
    Serial.println(",T");
  }
  //Serial.print(",")

  delay(10); // wait for 10ms before taking another reading
  //digitalWrite(CPin12, LOW);
}
"""

VOLTAGE_DIVIDER_SCRIPT = """const int topPin = A2;  // Analog pin connected to the voltage divider output
const int middlePin = A5;
const int bottomPin = A0;
const float referenceVoltage = 5.0;  // Reference voltage of the Arduino (in volts)
const float dividerResistance = 330000.0;  // Resistance of the fixed resistor in the voltage divider (in ohms)

void setup() {
  Serial.begin(9600);  // Initialize serial communication
}

void loop() {
  // Read the voltage from the voltage divider
  int topValue = analogRead(topPin);
  delay(20);
  int middleValue = analogRead(middlePin);
  delay(20);
  int bottomValue = analogRead(bottomPin);
  delay(20);
  
  // Convert the ADC reading to voltage
  float topVoltage = topValue * (referenceVoltage / 1023.0);
  float middleVoltage = middleValue * (referenceVoltage / 1023.0);
  float bottomVoltage = bottomValue * (referenceVoltage / 1023.0);
  
  // Calculate the resistance of the variable resistor
  float topResistance = dividerResistance * ((referenceVoltage / topVoltage) - 1.0);
  float middleResistance = dividerResistance * ((referenceVoltage / middleVoltage) - 1.0);
  float bottomResistance = dividerResistance * ((referenceVoltage / bottomVoltage) - 1.0);

  
  // Print the resistance value
  //Serial.print("Resistance: ");
  Serial.print(topResistance);
  Serial.print(", ");
  Serial.print(middleResistance);
  Serial.print(", ");
  Serial.println(bottomResistance);

  //Serial.println(" ohms");
  
  delay(10);  // Wait for 1 second before reading again
}
"""


def make_simple(name: str = "serial-reader_a0"):
    """Create an Arduino IDE compatible directory and file with a script for reading a single analog voltage.

    Args:
        name (str, optional): The name to use for the directory and filename (without the extension). This should not be a path. Defaults to "serial-reader_a0".
    """
    os.makedirs(name)
    path = f"{name}/{name}.ino"
    with open(path, "w") as f:
        f.write(SIMPLE_ANALOG_READER_SCRIPT)


def make_pcb_reader(name: str = "pcb-reader"):
    """Create an Arduino IDE compatible directory and file with a script for reading voltage data from the PCB.

    Args:
        name (str, optional): The name to use for the directory and filename (without the extension). This should not be a path. Defaults to "pcb-reader".
    """
    os.makedirs(name)
    path = f"{name}/{name}.ino"
    with open(path, "w") as f:
        f.write(PCB_ANALOG_READER_SCRIPT)


def make_voltage_divider(name: str = "voltage-divider-reader"):
    """Create an Arduino IDE compatible directory and file with a script for analyzing a voltage divider setup. The script will require configuration based on your known resistance values.

    Args:
        name (str, optional): The name to use for the directory and filename (without the extension). This should not be a path. Defaults to "voltage-divider-reader".
    """
    os.makedirs(name)
    path = f"{name}/{name}.ino"
    with open(path, "w") as f:
        f.write(VOLTAGE_DIVIDER_SCRIPT)
