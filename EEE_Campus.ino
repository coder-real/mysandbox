/* EEE Campus Integrated - HRP-1696 64x20 / ESP32
 * Native right-to-left scrolling, speed 80; no per-frame pixel updates.
 * DS3231 stores NIGERIA LOCAL TIME (UTC+1). Internet NTP uses UTC.
 * See README.md for wiring, library versions, setup and operational limits.
 */
#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEClient.h>
#include <RTClib.h>
// Matrix scanned below with stable single-key and release filtering.
#ifdef CLOSED
#undef CLOSED
#endif
#include <WiFi.h>
#include <esp_system.h>
#include <ESPmDNS.h>
#include <WebServer.h>
#include <esp_heap_caps.h>
#include <LittleFS.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <Wire.h>
#include <time.h>
#include <freertos/FreeRTOS.h>
#include <freertos/semphr.h>
#include <freertos/queue.h>
#include "eee_assets.h"
#if !defined(EEE_CAMPUS_ASSET_VERSION) || EEE_CAMPUS_ASSET_VERSION != 4
#error "Wrong EEE dashboard assets. Extract the complete corrected project into a NEW folder."
#endif

// ---------- User configuration ----------
#define DISPLAY_MAC_ADDRESS "7F:59:3A:63:C7:48"
#define UUID_WRITE "0000fa02-0000-1000-8000-00805f9b34fb"
const uint8_t NATIVE_SPEED=80; // Your preferred setting C.
const uint8_t BRIGHTNESS=80;
const int PIN_PIR=27, PIN_BUZZER=15;
const int I2C_SDA=21, I2C_SCL=22;
const int32_t UTC_OFFSET_SECONDS=3600; // Africa/Lagos, no DST.
const unsigned long PIR_TIMEOUT_MS=45000;
// No scroll-complete notification has been decoded. The v3 seed below
// uses the user's measured greeting pass; other lengths use width scaling.
// Web calibration remains available for subsequent timing adjustments.
// User measured one complete GOOD MORNING pass as 4 seconds.
// 12 chars * 14 px = 168 px + 64 px screen travel => 232 / 4 = 58 px/s.
const float DEFAULT_SCROLL_PIXELS_PER_SECOND=58.0f;
const char* CALIBRATION_KEY="scrollpps_v3"; // Never reuse old 8px/s calibration.
const unsigned long REENTRY_WINDOW_MS=15000;
const unsigned long GREETING_DURATION_MS=6000;
const size_t MAX_TEXT_CHARS=280;
const size_t GLYPH_COUNT=46;
const char* CLOSING_SUFFIX=" | BY ENGINEER DEMKAA & ATAYI | GOODBYE";
const size_t PREVIEW_PREFIX_LENGTH=8;
const unsigned long PIR_RESTART_DELAY_MS=10000;
uint32_t closingAnchor=0,cooldownWaitMs=0;
bool pendingShow=false;
String pendingShowLevel,pendingShowDay;
bool pendingShowPreview=false;
const size_t MAX_UPLOAD_BYTES=32768;
const size_t MAX_SEGMENT_PAYLOAD=4096;
const size_t MAX_ATT_WRITE=509;
const unsigned long CHUNK_PAUSE_MS=8, SEGMENT_PAUSE_MS=180;
const char* LEVELS[]={"100L","200L","300L","400L","500L"};
const char* DAYS[]={"Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"};
const byte KP_ROWS=4,KP_COLS=4;
byte rowPins[KP_ROWS]={13,12,14,33};
byte colPins[KP_COLS]={32,26,25,19};
char keys[KP_ROWS][KP_COLS]={{'1','2','3','A'},{'4','5','6','B'},{'7','8','9','C'},{'*','0','#','D'}};

RTC_DS3231 rtc;
const unsigned long KEY_STABLE_MS=75, KEY_RELEASE_MS=80;
char keyCandidate=0,lastStableKey=0;
bool keypadArmed=false; // Require all keys released after boot.
unsigned long keyCandidateSince=0,keyReleaseSince=0;
bool releaseTiming=false;
uint16_t lastKeyMask=0;
WebServer server(80);
Preferences preferences;
const char* ADMIN_AP_SSID="CampusDisplay-Offline";
const char* ADMIN_AP_PASSWORD="Campus1696";
// ESP32 AP and STA share a channel. Set the router to a fixed 2.4 GHz channel,
// then use that SAME channel here or in the dashboard. Six is only a default.
const uint8_t AP_CHANNEL=6;
const unsigned long STA_RETRY_MS=30000, STA_ATTEMPT_TIMEOUT_MS=8000;
struct WifiRequest { char ssid[33]; char password[65]; uint8_t channel; bool enabled; };
String stationSsid,stationPassword;
uint8_t configuredChannel=AP_CHANNEL;
bool stationEnabled=false,stationAttemptActive=false;
unsigned long lastStaTry=0,staAttemptStarted=0;
uint8_t bleConnectFails=0;
QueueHandle_t wifiQueue=nullptr;
bool webStarted=false;
bool bleRetryRequested=false;
unsigned long lastWebHeartbeat=0;
BLEClient* client=nullptr;
BLERemoteCharacteristic* writer=nullptr;
bool rtcPresent=false,clockValid=false,fsReady=false;
volatile bool bleReady=false;
bool entryDirty=false;
unsigned long entryChangedAt=0;
volatile bool motionFlag=false;
volatile uint32_t pendingUtc=0;
volatile uint32_t pendingCalibrationMs=0;
volatile bool requestWake=false;
volatile bool pendingStatus=false;
volatile bool uploadedTimetable=false;
// EEE data uses /eee_timetable.json; the previous /timetable.json is untouched.
// Multipart upload streams to disk. Never keep the full JSON body in RAM.
File uploadFile;
bool uploadStarted=false,uploadEnded=false,uploadFailed=false;
size_t uploadBytes=0;
String uploadError;
SemaphoreHandle_t fileMutex=nullptr;
SemaphoreHandle_t rtcMutex=nullptr;
enum AppState {STATE_CONNECT,STATE_IDLE,STATE_GREETING,STATE_LEVEL,STATE_TIMETABLE,STATE_GOODBYE,STATE_COOLDOWN,STATE_REENTRY,STATE_WEEKEND,STATE_WELCOME};
AppState state=STATE_CONNECT;
unsigned long lastActivity=0,stateStart=0,messageStart=0,messageHoldMs=0,reconnectAt=0;
unsigned long lastNtpCheck=0,lastNtpSync=0;
bool ntpSynced=false;
float scrollPps=DEFAULT_SCROLL_PIXELS_PER_SECOND;
String levelInput,selectedLevel,selectedDay,lastMessage;
String lastIdleClock;
bool idleClockDirty=true,lastDisplayStatic=false;
unsigned long lastClockCheck=0;
size_t lastPixelWidth=0;
uint16_t largeGlyphs[GLYPH_COUNT][14];

