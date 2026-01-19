//시리얼 모니터 데이터 JOSN으로 전송

const int LED_PIN = 13; 
const int SENSOR_PIN = A0;
bool ledState = false;
String inputString = "";
bool stringComplete = false;
unsigned long lastDataSend = 0;
const int DATA_INTERVAL = 500;

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.println("Arduino Web Monitor Ready");
}

void loop() {
  // 시리얼 데이터
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }

  // 명령 처리
  if (stringComplete) {
    inputString.trim();

    if (inputString == "ON") {
      ledState = true;
      digitalWrite(LED_PIN, HIGH);
      sendStatus();
    }
    else if (inputString == "OFF") {
      ledState = false;
      digitalWrite(LED_PIN, LOW);
      sendStatus();
    }
    else if (inputString == "STATUS") {
      sendStatus();
    }

    inputString = "";
    stringComplete = false;
  }

  // 주기적으로 데이터 전송 (JSON)
  if (millis() - lastDataSend >= DATA_INTERVAL) {
    lastDataSend = millis();
    sendData();
  }
}

void sendStatus() {
  if (ledState) {
    Serial.println("STATUS:ON");
  } else {
    Serial.println("STATUS:OFF");
  }
}

void sendData() {
  // JSON 형식으로 데이터 전송
  Serial.print("{");
  Serial.print("\"led\":");
  Serial.print(ledState ? 1 : 0);
  Serial.print(",\"sensor\":");
  Serial.print(analogRead(SENSOR_PIN));
  Serial.print(",\"time\":");
  Serial.print(millis());
  Serial.println("}");
}
