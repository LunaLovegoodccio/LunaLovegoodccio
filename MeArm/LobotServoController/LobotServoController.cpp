#include"LobotServoController.h"

#define GET_LOW_BYTE(A) (uint8_t)((A)) //宏函数 获得A的低八位
#define GET_HIGH_BYTE(A) (uint8_t)((A) >> 8) //宏函数 获得A的高八位
#define BYTE_TO_HW(A, B) ((((uint16_t)(A)) << 8) | (uint8_t)(B)) //宏函数 以A为高八位 B为低八位 合并为16位整形

LobotServoController::LobotServoController()
{
  //初始化运行动作组号为0xFF,运行次数为0，运行中标识为false,电池电压为0
  numOfActionRunning = 0xFF;
  actionGroupRunTimes = 0;
  isRunning = false;
  batteryVoltage = 0;
#if defined(_AVR_ATmefa32U4_)    //根据官方说明文档,除了Arduino Leonardo板(Serial1)，其余都是Serial
  SerialX = &Serial1;
#else 
  SerialX = &Serial;
#endif
}

LobotServoController::LobotServoController(HardwareSerial &A)
{
  LobotServoController();
  SerialX = &A;
}

LobotServoController::~LobotServoController()
{
}

//moveServo函数;控制单个舵机转动       //严格按照通讯协议进行编写
void LobotServoController::moveServo(uint8_t servoID, uint16_t Position, uint16_t Time)
{
  uint8_t buf[11];
  //舵机ID不能大于31,可根据对应控制板修改
  if (servoID > 31 || !(Time > 0)) {
    return;
  }
  buf[0] = FRAME_HEADER;
  buf[1] = FRAME_HEADER;
  buf[2] = 8;                      //由于为单个舵机，所以数据长度=要控制的舵机数*3+5
  buf[3] = CMD_SERVO_MOVE;         //舵机移动指令
  buf[4] = 1;                      //要控制的舵机数量
  buf[5] = GET_LOW_BYTE(Time);     //时间低八位
  buf[6] = GET_HIGH_BYTE(Time);    //时间高八位
  buf[7] = servoID;                //舵机ID
  buf[8] = GET_LOW_BYTE(Position); //位置低八位
  buf[9] = GET_HIGH_BYTE(Position);//位置高八位

  SerialX->write(buf, 10);
}  

//函数moveServos：控制多个舵机动
void LobotServoController::moveServos(LobotServo servos[], uint8_t Num, uint16_t Time)
{
  uint8_t buf[103];   //缓存数据
  if (Num < 1 || Num>32 || !(Time > 0)) {
    return;   //舵机数不能为0，且最大不超过32，时间不能为0
  }
  buf[0] = FRAME_HEADER;                    //帧头
  buf[1] = FRAME_HEADER;
  buf[2] = Num * 3 + 5;                     //数据长度
  buf[3] = CMD_SERVO_MOVE;
  buf[4] = Num;
  buf[5] = GET_LOW_BYTE(Time);
  buf[6] = GET_HIGH_BYTE(Time);
  uint8_t index = 7;
  for (uint8_t i = 0; i < Num; i++)
  {
    buf[index++] = servos[i].ID;    
    buf[index++] = GET_LOW_BYTE(servos[i].Position);  
    buf[index++] = GET_HIGH_BYTE(servos[i].Position);
  }

  SerialX->write(buf, buf[2] + 2);    //发送帧
}

//
void LobotServoController::moveServos(uint8_t Num, uint16_t Time, ...)
{
  uint8_t buf[128];
  va_list arg_ptr = NULL;
  va_start(arg_ptr, Time); //取得可变参数首地址
  if (Num < 1 || Num > 32 || (!(Time > 0)) || arg_ptr == NULL) {
    return; //舵机数不能为零和大与32，时间不能为零，可变参数不能为空
  }
  buf[0] = FRAME_HEADER;     //填充帧头
  buf[1] = FRAME_HEADER;
  buf[2] = Num * 3 + 5;      //数据长度 = 要控制舵机数 * 3 + 5
  buf[3] = CMD_SERVO_MOVE;   //舵机移动指令
  buf[4] = Num;              //要控制舵机数
  buf[5] = GET_LOW_BYTE(Time); //取得时间的低八位
  buf[6] = GET_HIGH_BYTE(Time); //取得时间的高八位
  uint8_t index = 7;
  for (uint8_t i = 0; i < Num; i++) { //从可变参数中取得并循环填充舵机ID和对应目标位置
    uint16_t tmp = va_arg(arg_ptr, uint16_t); //可参数中取得舵机ID
    buf[index++] = GET_LOW_BYTE(tmp); //貌似avrgcc中可变参数整形都是十六位
                                      //再取其低八位
    uint16_t pos = va_arg(arg_ptr, uint16_t); //可变参数中取得对应目标位置
    buf[index++] = GET_LOW_BYTE(pos); //填充目标位置低八位
    buf[index++] = GET_HIGH_BYTE(pos); //填充目标位置高八位
  }
  va_end(arg_ptr);     //置空arg_ptr
  SerialX->write(buf, buf[2] + 2); //发送帧
}

