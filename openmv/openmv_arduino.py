# Untitled - By: Administrator - 周日 7月 24 2022

#物料识别+二维码识别
#openmv : 1)获取二维码的信息 物料放置顺序，并串口输出QRx_XXX/WLx_XXX
#         2)解算机械臂在原料区的抓取顺序，并串口输出  CTx_XXX(X=1,2,3)  x定义表示AB物料区


import sensor, image, time,math,lcd

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)  #320x240 不确定是否足够还需调试
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False)  #关闭自动增益
sensor.set_auto_whitebal(False) #关闭白平衡

clock = time.clock()
red_block_x=1
green_block_x=2
blue_block_x=3
message=000

lcd.init()

threshold_index=0  # 0 for red, 1 for green, 2 for blue

#红绿蓝阈值设置       若不适配需重新调阈值
thresholds = [(30, 83, 47, 127, -128, 127), # generic_red_thresholds
              (19, 93, -128, -26, -128, 127), # generic_green_thresholds
              (0, 100, -20, 126, -128, -40)] # generic_blue_thresholds

#############OpenMv数据处理##################

PP_s="123"  #物料默认顺序  先A物料区 再B物料区逆时针     （决赛增加C物料顺序）

#需要的顺序
####根据放置顺序确定动作组的顺序####
AB_order=0  #AB物料区抓取顺序

Aorder=0   #A区物料放置顺序
Border=0   #B区物料放置顺序

Pos1="000"  #A层放置位置    #视觉机械臂定位
Pos2="000"  #B层放置位置

QRcode="00"  #搬运顺序


#Index_find
#输入：QRcode|任务码  Pos|物料放置位置
#解算：QRcode在物料区的抓取顺序X_order
def Index_find(QRCode,Pos):
    result=0
    for i in range(3)
        cc=Pos.find(QRcode[i])+1
        #print(cc)
        result=result*10+cc
    return result

#Move1=Index_find(QRcode,Pos1)
#Move2=Index_find(QRcode,Pos2)


###############Uart to Arduino#####################
from pyb import UART
#串口[TX-P4,RX-p5]
uart=UART(3,9600,timeout_char=50)

#串口收发数据
recv_data=""  #串口接收的数据
QR_flag=0
WL_flag_a=0
WL_flag_b=0

#串口发送 [QR_XX WL_XX CT_XX]
#对应QR|任务码 WL|物料位置 CT|机械臂抓取顺序(依据QR&WL计算)

def Uart_recv():  # 串口接收数据
    global QR_flag
    global WL_flag

    if(uart.any()):
       recv_data=eval(str.read())

       print(recv_data)

       if("CM+" in recv_data):    #根据串口发来的消息执行任务
          print("Openmv has recive CMD data")
          if("+QR" in recv_data):
             QR_flag=1
             print("Ready for QRcode task!")

          if("+WL" in recv_data):
             WL_flag=1
             print("Ready for WLpose task!")





#主函数
while(True):
    clock.tick()
    img = sensor.snapshot()

    Uart_recv()   #接收来自串口的数据(arduino)

    if(QR_flag):  #QR_flag
        # 1）进行二维码识别 放置相关函数
        #print("Start QRcode task !")

        img.lens_corr(1.8) # 1.8的强度适配于2.8mm的镜头
        #设置补光扩展版相关数值  控制亮度 0~100
        #开灯
