from pathlib import Path
import shutil
import os
import platform
import sys

from PIL import Image
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QComboBox, QMessageBox
from PyQt5.QtCore import Qt, QThread,pyqtSignal
from PyQt5 import QtCore, QtWidgets
from PyQt5.Qt import QApplication


class Thread_1(QThread):
    sig = pyqtSignal(str, str)  # 信号，发送处理进度
    err = pyqtSignal(str)  # 信号，发送 error 信息

    def __init__(self, images, value, mode):
        super(Thread_1, self).__init__()
        self.images = images
        self.mode = mode
        self.value = value
        self.len = len(self.images)

    def run(self):
        res = ''
        n = 0
        try:
            if self.mode == 'copy':
                for img in self.images:
                    n += 1
                    shutil.copy(img, self.value.new_path)
                    self.sig.emit(str(n), str(self.len))  # 发送当前执行进度数据
            elif self.mode == 'move':
                for img in self.images:
                    n+=1
                    shutil.move(img, self.value.new_path)
                    self.sig.emit(str(n), str(self.len))
        except Exception as e:
            res += str(e)
            res += '\n'
            print(e)
        self.err.emit(res)  # 发送错误信息


class Val(object):
    """
    存放用户在 UI 界面上输入的内容或设置
    """
    recursive = False  # 是否递归子文件夹
    img_path = ""  # 源图片路径
    new_path = ""  # 目标图片路径
    width_height = ""  # 长宽比
    width_height_sign = ">"  # 默认长宽比的符号
    width_height_pixel = ""  # 像素值
    width_height_pixel_sign = ">"


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.value = Val()
        self.setupUi()

    def setupUi(self):
        self.resize(592, 436)

        # 选择图片文件夹按钮
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(80, 60, 71, 21))

        # 用来显示文件夹路径
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setToolTip("左侧按钮选择你要处理的源图片文件夹")
        self.lineEdit.setGeometry(QtCore.QRect(160, 50, 261, 31))

        # 选择目标文件夹按钮
        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setGeometry(QtCore.QRect(80, 100, 71, 21))
        # 用来显示目标文件夹路径
        self.lineEdit_2 = QtWidgets.QLineEdit(self)
        self.lineEdit_2.setToolTip("左侧按钮选择你想要将图片移动或复制到的文件夹")
        self.lineEdit_2.setGeometry(QtCore.QRect(160, 90, 261, 31))

        # 勾选框，是否递归文件夹
        self.checkBox = QtWidgets.QCheckBox(self)
        self.checkBox.setGeometry(QtCore.QRect(440, 60, 81, 21))

        # 长宽比 label
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(80, 140, 50, 16))
        # 长宽比 输入框
        self.lineEdit_3 = QtWidgets.QLineEdit(self)
        self.lineEdit_3.setToolTip('示例：4/3 \n长宽比例条件，和下面的像素长宽这两个条件，只要有一个不满足，图片都不会选中。\n留空则忽略此条件。')
        self.lineEdit_3.setGeometry(QtCore.QRect(160, 130, 261, 31))

        # 像素 label
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(80, 180, 60, 12))

        # 像素输入框
        self.lineEdit_4 = QtWidgets.QLineEdit(self)
        self.lineEdit_4.setToolTip("示例：1920/1080 \n像素长宽值，和上面的长宽比例这两个条件，只要有一个不满足，图片都不会选中。\n留空则忽略此条件")
        self.lineEdit_4.setGeometry(QtCore.QRect(160, 170, 261, 31))

        # 长宽比 符号
        self.comboBox = QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(440, 130, 69, 22))
        self.comboBox.setToolTip("大于，意味着图片越宽越矮；反之图片越窄越高")
        self.comboBox.addItem(">")
        self.comboBox.addItem(">=")
        self.comboBox.addItem("=")
        self.comboBox.addItem("<=")
        self.comboBox.addItem("<")

        # 像素 符号
        self.comboBox_2 = QComboBox(self)
        self.comboBox_2.setGeometry(QtCore.QRect(440, 170, 69, 22))
        self.comboBox_2.setToolTip("大于，意味着目标图片的长和宽都要大于输入的长宽值")
        self.comboBox_2.addItem(">")
        self.comboBox_2.addItem(">=")
        self.comboBox_2.addItem("=")
        self.comboBox_2.addItem("<=")
        self.comboBox_2.addItem("<")

        # 复制 按钮
        self.pushButton_3 = QtWidgets.QPushButton(self)
        self.pushButton_3.setGeometry(QtCore.QRect(170, 280, 75, 23))

        # 移动 按钮
        self.pushButton_4 = QtWidgets.QPushButton(self)
        self.pushButton_4.setGeometry(QtCore.QRect(320, 280, 75, 23))

        # 给各个按钮绑定槽函数,一旦 UI 上各控件被点击或改动，就触发函数
        self.pushButton.clicked.connect(self.showDialog)
        self.pushButton_2.clicked.connect(self.showDialog2)
        self.checkBox.stateChanged.connect(self.recursive)
        self.lineEdit_3.textChanged.connect(self.width_height)
        self.lineEdit_4.textChanged.connect(self.width_height_pixel)
        # comboBox.activated[str]，必须加 [str]，否则会默认int，也就是说你选择下拉选项的第几个内容，会显示选项的索引数字而不是选项的文字内容
        self.comboBox.activated[str].connect(self.width_height_sign)
        self.comboBox_2.activated[str].connect(self.width_height_pixel_sign)
        self.pushButton_3.clicked.connect(self.calculate)
        self.pushButton_4.clicked.connect(self.calculate)

        self.set_title()
        self.show()

    def set_title(self):
        self.setWindowTitle("ImgSelector")
        self.pushButton.setText("图片文件夹")
        self.checkBox.setText("子文件夹")
        self.label.setText("长宽比例")
        self.label_2.setText("像素长宽")
        self.pushButton_2.setText("目标文件夹")
        self.pushButton_3.setText("复制")
        self.pushButton_4.setText("移动")

    def width_height_sign(self, text):
        """
        获取下拉框的内容
        :param text:
        :return:
        """
        self.value.width_height_sign = text

    def width_height_pixel_sign(self, text):
        """
        获取下拉框的内容
        :param text:
        :return:
        """
        self.value.width_height_pixel_sign = text

    def width_height(self, text):
        """
        长宽比 输入框，获取输入的内容
        :param text:
        :return:
        """
        self.lineEdit_3.setText(text)
        self.value.width_height = text
        # print('长宽比',self.value.width_height)

    def width_height_pixel(self, text):
        """
        像素 输入框，获取输入的内容
        :param text:
        :return:
        """
        self.lineEdit_4.setText(text)
        self.value.width_height_pixel = text
        # print('像素值',self.value.width_height_pixel)

    def recursive(self, state):
        """
        勾选框，设置是否递归子文件夹
        :param state:
        :return:
        """
        if state == Qt.Checked:
            self.value.recursive = True
        else:
            self.value.recursive = False
        # print(self.value.recursive)

    def showDialog(self):
        """
        文件夹对话框，选择图片所在的文件夹
        :return:
        """
        fname = QFileDialog.getExistingDirectory(self, 'Choose folder', DEFAULT_IMG_PATH)
        self.value.img_path = fname
        self.lineEdit.setText(fname)

    def showDialog2(self):
        """
        文件夹对话框，选择图片要移动或复制的新的文件夹
        :return:
        """
        fname = QFileDialog.getExistingDirectory(self, 'Choose folder', DEFAULT_IMG_PATH)
        self.value.new_path = fname
        self.lineEdit_2.setText(fname)

    def calculate(self):
        """
        计算图片是否满足条件，然后将满足条件的图片进行移动或复制
        :return:
        """
        file_list = []
        if self.value.recursive:
            files = Path(self.value.img_path).rglob("*.*")
        else:
            files = Path(self.value.img_path).glob("*.*")

        # 长宽比和像素值，这两个条件不写的话，默认是True，会处理文件夹中所有图片
        width_height_res = True
        width_height_pix_res = True
        # 获取符合条件的图片
        for file in files:
            try:
                img = Image.open(str(file))
                width = img.size[0]
                height = img.size[1]
                # self.value.width_height 有值，说明用户输入了长宽比条件，就对这个条件进行计算，图片是否满足条件
                if self.value.width_height:
                    width_height_res = eval(str(width / height)+ self.value.width_height_sign + self.value.width_height)
                if self.value.width_height_pixel:  # 像素值 条件
                    width = eval(str(width) + self.value.width_height_pixel_sign + self.value.width_height_pixel.split('/')[0])
                    height = eval(str(height) + self.value.width_height_pixel_sign + self.value.width_height_pixel.split('/')[1])
                    width_height_pix_res = width and height

                if width_height_res and width_height_pix_res:  # 意味着两个条件都满足，则图片符合条件（条件为空，默认是True)
                    file_list.append(str(file))
            except Exception as e:
                print(e)
                pass
        try:
            sender = self.sender()  # 获取是哪个按钮出发了此函数
            if sender == self.pushButton_3 or sender == self.pushButton_4:
                if not (self.value.new_path and self.value.img_path):  # 如果两个文件夹都是空的
                    QMessageBox.question(self, 'Message',"图片文件夹和目标文件夹均不能为空！", QMessageBox.Yes)
                else:
                    # 按钮置灰，不可再次点击
                    self.pushButton_3.setEnabled(False)
                    self.pushButton_4.setEnabled(False)

                    if sender == self.pushButton_3:  # 复制按钮
                        self.statusBar().showMessage('Copying...')  # 底部状态栏
                        self.thread = Thread_1(file_list, self.value, 'copy')  # 创建线程
                        self.thread.sig.connect(self.copy_show)
                        self.thread.err.connect(self.thread_err)
                        self.thread.start()
                    else:  # 移动按钮
                        self.statusBar().showMessage('Moving...')
                        self.thread = Thread_1(file_list, self.value, 'move')
                        self.thread.sig.connect(self.move_show)
                        self.thread.err.connect(self.thread_err)
                        self.thread.start()

        except Exception as e:
            print(e)

    def thread_err(self, error):
        """
        查看是否有从线程返回的错误信息，有就显示出来
        :param error:
        :return:
        """
        if error:
            QMessageBox.information(self, 'Errors', error, QMessageBox.Yes)
        self.statusBar().showMessage("Ready")
        # 按钮置为可点击状态
        self.pushButton_3.setEnabled(True)
        self.pushButton_4.setEnabled(True)

    def copy_show(self, cur, all):
        """
        将从线程中的信号 emit 过来的值，显示在状态栏，可以查看处理进度
        :param cur:
        :param all:
        :return:
        """
        self.statusBar().showMessage(f"Copying {cur} of {all}")

    def move_show(self, cur, all):
        self.statusBar().showMessage(f"Moving {cur} of {all}")


def get_desktop_path():
    # windows 获取当前用户的 Desktop
    if platform.system() == "Windows":
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    elif platform.system() == 'Linux':
        # linux 获取家目录，如：/root
        return os.path.expanduser('~')


if __name__ == '__main__':
    DEFAULT_IMG_PATH = r'C:\Users\wztshine\Desktop'
    path = Path(DEFAULT_IMG_PATH)
    if not path.exists():
        DEFAULT_IMG_PATH = get_desktop_path()

    app = QApplication(sys.argv)
    ex = Ui_MainWindow()
    sys.exit(app.exec_())