int fontIndex(char c){
 if(c==' ')return 0;
 if(c>='0'&&c<='9')return 1+c-'0';
 if(c>='A'&&c<='Z')return 11+c-'A';
 if(c=='.')return 37;if(c==':')return 38;
 if(c=='-'||c=='|')return 39;if(c=='!')return 40;
 if(c=='#')return 41;if(c=='&')return 43;if(c=='/')return 44;if(c=='*')return 45;return 42;
}
void preloadGlyphs(){
 memset(largeGlyphs,0,sizeof(largeGlyphs));
 for(size_t g=0;g<GLYPH_COUNT;g++)for(int y=0;y<7;y++){
  uint8_t row=pgm_read_byte(&FONT[g][y]);uint16_t out=0;
  for(int x=0;x<6;x++)if(row&(0x20>>x))out|=(uint16_t)(3U<<(2*x));
  largeGlyphs[g][2*y]=out;largeGlyphs[g][2*y+1]=out;
 }
}
void setupKeypad(){
 for(byte row=0;row<KP_ROWS;row++)pinMode(rowPins[row],INPUT_PULLUP);
 for(byte col=0;col<KP_COLS;col++){
  digitalWrite(colPins[col],LOW);pinMode(colPins[col],INPUT);
 }
 Serial.println("Keypad guard: one key stable 75 ms; all released 80 ms; invalid levels ignored.");
}
// Rows have pull-ups; only ONE column is driven LOW at a time. Other columns
// stay high-impedance, not driven HIGH, to avoid contention on multiple presses.
char scanKeypad(){
 uint16_t mask=0;int count=0;char found=0;
 for(byte col=0;col<KP_COLS;col++){
  digitalWrite(colPins[col],LOW);pinMode(colPins[col],OUTPUT);
  delayMicroseconds(50);
  for(byte row=0;row<KP_ROWS;row++)if(digitalRead(rowPins[row])==LOW){
   mask|=(uint16_t)(1U<<(row*KP_COLS+col));found=keys[row][col];count++;
  }
  pinMode(colPins[col],INPUT);
 }
 lastKeyMask=mask;
 if(count==0)return 0;
 return count==1?found:(char)1; // 1 is an invalid/multiple-key sentinel.
}
char getStableKey(){
 char raw=scanKeypad();unsigned long now=millis();
 if(raw==0){
  keyCandidate=0;
  if(!releaseTiming){releaseTiming=true;keyReleaseSince=now;}
  if(now-keyReleaseSince>=KEY_RELEASE_MS)keypadArmed=true;
  return 0;
 }
 releaseTiming=false;
 if(raw==(char)1){keypadArmed=false;keyCandidate=0;return 0;}
 if(!keypadArmed)return 0;
 if(raw!=keyCandidate){keyCandidate=raw;keyCandidateSince=now;return 0;}
 if(now-keyCandidateSince<KEY_STABLE_MS)return 0;
 keypadArmed=false;keyCandidate=0;lastStableKey=raw;
 Serial.printf("KEY stable='%c', mask=0x%04x, state=%d, input='%s'\n",
  raw,(unsigned)lastKeyMask,(int)state,levelInput.c_str());
 return raw;
}

uint32_t crcByte(uint32_t crc,uint8_t v){
 crc^=v;for(int i=0;i<8;i++)crc=(crc>>1)^((crc&1)?0xedb88320UL:0);return crc;
}
void putLE(uint8_t* p,uint32_t v,int bytes){for(int i=0;i<bytes;i++)p[i]=(v>>(8*i))&255;}
#include "idle_clock.h"

bool connected(){return client&&client->isConnected()&&writer;}
void control(uint8_t* p,size_t n){if(connected()){writer->writeValue(p,n,false);delay(120);}}
void power(bool on){uint8_t p[]={5,0,7,1,(uint8_t)(on?1:0)};control(p,sizeof(p));}
void brightness(){uint8_t p[]={5,0,4,0x80,BRIGHTNESS};control(p,sizeof(p));}

// Render the WHOLE message into 8-column bitmap tiles. The tiles are content
// records, not animation frames. Native mode scrolls this strip on the panel.
// Characters are 12x14 with 2 columns of spacing; letters/digits same scale.
uint8_t payloadByte(size_t index,const String& text,size_t tiles){
 if(index<14){
  uint8_t header[14]={0,0,1,1,1,NATIVE_SPEED,1,8,0xff,0,0,0,0,0};
  putLE(header,tiles,2);return header[index];
 }
 size_t record=(index-14)/20,field=(index-14)%20;
 if(field<6){const uint8_t meta[6]={0,8,0xff,0,0,0};return meta[field];}
 int row=field-6;uint8_t bits=0;
 for(int bit=0;bit<8;bit++){
  size_t x=record*8+bit,character=x/14,col=x%14;
  if(character<text.length()&&col<12&&
     (largeGlyphs[fontIndex(text[character])][row]&(1U<<col)))bits|=(1U<<bit);
 }
 return bits;
}
bool uploadNative(String text){
 if(!connected())return false;
 text.toUpperCase();text.trim();if(!text.length())text=" ";
 if(text.length()>MAX_TEXT_CHARS){Serial.println("Message exceeds 280 characters; not truncated.");return false;}
 size_t tiles=(text.length()*14+7)/8;
 size_t payloadSize=14+tiles*20;
 uint32_t crc=0xffffffffUL;
 for(size_t i=0;i<payloadSize;i++)crc=crcByte(crc,payloadByte(i,text,tiles));
 crc=~crc;
 size_t mtu=client->getMTU();if(mtu<23)return false;
 size_t att=min(MAX_ATT_WRITE,mtu-3);
 uint8_t chunk[MAX_ATT_WRITE];
 for(size_t offset=0;offset<payloadSize;offset+=MAX_SEGMENT_PAYLOAD){
  size_t part=min(MAX_SEGMENT_PAYLOAD,payloadSize-offset);
  uint8_t envelope[15]={0};putLE(envelope,part+15,2);
  envelope[3]=1;envelope[4]=(offset==0?0:2);
  putLE(envelope+5,payloadSize,4);putLE(envelope+9,crc,4);envelope[14]=0x65;
  for(size_t pos=0;pos<part+15;pos+=att){
   if(!connected())return false;
   size_t n=min(att,part+15-pos);
   for(size_t k=0;k<n;k++){
    size_t relative=pos+k;
    chunk[k]=(relative<15)?envelope[relative]:payloadByte(offset+relative-15,text,tiles);
   }
   writer->writeValue(chunk,n,false);delay(CHUNK_PAUSE_MS);
  }
  if(offset+part<payloadSize)delay(SEGMENT_PAUSE_MS);
 }
 lastMessage=text;lastPixelWidth=tiles*8;
 messageStart=millis();
 messageHoldMs=(unsigned long)(((lastPixelWidth+64)*1000.0f)/scrollPps)+3000;
 Serial.println("DISPLAY TEXT: ["+text+"]");
 Serial.printf("Native upload: %u chars, %u tiles, %u payload bytes, speed=%u; estimated pass hold=%lu ms\n",
   (unsigned)text.length(),(unsigned)tiles,(unsigned)payloadSize,NATIVE_SPEED,messageHoldMs);
 return true;
}
void cleanupBLE(){bleReady=false;writer=nullptr;if(client){if(client->isConnected())client->disconnect();delete client;client=nullptr;}}
bool connectDisplay(){
 cleanupBLE();Serial.println("Connecting to " DISPLAY_MAC_ADDRESS);
 client=BLEDevice::createClient();
 if(!client->connect(BLEAddress(DISPLAY_MAC_ADDRESS)))return false;
 client->setMTU(512);delay(500);
 auto* services=client->getServices();if(!services)return false;
 for(auto& s:*services){auto* chars=s.second->getCharacteristics();if(!chars)continue;
  for(auto& c:*chars){String u=c.second->getUUID().toString().c_str();if(u.equalsIgnoreCase(UUID_WRITE)){writer=c.second;break;}}
  if(writer)break;
 }
 if(!writer||!writer->canWriteNoResponse())return false;
 bleReady=true;Serial.printf("BLE ready, MTU=%u (512 preferred).\n",(unsigned)client->getMTU());return true;
}
DateTime readClock(){
 if(!rtcPresent)return DateTime(2000,1,1);
 xSemaphoreTake(rtcMutex,portMAX_DELAY);DateTime value=rtc.now();xSemaphoreGive(rtcMutex);return value;
}
bool setClockUtc(uint32_t utc,const char* source){
 if(!rtcPresent||utc<1704067200UL||utc>4102444799UL)return false;
 xSemaphoreTake(rtcMutex,portMAX_DELAY);rtc.adjust(DateTime(utc+UTC_OFFSET_SECONDS));xSemaphoreGive(rtcMutex);
 clockValid=true;Serial.println(String("RTC set from ")+source+": "+readClock().timestamp()+" WAT (UTC+1)");return true;
}
String currentDay(){return DAYS[readClock().dayOfTheWeek()];}
String greeting(){if(!clockValid)return "WELCOME";int h=readClock().hour();
 if(h>=5&&h<12)return "GOOD MORNING";if(h>=12&&h<17)return "GOOD AFTERNOON";return "GOOD EVENING";}
