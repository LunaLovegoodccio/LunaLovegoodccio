#ifndef LOBOTSERVOCONTROLLER_H
#define LOBOTSERVOCONTROLLER_H

#include<Arduino.h>

//发送指令部分
#define  FRAME_HEADER              0x55     //帧头
#define  CMD_SERVO_MOVE            0x03     //舵机移动指令
#define  CMD_ACTION_GROUP_RUN      0x06     //动作组运行指令
#define  CMD_ACTION_GROUP_STOP     0x07     //动作组停止指令
#define  CMD_ACTION_GROUP_SPEED    0x0B     //动作组速度指令
#define  CMD_GET_BATTERY_VOLTAGE   0x0F     //获取控制板电池电压
#define  CMD_MULT_SERVO_UNLOAD     0x14     //控制多个舵机马达掉电卸力
#define  CMD_MULT_SERVO_POS_READ   0x15     //读取多个舵机的角度位置值

//控制板主动给用户发送数据部分
#define  BATTERY_VOLTAGE           0x0F     //电池电压
#define  ACTION_GROUP_RUNNING      0x06     //动作组被运行
#define  ACTION_GROUP_STOPPED      0x07     //动作组被停止
#define  ACTION_GROUP_COMPLETE     0x08     //动作组完成

//舵机ID和位置结构体
struct LobotServo {
  uint8_t   ID;
  uint16_t  Position;      
};


class LobotServoController {
public:
  LobotServoController();          //构造函数自动调用且只调用一次，可以发生重载   //无参构造
  LobotServoController(HardwareSerial &A);     //有参构造函数
  ~LobotServoController();         //析构函数的调用，在程序销毁前调用

  void moveServo(uint8_t servoID, uint16_t Position, uint16_t Time);
  void moveServos(LobotServo servos[], uint8_t Num, uint16_t Time);   //控制多个舵机转动
  void moveServos(uint8_t Num, uint16_t Time, ...);
  void runActionGroup(uint8_t NumOfAction, uint16_t Times);
  void stopActionGroup(void);
  void setActionGroupSpeed(uint8_t NumOfAction, uint8_t Speed);
  void setAllActionGroupSpeed(uint16_t Speed);

  void getBatteryVoltage();
  void receiveHandle(void);


public:
  uint8_t numOfActionRunning;   //正在运行的动作组序号
  uint16_t actionGroupRunTimes;  //正在运行的动作组的次数
  bool isRunning;  //有动作组正在运行?
  uint16_t batteryVoltage; //控制板的电池电压

  HardwareSerial *SerialX;

};

#endif