//runActionGroup函数：运行指定动作组,前提是动作已经下载至控制板
void LobotServoController::runActionGroup(uint8_t NumOfAction, uint16_t Times)
{
  uint8_t buf[7];
  buf[0] = FRAME_HEADER;
  buf[1] = FRAME_HEADER;
  buf[2] = 5;
  buf[3] = CMD_ACTION_GROUP_RUN;
  buf[4] = NumOfAction;    //运行的动作组号
  buf[5] = GET_LOW_BYTE(Times);   //运行次数
  buf[6] = GET_HIGH_BYTE(Times);

  SerialX->write(buf, 7);
}


//函数stopActionGroup：停止动作组运行
void LobotServoController::stopActionGroup(void)
{
  uint8_t buf[4];
  buf[0] = FRAME_HEADER;
  buf[1] = FRAME_HEADER;
  buf[2] = 2;
  buf[3] = CMD_ACTION_GROUP_STOP;

  SerialX->write(buf, 4);
}

//函数setActionGroupSpeed：设定指定动作组的运行速度
void LobotServoController::setActionGroupSpeed(uint8_t NumOfAction, uint8_t Speed)
{
  uint8_t buf[7];
  buf[0] = FRAME_HEADER;
  buf[1] = FRAME_HEADER;
  buf[2] = 5;
  buf[3] = CMD_ACTION_GROUP_SPEED;
  buf[4] = NumOfAction;
  buf[5] = GET_LOW_BYTE(Speed); 
  buf[6] = GET_HIGH_BYTE(Speed);

  SerialX->write(buf, 7);
}

//函数setAllActionGroupSpeed:设定所有动作组的运行速度
void LobotServoController::setAllActionGroupSpeed(uint16_t Speed)
{
  setActionGroupSpeed(0xFF, Speed);   //调用动作组速度设定，组号为0xFF时设置所有组的速度
}


//函数getBatteryVoltage：发送获取电池电压命令
void LobotServoController::getBatteryVoltage()
{
  uint8_t buf[4];
  buf[0] = FRAME_HEADER;         //填充帧头
  buf[1] = FRAME_HEADER;
  buf[2] = 2;                   //数据长度，数据帧除帧头部分数据字节数，此命令固定为2
  buf[3] = CMD_GET_BATTERY_VOLTAGE; //填充后的电池电压命令

  SerialX->write(buf, 4);        //发送数据帧
}


//函数receiveHandle:处理串口接收数据
void LobotServoController::receiveHandle()
{
  uint8_t buf[16];
  static uint8_t len = 0;
  static uint8_t getHeader = 0;
  if (!SerialX->available())
    return;   //如果没有数据则返回
  do {
    switch (getHeader){
    case 0:
      if (SerialX->read() == FRAME_HEADER) {
        getHeader = 1;
      }
      break;
    case 1:
      if (SerialX->read() == FRAME_HEADER) {
        getHeader = 2;
      }
      else {
        getHeader = 0;
      }
      break;
    case 2:
      len = SerialX->read();
      getHeader = 3;
      break;
    case 3:
      if (SerialX->readBytes(buf, len - 1) > 0) {
        getHeader = 4;
      }
      else {
        len = 0;
        getHeader = 0;
        break;
      }
    case 4:
      switch (buf[0]){
      case BATTERY_VOLTAGE:
        batteryVoltage = BYTE_TO_HW(buf[2], buf[1]);   //高低八位组合成的电池电压
        break;
      case ACTION_GROUP_RUNNING:
        numOfActionRunning = buf[1];
        actionGroupRunTimes = BYTE_TO_HW(buf[3], buf[2]); //高低八位组合成运行次数
        isRunning = true; //设置运行中标识为真
        break;
      case ACTION_GROUP_STOPPED:
        break;
      case ACTION_GROUP_COMPLETE:
        isRunning = false; 
        numOfActionRunning = 0xFF; //设置运行中动作组号为0xFF
        actionGroupRunTimes = 0; //设置运行次数为0
        break;
      default:
        break;
      }
    default:
      len = 0;
      getHeader = 0;
      break;
    }
  } while (SerialX->available());
}