void serviceTime(){
 if(pendingUtc){uint32_t utc=pendingUtc;pendingUtc=0;setClockUtc(utc,"browser");}
 if(WiFi.status()!=WL_CONNECTED||millis()-lastNtpCheck<2000)return;
 lastNtpCheck=millis();time_t now=time(nullptr);
 if(now<1704067200LL)return;
 if(!ntpSynced||millis()-lastNtpSync>86400000UL){
  if(setClockUtc((uint32_t)now,"NTP")){ntpSynced=true;lastNtpSync=millis();}
 }
}
String levelFromDigits(const String& s){for(auto level:LEVELS)if(s+"L"==level)return String(level);return "";}

bool validHHMM(const String& t){
 return t.length()==5&&t[2]==':'&&isDigit(t[0])&&isDigit(t[1])&&isDigit(t[3])&&isDigit(t[4])&&
  t.substring(0,2).toInt()<24&&t.substring(3).toInt()<60;
}
bool validCourseCode(const String& code){
 if(!code.length()||code.length()>24)return false;
 bool hasAlnum=false;
 for(size_t i=0;i<code.length();i++){
  char c=toupper((unsigned char)code[i]);
  if((c>='A'&&c<='Z')||(c>='0'&&c<='9')){hasAlnum=true;continue;}
  if(c!=' '&&c!='.'&&c!=':'&&c!='-'&&c!='!'&&c!='#'&&c!='?'&&c!='|'&&c!='/'&&c!='&')return false;
 }
 return hasAlnum;
}
// Caller holds fileMutex; root/day filters keep RAM usage independent of file size.
bool readCourses(const char* path,const String& level,const String& day,String& result,String& error){
 if(ESP.getFreeHeap()<14000||heap_caps_get_largest_free_block(MALLOC_CAP_8BIT)<8192){
  error="Insufficient free RAM for validation; close other clients and retry";return false;
 }
 File f=LittleFS.open(path,"r");if(!f){error="Cannot open timetable";return false;}
 StaticJsonDocument<256> filter;filter[level][day]=true;
 DynamicJsonDocument doc(6144);
 if(!doc.capacity()){error="Insufficient RAM";f.close();return false;}
 auto e=deserializeJson(doc,f,DeserializationOption::Filter(filter));f.close();
 if(e){error=String("JSON: ")+e.c_str();return false;}
 if(!doc.is<JsonObject>()||!doc[level].is<JsonObject>()||!doc[level][day].is<JsonArray>()){
  error="Missing level/day array: "+level+" / "+day;return false;
 }
 JsonArray courses=doc[level][day].as<JsonArray>();
 if(courses.size()>16){error="Maximum 16 classes per day";return false;}
 result=level+" "+day+" | ";
 if(courses.size()==0){
  result+="NO COURSES LISTED - CHECK DEPARTMENT";return true;
 }
 bool first=true;
 for(JsonVariant item:courses){
  if(!item.is<JsonObject>()||!item["code"].is<const char*>()||!item["time"].is<const char*>()||!item["venue"].is<const char*>()){
   error="Each class needs string code, time and venue";return false;
  }
  String code=item["code"].as<String>(),t=item["time"].as<String>(),venue=item["venue"].as<String>();
  String endTime="";
  if(item.containsKey("end")){
   if(!item["end"].is<const char*>()){error="end must be a HH:MM string";return false;}
   endTime=item["end"].as<String>();
  }
  if(!validCourseCode(code)||code.length()>24||!venue.length()||venue.length()>32||!validHHMM(t)||
    (endTime.length()&&(!validHHMM(endTime)||endTime<=t))){
   error="Use a course code, venue, valid HH:MM start and a later end time";return false;
  }
  String fields=code+venue;
  for(size_t i=0;i<fields.length();i++){
   char c=toupper((unsigned char)fields[i]);
   if(!((c>='A'&&c<='Z')||(c>='0'&&c<='9')||c==' '||c=='.'||c==':'||c=='-'||c=='!'||c=='#'||c=='?'||c=='|'||c=='/'||c=='&')){
    error="Unsupported display character in code/venue";return false;
   }
  }
  if(!first)result+=" | ";first=false;
  String interval=t;if(endTime.length())interval+="-"+endTime;
  result+=code+" "+interval+" "+venue;
 }
 if(result.length()+strlen(CLOSING_SUFFIX)+PREVIEW_PREFIX_LENGTH>MAX_TEXT_CHARS){
  error="Day text plus credits/preview exceeds 280 characters; shorten venue names";return false;
 }
 return true;
}
bool validateTimetable(const char* path,String& error){
 for(auto level:LEVELS)for(auto day:DAYS){String result;if(!readCourses(path,level,day,result,error))return false;delay(1);}
 return true;
}

// Native mode has no decoded finish ACK. Remove the old 3-second hold
// margin for a one-pass estimate, without changing any transport bytes.
void useSinglePassEstimate(){
 lastDisplayStatic=false;
 messageHoldMs=messageHoldMs>3000?messageHoldMs-3000:1;
 Serial.printf("Session one-pass hold estimate=%lu ms\n",messageHoldMs);
}
void armClosingCooldown(){
 useSinglePassEstimate();
 closingAnchor=messageStart;
 int goodbyeIndex=lastMessage.lastIndexOf("GOODBYE");
 if(goodbyeIndex<0)goodbyeIndex=lastMessage.lastIndexOf("SEE YOU ON MONDAY");
 // Estimate when GOODBYE's first column reaches the right edge. The
 // complete-pass estimate includes the additional screen-exit width.
 unsigned long entryMs=goodbyeIndex<0?0:(unsigned long)(goodbyeIndex*14.0f*1000.0f/scrollPps);
 if(entryMs>messageHoldMs)entryMs=messageHoldMs;
 cooldownWaitMs=entryMs+PIR_RESTART_DELAY_MS;
 Serial.printf("Closing marker entry estimated at +%lu ms; restart eligible at +%lu ms, only after ending finishes.\n",entryMs,cooldownWaitMs);
}
uint32_t cooldownRemaining(uint32_t now){
 uint32_t elapsed=now-closingAnchor;
 return elapsed>=cooldownWaitMs?0:cooldownWaitMs-elapsed;
}
bool cooldownElapsed(uint32_t now){return cooldownRemaining(now)==0;}
bool shouldStartSession(uint32_t now,bool pirHigh,bool manualWake){
 if(!pirHigh&&!manualWake)return false;
 return state==STATE_IDLE||(state==STATE_COOLDOWN&&cooldownElapsed(now));
}

