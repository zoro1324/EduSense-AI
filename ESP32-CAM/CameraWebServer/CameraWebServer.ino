#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

void startCameraServer();

const char* ssid = "zoro";
const char* password = "1234567890";

const char* serverURL = "http://10.21.247.170:8000/api/attendance/camera-mark/?period=1";
const char* deviceToken = "YOUR_DEVICE_TOKEN";

#define TRIG_PIN 14
#define ECHO_PIN 15

const long DETECTION_DISTANCE_CM = 25;
const int REQUIRED_CONSECUTIVE_DETECTIONS = 2;
const unsigned long CAPTURE_COOLDOWN_MS = 5000;

unsigned long lastCaptureAtMs = 0;
int consecutiveDetections = 0;

// AI Thinker Camera Pins
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

long getDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  long distance = duration * 0.034 / 2;
  return distance;
}

void sendImage(camera_fb_t * fb) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Skipping upload.");
    return;
  }

  HTTPClient http;
  http.begin(serverURL);
  http.setTimeout(15000);
  http.addHeader("Content-Type", "image/jpeg");
  if (strlen(deviceToken) > 0) {
    http.addHeader("X-Device-Token", deviceToken);
  }

  int httpResponseCode = http.POST(fb->buf, fb->len);
  String responseBody = http.getString();

  Serial.print("HTTP status: ");
  Serial.println(httpResponseCode);
  if (responseBody.length() > 0) {
    Serial.println("Server response:");
    Serial.println(responseBody);
  }
  http.end();
}

camera_fb_t* captureStableFrame() {
  camera_fb_t *warmup = esp_camera_fb_get();
  if (warmup) {
    esp_camera_fb_return(warmup);
  }
  delay(120);
  return esp_camera_fb_get();
}

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Camera Init Failed!");
    return;
  }

  sensor_t *sensor = esp_camera_sensor_get();
  if (sensor) {
    sensor->set_brightness(sensor, 1);
    sensor->set_contrast(sensor, 1);
    sensor->set_saturation(sensor, 0);
  }

  startCameraServer();
  Serial.println("Camera stream server started");
  Serial.print("Open stream: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/stream");
  Serial.print("Open controls: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/");
}

void loop() {
  long dist = getDistance();
//  Serial.print("Distance: ");
//  Serial.println(dist);

  bool detected = dist > 0 && dist <= DETECTION_DISTANCE_CM;
  if (detected) {
    consecutiveDetections++;
  } else {
    consecutiveDetections = 0;
  }

  unsigned long now = millis();
  bool cooldownComplete = (now - lastCaptureAtMs) >= CAPTURE_COOLDOWN_MS;

  if (detected && cooldownComplete && consecutiveDetections >= REQUIRED_CONSECUTIVE_DETECTIONS) {
    Serial.println("Presence detected. Capturing image...");

    camera_fb_t *fb = captureStableFrame();
    if (!fb) {
      Serial.println("Camera capture failed");
      return;
    }

    sendImage(fb);
    esp_camera_fb_return(fb);

    lastCaptureAtMs = now;
    consecutiveDetections = 0;
    delay(200);
  }

  delay(150);
}
