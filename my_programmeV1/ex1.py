# -*- coding: utf-8 -*-
#!/usr/bin/env python

#实现检测场景内是否有物体移动，并进行人脸检测抓拍
import cv2
import time

# 行人检测的部分
save_path = './pedestrian/'
cascade = cv2.CascadeClassifier('MyPedestrian.xml')


camera = cv2.VideoCapture('2.MP4') # 调用视频
# camera = cv2.VideoCapture(0) # 参数0表示第一个摄像头

# 判断视频是否打开
if (camera.isOpened()):
    print('Open')
else:
    print('摄像头未打开')

# 测试用,查看视频size
# size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
#         int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
# print('size:'+repr(size))

fps = 15  # 帧率
pre_frame = None  # 总是取视频流前一帧做为背景相对下一帧进行比较
i = 0
while True:
    start = time.time()
    grabbed, frame_lwpCV = camera.read() # 读取视频流
    gray_lwpCV = cv2.cvtColor(frame_lwpCV, cv2.COLOR_BGR2GRAY) # 转灰度图

    if not grabbed:
        break
    end = time.time()



    #行人检测部分
    features = cascade.detectMultiScale(gray_lwpCV, scaleFactor=1.1, minNeighbors=15, minSize=(26, 74),maxSize=(70, 174))

    for (x, y, w, h) in features:
        cv2.rectangle(frame_lwpCV, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray_lwpCV = gray_lwpCV[y:y + h, x:x + w]
        
        cv2.imwrite(save_path + str(i) + '.jpg', frame_lwpCV[y:y + h, x:x + w])
        i += 1

    cv2.imshow('lwpCVWindow', frame_lwpCV)


    # 运动检测部分
    seconds = end - start
    if seconds < 1.0 / fps:
        time.sleep(1.0 / fps - seconds)
    gray_lwpCV = cv2.resize(gray_lwpCV, (500, 500))
    # 用高斯滤波进行模糊处理，进行处理的原因：每个输入的视频都会因自然震动、光照变化或者摄像头本身等原因而产生噪声。对噪声进行平滑是为了避免在运动和跟踪时将其检测出来。
    gray_lwpCV = cv2.GaussianBlur(gray_lwpCV, (21, 21), 0)

    # 在完成对帧的灰度转换和平滑后，就可计算与背景帧的差异，并得到一个差分图（different map）。还需要应用阈值来得到一幅黑白图像，并通过下面代码来膨胀（dilate）图像，从而对孔（hole）和缺陷（imperfection）进行归一化处理
    if pre_frame is None:
        pre_frame = gray_lwpCV
    else:
        img_delta = cv2.absdiff(pre_frame, gray_lwpCV)
        thresh = cv2.threshold(img_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            if cv2.contourArea(c) < 1000: # 设置敏感度
                continue
            else:
                print("咦,有什么东西在动0.0")
                break
        pre_frame = gray_lwpCV
    key = cv2.waitKey(1) & 0xFF
    # 按'q'健退出循环
    if key == ord('q'):
        break
# When everything done, release the capture
camera.release()
cv2.destroyAllWindows()