bool isWeekendDay(const String& day){return day=="Saturday"||day=="Sunday";}
bool showWeekend(bool preview){
 String message="WELCOME HAPPY WEEKEND | WELCOME TO ELECTRICAL | NO LECTURES TODAY | SEE YOU ON MONDAY - BY ENGINEER DEMKAA & ATAYI";
 if(preview)message="PREVIEW "+message;
 power(true);brightness();if(!uploadNative(message))return false;
 armClosingCooldown();state=STATE_WEEKEND;
 selectedLevel="";selectedDay="";entryDirty=false;levelInput="";
 return true;
}
void beginClosing(bool noEntry){
 lastDisplayStatic=false;
 String message=noEntry?"NO ENTRY | GOODBYE - BY ENGINEER DEMKAA & ATAYI":"BY ENGINEER DEMKAA & ATAYI | GOODBYE";
 if(!uploadNative(message))return;
 armClosingCooldown();state=STATE_GOODBYE;stateStart=millis();entryDirty=false;
}
void enterReentry(){
 lastDisplayStatic=false;
 if(!uploadNative("PRESS * TO RE-ENTER LEVEL"))return;
 state=STATE_REENTRY;stateStart=millis();entryDirty=false;
 Serial.println("RE-ENTRY: press * within 15 seconds for another level or repeat; otherwise credits/GOODBYE.");
}

bool showLevel(const String& level,const String& day,bool preview){
 lastDisplayStatic=false;
 if(!connected())return false;
 if(!preview&&!clockValid){power(true);brightness();uploadNative("CLOCK NOT SET - SYNC CLOCK ON WEB PAGE");state=STATE_LEVEL;return false;}
 if(isWeekendDay(day))return showWeekend(preview);
 String message,error;
 if(!fsReady){message="FILESYSTEM ERROR";}
 else if(xSemaphoreTake(fileMutex,pdMS_TO_TICKS(1000))==pdTRUE){
  bool ok=readCourses("/eee_timetable.json",level,day,message,error);xSemaphoreGive(fileMutex);
  if(!ok){Serial.println("LOOKUP ERROR: "+error);message="TIMETABLE ERROR - CHECK WEB PAGE";}
 }else message="TIMETABLE BUSY - TRY AGAIN";
 if(preview)message="PREVIEW "+message;
 power(true);brightness();
 if(!uploadNative(message))return false;
 useSinglePassEstimate();
 selectedLevel=level;selectedDay=preview?"":day;
 state=STATE_TIMETABLE;lastActivity=millis();entryDirty=false;
 Serial.printf("LEVEL SESSION: level=%s day=%s preview=%s; timetable then 15-second re-entry opportunity\n",level.c_str(),day.c_str(),preview?"YES":"NO");
 return true;
}
bool uploadIdleClock(const String& text){
 if(!connected()||text.length()!=5)return false;
 uint8_t packet[IDLE_CLOCK_PACKET_SIZE];buildIdleClockPacket(text.c_str(),packet);
 size_t mtu=client->getMTU();if(mtu<23)return false;
 size_t chunk=min(MAX_ATT_WRITE,mtu-3);
 for(size_t i=0;i<IDLE_CLOCK_PACKET_SIZE;i+=chunk){
  if(!connected())return false;
  size_t count=min(chunk,IDLE_CLOCK_PACKET_SIZE-i);
  writer->writeValue(packet+i,count,false);delay(CHUNK_PAUSE_MS);
 }
 lastMessage=text;lastDisplayStatic=true;return true;
}
void serviceIdleClock(bool force=false){
 if(!connected()||(state!=STATE_IDLE&&state!=STATE_COOLDOWN))return;
 unsigned long now=millis();
 if(!force&&!idleClockDirty&&now-lastClockCheck<1000)return;
 lastClockCheck=now;
 char timeText[6]="--:--";
 if(clockValid){DateTime dt=readClock();snprintf(timeText,sizeof(timeText),"%02u:%02u",(unsigned)dt.hour(),(unsigned)dt.minute());}
 String text=timeText;
 if(!force&&!idleClockDirty&&text==lastIdleClock)return;
 power(true);brightness();
 if(uploadIdleClock(text)){lastIdleClock=text;idleClockDirty=false;}
}
void finishLevelSession(){
 state=STATE_COOLDOWN;levelInput="";selectedLevel="";selectedDay="";entryDirty=false;
 motionFlag=false;idleClockDirty=true;serviceIdleClock(true);
 Serial.println("SESSION FINISHED: stationary clock. Waiting for restart gate and PIR HIGH.");
}

void ensureSample(){
 if(!fsReady)return;
 if(LittleFS.exists("/eee_timetable.json")){Serial.println("Saved EEE timetable retained.");return;}
 // Recover a previous timetable if replacement was interrupted.
 if(LittleFS.exists("/eee_timetable.bak")){LittleFS.rename("/eee_timetable.bak","/eee_timetable.json");return;}
 File f=LittleFS.open("/eee_timetable.json","w");if(f){f.print(SAMPLE_TIMETABLE);f.close();Serial.println("Extracted EEE DRAFT timetable installed. Verify with department.");}
}
const char* resetReasonName(){
 switch(esp_reset_reason()){
  case ESP_RST_POWERON:return "POWERON";
  case ESP_RST_EXT:return "EXTERNAL";
  case ESP_RST_SW:return "SOFTWARE";
  case ESP_RST_PANIC:return "PANIC";
  case ESP_RST_INT_WDT:return "INTERRUPT_WATCHDOG";
  case ESP_RST_TASK_WDT:return "TASK_WATCHDOG";
  case ESP_RST_WDT:return "WATCHDOG";
  case ESP_RST_DEEPSLEEP:return "DEEP_SLEEP";
  case ESP_RST_BROWNOUT:return "BROWNOUT";
  case ESP_RST_SDIO:return "SDIO";
  default:return "OTHER_OR_UNKNOWN";
 }
}