#       light=Timer(2,freq=50000).channel(1,Timer.PWM,pin=Pin("P6"))
#       light.pulse_width_percent(10)

        #QRcode解码
        #qrcode.payload()返回二维码有效载荷的字符串，例如URL 。
        for code in img.find_qrcodes():
         #  img.draw_rectangle(code.rect(),color=(255,0,0))  #将二维码用红框框起来
            print(code.payload())
            if message!=code.payload():   #判断摄像头是否成功读取到二维码的数据/若二维码读取不为空则执行下列语句
                #message=code.payload()
                #print("The order is:%s" %( message))   #检测点
                String=list(str(code.payload()))
                AB_order=String[0]+String[1]   #AB区抓取颜色顺序相同

                #成功识别后，进行数据处理/串口发送数据
                uart.write("QR_"+AB_order+"\r\n")
                time.sleep(50)  #延时50ms 以防占用串口
                print("QR_"+AB_order)  #检测点

                #复位
                QR_flag = 0
                print("QRcode task done!")

        img.draw_string(0,0,str(above_order)+"\r+\r"+str(bottom_order),color=(255,0,0),scale = 7,x_spacing=-16,y_spacing=-21)
        light.pulse_width_percent(0) # 关灯

    if(WL_flag_a):     # 识别A区物料    WL_flag_a

        clock.tick()
        light = Timer(2, freq=50000).channel(1, Timer.PWM, pin=Pin("P6"))  #开灯
        light.pulse_width_percent(100)

        img = sensor.snapshot()

        #红色   #roi根据实际情况调整
        #area_threshold 面积阈值，如果色块被框起来的面积小于这个值，会被过滤掉
        #pixels_threshold 像素个数阈值，如果色块像素数量小于这个值，会被过滤掉
        for r in img.find_blobs([thresholds[0]],roi=[0,140,320,100],pixels_threshold=200,area_threshold=200,merge=True):
            img.draw_rectangle(r.rect())
            img.draw_cross(r.cx(), r.cy())  #在色块中心画十字
            img.draw_keypoints([(r.cx(), r.cy(), int(math.degrees(r.rotation())))], size=20) #绘制特征点
            red_block_x=r.cx()

        #绿色
        for g in img.find_blobs([thresholds[1]],roi=[0,140,320,100],pixels_threshold=200,area_threshold=200,merge=True):
            img.draw_rectangle(g.rect())
            img.draw_cross(g.cx(), g.cy())  #在色块中心画十字
            img.draw_keypoints([(g.cx(), g.cy(), int(math.degrees(g.rotation())))], size=20) #绘制特征点
            green_block_x=g.cx()

        #蓝色
        for b in img.find_blobs([thresholds[2]],roi=[0,140,320,100],pixels_threshold=200,area_threshold=200,merge=True):
            img.draw_rectangle(b.rect())
            img.draw_cross(b.cx(), b.cy())  #在色块中心画十字
            img.draw_keypoints([(b.cx(), b.cy(), int(math.degrees(b.rotation())))], size=20) #绘制特征点
            blue_block_x=b.cx()


            if int(red_block_x)<int(green_block_x) and int(green_block_x)<int(blue_block_x):
                if Aorder!=123:
                        #print("A区物料顺序为：红绿蓝")
                        #print(red_block_x,green_block_x,blue_block_x)
                        #print(blob.h(),blob.w() )
                        Aorder=123
            elif int(blue_block_x)<int(green_block_x) and int(green_block_x)<int(red_block_x):
                if Aorder!=321:
                        #print("A区物料顺序为：蓝绿红")
                        #print(red_block_x,green_block_x,blue_block_x)
                        #print(blob.h(),blob.w() )
                        Aorder=321
            elif int(red_block_x)<int(blue_block_x) and int(blue_block_x)<int(green_block_x):
                if Arder!=132:
                        #print("A区物料顺序为：红蓝绿")
                        #print(red_block_x,green_block_x,blue_block_x)
                        #print(blob.h(),blob.w() )
                        Aorder=132
            elif int(green_block_x)<int(blue_block_x) and int(blue_block_x)<int(red_block_x):
                if Aorder!=231:
                        #print("A区物料顺序为：绿蓝红")
                        # print(red_block_x,green_block_x,blue_block_x)
                        #print(blob.h(),blob.w() )
                        Aorder=231
            elif int(blue_block_x)<int(red_block_x) and int(red_block_x)<int(green_block_x):
                if Aorder!=312:
                        #print("A区物料顺序为：蓝红绿")
                        #print(red_block_x,green_block_x,blue_block_x)
                        #print(blob.h(),blob.w() )
                        Aorder=312
            elif int(green_block_x)<int(red_block_x) and int(red_block_x)<int(blue_block_x):
                if Aorder!=213:
                        #print("A区物料顺序为：绿红蓝")
                        #print(red_block_x,green_block_x,blue_block_x)
                        #print(blob.h(),blob.w() )
                        Aorder=213



    if(WL_flag_b):     # 识别B区物料    WL_flag_b

        clock.tick()
        light = Timer(2, freq=50000).channel(1, Timer.PWM, pin=Pin("P6"))  #开灯
        light.pulse_width_percent(100)

        img = sensor.snapshot()

        #红色   #roi根据实际情况调整
        #area_threshold 面积阈值，如果色块被框起来的面积小于这个值，会被过滤掉
        #pixels_threshold 像素个数阈值，如果色块像素数量小于这个值，会被过滤掉
        for r in img.find_blobs([thresholds[0]],roi=[0,140,320,100],pixels_threshold=200,area_threshold=200,merge=True):
            img.draw_rectangle(r.rect())
            img.draw_cross(r.cx(), r.cy())  #在色块中心画十字
            img.draw_keypoints([(r.cx(), r.cy(), int(math.degrees(r.rotation())))], size=20) #绘制特征点
            red_block_x=r.cx()

        #绿色
        for g in img.find_blobs([thresholds[1]],roi=[0,140,320,100],pixels_threshold=200,area_threshold=200,merge=True):
            img.draw_rectangle(g.rect())
            img.draw_cross(g.cx(), g.cy())  #在色块中心画十字
            img.draw_keypoints([(g.cx(), g.cy(), int(math.degrees(g.rotation())))], size=20) #绘制特征点
            green_block_x=g.cx()

        #蓝色
        for b in img.find_blobs([thresholds[2]],roi=[0,140,320,100],pixels_threshold=200,area_threshold=200,merge=True):
            img.draw_rectangle(b.rect())
            img.draw_cross(b.cx(), b.cy())  #在色块中心画十字
            img.draw_keypoints([(b.cx(), b.cy(), int(math.degrees(b.rotation())))], size=20) #绘制特征点
            blue_block_x=b.cx()


            if int(red_block_x)<int(green_block_x) and int(green_block_x)<int(blue_block_x):
                if Border!=123:
                        #print("B区物料顺序为：红绿蓝")
                        #print(red_block_x,green_block_x,blue_block_x)
                        #print(blob.h(),blob.w() )
                        Border=123
            elif int(blue_block_x)<int(green_block_x) and int(green_block_x)<int(red_block_x):
                if Border!=321:
                        #print("B区物料顺序为：蓝绿红")
                        #print(red_block_x,green_block_x,blue_block_x)
                        #print(blob.h(),blob.w() )
                        Border=321
            elif int(red_block_x)<int(blue_block_x) and int(blue_block_x)<int(green_block_x):
                if Border!=132:
                        #print("B区物料顺序为：红蓝绿")
                        #print(red_block_x,green_block_x,blue_block_x)
                        #print(blob.h(),blob.w() )
                        Border=132
            elif int(green_block_x)<int(blue_block_x) and int(blue_block_x)<int(red_block_x):
                if Border!=231:
                        #print("B区物料顺序为：绿蓝红")
                        # print(red_block_x,green_block_x,blue_block_x)
                        #print(blob.h(),blob.w() )
                        Aorder=231
            elif int(blue_block_x)<int(red_block_x) and int(red_block_x)<int(green_block_x):
                if Border!=312:
                        #print("B区物料顺序为：蓝红绿")
                        #print(red_block_x,green_block_x,blue_block_x)
                        #print(blob.h(),blob.w() )
                        Aorder=312
            elif int(green_block_x)<int(red_block_x) and int(red_block_x)<int(blue_block_x):
                if Border!=213:
                        #print("B区物料顺序为：绿红蓝")
                        #print(red_block_x,green_block_x,blue_block_x)
                        #print(blob.h(),blob.w() )
                        Border=213

        print("%dand%d"%(int(Aorder),int(Border)))
        if int(Aorder)!=0 and int(Border)!=0
            print("OK")

            Pos1=str(Aorder)
            Pos2=str(Border)
            Move1=Index_find(QRcode,Pos1)
            Move2=Index_find(QRcode,Pos2)

            #物料识别成功后，处理数据并发送
            print("WL_"+Pos1+Pos2)
            #方案一
            uart.write("WL_"+Pos1+Pos2+"\r\n")   #向串口发送物料位置的消息
            #方案二
            uart.write("CT+"+Move1+Move2+"\r\n")
            WL_flag_a=0
            WL_flag_b=0    #颜色识别结束
            light.pulse_width_percent(0)

