import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
                             QFileDialog, QTextEdit, QMessageBox, QLineEdit, QDialog, QStyle)
from PyQt5.QtGui import QPixmap, QImage, QPalette, QBrush, QFont
from PyQt5.QtCore import Qt, QSize
from ultralytics import YOLO
import cv2
import numpy as np


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # 设置窗口标题
        self.setWindowTitle('登录系统')

        # 固定窗口大小
        self.setFixedSize(400, 300)

        # 设置主布局
        mainLayout = QVBoxLayout()

        # 创建用户名布局
        usernameLayout = QHBoxLayout()
        usernameLabel = QLabel('用户名:', self)
        usernameLabel.setFont(QFont('Arial', 15))
        self.usernameInput = QLineEdit(self)
        self.usernameInput.setFixedSize(250, 40)
        self.usernameInput.setFont(QFont('Arial', 15))
        usernameLayout.addWidget(usernameLabel)
        usernameLayout.addWidget(self.usernameInput)
        usernameLayout.setSpacing(5)  # 设置用户名和输入框之间的间距

        # 创建密码布局
        passwordLayout = QHBoxLayout()
        passwordLabel = QLabel('密码:', self)
        passwordLabel.setFont(QFont('Arial', 15))
        self.passwordInput = QLineEdit(self)
        self.passwordInput.setEchoMode(QLineEdit.Password)
        self.passwordInput.setFixedSize(250, 40)
        self.passwordInput.setFont(QFont('Arial', 15))
        passwordLayout.addWidget(passwordLabel)
        passwordLayout.addWidget(self.passwordInput)
        passwordLayout.setSpacing(5)  # 设置密码和输入框之间的间距

        # 创建按钮布局
        buttonLayout = QHBoxLayout()
        self.loginButton = QPushButton('登录', self)
        self.loginButton.setFixedSize(100, 40)
        self.loginButton.setFont(QFont('Arial', 15))
        self.loginButton.setStyleSheet(self.buttonStyleSheet())
        self.loginButton.clicked.connect(self.checkLogin)

        self.exitButton = QPushButton('退出', self)
        self.exitButton.setFixedSize(100, 40)
        self.exitButton.setFont(QFont('Arial', 15))
        self.exitButton.setStyleSheet(self.buttonStyleSheet())
        self.exitButton.clicked.connect(self.exitSystem)

        buttonLayout.addWidget(self.loginButton)
        buttonLayout.addWidget(self.exitButton)
        buttonLayout.setSpacing(50)  # 设置两个按钮之间的间距
        buttonLayout.setAlignment(Qt.AlignCenter)  # 按钮整体左右居中

        # 添加控件到主布局
        mainLayout.addStretch(1)
        mainLayout.addLayout(usernameLayout)
        mainLayout.addSpacing(20)  # 设置两行之间的间距
        mainLayout.addLayout(passwordLayout)
        mainLayout.addSpacing(40)  # 设置两行之间的间距
        mainLayout.addLayout(buttonLayout)
        mainLayout.addStretch(1)
        mainLayout.setAlignment(Qt.AlignCenter)

        # 设置主布局
        self.setLayout(mainLayout)

    def buttonStyleSheet(self):
        # 定义按钮的样式
        return """
            QPushButton {
                background-color: #428bca;
                color: white;
                border: 2px solid #428bca;
                border-radius: 10px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #d9534f;
                border: 2px solid #d9534f;
            }
            QPushButton:pressed {
                background-color: #449d44;
            }
        """

    def checkLogin(self):
        username = self.usernameInput.text()
        password = self.passwordInput.text()

        if username == 'admin' and password == '123456':
            self.showMessageBox('成功', '登陆成功！', True)
        elif username != 'admin':
            self.showMessageBox('错误', '用户名输入错误！', False)
            self.usernameInput.clear()
            self.passwordInput.clear()
        elif password != '123456':
            self.showMessageBox('错误', '密码输入错误！', False)
            self.passwordInput.clear()

    def showMessageBox(self, title, message, success=False):
        # 自定义消息对话框
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(300, 200)

        # 设置布局
        layout = QVBoxLayout()

        # 设置图标和文本布局
        iconLabel = QLabel()
        icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
        if success:
            icon = self.style().standardIcon(QStyle.SP_MessageBoxInformation)
        iconLabel.setPixmap(icon.pixmap(64, 64))

        messageLabel = QLabel(message)
        messageLabel.setFont(QFont('Arial', 15))

        textLayout = QHBoxLayout()
        textLayout.addStretch(1)
        textLayout.addWidget(iconLabel)
        textLayout.addWidget(messageLabel)
        textLayout.addStretch(1)

        # 设置按钮
        buttonLayout = QHBoxLayout()
        okButton = QPushButton('确定')
        okButton.setFont(QFont('Arial', 20))
        okButton.setFixedSize(100, 40)
        okButton.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                color: white;
                background-color: #428bca;
                border: 2px solid #428bca;
                border-radius: 10px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #d9534f;
                border: 2px solid #d9534f;
            }
            QPushButton:pressed {
                background-color: #449d44;
            }
        """)
        okButton.clicked.connect(dialog.accept)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(okButton)
        buttonLayout.addStretch(1)

        layout.addLayout(textLayout)
        layout.addLayout(buttonLayout)

        dialog.setLayout(layout)
        dialog.exec()

        if success:
            self.mainWindow = ImageUploader()
            self.mainWindow.show()
            self.close()

    def exitSystem(self):
        QApplication.quit()


class ImageUploader(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.model = YOLO('yolov8n.pt').to('cpu')  # 默认加载YOLOv8n模型
        self.save_count = 0  # 计数器，记录保存图片的次数

    def initUI(self):
        # 设置窗口标题
        self.setWindowTitle('白粉病菌孢子实例分割与定量识别系统')

        # 固定窗口大小
        self.setFixedSize(1200, 900)

        # 设置背景图片
        self.set_background("background.jpg")

        # 创建主布局
        mainLayout = QHBoxLayout()

        # 创建垂直布局用于左边的图片显示和文本框
        leftLayout = QVBoxLayout()

        # 创建图片显示标签
        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setFixedSize(900, 750)  # 固定图片标签大小
        self.imageLabel.setText("图片显示区域")
        self.imageLabel.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px solid #cccccc;
                border-radius: 10px;
                font-size: 20px;
                padding: 10px;
            }
        """)
        leftLayout.addWidget(self.imageLabel)

        # 创建文本框用于显示文字性结果
        self.textBox = QTextEdit(self)
        self.textBox.setFixedSize(900, 100)  # 固定文本框大小
        self.textBox.setStyleSheet("""
            QTextEdit {
                font-size: 20px;
                border: 2px solid #cccccc;
                border-radius: 10px;
                padding: 10px;
                background-color: #f9f9f9;
            }
        """)
        self.textBox.setReadOnly(True)  # 设置为只读
        self.textBox.setAlignment(Qt.AlignLeft)  # 设置左对齐
        self.textBox.append("欢迎使用白粉病菌孢子实例分割与定量识别系统！")  # 欢迎信息
        leftLayout.addWidget(self.textBox)

        # 将左侧布局添加到主布局
        mainLayout.addLayout(leftLayout)

        # 创建垂直布局用于右边的按钮
        rightLayout = QVBoxLayout()

        # 创建上传图片的按钮
        self.uploadButton = QPushButton('上传图片', self)
        self.uploadButton.setFixedSize(180, 60)  # 固定按钮大小
        self.uploadButton.setStyleSheet(self.buttonStyleSheet())  # 设置按钮样式
        self.uploadButton.clicked.connect(self.showFileDialog)

        # 创建选择模型的按钮
        self.selectModelButton = QPushButton('选择模型', self)
        self.selectModelButton.setFixedSize(180, 60)  # 固定按钮大小
        self.selectModelButton.setStyleSheet(self.buttonStyleSheet())  # 设置按钮样式
        self.selectModelButton.clicked.connect(self.selectModel)

        # 创建自动计数的按钮
        self.countButton = QPushButton('自动计数', self)
        self.countButton.setFixedSize(180, 60)  # 固定按钮大小
        self.countButton.setStyleSheet(self.buttonStyleSheet())  # 设置按钮样式
        self.countButton.clicked.connect(self.autoCount)

        # 创建保存图片的按钮
        self.saveButton = QPushButton('保存图片', self)
        self.saveButton.setFixedSize(180, 60)  # 固定按钮大小
        self.saveButton.setStyleSheet(self.buttonStyleSheet())  # 设置按钮样式
        self.saveButton.clicked.connect(self.saveImage)

        # 创建返回登录界面的按钮
        self.returnLoginButton = QPushButton('返回登录', self)
        self.returnLoginButton.setFixedSize(180, 60)  # 固定按钮大小
        self.returnLoginButton.setStyleSheet(self.buttonStyleSheet())  # 设置按钮样式
        self.returnLoginButton.clicked.connect(self.returnLogin)

        # 创建退出系统的按钮
        self.exitButton = QPushButton('退出系统', self)
        self.exitButton.setFixedSize(180, 60)  # 固定按钮大小
        self.exitButton.setStyleSheet(self.buttonStyleSheet())  # 设置按钮样式
        self.exitButton.clicked.connect(self.exitSystem)

        # 添加拉伸使按钮上下居中
        rightLayout.addStretch(1)
        rightLayout.addWidget(self.uploadButton)
        rightLayout.addStretch(1)  # 添加拉伸增加间距
        rightLayout.addWidget(self.selectModelButton)
        rightLayout.addStretch(1)  # 添加拉伸增加间距
        rightLayout.addWidget(self.countButton)
        rightLayout.addStretch(1)  # 添加拉伸增加间距
        rightLayout.addWidget(self.saveButton)
        rightLayout.addStretch(1)  # 添加拉伸增加间距
        rightLayout.addWidget(self.returnLoginButton)
        rightLayout.addStretch(1)  # 添加拉伸增加间距
        rightLayout.addWidget(self.exitButton)
        rightLayout.addStretch(1)

        # 将右侧布局添加到主布局
        mainLayout.addLayout(rightLayout)

        # 设置主布局
        self.setLayout(mainLayout)

    def buttonStyleSheet(self):
        # 定义按钮的样式
        return """
            QPushButton {
                font-size: 20px;
                color: white;
                background-color: #428bca;
                border: 2px solid #4cae4c;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #d9534f;
            }
            QPushButton:pressed {
                background-color: #449d44;
            }
        """

    def set_background(self, image_path):
        # 设置背景图片
        oImage = QImage(image_path)
        sImage = oImage.scaled(QSize(1200, 900))  # 缩放图片
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def showFileDialog(self):
        # 打开文件选择对话框
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "选择图片文件", "", "图片文件 (*.png *.jpg *.jpeg *.bmp);;所有文件 (*)",
                                                  options=options)
        if fileName:
            # 加载并显示选定的图片
            self.currentFileName = fileName
            pixmap = QPixmap(fileName)
            self.imageLabel.setPixmap(pixmap)
            self.imageLabel.setScaledContents(True)  # 自适应标签大小
            self.textBox.append("图片已上传！")  # 更新文本框内容

    def selectModel(self):
        # 弹出消息框选择模型
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setWindowTitle("选择模型")
        msgBox.setText("请选择要使用的YOLO模型")
        msgBox.setStyleSheet("""
            QMessageBox {
                background-color: #f0f0f0;
                font-size: 18px;
            }
            QMessageBox QLabel {
                color: #333;
            }
            QMessageBox QPushButton {
                font-size: 16px;
                background-color: #5cb85c;
                border: 2px solid #4cae4c;
                border-radius: 10px;
                padding: 5px 10px;
            }
            QMessageBox QPushButton:hover {
                background-color: #4cae4c;
            }
            QMessageBox QPushButton:pressed {
                background-color: #449d44;
            }
        """)
        yoloV8nButton = QPushButton("YOLOv8n模型")
        yoloV8lButton = QPushButton("YOLOv8l模型")
        yoloV8mButton = QPushButton("YOLOv8m模型")
        yoloV8sButton = QPushButton("YOLOv8s模型")

        yoloV8nButton.setStyleSheet(self.buttonStyleSheetForMsgBox())
        yoloV8lButton.setStyleSheet(self.buttonStyleSheetForMsgBox())
        yoloV8mButton.setStyleSheet(self.buttonStyleSheetForMsgBox())
        yoloV8sButton.setStyleSheet(self.buttonStyleSheetForMsgBox())

        msgBox.addButton(yoloV8nButton, QMessageBox.ActionRole)
        msgBox.addButton(yoloV8lButton, QMessageBox.ActionRole)
        msgBox.addButton(yoloV8mButton, QMessageBox.ActionRole)
        msgBox.addButton(yoloV8sButton, QMessageBox.ActionRole)
        msgBox.addButton(QMessageBox.Cancel)

        # 设置按钮之间的间距
        msgBox.layout().itemAt(0).widget().setContentsMargins(10, 10, 10, 10)

        # 显示消息框并等待用户选择
        msgBox.exec_()

        if msgBox.clickedButton() == yoloV8nButton:
            self.model = YOLO('yolov8n.pt').to('cpu')
            self.textBox.append("已选择 YOLOv8n 模型！")
        elif msgBox.clickedButton() == yoloV8lButton:
            self.model = YOLO('yolov8l.pt').to('cpu')
            self.textBox.append("已选择 YOLOv8l 模型！")
        elif msgBox.clickedButton() == yoloV8mButton:
            self.model = YOLO('yolov8m.pt').to('cpu')
            self.textBox.append("已选择 YOLOv8m 模型！")
        elif msgBox.clickedButton() == yoloV8sButton:
            self.model = YOLO('yolov8s.pt').to('cpu')
            self.textBox.append("已选择 YOLOv8s 模型！")

    def buttonStyleSheetForMsgBox(self):
        # 定义消息框按钮的样式
        return """
            QPushButton {
                font-size: 16px;
                color: white;
                background-color: #5cb85c;
                border: 2px solid #4cae4c;
                border-radius: 10px;
                padding: 5px 10px;
                margin: 5px 0;
            }
            QPushButton:hover {
                background-color: #d9534f;
            }
            QPushButton:pressed {
                background-color: #449d44;
            }
        """

    def autoCount(self):
        if hasattr(self, 'currentFileName'):
            # 使用YOLOv8模型进行实例分割
            results = self.model(self.currentFileName)

            # 确保results是一个列表
            if isinstance(results, list):
                results = results[0]

            # 获取分割后的图片
            result_image = results.plot()  # 使用plot()方法获取带有分割结果的图片

            # 将分割后的图片转换为QPixmap
            try:
                result_image = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
                height, width, channel = result_image.shape
                bytesPerLine = 3 * width
                self.result_image = result_image  # 保存结果图片数据以便后续使用
                qImg = QImage(result_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg)

                self.imageLabel.setPixmap(pixmap)
                self.imageLabel.setScaledContents(True)  # 自适应标签大小

                # 更新文本框内容为实例分割框的个数
                self.textBox.append(f"白粉病菌孢子的个数为：{len(results.boxes)} 个")
            except Exception as e:
                print(f"Error displaying image: {e}")

    def saveImage(self):
        if hasattr(self, 'result_image'):
            # 生成默认文件名
            default_file_name = f"result{self.save_count}" if self.save_count > 0 else "result"
            self.save_count += 1

            # 打开文件保存对话框
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(self, "保存图片", default_file_name,
                                                      "图片文件 (*.png *.jpg *.jpeg *.bmp);;所有文件 (*)",
                                                      options=options)
            if fileName:
                # 保存分割后的图片
                cv2.imwrite(fileName, cv2.cvtColor(self.result_image, cv2.COLOR_RGB2BGR))
                self.textBox.append(f"图片已保存：{fileName}")  # 更新文本框内容

    def returnLogin(self):
        # 返回登录界面
        self.loginWindow = LoginWindow()
        self.loginWindow.show()
        self.close()

    def exitSystem(self):
        QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