String statusJson(){
 StaticJsonDocument<2048> doc;
 doc["ble_connected"]=(bool)bleReady;doc["wifi_connected"]=WiFi.status()==WL_CONNECTED;
 doc["ip"]=WiFi.localIP().toString();doc["ap_ip"]=WiFi.softAPIP().toString();
 doc["ap_clients"]=WiFi.softAPgetStationNum();doc["web_started"]=webStarted;
 doc["wifi_status"]=(int)WiFi.status();doc["uptime_seconds"]=millis()/1000;
 doc["reset_reason"]=(int)esp_reset_reason();
 doc["reset_reason_name"]=resetReasonName();
 doc["brownout_reset"]=(esp_reset_reason()==ESP_RST_BROWNOUT);
 doc["configured_channel"]=configuredChannel;doc["actual_channel"]=WiFi.channel();
 doc["station_enabled"]=stationEnabled;doc["station_ssid"]=stationSsid;
 doc["station_attempt_active"]=stationAttemptActive;
 doc["ble_connect_failures"]=bleConnectFails;
 doc["rtc_present"]=rtcPresent;doc["clock_valid"]=clockValid;
 doc["local_time"]=rtcPresent?readClock().timestamp():"RTC missing";
 doc["timezone"]="Africa/Lagos UTC+1";doc["day"]=clockValid?currentDay():"Unknown";
 doc["native_speed"]=NATIVE_SPEED;doc["free_heap"]=ESP.getFreeHeap();
 doc["minimum_free_heap"]=ESP.getMinFreeHeap();
 doc["largest_free_block"]=heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
 doc["web_backend"]="WebServer single-client";
 doc["state"]=(int)state;doc["pixels_per_second_estimate"]=scrollPps;
 doc["last_message_pixels"]=(unsigned)lastPixelWidth;
 doc["pass_hold_ms"]=messageHoldMs;
 doc["project_version"]="Electrical Campus Session v4";
 doc["session_active"]=(state==STATE_GREETING||state==STATE_LEVEL||state==STATE_TIMETABLE||state==STATE_GOODBYE||state==STATE_REENTRY||state==STATE_WEEKEND||state==STATE_WELCOME);
 doc["motion_ignored_during_session"]=true;
 doc["restart_delay_ms"]=PIR_RESTART_DELAY_MS;
 doc["cooldown_remaining_ms"]=state==STATE_COOLDOWN?cooldownRemaining(millis()):0;doc["department"]="Electrical - all course prefixes";
 doc["closing_included"]=true;
 doc["reentry_window_ms"]=REENTRY_WINDOW_MS;
 doc["calibration_key"]=CALIBRATION_KEY;
 doc["greeting_reference_ms"]=4000;
 doc["greeting_duration_ms"]=GREETING_DURATION_MS;
 doc["display_static"]=lastDisplayStatic;
 doc["keypad_mask"]=(unsigned)lastKeyMask;
 if(lastStableKey){char key[2]={lastStableKey,0};doc["last_stable_key"]=key;}
 String out;serializeJson(doc,out);return out;
}
// WebServer's multipart parser hands us small upload buffers. JSON is written
// straight to LittleFS, then filter-validated after reception. Raw JSON POST
// is intentionally NOT supported: WebServer would buffer that body in a String.
void receiveTimetableUpload(){
 HTTPUpload& upload=server.upload();
 if(upload.status==UPLOAD_FILE_START){
  if(uploadStarted){uploadFailed=true;uploadError="Send exactly one file per request";return;}
  uploadStarted=true;uploadEnded=false;uploadFailed=false;uploadBytes=0;uploadError="";
  if(!fsReady){uploadFailed=true;uploadError="LittleFS unavailable";return;}
  uploadFile=LittleFS.open("/eee_timetable.upload","w");
  if(!uploadFile){uploadFailed=true;uploadError="Cannot create temporary timetable";}
 }else if(upload.status==UPLOAD_FILE_WRITE){
  if(uploadFailed||!uploadStarted)return;
  if(uploadBytes+upload.currentSize>MAX_UPLOAD_BYTES){
   uploadFailed=true;uploadError="JSON exceeds 32768 bytes";
   if(uploadFile)uploadFile.close();return;
  }
  if(!uploadFile||uploadFile.write(upload.buf,upload.currentSize)!=upload.currentSize){
   uploadFailed=true;uploadError="Temporary file write failed";return;
  }
  uploadBytes+=upload.currentSize;delay(1);
 }else if(upload.status==UPLOAD_FILE_END){
  if(uploadFile)uploadFile.close();uploadEnded=true;
  if(uploadBytes==0){uploadFailed=true;uploadError="Empty upload";}
 }else if(upload.status==UPLOAD_FILE_ABORTED){
  if(uploadFile)uploadFile.close();
  uploadStarted=false;uploadEnded=false;uploadFailed=false;uploadBytes=0;
  if(fsReady)LittleFS.remove("/eee_timetable.upload");
 }
}
void finishTimetableUpload(){
 if(uploadFile)uploadFile.close();
 if(!uploadStarted||!uploadEnded||uploadFailed){
  String reason=uploadError.length()?uploadError:"Use multipart/form-data with one JSON file (not a raw JSON body)";
  if(fsReady)LittleFS.remove("/eee_timetable.upload");
  server.send(400,"text/plain",reason);
 }else{
  String error;
  bool valid=validateTimetable("/eee_timetable.upload",error),saved=false;
  if(valid){
   LittleFS.remove("/eee_timetable.bak");
   bool moved=!LittleFS.exists("/eee_timetable.json")||LittleFS.rename("/eee_timetable.json","/eee_timetable.bak");
   saved=moved&&LittleFS.rename("/eee_timetable.upload","/eee_timetable.json");
   if(!saved&&LittleFS.exists("/eee_timetable.bak"))LittleFS.rename("/eee_timetable.bak","/eee_timetable.json");
  }
  if(!saved)LittleFS.remove("/eee_timetable.upload");
  if(saved){uploadedTimetable=true;server.send(200,"text/plain","Timetable validated and saved");}
  else server.send(valid?500:400,"text/plain",valid?"Replacement failed; old data retained":error);
 }
 uploadStarted=false;uploadEnded=false;uploadFailed=false;uploadBytes=0;uploadError="";
}
void setupServer(){
 server.on("/health",HTTP_GET,[](){
  Serial.println("HTTP GET /health reached ESP32");
  server.send(200,"text/plain","Smart Campus webserver OK");
 });
 server.on("/api/wifi",HTTP_POST,[](){
  bool enabled=!server.hasArg("enabled")||server.arg("enabled")!="0";
  String ssid=server.hasArg("ssid")?server.arg("ssid"):"";
  String password=server.hasArg("password")?server.arg("password"):"";
  String channel=server.hasArg("channel")?server.arg("channel"):String(configuredChannel);
  int ch=channel.toInt();
  bool numeric=channel.length()>0;
  for(size_t i=0;i<channel.length();i++)if(!isDigit(channel[i]))numeric=false;
  if(!numeric||ch<1||ch>11){server.send(400,"text/plain","Choose a router/AP channel from 1 to 11");return;}
  if(enabled&&(!ssid.length()||ssid.length()>32||password.length()>64)){
   server.send(400,"text/plain","SSID must be 1-32 bytes; password max 64 bytes");return;
  }
  WifiRequest request={};ssid.toCharArray(request.ssid,sizeof(request.ssid));
  password.toCharArray(request.password,sizeof(request.password));
  request.channel=(uint8_t)ch;request.enabled=enabled;
  if(xQueueSend(wifiQueue,&request,0)!=pdTRUE){server.send(409,"text/plain","A Wi-Fi request is already pending");return;}
  server.send(202,"text/plain",enabled?
   "Saved request. AP and station will use the selected channel. A channel change briefly disconnects AP clients: rejoin CampusDisplay-Offline. Use the router's actual fixed channel.":
   "Offline-only mode queued. Router retries will stop; the admin AP remains available.");
 });
 server.on("/",HTTP_GET,[](){Serial.println("HTTP GET / reached ESP32");
  if(ESP.getFreeHeap()<12000||heap_caps_get_largest_free_block(MALLOC_CAP_8BIT)<4096){server.send(503,"text/plain","Low RAM; close other clients and retry");return;}
  server.sendHeader("Cache-Control","no-store");server.sendHeader("Connection","close");
  server.sendHeader("Content-Encoding","gzip");
  server.send_P(200,"text/html",reinterpret_cast<const char*>(WEB_PAGE_GZ),sizeof(WEB_PAGE_GZ));});
 server.on("/api/source-timetable",HTTP_GET,[](){
  server.sendHeader("Cache-Control","no-store");server.send_P(200,"application/json",SAMPLE_TIMETABLE);
 });
 server.on("/api/display",HTTP_GET,[](){server.send(200,"text/plain",lastMessage);});
 server.on("/api/show",HTTP_POST,[](){
  String level=server.arg("level");bool known=false;
  for(auto v:LEVELS)if(level==v)known=true;
  if(!known){server.send(400,"text/plain","Choose 100L-500L");return;}
  bool preview=server.hasArg("day");String day=preview?server.arg("day"):(clockValid?currentDay():"");
  bool dayKnown=false;for(auto v:DAYS)if(day==v)dayKnown=true;
  if(!dayKnown){server.send(400,"text/plain","Set the clock or choose a valid preview day");return;}
  if(!connected()){server.send(503,"text/plain","BLE not connected");return;}
  pendingShowLevel=level;pendingShowDay=day;pendingShowPreview=preview;pendingShow=true;
  server.send(202,"text/plain",isWeekendDay(day)?"Weekend message queued; no level entry":(preview?"Saved day preview queued, then 15-second re-entry window and closing":"Today's saved EEE schedule queued, then 15-second re-entry window and closing"));
 });
 server.on("/api/status",HTTP_GET,[](){if(ESP.getFreeHeap()<12000){server.send(503,"text/plain","Low RAM");return;}
  server.sendHeader("Cache-Control","no-store");server.send(200,"application/json",statusJson());});
 server.on("/api/timetable",HTTP_GET,[](){
  if(!fsReady||!LittleFS.exists("/eee_timetable.json")){server.send(404,"text/plain","No timetable");return;}
  File file=LittleFS.open("/eee_timetable.json","r");
  if(!file){server.send(500,"text/plain","Cannot read timetable");return;}
  server.streamFile(file,"application/json");file.close();
 });
 server.on("/api/time",HTTP_POST,[](){
  if(!rtcPresent){server.send(503,"text/plain","DS3231 not detected; check wiring");return;}
  if(!server.hasArg("utc")){server.send(400,"text/plain","UTC epoch required");return;}
  String input=server.arg("utc");
  for(size_t i=0;i<input.length();i++)if(!isDigit(input[i])){server.send(400,"text/plain","Invalid epoch");return;}
  uint64_t utc=strtoull(input.c_str(),nullptr,10);
  if(utc<1704067200ULL||utc>4102444799ULL){server.send(400,"text/plain","Date outside 2024-2099");return;}
  pendingUtc=(uint32_t)utc;server.send(202,"text/plain","Clock update queued (Nigeria UTC+1)");
 });
 server.on("/api/ble-retry",HTTP_POST,[](){bleRetryRequested=true;server.send(202,"text/plain","BLE retry queued; HTTP may pause during the blocking connect");});
 server.on("/api/test",HTTP_POST,[](){
  if(!shouldStartSession(millis(),false,true)){server.send(409,"text/plain","Session in progress or cooldown active; wake ignored");return;}
  requestWake=true;server.send(202,"text/plain","Wake requested");
 });
 server.on("/api/calibrate",HTTP_POST,[](){
  if(!server.hasArg("seconds")){server.send(400,"text/plain","seconds required");return;}
  float seconds=server.arg("seconds").toFloat();
  if(seconds<2||seconds>3600){server.send(400,"text/plain","Use 2-3600 seconds");return;}
  if(lastDisplayStatic||!lastPixelWidth){server.send(409,"text/plain","Display a scrolling message first; do not calibrate the static clock");return;}
  pendingCalibrationMs=(uint32_t)(seconds*1000);server.send(202,"text/plain","Calibration queued; applies to subsequent messages");
 });
 server.on("/upload",HTTP_POST,finishTimetableUpload,receiveTimetableUpload);
 server.onNotFound([](){server.send(404,"text/plain","Not found. Open / for dashboard or /health for diagnostics.");});
 server.begin();webStarted=true;
 Serial.println("Synchronous single-client HTTP server started on port 80. Diagnostic URL: http://192.168.4.1/health");
}
void startStationAttempt(){
 if(!stationEnabled||!stationSsid.length())return;
 WiFi.disconnect(false,false); // STA only, preserve AP.
 lastStaTry=millis();staAttemptStarted=lastStaTry;stationAttemptActive=true;
 // Supply the expected channel instead of an unconstrained begin(). Driver
 // scan details remain core-dependent; AP+STA cannot independently pin two.
 // For guaranteed no-STA-attempt periods, select offline-only mode.
 WiFi.begin(stationSsid.c_str(),stationPassword.c_str(),configuredChannel);
 WiFi.setAutoReconnect(false);
 Serial.printf("STA attempt on fixed channel %u, timeout %lu ms.\n",configuredChannel,STA_ATTEMPT_TIMEOUT_MS);
}
void setupNetwork(){
 stationSsid=preferences.getString("wifi_ssid","");
 stationPassword=preferences.getString("wifi_pass","");
 stationEnabled=preferences.getBool("wifi_on",stationSsid.length()>0);
 configuredChannel=preferences.getUChar("wifi_chan",AP_CHANNEL);
 if(configuredChannel<1||configuredChannel>11)configuredChannel=AP_CHANNEL;
 WiFi.mode(WIFI_AP_STA);
 WiFi.setAutoReconnect(false);
 // Do not force WiFi.setSleep(false). Keep the core's default power-saving
 // policy for this coexistence test; modem sleep is platform/mode dependent.
 IPAddress ip(192,168,4,1),gateway(192,168,4,1),mask(255,255,255,0);
 bool configured=WiFi.softAPConfig(ip,gateway,mask);
 bool started=WiFi.softAP(ADMIN_AP_SSID,ADMIN_AP_PASSWORD,configuredChannel,0,1);
 Serial.printf("Admin AP configured=%s started=%s, channel=%u\n",configured?"YES":"NO",started?"YES":"NO",configuredChannel);
 Serial.printf("Join %s; password %s\n",ADMIN_AP_SSID,ADMIN_AP_PASSWORD);
 Serial.println("Actual AP IP: "+WiFi.softAPIP().toString());
 setupServer();
 if(stationEnabled&&stationSsid.length())startStationAttempt();
 else Serial.println("Offline-only: no station scan; set credentials/channel in dashboard to enable STA.");
}
void serviceNetwork(){
 WifiRequest request;
 if(xQueueReceive(wifiQueue,&request,0)==pdTRUE){
  stationEnabled=request.enabled;preferences.putBool("wifi_on",stationEnabled);
  if(stationEnabled){
   stationSsid=request.ssid;stationPassword=request.password;
   preferences.putString("wifi_ssid",stationSsid);preferences.putString("wifi_pass",stationPassword);
  }
  bool channelChanged=request.channel!=configuredChannel;
  configuredChannel=request.channel;preferences.putUChar("wifi_chan",configuredChannel);
  WiFi.disconnect(false,false);stationAttemptActive=false;WiFi.setAutoReconnect(false);
  if(channelChanged){
   // Reconfiguration is explicit, not an automatic retry side effect.
   bool ok=WiFi.softAP(ADMIN_AP_SSID,ADMIN_AP_PASSWORD,configuredChannel,0,1);
   Serial.printf("Requested AP channel change to %u: %s. Rejoin AP if needed.\n",configuredChannel,ok?"OK":"FAILED");
  }
  if(stationEnabled)startStationAttempt();
  else Serial.println("Offline-only selected: automatic STA retries disabled.");
 }
 static bool wasConnected=false;
 bool online=WiFi.status()==WL_CONNECTED;
 if(online){stationAttemptActive=false;}
 if(online&&!wasConnected){
  Serial.println("Station connected. Network dashboard: http://"+WiFi.localIP().toString());
  Serial.printf("Radio actual channel=%u; configured channel=%u\n",WiFi.channel(),configuredChannel);
  configTime(0,0,"pool.ntp.org","time.google.com");
  MDNS.end();if(MDNS.begin("campus-display"))MDNS.addService("http","tcp",80);
 }else if(!online&&wasConnected){
  Serial.println("Station Wi-Fi disconnected; admin AP remains enabled. Retry is controlled.");
  lastStaTry=millis();
 }
 wasConnected=online;
 if(!online&&stationAttemptActive&&millis()-staAttemptStarted>=STA_ATTEMPT_TIMEOUT_MS){
  WiFi.disconnect(false,false);stationAttemptActive=false;lastStaTry=millis();
  Serial.println("STA attempt stopped after timeout; AP kept running.");
 }
 // Prefer stable offline administration over background connection attempts.
 // Explicit dashboard requests can connect while clients are associated.
 if(!online&&!stationAttemptActive&&stationEnabled&&stationSsid.length()&&
    WiFi.softAPgetStationNum()==0&&millis()-lastStaTry>=STA_RETRY_MS){startStationAttempt();}
 if(millis()-lastWebHeartbeat>=30000){
  lastWebHeartbeat=millis();
  Serial.printf("Web alive: uptime=%lu s, AP clients=%u, STA=%d, channel=%u, trying=%s, heap=%u\n",
   millis()/1000,(unsigned)WiFi.softAPgetStationNum(),(int)WiFi.status(),WiFi.channel(),
   stationAttemptActive?"YES":"NO",(unsigned)ESP.getFreeHeap());
  Serial.printf("Heap detail: largest block=%u, minimum free=%u\n",
   (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_8BIT),(unsigned)ESP.getMinFreeHeap());
 }
}

