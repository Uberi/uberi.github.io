// controller for [Peltier cooler project](http://anthony-zhang.me/blog/peltier-cooler/)
// written for the Adafruit Trinket 5V (8MHz)

// digital pin that determines whether the cooler is on - should not be PWM'd since that might interfere with the regulator functionality
#define COOLER_ENABLE_PIN 1
// analog pin to read the temperature from (in increments of 0.0195 V/K) - note that analog pin 1 is actually pin 2
#define TEMPERATURE_PIN 1

// temperature reading in hundreds of microVolts at 25 degrees Celsius, used for calculating absolute temperature (the temperature sensor isn't factory calibrated)
#define TEMPERATURE_REFERENCE_25 9500
// change in temperature reading in hundreds of microVolts given a 1 degree Celsius change in temperature
#define TEMPERATURE_SLOPE 195
// temperature in Celsius when reading 0 Volts
#define TEMPERATURE_MIN (25 - (TEMPERATURE_REFERENCE_25 / TEMPERATURE_SLOPE))
// temperature in Celsius when reading 5 Volts
#define TEMPERATURE_MAX (25 + ((50000 - TEMPERATURE_REFERENCE_25) / TEMPERATURE_SLOPE))

int target_temperature = 37; // target temperature in Celsius

void setup() {
  pinMode(COOLER_ENABLE_PIN, OUTPUT);
}
 
void loop() {
    int current_temperature = map(analogRead(TEMPERATURE_PIN), 0, 1023, TEMPERATURE_MIN, TEMPERATURE_MAX); // current temperature in Celsius
    digitalWrite(COOLER_ENABLE_PIN, current_temperature >= target_temperature ? HIGH : LOW); // turn on the cooler if and only if the temperature is too high
    delay(1000);
}

