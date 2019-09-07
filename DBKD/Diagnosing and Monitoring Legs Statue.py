from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import sys, subprocess, cv2, os, math
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from tempfile import NamedTemporaryFile
from shutil import copyfile
from matplotlib import pyplot as plt

path = "Category"
imgs = ['lb.jpg', 'lt.jpg', 'rb.jpg', 'rt.jpg']

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 600)
        MainWindow.setMinimumSize(QtCore.QSize(1000, 600))
        MainWindow.setMaximumSize(QtCore.QSize(1000, 600))
        self.mw = MainWindow
        icon = QtGui.QIcon.fromTheme("logo.png")
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.AddXRay = QtWidgets.QPushButton(self.centralwidget)
        self.AddXRay.setGeometry(QtCore.QRect(40, 30, 211, 41))
        self.AddXRay.setAutoFillBackground(False)
        self.AddXRay.setStyleSheet("background-color: rgba(116, 255, 56, 50);")
        self.AddXRay.setObjectName("AddXRay")
        self.AddXRay.clicked.connect(self.clicked_)
        self.DisplayResult = QtWidgets.QPushButton(self.centralwidget)
        self.DisplayResult.setGeometry(QtCore.QRect(720, 30, 241, 41))
        self.DisplayResult.setStyleSheet("background-color: rgba(255, 85, 0, 50);")
        self.DisplayResult.setObjectName("DisplayResult")
        self.DisplayResult.clicked.connect(self.displayR)
        self.fileName = QtWidgets.QLineEdit(self.centralwidget)
        self.fileName.setGeometry(QtCore.QRect(310, 40, 351, 20))
        self.fileName.setReadOnly(True)
        self.fileName.setObjectName("fileName")
        self.resultEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.resultEdit.setGeometry(QtCore.QRect(40, 100, 921, 451))
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(14)
        self.resultEdit.setFont(font)
        self.resultEdit.setReadOnly(True)
        self.resultEdit.setObjectName("resultEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.choose = False

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Diagnosing and Monitoring Legs Statue intensively"))
        self.AddXRay.setText(_translate("MainWindow", "Add X-Ray"))
        self.DisplayResult.setText(_translate("MainWindow", "Display Result"))

    def clicked_(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self.mw,"QFileDialog.getOpenFileName()", "","Image Files (*.png *.jpg *.jpeg *.tiff *.gif *.bmp)", options=options)
        if fileName:
            self.fileName.setText(fileName)
            self.filePath = fileName
            target_image = fileName

            im = cv2.imread(target_image)
            centers = []

            f = os.path.join(os.path.dirname(target_image), 'newImg.png')
            copyfile(target_image, f)
            for i in range(4):
                tmp = cv2.imread(os.path.join(path, imgs[i]))

                image_size = im.shape[:2]
                template_size = tmp.shape[:2]

                result = cv2.matchTemplate(im, tmp, cv2.TM_SQDIFF)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                confidence = (9999999999 - min_val) / 100000000
                print ('primary confidence', '%.2f %%' % confidence)

                altconfidence = 100 - ((min_val / max_val)*100)
                print ('alternate confidence', '%.2f %%' % altconfidence)

                topleftx = min_loc[0]
                toplefty = min_loc[1]
                sizex = template_size[1]
                sizey = template_size[0]

                if (altconfidence > 99) or ((confidence > 97) and (altconfidence > 93)) or ((confidence > 95.7) and (altconfidence > 96.3)):
                    print ('The image of size', template_size, '(y,x) was found at', min_loc)
                    print ('Marking', f, 'with a red rectangle')
                    marked = Image.open(f)
                    draw = ImageDraw.Draw(marked)
                    draw.line(((topleftx,         toplefty),         (topleftx + sizex, toplefty)),           fill="blue", width=4)
                    draw.line(((topleftx + sizex, toplefty),         (topleftx + sizex, toplefty + sizey)),   fill="blue", width=4)
                    draw.line(((topleftx + sizex, toplefty + sizey), (topleftx,         toplefty + sizey)),   fill="blue", width=4)
                    draw.line(((topleftx,         toplefty + sizey), (topleftx,         toplefty)),           fill="blue", width=4)
                    if i == 0:
                        centers.append((topleftx + (sizex/2),toplefty + (sizey/2)))
                    elif i == 1:
                        angle = math.degrees(math.atan((centers[0][0]-(topleftx + (sizex/2)))/(centers[0][1]-(toplefty + (sizey/2))))) + 15
                        self.angle1 = angle
                        draw.line(((centers[0][0], toplefty + (sizey/2)), centers[0]), fill="red", width=4)
                        draw.line(((topleftx + (sizex/2), toplefty + (sizey/2)), centers[0]), fill="blue", width=4)
                        draw.text((centers[0][0], centers[0][1]), '%.2f°' % angle, font=ImageFont.truetype("micross.ttf", 36))
                    elif i == 2:
                        centers.append((topleftx + (sizex/2),toplefty + (sizey/2)))
                    else:
                        angle = math.degrees(math.atan((centers[1][0]-(topleftx + (sizex/2)))/(centers[1][1]-(toplefty + (sizey/2))))) + 15
                        self.angle2 = angle
                        draw.line(((centers[1][0], toplefty + (sizey/2)), centers[1]), fill="red", width=4)
                        draw.line(((topleftx + (sizex/2)-1, toplefty + (sizey/2)), centers[1]), fill="blue", width=4)
                        draw.text((centers[1][0], centers[1][1]), '%.2f°' % angle, font=ImageFont.truetype("micross.ttf", 36))
                    del draw
                    marked.save(f, "PNG")
                else:
                    print ('The image was not found')
                    return
            self.fn = f
            self.choose = True
            stats = 'Negative' if (self.angle1<=20 and self.angle1>=10) and (self.angle2<=20 and self.angle2>=10) else 'Posetive'
            typ = 'Normal'
            if not (self.angle1<=20 and self.angle1>=10) and (self.angle2<=20 and self.angle2>=10):
                if (self.angle1>20 or self.angle2>20):
                    typ = 'Bow-Legged'
                if (self.angle1<10 or self.angle2<10):
                    if typ == '':
                        typ = 'Knock-kneed'
                    else:
                        typ = 'Both (Bow-Legged, Knock-kneed)'
            rd = 'Negative'
            if self.angle1 > 20:
                rd = 'Bow-Legged'
            elif self.angle1 < 10:
                rd = 'Knock need'
            ld = 'Negative'
            if self.angle2 > 20:
                ld = 'Bow-Legged'
            elif self.angle2 < 10:
                ld = 'Knock need'
            self.resultEdit.setText("""Stats : {}\nType : {}\n\nRight :-
Right Angle : {}\nRight Disease : {}\n\nLeft :- \nLeft Angle : {}\nLeft Disease : {}""".format(stats, typ, self.angle1, rd, self.angle2, ld))

    def displayR(self):
        if self.choose:
            img = cv2.imread(self.fn)
            plt.imshow(img, cmap = 'gray', interpolation = 'bicubic')
            plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
            plt.show()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    sys._excepthook = sys.excepthook 
    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback) 
        sys.exit(1) 
    sys.excepthook = exception_hook
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