void printStatus(){Serial.println(statusJson());}
void serialCommands(){
 static String line;
 while(Serial.available()){
  char c=Serial.read();if(c=='\r')continue;
  if(c=='\n'){
   line.trim();
   if(line=="KEY?"){
    char raw=scanKeypad();
    Serial.printf("KEY raw_mask=0x%04x raw_code=%u (0=none,1=multiple); no keys pressed should read 0x0000\n",
      (unsigned)lastKeyMask,(unsigned)(uint8_t)raw);
   }
   else if(line=="TIME?"){printStatus();}
   else if(line=="T"||line=="t"){requestWake=true;}
   else if(line=="H"||line=="h"){
    if(connected()){selectedLevel="";power(true);brightness();uploadNative("EEE CAMPUS FONT TEST 0123456789 / &");useSinglePassEstimate();lastActivity=millis();state=STATE_TIMETABLE;}
   }else if(line.startsWith("TIME ")){
    String t=line.substring(5);
    bool shape=t.length()==19&&t[4]=='-'&&t[7]=='-'&&t[10]==' '&&t[13]==':'&&t[16]==':';
    for(int i=0;i<(int)t.length()&&shape;i++)if(i!=4&&i!=7&&i!=10&&i!=13&&i!=16&&!isDigit(t[i]))shape=false;
    if(shape){
     DateTime dt(t.substring(0,4).toInt(),t.substring(5,7).toInt(),t.substring(8,10).toInt(),
       t.substring(11,13).toInt(),t.substring(14,16).toInt(),t.substring(17).toInt());
     if(dt.isValid()&&dt.year()>=2024&&dt.year()<=2099)setClockUtc(dt.unixtime()-UTC_OFFSET_SECONDS,"Serial local time");
     else Serial.println("Invalid date/time");
    }else Serial.println("Use TIME YYYY-MM-DD HH:MM:SS (Nigeria local time)");
   }else if(line.startsWith("CAL ")){
    float seconds=line.substring(4).toFloat();if(seconds>=2&&seconds<=3600&&lastPixelWidth&&!lastDisplayStatic)pendingCalibrationMs=(uint32_t)(seconds*1000);
   }else if(line.length())Serial.println("Commands: T, H, KEY?, TIME?, TIME YYYY-MM-DD HH:MM:SS, CAL seconds (send Newline)");
   line="";
  }else if(line.length()<80)line+=c;
 }
}
void IRAM_ATTR onMotion(){motionFlag=true;}
void wakeDisplay(){
 lastDisplayStatic=false;idleClockDirty=true;
 if(clockValid&&isWeekendDay(currentDay())){showWeekend(false);return;}
 power(true);brightness();
 if(!uploadNative(greeting())){power(false);state=STATE_IDLE;return;}
 useSinglePassEstimate();messageHoldMs=GREETING_DURATION_MS;state=STATE_GREETING;
 selectedLevel="";selectedDay="";levelInput="";entryDirty=false;
 stateStart=millis();lastActivity=millis();
}
void enterLevel(){
 lastDisplayStatic=false;
 entryDirty=false;levelInput="";uploadNative("ENTER LEVEL 100-500 THEN PRESS #");
 state=STATE_LEVEL;lastActivity=millis(); // Full entry timeout starts after greeting/prompt.
}

