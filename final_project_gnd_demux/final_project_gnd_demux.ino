#include <WiFi.h> //Connect to WiFi
#include <math.h>
#include <string.h>

char host[] = "qrcode-backend-application.herokuapp.com";

//Some constants and some resources:
const int RESPONSE_TIMEOUT = 6000; //ms to wait for response from host
const uint16_t OUT_BUFFER_SIZE = 5000; //size of buffer to hold HTTP response
char network[] = "MIT";  //SSID for 6.08 Lab
char password[] = ""; //Password for 6.08 Lab

// QR CODE MAXTRIX TO GO HERE

char QR_MATRIX[23][23];

boolean gotQR = false;

//--- Multiplexer input pins (for ESP32) ---
//-------------ROWS-------------------
int top_row_select_0 =    13;
int top_row_select_1 =    14;
int top_row_select_2 =    27;
int top_row_select_3 =    26;
//------------------------------------
int bottom_row_select_0 = 21;
int bottom_row_select_1 = 25;
int bottom_row_select_2 = 22;
int bottom_row_select_3 = 23;
//------------COLUMNS-----------------
int top_col_select_0 =    19;
int top_col_select_1 =    18;
int top_col_select_2 =    5;
int top_col_select_3 =    17;
//------------------------------------
int bottom_col_select_0 = 15;
int bottom_col_select_1 = 2;
int bottom_col_select_2 = 4;
int bottom_col_select_3 = 16;
//------------------------------------

void do_http_request(char* host, char* request, char* response, uint16_t response_size, uint16_t response_timeout, uint8_t serial) {
  WiFiClient client; //instantiate a client object
  if (client.connect(host, 80)) { //try to connect to host on port 80
    if (serial) Serial.print(request);//Can do one-line if statements in C without curly braces
    client.print(request);
    memset(response, 0, response_size); //Null out (0 is the value of the null terminator '\0') entire buffer
    uint32_t count = millis();
    while (client.connected()) { //while we remain connected read out data coming back
      client.readBytesUntil('\n', response, response_size);
      if (serial) Serial.println(response);
      if (strcmp(response, "\r") == 0) { //found a blank line!
        break;
      }
      memset(response, 0, response_size);
      if (millis() - count > response_timeout) break;
      
    }
    memset(response, 0, response_size);
    count = millis();
    while (client.available()) { //read out remaining text (body of response)
      char_append(response, client.read(), OUT_BUFFER_SIZE);
    }
    if (serial) Serial.println(response);
    client.stop();
    if (serial) Serial.println("-----------");
  } else {
    if (serial) Serial.println("connection failed 😕");
    if (serial) Serial.println("wait 0.5 sec...");
    client.stop();
  }
}

/*----------------------------------
  char_append Function:
  Arguments:
     char* buff: pointer to character array which we will append a
     char c:
     uint16_t buff_size: size of buffer buff
  Return value:
     boolean: True if character appended, False if not appended (indicating buffer full)
*/
uint8_t char_append(char* buff, char c, uint16_t buff_size) {
  int len = strlen(buff);
  if (len > buff_size) return false;
  buff[len] = c;
  buff[len + 1] = '\0';
  return true;
}


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(top_row_select_0, OUTPUT);
  pinMode(top_row_select_1, OUTPUT);
  pinMode(top_row_select_2, OUTPUT);
  pinMode(top_row_select_3, OUTPUT);

  pinMode(bottom_row_select_0, OUTPUT);
  pinMode(bottom_row_select_1, OUTPUT);
  pinMode(bottom_row_select_2, OUTPUT);
  pinMode(bottom_row_select_3, OUTPUT);
  
  pinMode(top_col_select_0, OUTPUT);
  pinMode(top_col_select_1, OUTPUT);
  pinMode(top_col_select_2, OUTPUT);
  pinMode(top_col_select_3, OUTPUT);

  pinMode(bottom_col_select_0, OUTPUT);
  pinMode(bottom_col_select_1, OUTPUT);
  pinMode(bottom_col_select_2, OUTPUT);
  pinMode(bottom_col_select_3, OUTPUT);

  for (int i = 0; i < 23; i++){
    for (int j = 0; j < 23; j++){
      if (i%2==0){
        QR_MATRIX[i][j] = 'W';
      } else {
        QR_MATRIX[i][j] = 'B';
      }
    }
  }

  WiFi.begin(network, password); //attempt to connect to wifi
  uint8_t count = 0; //count used for Wifi check times
  Serial.print("Attempting to connect to ");
  Serial.println(network);
  while (WiFi.status() != WL_CONNECTED && count < 12) {
    delay(500);
    Serial.print(".");
    count++;
  }
  delay(2000);
  if (WiFi.isConnected()) { //if we connected then print our IP, Mac, and SSID we're on
    Serial.println("CONNECTED!");
    Serial.printf("%d:%d:%d:%d (%s) (%s)\n", WiFi.localIP()[3], WiFi.localIP()[2],
                  WiFi.localIP()[1], WiFi.localIP()[0],
                  WiFi.macAddress().c_str() , WiFi.SSID().c_str());    delay(500);
  } else { //if we failed to connect just Try again.
    Serial.println("Failed to Connect 😕  Going to restart");
    Serial.println(WiFi.status());
    ESP.restart(); // restart the ESP (proper way)
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  //----- Read through the receiver pins periodically -----
  if (!gotQR){
    char request[500];
    char body[200];
    char response[5000];
    String body_data = "55.5";
    sprintf(body, "size=23x23&data=%s&charset-target=UTF-8&format=png", body_data);
    Serial.println("finishes thing");
    sprintf(request, "GET /?%s HTTP/1.1\r\n", body);
    sprintf(request + strlen(request), "Host: %s\r\n\r\n",host);
    Serial.println(request);
    Serial.println("Finishes copying");
    do_http_request(host, request, response, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);
    char output[100];
  
    char* token = strtok(response, "\n");
    int row = 0;
    while (token != NULL){
      for (int col = 0; col < 23; col+= 1){
        QR_MATRIX[row][col] = token[col];
      }
      row += 1;
      token = strtok(NULL, "\n");
    }
    gotQR = true;
  }
  
  for (int i = 0; i <23; i++){
    for (int j = 0; j <23; j++){
      if (QR_MATRIX[i][j] == 'W'){
        selectChannelOutRow(i);
        selectChannelOutCol(j);
        delay(2);
      }
    }
  }
  
}

