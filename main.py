import sys
import numpy as np
from PyQt5 import QtGui
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui
import sys
import cv2
import numpy as np
from QGStreamer import GStreamerFeed



class VideoFeedThread(QThread):
    '''

    Thread for reading frames from gstreamer appsink.

    '''

    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        self.cap = GStreamerFeed()
        self.cap.startPrev()

        self.__run = True
        while True:
            if self.cap.isFrameReady() and self.__run:
                np_img = self.cap.getFrame()
                self.change_pixmap_signal.emit(np_img)

    def taskStop(self):
        self.__run = False

    def taskStart(self):
        self.__run = True



class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GStreamer With PyQt5")
        
        self.disply_width = 540
        self.display_height = 280
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)


        # create a vertical box layout and add the widget
        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

        # create the video capture thread
        self.thread = VideoFeedThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()



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
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_BGR888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
if __name__=="__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())
