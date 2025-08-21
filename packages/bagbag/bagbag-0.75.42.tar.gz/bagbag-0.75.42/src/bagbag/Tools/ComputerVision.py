from __future__ import annotations

import numpy as np
import cv2
import types
import typing
import time
import os
import copy
import flask

from ..Thread import Thread
from .. import Time
from .Ratelimit_src import RateLimit
from .. import Socket
from ..String import String
from .. import Lg
from .. import Base64
from .. import Http
from .. import Json
from .. import Random

#print("load " + '/'.join(__file__.split('/')[-2:]))

here = os.path.dirname(os.path.abspath(__file__))

netssd = None 
classesssd = ["background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"]
colorsssd = np.random.uniform(0, 255, size=(len(classesssd), 3))

netyolo = None 
classesyolo = []
colorsyolo = []

colorsapiserver = {}

class cvStreamFrameObjectDetectionResult():
    def __init__(self, detections, objectDetectModel, frame) -> None:
        self.detections = detections
        self.objectDetectModel = objectDetectModel
        self.frame = frame 

        if self.objectDetectModel == "YOLO":
            self.prepareYOLO()

    def drawBySSD(self, frame:cvStreamFrame, filterAbove:int=0, filterName:list=[]) -> cvStreamFrame:
        """
        > Draws a rectangle around each object detected by the SSD model, and displays the object's name
        and confidence level
        
        :param frame: the frame to draw on
        :type frame: cvStreamFrame
        :param filterAbove: Filter out detections with confidence below this value, defaults to 0. 百分比, 100为完全匹配.
        :type filterAbove: int (optional)
        :param filterName: list of strings, names of objects to filter out
        :type filterName: list
        :return: A frame with the detections drawn on it.
        """
        frame = copy.deepcopy(frame)
        (H, W) = frame.frame.shape[:2]

        for i in np.arange(0, self.detections.shape[2]):
            # extract the confidence (i.e., probability) associated
            # with the prediction
            confidence = self.detections[0, 0, i, 2]
            # filter out weak detections by ensuring the `confidence`
            # is greater than the minimum confidence
            if confidence > filterAbove / 100:
                # extract the index of the class label from the
                # detections list
                idx = int(self.detections[0, 0, i, 1])
                name = classesssd[idx]
                if name in filterName:
                    continue 
                # if the class label is not a car, ignore it
                # if classesssd[idx] != "car":
                #     continue
                # compute the (x, y)-coordinates of the bounding box
                # for the object
                box = self.detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                (startX, startY, endX, endY) = box.astype("int")
                
                cv2.rectangle(
                    frame.frame, 
                    (startX, startY), 
                    (endX, endY), 
                    (0, 255, 0), 1)

                cv2.putText(frame.frame, '%s: %.2f%%' % (name, confidence*100),
                        (startX+25, startY+30),
                        cv2.FONT_HERSHEY_DUPLEX,
                        1, (0, 255, 0), 1) 
        
        return frame
    
    def prepareYOLO(self):
        self.class_ids = []
        self.confidences = []
        self.boxes = []
        conf_threshold = 0.5
        nms_threshold = 0.4

        Width = self.frame.shape[1]
        Height = self.frame.shape[0]

        for out in self.detections:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                self.class_ids.append(class_id)
                self.confidences.append(float(confidence))
                self.boxes.append([x, y, w, h])
        
        self.indices = cv2.dnn.NMSBoxes(self.boxes, self.confidences, conf_threshold, nms_threshold)

    def drawByYOLO(self, frame:cvStreamFrame, filterAbove:int=0, filterName:list=[]) -> cvStreamFrame:
        frame = copy.deepcopy(frame)

        for i in self.indices:
            try:
                box = self.boxes[i]
            except:
                i = i[0]
                box = self.boxes[i]
            
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]

            label = str(classesyolo[self.class_ids[i]])
            color = colorsyolo[self.class_ids[i]]
            confidence = self.confidences[i]
            cv2.rectangle(frame.frame, (round(x), round(y)), (round(x+w), round(y+h)), color, 1)
            # print('%s: %.2f%%' % (label, confidence*100))
            # print(x+25, y+30)
            cv2.putText(frame.frame, '%s: %.2f%%' % (label, confidence*100),
                        (round(x)+5, round(y)+15),
                        cv2.FONT_HERSHEY_DUPLEX,
                        0.5, color, 0.5) 
    
        return frame 

    def drawByAPIServer(self, frame:cvStreamFrame, filterAbove:int=0, filterName:list=[]) -> cvStreamFrame:
        frame = copy.deepcopy(frame)

        global colorsapiserver

        for i in self.detections:
            if i["name"] not in colorsapiserver:
                colorsapiserver[i["name"]] = (Random.Int(0, 256), Random.Int(0, 256), Random.Int(0, 256))

            cv2.rectangle(
                frame.frame, 
                (i['coordinate'][0][0], i['coordinate'][0][1]), 
                (i['coordinate'][1][0], i['coordinate'][1][1]), 
                (0, 255, 0), 1)

            cv2.putText(frame.frame, '%s: %.2f%%' % (i['name'], i['confidence']*100),
                    (i['coordinate'][0][0]+25, i['coordinate'][0][1]+30),
                    cv2.FONT_HERSHEY_DUPLEX,
                    1, (0, 255, 0), 1) 
        
        return frame

    def Draw(self, frame:cvStreamFrame, filterAbove:int=0, filterName:list=[]) -> cvStreamFrame:
        if self.objectDetectModel == "SSD":
            return self.drawBySSD(frame, filterAbove, filterName)
        elif self.objectDetectModel == "YOLO":
            return self.drawByYOLO(frame, filterAbove, filterName)  
        elif self.objectDetectModel.startswith("APIServer"):
            return self.drawByAPIServer(frame, filterAbove, filterName)  

    def Objects(self) -> dict:
        resp = {}

        if self.objectDetectModel == "SSD":
            for i in np.arange(0, self.detections.shape[2]):
                confidence = self.detections[0, 0, i, 2]
                idx = int(self.detections[0, 0, i, 1])
                name = classesssd[idx]
                resp[name] = confidence
        elif self.objectDetectModel == "YOLO":
            for i in self.indices:
                name = str(classesyolo[self.class_ids[i]])
                confidence = self.confidences[i]
                resp[name] = confidence
        elif self.objectDetectModel.startswith("APIServer"):
             for i in self.detections:
                resp[i['name']] = i['confidence']
        else:
            raise Exception("需要先加载模型: SetSSDModelForObjectDetect or SetYoloModelForObjectDetect or SetAPIServerForObjectDetect")
        
        return resp

