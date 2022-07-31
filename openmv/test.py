# Untitled - By: Administrator - 周五 7月 29 2022

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

#lcd.init()

threshold_index=0  # 0 for red, 1 for green, 2 for blue

#红绿蓝阈值设置       若不适配需重新调阈值
#thresholds = [(30, 83, 47, 127, -128, 127), # generic_red_thresholds
#              (19, 93, -128, -26, -128, 127), # generic_green_thresholds
#              (0, 100, -20, 126, -128, -40)] # generic_blue_thresholds


thresholds = [(58, 41, 52, 13, 13, -9), # generic_red_thresholds
              (43, 81, -52, -12, 20, -14), # generic_green_thresholds
               (19, 85, -128, 109, -27, -53)] # generic_blue_thresholds

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




while(True):

    clock.tick()


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
                    print("A区物料顺序为：红绿蓝")
                    print(red_block_x,green_block_x,blue_block_x)
                    #print(blob.h(),blob.w() )
                    Aorder=123
        elif int(blue_block_x)<int(green_block_x) and int(green_block_x)<int(red_block_x):
            if Aorder!=321:
                    print("A区物料顺序为：蓝绿红")
                    print(red_block_x,green_block_x,blue_block_x)
                    #print(blob.h(),blob.w() )
                    Aorder=321
        elif int(red_block_x)<int(blue_block_x) and int(blue_block_x)<int(green_block_x):
            if Arder!=132:
                    print("A区物料顺序为：红蓝绿")
                    print(red_block_x,green_block_x,blue_block_x)
                    x#print(blob.h(),blob.w() )
                    Aorder=132
        elif int(green_block_x)<int(blue_block_x) and int(blue_block_x)<int(red_block_x):
            if Aorder!=231:
                    print("A区物料顺序为：绿蓝红")
                    print(red_block_x,green_block_x,blue_block_x)
                    #print(blob.h(),blob.w() )
                    Aorder=231
        elif int(blue_block_x)<int(red_block_x) and int(red_block_x)<int(green_block_x):
            if Aorder!=312:
                    print("A区物料顺序为：蓝红绿")
                    print(red_block_x,green_block_x,blue_block_x)
                    #print(blob.h(),blob.w() )
                    Aorder=312
        elif int(green_block_x)<int(red_block_x) and int(red_block_x)<int(blue_block_x):
            if Aorder!=213:
                    print("A区物料顺序为：绿红蓝")
                    print(red_block_x,green_block_x,blue_block_x)
                    #print(blob.h(),blob.w() )
                    Aorder=213






