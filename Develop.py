from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QPushButton,QFileDialog,QSlider
from PyQt5.QtGui import QPixmap
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
import time

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0)
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()
class ImageThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.ImageL = ""
        self.Image = 0
    def run(self):
        # capture from web cam
        self.Image = cv2.imread(self.ImageL,cv2.IMREAD_COLOR)
        self.change_pixmap_signal.emit(self.Image)
        # shut down capture system
    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()
    def setFileName(self,ImageL):
        self.ImageL = ImageL
        print(self.ImageL)
    def getFileName(self):
        return self.Image
    def Threshold(self,High,Low):
        self.Image = cv2.imread(self.ImageL,cv2.IMREAD_COLOR)
        image_data = np.asarray(self.Image)
        for i in range(len(image_data)):
            for j in range(len(image_data[0])):
                if(image_data[i][j][0] < High):
                    image_data[i][j] = 255
        self.image2 = image_data
        self.change_pixmap_signal.emit(self.image2)

    def SobelX(self):
        sobel_Xfilter = np.array([[-1,0,1],[-2,0,2],[-1,0,1]])
        self.Image = cv2.imread(self.ImageL,cv2.IMREAD_COLOR)
        image_data = np.asarray(self.Image)
        for width in range(0,len(image_data)-3,3):
            for height in range(3,len(image_data[0])-3,3):
                for i in range(0,3):
                    for j in range(0,3):
                        image_data[width+i][height+j] = image_data[width+i][height+j][0] * sobel_Xfilter[i][j]
        self.image2 = image_data
        self.change_pixmap_signal.emit(self.image2)
        return self.image2
    def SobelY(self):
        sobel_Yfilter = np.array([[1,2,1],[0,0,0],[-1,-2,-1]])
        self.Image = cv2.imread(self.ImageL,cv2.IMREAD_COLOR)
        image_data = np.asarray(self.Image)
        for width in range(0,len(image_data)-3,3):
            for height in range(3,len(image_data[0])-3,3):
                for i in range(0,3):
                    for j in range(0,3):
                        image_data[width+i][height+j] = image_data[width+i][height+j][0] * sobel_Yfilter[i][j]
        self.image2 = image_data
        self.change_pixmap_signal.emit(self.image2)
        return self.image2
    def SobelXY(self):
        SobelX = self.SobelX()
        SobelY = self.SobelX()
        Sobel = SobelX + SobelY
        self.change_pixmap_signal.emit(Sobel)
class App(QWidget):
    def __init__(self):
        super().__init__()
        ##

        ##

        self.setWindowTitle(" Program ")
        self.disply_width = 1600
        self.display_height = 800
        self.resize(1600,1400)
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)
        # create a text label
        self.textLabel = QLabel('Webcam')
        self.push_button1 = QPushButton('라이브')
        self.push_button2 = QPushButton('이미지 로드')
        self.push_button3 = QPushButton('이진화')
        ### 슬라이더 추가
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setGeometry(10,10,200,30)
        self.slider.setRange(0,255)
        self.slider.valueChanged.connect(self.value_changed)
        self.Videothread = VideoThread()

        self.Imagethread = ImageThread()
        #self.Imagethread.setFileName("/Users/lim/Desktop/lena.png")
        self.Imagethread.setFileName("/Users/lim/Desktop/Rectangle.png")
        self.Imagethread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.Imagethread.start()
        ###
        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)
        vbox.addWidget(self.textLabel)
        vbox.addWidget(self.push_button1)
        vbox.addWidget(self.push_button2)
        vbox.addWidget(self.push_button3)
        vbox.addWidget(self.slider)
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)
        self.push_button1.clicked.connect(self.start)
        self.push_button2.clicked.connect(self.FileLoad)
        # create the video capture thread
    def value_changed(self,value):
        print(value)
        #self.Imagethread.Threshold(value,255)
        self.Imagethread.SobelX()
    def FileLoad(self):
        fname = QFileDialog.getOpenFileName(self)
        # connect its signal to the update_image slot
        self.Imagethread.setFileName(fname[0])
        self.Imagethread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.Imagethread.start()
    def start(self):
        # connect its signal to the update_image slot
        self.Videothread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.Videothread.start()

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())