class cvStreamFrameDifference():
    def __init__(self, cnts) -> None:
        self.cnts = cnts

    def Draw(self, frame:cvStreamFrame) -> cvStreamFrame:
        frame = copy.deepcopy(frame)
        for c in self.cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame.frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
        
        return frame

    def HasDifference(self) -> bool:
        return len(self.cnts) != 0

class cvStreamFrame():
    def __init__(self, frame, objectDetectModel) -> None:
        self.frame = frame
        self.grayFrame = None 
        self.objectDetectModel = objectDetectModel
        self.createTime = Time.Now()

    def __grayFrame(self):
        # print(type(self.grayFrame))
        if type(self.grayFrame) == types.NoneType:
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            self.grayFrame = cv2.GaussianBlur(gray, (21, 21), 0)
        
        return self.grayFrame
    
    def objectsBySSD(self) -> cvStreamFrameObjectDetectionResult:
        # convert the frame to a blob and pass the blob through the
        # network and obtain the detections
        blob = cv2.dnn.blobFromImage(self.frame, size=(600, 600), ddepth=cv2.CV_8U)
        netssd.setInput(blob, scalefactor=1.0/127.5, mean=[127.5, 127.5, 127.5])
        detections = netssd.forward()

        return cvStreamFrameObjectDetectionResult(detections, self.objectDetectModel, self.frame)

    def objectsByYOLO(self) -> cvStreamFrameObjectDetectionResult:
        scale = 0.00392

        blob = cv2.dnn.blobFromImage(self.frame, scale, (416,416), (0,0,0), True, crop=False)

        netyolo.setInput(blob)

        layer_names = netyolo.getLayerNames()
        try:
            output_layers = [layer_names[i - 1] for i in netyolo.getUnconnectedOutLayers()]
        except:
            output_layers = [layer_names[i[0] - 1] for i in netyolo.getUnconnectedOutLayers()]


        detections = netyolo.forward(output_layers)

        return cvStreamFrameObjectDetectionResult(detections, self.objectDetectModel, self.frame)

    def objectsByAPIServer(self) -> cvStreamFrameObjectDetectionResult:
        (flag, encodedImage) = cv2.imencode(".jpg", self.frame)
        encodedImage = bytearray(encodedImage)
        encodedImage = Base64.Encode(encodedImage)

        a = self.objectDetectModel.split("|")
        server = a[1]
        model = a[2]

        if not server.startswith("http://") and not server.startswith("https://"):
            server = "https://" + server 

        while True:
            try:
                resp = Http.PostJson(server + "/object-detect", {
                    "model": model,
                    "data": encodedImage,
                }, timeout=60)
                break
            except Exception as e:
                Lg.Warn("调用API服务器识别失败:", e)
                Time.Sleep(5)
                pass 

            if resp.StatusCode > 500:
                Lg.Warn("调用API服务器识别失败: " + str(resp.StatusCode))
                Time.Sleep(1)
                Lg.Trace("重试")
            elif resp.StatusCode == 500:
                raise Exception("调用API服务器识别失败: " + str(resp.StatusCode))
            else:
                break 
        
        res = Json.Loads(resp.Content)
        if res['code'] != 200:
            raise Exception("调用API服务器识别失败:" + res['message'])

        return cvStreamFrameObjectDetectionResult(res['result'], self.objectDetectModel, self.frame)

    def Objects(self, objectDetectModel:str=None) -> cvStreamFrameObjectDetectionResult:
        if objectDetectModel == None:
            if self.objectDetectModel == "SSD":
                return self.objectsBySSD()
            elif self.objectDetectModel == "YOLO":
                return self.objectsByYOLO()
            elif self.objectDetectModel.startswith("APIServer"):
                return self.objectsByAPIServer()
            else:
                raise Exception("需要先加载模型: SetSSDModelForObjectDetect or SetYoloModelForObjectDetect or SetAPIServerForObjectDetect")
        
        else:
            if objectDetectModel == "SSD":
                return self.objectsBySSD()
            elif objectDetectModel == "YOLO":
                return self.objectsByYOLO()
            elif objectDetectModel.startswith("APIServer"):
                return self.objectsByAPIServer()
            else:
                raise Exception("需要先加载模型: SetSSDModelForObjectDetect or SetYoloModelForObjectDetect or SetAPIServerForObjectDetect")
        

    def Compare(self, frame:cvStreamFrame, size:int=250) -> cvStreamFrameDifference:
        # Compare the difference between current frame and the background frame 
        frameDelta = cv2.absdiff(self.__grayFrame(), frame.__grayFrame())
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # Expand the threshold image to fill the hole, and then find the contour on the threshold image
        thresh = cv2.dilate(thresh, None, iterations=2)
        (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        
        ccnts = []
        for c in cnts:
            if cv2.contourArea(c) < size:
                continue
            ccnts.append(c)
        
        return cvStreamFrameDifference(cnts)

    def Show(self, title:str="", wait:bool=False):
        cv2.imshow(title, self.frame) 
        if wait == True:
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def Save(self, path:str):
        try:
            cv2.imwrite(path, self.frame)
        except Exception as e:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
                cv2.imwrite(path, self.frame)
            else:
                raise e

    def Resize(self, precent:float) -> cvStreamFrame:
        """
        转换图片/帧的大小, precent为百分比. 大于100为放大, 小于100为缩小. 
        
        :param precent: The percentage of the original size you want to resize the image to
        :type precent: int
        :return: A cvStreamFrame object
        """
        precent = precent / 100
        frame = cv2.resize(self.frame, (0, 0), fx=precent, fy=precent)
        return cvStreamFrame(frame, self.objectDetectModel)

    def Bright(self, times:int=None) -> cvStreamFrame:
        """
        > It takes an image and a number, and returns a brighter version of the image
        
        :param times: How many times to brighter
        :type times: int
        :return: A cvStreamFrame object.
        """
        # print("times:", times)
        if times == None:
            if self.Brightness() != "dark":
                return self 
            
            brightcount = 2
            while True:
                # print(brightcount)
                frame = copy.deepcopy(self)
                frame = frame.Bright(brightcount)
                if frame.Brightness() != "dark":
                    return frame
                
                brightcount += 1
        else:
            if times == 1:
                return self
            
            img2 = cv2.add(self.frame, self.frame)
            if times == 2:
                return cvStreamFrame(img2, self.objectDetectModel) 
            else:
                for _ in range(2, times):
                    # print("add", _)
                    img2 = cv2.add(img2, self.frame)

                    # cvStreamFrame(img2).Show(wait=True)
            
                return cvStreamFrame(img2, self.objectDetectModel)
    
    def BrightCheck(self) -> int:
        if self.Brightness() != "dark":
            return 1
            
        brightcount = 2
        while True:
            # print(brightcount)
            frame = copy.deepcopy(self)
            frame = frame.Bright(brightcount)
            if frame.Brightness() != "dark":
                return brightcount
            
            brightcount += 1
        
    def Brightness(self) -> str:
        # 把图片转换为单通道的灰度图
        gray_img = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        
        # 获取形状以及长宽
        img_shape = gray_img.shape
        height, width = img_shape[0], img_shape[1]
        size = gray_img.size
        # 灰度图的直方图
        hist = cv2.calcHist([gray_img], [0], None, [256], [0, 256])
        
        # 计算灰度图像素点偏离均值(128)程序
        ma = 0
        reduce_matrix = np.full((height, width), 128)
        shift_value = gray_img - reduce_matrix
        shift_sum = sum(map(sum, shift_value))

        da = shift_sum / size
        # 计算偏离128的平均偏差
        for i in range(256):
            ma += (abs(i-128-da) * hist[i])
        m = abs(ma / size)
        # 亮度系数
        k = abs(da) / m
        # print(k, da)
        if k[0] > 1:
            # 过亮
            if da > 0:
                # print("过亮")
                return 'light'
            else:
                # print("过暗")
                return 'dark'
        else:
            # print("亮度正常")
            return 'normal'

    def Rotate(self, side:int) -> cvStreamFrame:
        """
        旋转或者镜像

        :param side: 0, 1, -1分别为逆时针旋转90度, 180度, 左右镜像
        :type side: int
        :return: A cvStreamFrame object
        """
        frame = cv2.flip(cv2.transpose(self.frame), side)
        return cvStreamFrame(frame, self.objectDetectModel)

    def Text(self, text:str, x:int=10, y:int=-10) -> cvStreamFrame:
        if x < 0:
            x = self.frame.shape[1] + x
        if y < 0:
            y = self.frame.shape[0] + y
        cv2.putText(self.frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        return self
    
    def Size(self) -> typing.Tuple[int, int]:
        """
        宽和高, w and h
        """
        return self.frame.shape[0], self.frame.shape[1]

class StreamSync():
    def __init__(self, source:int|str) -> None:
        """
        source可以是数字, 0, 1, 2, 表示摄像头的编号. 可以是本地视频文件的路径. 可以是远程摄像头的http地址.
        
        :param source: The source of the video. 
        :type source: int|str
        """
        self.source = source
        self.stream = cv2.VideoCapture(source)
    
        self.objectDetectModel = None 

        self.fpss = []
        self.frameCountSec = 0
        self.lastTimeForCaclFPS = None

        self.FPS = 0
        self.FPSAverage = 0

    def SetSSDModelForObjectDetect(self, prototxt:str="MobileNetSSD_deploy.prototxt.txt", caffemodel:str="MobileNetSSD_deploy.caffemodel"):
        self.objectDetectModel = "SSD"
        global netssd

        netssd = cv2.dnn.readNetFromCaffe(
            prototxt, 
            caffemodel,
        )

    def SetYoloModelForObjectDetect(self, weights:str="yolov4.weights", config:str="yolov4.cfg", classes:str="yolov4.txt"):
        self.objectDetectModel = "YOLO"
        global classesyolo
        global colorsyolo
        global netyolo

        if netyolo == None:
            with open(classes, 'r') as f:
                classesyolo = [line.strip() for line in f.readlines()]

            colorsyolo = np.random.uniform(0, 255, size=(len(classesyolo), 3))

            netyolo = cv2.dnn.readNet(weights, config)
    
    def SetAPIServerForObjectDetect(self, server:str, model:str="yolo"):
        self.objectDetectModel = f"APIServer|{server}|{model}"

    def Close(self):
        try:
            self.stream.release()
        except:
            pass 
        try:
            cv2.destroyAllWindows()
        except:
            pass
    
    def Get(self) -> cvStreamFrame:
        (grabbed, frame) = self.stream.read()

        if not grabbed:
            return 
        
        self.frameCountSec += 1
        
        if self.frameCountSec != 0 and (self.lastTimeForCaclFPS == None or Time.Now() - self.lastTimeForCaclFPS >= 1):
            self.FPS = self.frameCountSec

            self.fpss.append(self.frameCountSec)

            while len(self.fpss) > 180:
                self.fpss.pop(0)

            self.FPSAverage = int(sum(self.fpss)/len(self.fpss))
            
            self.lastTimeForCaclFPS = Time.Now()
            self.frameCountSec = 0
        
        return cvStreamFrame(frame, self.objectDetectModel)

    def __iter__(self) -> typing.Iterator[cvStreamFrame]:
        while True:
            (grabbed, frame) = self.stream.read()

            if not grabbed:
                self.Close()
                return 
            
            self.frameCountSec += 1
        
            if self.frameCountSec != 0 and (self.lastTimeForCaclFPS == None or Time.Now() - self.lastTimeForCaclFPS >= 1):
                self.FPS = self.frameCountSec

                self.fpss.append(self.frameCountSec)

                while len(self.fpss) > 180:
                    self.fpss.pop(0)

                self.FPSAverage = int(sum(self.fpss)/len(self.fpss))
                
                self.lastTimeForCaclFPS = Time.Now()
                self.frameCountSec = 0

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

            yield cvStreamFrame(frame, self.objectDetectModel)
            
    def __enter__(self):
        return self 
    
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.Close()
        except:
            pass

class StreamAsync():
    def __init__(self, source:int|str) -> None:
        """
        source可以是数字, 0, 1, 2, 表示摄像头的编号. 可以是远程摄像头的http地址.
        
        :param source: The source of the video. 
        :type source: int|str
        """
        self.source = source

        self.closed = False

        self.lastFrameUpdateTime = None
        self.lastFrame = None 

        self.lastGetFrameTime = None 

        self.lastTimeForCaclFPS = None
        self.frameCountSec = 0
        self.fpss = []

        self.FPS = None
        self.FPSAverage = None
        self.webVideoFeedLastGet = {} 

        self.FPSRead = None 

        self.objectDetectModel = "SSD"

        Thread(self.run)

        # print(0)
        while self.lastFrameUpdateTime == None:
            Time.Sleep(0.1)

        # print(2)
        while self.FPS == None:
            self.Get()
    
    def SetSSDModelForObjectDetect(self, prototxt:str="MobileNetSSD_deploy.prototxt.txt", caffemodel:str="MobileNetSSD_deploy.caffemodel"):
        self.objectDetectModel = "SSD"
        global netssd

        netssd = cv2.dnn.readNetFromCaffe(
            prototxt, 
            caffemodel,
        )

    def SetYoloModelForObjectDetect(self, weights:str="yolov4.weights", config:str="yolov4.cfg", classes:str="yolov4.txt"):
        self.objectDetectModel = "YOLO"
        global classesyolo
        global colorsyolo
        global netyolo

        if netyolo == None:
            with open(classes, 'r') as f:
                classesyolo = [line.strip() for line in f.readlines()]

            colorsyolo = np.random.uniform(0, 255, size=(len(classesyolo), 3))

            netyolo = cv2.dnn.readNet(weights, config)
    
    def SetAPIServerForObjectDetect(self, server:str, model:str="yolo"):
        self.objectDetectModel = f"APIServer|{server}|{model}"
        
    def Close(self, destroyAllWindows:bool=True):
        self.closed = True
        try:
            if self.stype == "c":
                Lg.Trace("关闭stream")
                self.stream.release()
            elif self.stype == "n":
                Lg.Trace("关闭socket")
                self.stream.Close()
        except Exception as e:
            Lg.Trace("关闭有异常:", e)
            pass 
    
        if destroyAllWindows:
            try:
                Lg.Trace("销毁所有窗口")
                cv2.destroyAllWindows()
            except Exception as e:
                Lg.Trace("销毁有异常:", e)
                pass
        Lg.Trace("关闭完成")

    def openStream(self):
        if type(self.source) == str and self.source.startswith("socket://"):
            Lg.Trace("打开网络接口")
            self.stype = "n"
            _ = String(self.source).RegexFind("socket://(.+?):(.+)")
            # print(_[0])
            self.stream = Socket.TCP.Connect(_[0][1], int(_[0][2])).PacketConnection()
        else:
            self.stream = cv2.VideoCapture(self.source)
            self.stype = "c"
        Lg.Trace("开启stream完成, 模式:", self.stype)

    def run(self):
        self.openStream()

        frameCountSec = 0
        lastSec = Time.Now()
        while True:
            if self.stype == "c":
                (grabbed, frame) = self.stream.read()

                if not grabbed:
                    Lg.Trace("没有抓到帧")
                    try:
                        Lg.Trace("关闭stream")
                        self.stream.release()
                    except Exception as e:
                        Lg.Trace("关闭有异常:", e)
                        pass 
                    time.sleep(1)
                    Lg.Trace("重新尝试")
                    self.openStream()
                    time.sleep(1)
                    continue 
                
            elif self.stype == "n":
                # print(2)
                try:
                    self.stream.Send("d")
                    imgdata = self.stream.Recv()
                except Exception as e:
                    Lg.Trace("从socket抓帧报错了:", e)
                    try:
                        Lg.Trace("关闭socket")
                        self.stream.Close()
                    except Exception as e:
                        Lg.Trace("关闭有异常:", e)
                        pass 
                    time.sleep(1)
                    Lg.Trace("重新尝试")
                    self.openStream()
                    time.sleep(1)
                    continue 
                
                nparr = np.fromstring(imgdata, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                # print(3)
            
            frameCountSec += 1
            
            if Time.Now() - lastSec > 1 and frameCountSec != 0:
                self.FPSRead = frameCountSec
                frameCountSec = 0
                lastSec = Time.Now()

            # # print(4)
            self.lastFrame = cvStreamFrame(frame, self.objectDetectModel)
            self.lastFrameUpdateTime = Time.Now()
        
    def socketserverrunner(self, tc:Socket.TCP.PacketConnection):
        lastgettime = None
        while True:
            if self.closed == True:
                break 

            # print(504)
            # print(505, tc.Recv())
            # print(506)

            while lastgettime == self.lastFrameUpdateTime:
                if self.FPSRead != None:
                    Time.Sleep(1/self.FPSRead)
                else:
                    Time.Sleep(1/30)

            (flag, encodedImage) = cv2.imencode(".jpg", self.lastFrame.frame)
            if not flag:
                if self.FPSRead != None:
                    Time.Sleep(1/self.FPSRead)
                else:
                    Time.Sleep(1/30)
                continue

            encodedImage = encodedImage.tobytes()
            try:
                tc.Send(encodedImage)
            except:
                break

            lastgettime = self.lastFrameUpdateTime

        tc.Close()

    def socketServer(self, ipaddr:str, port:int):
        for tc in Socket.TCP.Listen(ipaddr, port):
            tc = tc.PacketConnection()
            Thread(self.socketserverrunner, tc)
    
    def SocketServer(self, ipaddr:str="0.0.0.0", port:int=7283):
        Thread(self.socketServer, ipaddr, port)

    def Get(self) -> cvStreamFrame:
        while True:
            #print(self.frameCountSec)
            if self.frameCountSec != 0 and (self.lastTimeForCaclFPS == None or Time.Now() - self.lastTimeForCaclFPS >= 1):
                self.FPS = self.frameCountSec

                self.fpss.append(self.frameCountSec)

                while len(self.fpss) > 180:
                    self.fpss.pop(0)

                self.FPSAverage = int(sum(self.fpss)/len(self.fpss))
                
                self.lastTimeForCaclFPS = Time.Now()
                self.frameCountSec = 0

            if self.lastGetFrameTime != self.lastFrameUpdateTime:
                self.frameCountSec += 1
                #print(self.lastGetFrameTime, self.lastFrameUpdateTime)
                self.lastGetFrameTime = self.lastFrameUpdateTime
                return self.lastFrame

            if self.closed == True:
                return None 
            
            if self.FPS != None:
                Time.Sleep(1/self.FPS)
            else:
                Time.Sleep(1/30)
    
    def webResponseImageGenerate(self) -> bytes:
        while True:
            if self.closed == True:
                break 
            
            (flag, encodedImage) = cv2.imencode(".jpg", self.lastFrame.frame)
            # ensure the frame was successfully encoded
            if not flag:
                if self.FPSRead != None:
                    Time.Sleep(1/self.FPSRead)
                else:
                    Time.Sleep(1/30)
                continue
            
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

            if self.FPSRead != None:
                Time.Sleep(1/self.FPSRead)
            else:
                Time.Sleep(1/30)

    def webResponseVideoFeed(self):
        return flask.Response(self.webResponseImageGenerate(),
            mimetype = "multipart/x-mixed-replace; boundary=frame")
    
    def RunWebServer(self, ipaddr:str="0.0.0.0", port:int=9987, url:str="/camera/video"):
        flaskapp = flask.Flask("whatevername")
        flaskapp.add_url_rule(url, 'webResponseVideoFeed', self.webResponseVideoFeed)

        Thread(flaskapp.run, ipaddr, port)

    def __iter__(self) -> typing.Iterator[cvStreamFrame]:
        while True:
            frame = self.Get()

            if frame == None:
                return
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                self.closed = True
                break

            yield frame
            
    def __enter__(self):
        return self 
    
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.Close()
        except:
            pass

def LoadImage(path:str, objectDetectModel:str="SSD", weights:str="yolov4.weights", config:str="yolov4.cfg", classes:str="yolov4.txt") -> cvStreamFrame:
    if objectDetectModel == "YOLO":
        global classesyolo
        global colorsyolo
        global netyolo

        with open(classes, 'r') as f:
            classesyolo = [line.strip() for line in f.readlines()]

        colorsyolo = np.random.uniform(0, 255, size=(len(classesyolo), 3))

        netyolo = cv2.dnn.readNet(weights, config)

    return cvStreamFrame(cv2.imread(path), objectDetectModel)

class VideoWriter():
    def __init__(self, path:str, fps:int, width:int, height:int) -> None:
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.writer = cv2.VideoWriter(path, fourcc, fps, (height, width))
        self.closed = False

    def Write(self, frame:cvStreamFrame):
        if self.closed == False:
            self.writer.write(frame.frame) 

    def Close(self):
        if self.closed == False:
            self.closed = True 
            self.writer.release() 

class ComputerVision:
    VideoWriter
    LoadImage
    StreamAsync
    StreamSync

if __name__ == "__main__":
    import os
    import datetime 
    
    # web camera
    # stream = Stream("http://10.129.129.207:8080/video")

    # usb camera
    # stream = Stream(0)

    # print(stream.FPS())

    # Video file
    # stream = StreamSync(os.getenv("HOME") + "/Desktop/1080p/221105.mp4")

    # stream.RunWebServer()

    # for frame in stream:
    #     frame.Text(str(stream.FPS) + "/" + str(stream.FPSAverage)).Show("")

    # bg = stream.Get()
    # for frame in stream:
    #     frame.Compare(bg).Draw(frame).Text(datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")).Show("test")

    # bg = stream.Get().Bright(5).Rotate(0)
    # for frame in stream:
    #     frame = frame.Bright(5).Rotate(0)
    #     frame.Compare(bg).Draw(frame).Text(datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")).Show("test")

    # for frame in stream:
    #     frame.Objects().Draw(frame, filterAbove=70).Show("")

    # frame = stream.Get()
    # w, h = frame.Size()
    # print(w,h )
    # writer = VideoWriter("video.mp4", 25, w, h)

    # for _ in range(0, 250):
    #     writer.Write(stream.Get())
    
    # writer.Close()

    #####################3

    # stream = Tools.ComputerVision.StreamSync(0)
    # stream.SetAPIServerForObjectDetect("example.com")
    # for frame in stream:
    #     frame = frame.Rotate(0).Text(f"fps:{stream.FPS}")
    #     frame = frame.Objects().Draw(frame)
    #     frame.Show()
    pass 