void enterWelcome(){
 if(!uploadNative("WELCOME TO ELECTRICAL"))return;
 useSinglePassEstimate();state=STATE_WELCOME;
}
void serviceSessionTimers(uint32_t now){
 if(state==STATE_GREETING&&now-messageStart>=messageHoldMs){enterWelcome();return;}
 if(state==STATE_WELCOME&&now-messageStart>=messageHoldMs){enterLevel();return;}
 if(state==STATE_TIMETABLE&&now-messageStart>=messageHoldMs){enterReentry();return;}
 if(state==STATE_REENTRY&&now-stateStart>=REENTRY_WINDOW_MS){beginClosing(false);return;}
 // Only user entry has an inactivity timeout. PIR is intentionally ignored.
 if(state==STATE_LEVEL&&now-lastActivity>PIR_TIMEOUT_MS){
  beginClosing(true);
  return; // Do not subtract a pre-upload timestamp from the new messageStart.
 }
 if((state==STATE_GOODBYE||state==STATE_WEEKEND)&&now-messageStart>=messageHoldMs){finishLevelSession();return;}

}

void setup(){
 Serial.begin(115200);delay(500);
 Serial.printf("Reset reason=%d (%s); free heap at startup=%u bytes\n",(int)esp_reset_reason(),resetReasonName(),(unsigned)ESP.getFreeHeap());
 if(esp_reset_reason()==ESP_RST_BROWNOUT)Serial.println("BROWNOUT detected: inspect supply, USB cable, loads and wiring.");
 Serial.println("\n=== Electrical Campus Session v4: 6-second greeting, electrical welcome, static idle clock, all course prefixes ===");
 fileMutex=xSemaphoreCreateMutex();rtcMutex=xSemaphoreCreateMutex();wifiQueue=xQueueCreate(1,sizeof(WifiRequest));
 if(!fileMutex||!rtcMutex||!wifiQueue){Serial.println("Fatal: mutex allocation failed");while(true)delay(1000);}
 preferences.begin("campus",false);scrollPps=preferences.getFloat(CALIBRATION_KEY,DEFAULT_SCROLL_PIXELS_PER_SECOND);
 if(scrollPps<0.1f||scrollPps>1000)scrollPps=DEFAULT_SCROLL_PIXELS_PER_SECOND;
 Serial.printf("Timing v3: %.2f px/s (GOOD MORNING reference: 4 seconds); old calibration is not reused.\n",scrollPps);
 preloadGlyphs();
 // Never format automatically: preserve existing timetable on mount failure.
 fsReady=LittleFS.begin(false);
 if(!fsReady)Serial.println("LittleFS mount failed. See README; no data was erased.");else ensureSample();
 Wire.begin(I2C_SDA,I2C_SCL);rtcPresent=rtc.begin();
 if(rtcPresent){DateTime dt=readClock();clockValid=!rtc.lostPower()&&dt.isValid()&&dt.year()>=2024&&dt.year()<=2099;}
 Serial.println(rtcPresent?(clockValid?"RTC valid; stores Nigeria local time":"RTC needs setting via web/Serial/NTP"):"RTC missing; check SDA21/SCL22 and power");
 setupKeypad();
 pinMode(PIN_PIR,INPUT);pinMode(PIN_BUZZER,OUTPUT);
 attachInterrupt(digitalPinToInterrupt(PIN_PIR),onMotion,RISING);
 setupNetwork();
 Serial.printf("HEAP after AP/web: free=%u maxblock=%u\n",(unsigned)ESP.getFreeHeap(),(unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_8BIT));
 BLEDevice::init("ESP32-EEE-Campus");BLEDevice::setMTU(512);
 Serial.printf("HEAP after BLE init: free=%u maxblock=%u\n",(unsigned)ESP.getFreeHeap(),(unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_8BIT));
 Serial.println("Serial at 115200, Newline: T, H, KEY?, TIME?, TIME YYYY-MM-DD HH:MM:SS, CAL seconds");
}
void loop(){
 server.handleClient(); // Serve one HTTP request at a time in the main task.
 serialCommands();serviceNetwork();serviceTime();
 if(pendingShow){
  pendingShow=false;showLevel(pendingShowLevel,pendingShowDay,pendingShowPreview);
 }
 char k=getStableKey();
 if(pendingCalibrationMs){
  uint32_t duration=pendingCalibrationMs;pendingCalibrationMs=0;
  if(lastPixelWidth){scrollPps=(lastPixelWidth+64)*1000.0f/duration;preferences.putFloat(CALIBRATION_KEY,scrollPps);
   Serial.printf("Scroll duration calibration saved: %.2f estimated pixels/second\n",scrollPps);}
 }
 if(uploadedTimetable){
  uploadedTimetable=false;Serial.println("Timetable saved; applies on the next explicit lookup/session. Active message is not restarted.");
 }
 unsigned long now=millis();
 motionFlag=false; // Discard all queued edges: only present PIR level matters.
 bool manualWake=requestWake;requestWake=false;
 bool pirHigh=digitalRead(PIN_PIR)==HIGH;
 // Motion NEVER refreshes activity or restarts an active session.
 if(manualWake&&!shouldStartSession(now,false,true))Serial.println("Manual wake ignored: session/cooldown in progress.");
 if(state!=STATE_CONNECT&&!connected()){bleReady=false;state=STATE_CONNECT;reconnectAt=now;}
 if(state==STATE_CONNECT){
  // After a failed connect, prioritize the single admin client. Without
  // this guard a synchronous server could stall repeatedly in BLE connect().
  bool allowBleRetry=bleConnectFails==0||WiFi.softAPgetStationNum()==0||bleRetryRequested;
  if((long)(now-reconnectAt)>=0&&!stationAttemptActive&&allowBleRetry){
   bleRetryRequested=false;
   if(connectDisplay()){bleConnectFails=0;motionFlag=false;state=STATE_IDLE;idleClockDirty=true;serviceIdleClock(true);Serial.println("READY: stationary clock; waiting for motion.");}
   else{
    cleanupBLE();if(bleConnectFails<6)bleConnectFails++;
    unsigned long wait=4000UL*bleConnectFails;reconnectAt=millis()+wait;
    Serial.printf("BLE failed (%u); retrying in %lu ms.\n",bleConnectFails,wait);
   }
  }
  delay(5);return;
 }
 if(state==STATE_COOLDOWN&&cooldownElapsed(now))state=STATE_IDLE;
 if(state==STATE_IDLE||state==STATE_COOLDOWN){
  if(shouldStartSession(now,pirHigh,manualWake))wakeDisplay();
  else serviceIdleClock();
  delay(5);return;
 }
 // Manual wake requests are also ignored while a session is already active.
 // Poll keypad in all active states; * always returns to a fresh level entry.
 if(k){
  // Ignore A/B/C/D and all keys during shutdown; motion cannot interrupt it.
  if(state==STATE_GOODBYE||state==STATE_WEEKEND){Serial.println("KEY ignored during closing/weekend message");return;}
  bool accepted=false;
  if(k=='*'){
   tone(PIN_BUZZER,1000,70);lastActivity=millis();enterLevel();return;
  }
  if(k>='0'&&k<='9'){
   // Do not let stray digits hijack a greeting or a displayed timetable.
   // Press * deliberately to enter/change a level from those states.
   if(state!=STATE_LEVEL){Serial.println("KEY digit ignored outside level entry; press * first");return;}
   if(levelInput.length()==0){
    if(k>='1'&&k<='5'){levelInput+=k;accepted=true;}
   }else if(levelInput.length()<3&&k=='0'){
    levelInput+=k;accepted=true;
   }
   if(accepted){entryDirty=true;entryChangedAt=millis();}
   else Serial.println("KEY ignored: allowed levels are 100/200/300/400/500");
  }else if(k=='#'){
   if(state!=STATE_LEVEL){Serial.println("KEY # ignored outside level entry; press * first");return;}
   selectedLevel=levelFromDigits(levelInput);entryDirty=false;
   if(selectedLevel==""){
    Serial.println("KEY # ignored: incomplete level; finish digits or press * to clear");
   }else{
    accepted=true;selectedDay=clockValid?currentDay():"";
    Serial.printf("LOOKUP level=%s day=%s RTC=%s\n",selectedLevel.c_str(),
      selectedDay.c_str(),readClock().timestamp().c_str());
    showLevel(selectedLevel,selectedDay,false);
   }
  }
  if(accepted){tone(PIN_BUZZER,1000,70);lastActivity=millis();}
 }
 // Batch digit feedback: do not block BLE uploads between rapid 1,0,0,# taps.
 if(state==STATE_LEVEL&&entryDirty&&millis()-entryChangedAt>=700){
  entryDirty=false;uploadNative("LEVEL "+levelInput+" PRESS #");
 }
 now=millis();
 serviceSessionTimers(now);

 delay(5);
}