//----- TODO: Set Select ROW Pin Values -----
void selectChannelOutRow(int channel) {
    int select_3_write = (((channel%12) & 8) == 8) ? HIGH : LOW;
    int select_2_write = (((channel%12) & 4) == 4) ? HIGH : LOW;
    int select_1_write = (((channel%12) & 2) == 2) ? HIGH : LOW;
    int select_0_write = (((channel%12) & 1) == 1) ? HIGH : LOW;

    if (channel < 12){
      digitalWrite(bottom_row_select_0, HIGH);
      digitalWrite(bottom_row_select_1, HIGH);
      digitalWrite(bottom_row_select_2, HIGH);
      digitalWrite(bottom_row_select_3, HIGH);  
      digitalWrite(top_row_select_0, select_0_write);
      digitalWrite(top_row_select_1, select_1_write);
      digitalWrite(top_row_select_2, select_2_write);
      digitalWrite(top_row_select_3, select_3_write);  
    } else {
      digitalWrite(top_row_select_0, HIGH);
      digitalWrite(top_row_select_1, HIGH);
      digitalWrite(top_row_select_2, HIGH);
      digitalWrite(top_row_select_3, HIGH);  
      digitalWrite(bottom_row_select_0, select_0_write);
      digitalWrite(bottom_row_select_1, select_1_write);
      digitalWrite(bottom_row_select_2, select_2_write);
      digitalWrite(bottom_row_select_3, select_3_write);      
    }
}

//----- TODO: Set Select COL Pin Values -----
void selectChannelOutCol(int channel) {
    int select_3_write = (((channel%12) & 8) == 8) ? HIGH : LOW;
    int select_2_write = (((channel%12) & 4) == 4) ? HIGH : LOW;
    int select_1_write = (((channel%12) & 2) == 2) ? HIGH : LOW;
    int select_0_write = (((channel%12) & 1) == 1) ? HIGH : LOW;

    if (channel < 12){
      digitalWrite(bottom_col_select_0, HIGH);
      digitalWrite(bottom_col_select_1, HIGH);
      digitalWrite(bottom_col_select_2, HIGH);
      digitalWrite(bottom_col_select_3, HIGH);
      digitalWrite(top_col_select_0, select_0_write);
      digitalWrite(top_col_select_1, select_1_write);
      digitalWrite(top_col_select_2, select_2_write);
      digitalWrite(top_col_select_3, select_3_write); 
    } else {
      digitalWrite(top_col_select_0, HIGH);
      digitalWrite(top_col_select_1, HIGH);
      digitalWrite(top_col_select_2, HIGH);
      digitalWrite(top_col_select_3, HIGH);  
      digitalWrite(bottom_col_select_0, select_0_write);
      digitalWrite(bottom_col_select_1, select_1_write);
      digitalWrite(bottom_col_select_2, select_2_write);
      digitalWrite(bottom_col_select_3, select_3_write);      
    } 
}
