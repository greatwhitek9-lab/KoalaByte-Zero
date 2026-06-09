#include <Arduino.h>
#include <TFT_eSPI.h>
#include <SPI.h>
#include <XPT2046_Touchscreen.h>

#ifndef TOUCH_CS
#define TOUCH_CS 33
#endif
#ifndef TOUCH_IRQ
#define TOUCH_IRQ 36
#endif

// Configuration constants
#define MAX_JETSON_LINE_LENGTH 48
#define SERIAL_BAUD_RATE 115200
#define PING_INTERVAL 5000
#define LOOP_DELAY 20
#define TOUCH_DEBOUNCE_MS 120
#define MENU_ITEM_HEIGHT 30
#define MENU_START_Y 46

// Color scheme
#define COLOR_HEADER_BG TFT_BLACK
#define COLOR_HEADER_TEXT TFT_GREEN
#define COLOR_STATUS_TEXT TFT_PURPLE
#define COLOR_MENU_HIGHLIGHT_BG TFT_DARKGREY
#define COLOR_MENU_HIGHLIGHT_TEXT TFT_CYAN
#define COLOR_MENU_NORMAL_TEXT TFT_WHITE
#define COLOR_WARNING_TEXT TFT_ORANGE
#define COLOR_INFO_TEXT TFT_LIGHTGREY

TFT_eSPI tft = TFT_eSPI();
XPT2046_Touchscreen ts(TOUCH_CS, TOUCH_IRQ);

struct MenuItem {
  const char* label;
  const char* command;
};

MenuItem menu[] = {
  {"Status", "CMD:STATUS"},
  {"Passive WiFi Scan", "CMD:PASSIVE_WIFI_SCAN"},
  {"GPS / Wardrive Status", "CMD:GPS_STATUS"},
  {"Pandagotchi", "CMD:PET_STATUS"},
  {"LED Eye Test", "CMD:LED_TEST"},
  {"Lock Lab Mode", "CMD:LOCK_LAB_MODE"}
};

const int MENU_COUNT = sizeof(menu) / sizeof(menu[0]);
int selected = 0;
String lastJetsonLine = "Waiting for Jetson...";
unsigned long lastHello = 0;
bool displayInitialized = false;

/**
 * Safely truncate string to maximum length
 * @param str Input string
 * @param maxLen Maximum output length
 * @return Safe truncated substring
 */
String safeTruncate(const String& str, int maxLen) {
  if (str.length() <= maxLen) {
    return str;
  }
  return str.substring(0, maxLen);
}

/**
 * Validate menu index for bounds safety
 * @param idx Index to validate
 * @return True if valid
 */
bool isValidMenuIndex(int idx) {
  return (idx >= 0 && idx < MENU_COUNT);
}

/**
 * Draw UI header with title and status
 */
void drawHeader() {
  tft.fillRect(0, 0, 320, 34, COLOR_HEADER_BG);
  tft.setTextColor(COLOR_HEADER_TEXT, COLOR_HEADER_BG);
  tft.setTextSize(2);
  tft.setCursor(8, 8);
  tft.print("KoalaByte CYD");
  tft.setTextColor(COLOR_STATUS_TEXT, COLOR_HEADER_BG);
  tft.setCursor(220, 8);
  tft.print("SAFE");
}

/**
 * Render main menu screen
 */
void drawMenu() {
  if (!displayInitialized) {
    return;
  }

  tft.fillScreen(TFT_BLACK);
  drawHeader();
  tft.setTextSize(2);

  // Draw menu items
  for (int i = 0; i < MENU_COUNT; i++) {
    int y = MENU_START_Y + i * MENU_ITEM_HEIGHT;
    
    if (i == selected) {
      tft.fillRect(4, y - 4, 312, 26, COLOR_MENU_HIGHLIGHT_BG);
      tft.setTextColor(COLOR_MENU_HIGHLIGHT_TEXT, COLOR_MENU_HIGHLIGHT_BG);
    } else {
      tft.setTextColor(COLOR_MENU_NORMAL_TEXT, TFT_BLACK);
    }
    
    tft.setCursor(12, y);
    tft.print(menu[i].label);
  }

  // Draw footer information
  tft.setTextSize(1);
  tft.setTextColor(COLOR_WARNING_TEXT, TFT_BLACK);
  tft.setCursor(8, 232);
  tft.print("Authorized lab use only. UI commands only.");
  
  tft.setTextColor(COLOR_INFO_TEXT, TFT_BLACK);
  tft.setCursor(8, 246);
  tft.print(safeTruncate(lastJetsonLine, MAX_JETSON_LINE_LENGTH).c_str());
}

/**
 * Send selected menu command to Jetson
 */
void sendSelected() {
  if (!isValidMenuIndex(selected)) {
    return;
  }

  Serial.println(menu[selected].command);
  lastJetsonLine = String("Sent: ") + menu[selected].command;
  drawMenu();
}

/**
 * Handle touchscreen input with debouncing
 */
void handleTouch() {
  if (!ts.touched()) {
    return;
  }

  TS_Point p = ts.getPoint();
  
  // CYD orientation approximation; calibrate per board as needed
  int y = map(p.x, 300, 3800, 0, 240);
  int x = map(p.y, 300, 3800, 0, 320);

  // Ignore touches in header area
  if (y < 40) {
    return;
  }

  // Calculate menu item index from touch position
  int idx = (y - (MENU_START_Y - 4)) / MENU_ITEM_HEIGHT;

  if (isValidMenuIndex(idx)) {
    selected = idx;
    drawMenu();
    delay(TOUCH_DEBOUNCE_MS);
    
    // Send command if still touched after debounce
    if (ts.touched()) {
      sendSelected();
    }
  }
}

/**
 * Process incoming serial commands from Jetson
 */
void handleSerial() {
  while (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    
    if (line.length() > 0 && line.length() <= 255) {
      lastJetsonLine = "Jetson: " + line;
      drawMenu();
    }
  }
}

/**
 * Initialize hardware and display
 */
void setup() {
  Serial.begin(SERIAL_BAUD_RATE);
  delay(200);

  // Initialize TFT display
  tft.init();
  tft.setRotation(1);

  // Enable backlight if available
  #ifdef TFT_BL
  pinMode(TFT_BL, OUTPUT);
  digitalWrite(TFT_BL, HIGH);
  #endif

  // Initialize touchscreen
  if (!ts.begin()) {
    Serial.println("ERROR: Touchscreen initialization failed!");
    displayInitialized = false;
    return;
  }
  
  ts.setRotation(1);
  displayInitialized = true;
  
  drawMenu();
  Serial.println("HELLO_KOALABYTE_CYD");
}

/**
 * Main loop: handle serial, touch, and periodic keepalive
 */
void loop() {
  handleSerial();
  handleTouch();

  // Send keepalive ping to Jetson at regular intervals
  unsigned long currentTime = millis();
  if (currentTime - lastHello > PING_INTERVAL) {
    Serial.println("PING:CYD_UI_READY");
    lastHello = currentTime;
  }

  delay(LOOP_DELAY);
}
