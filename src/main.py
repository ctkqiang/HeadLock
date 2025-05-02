try:
    import cv2 as 计算机视觉_2
    import mediapipe as 媒体管道
    from tkinter import Tk, Label
    from PIL import Image, ImageTk
except ImportError:
    print("请先安装必要的库：pip3 install opencv-python mediapipe tkinter pillow")
    exit()


class 狙心介面:
    def __init__(self) -> None:
        super(狙心介面, self).__init__()

        self.前一横坐标 = None
        self.前一纵坐标 = None

        self.窗口 = Tk()
        self.窗口.title("狙心 · 中文编程")

        # 初始化人脸网格检测器
        self.面部网格模块 = 媒体管道.solutions.face_mesh
        self.面部检测器 = self.面部网格模块.FaceMesh(
            static_image_mode=False, max_num_faces=1, refine_landmarks=True
        )

        # FaceMesh 中额头中点的 landmark 编号
        self.额头点编号 = 10

        self.显示标签 = Label(self.窗口)
        self.显示标签.pack()

        self.摄像头 = 计算机视觉_2.VideoCapture(0)
        self.更新画面()
        self.窗口.protocol("WM_DELETE_WINDOW", self.关闭窗口)
        self.窗口.mainloop()

    def 画十字准星(self, 图像, 横坐标, 纵坐标, 颜色=(0, 255, 255), 粗细=3) -> None:
        高度, 宽度, _ = 图像.shape

        # 绘制竖线：贯穿上下
        计算机视觉_2.line(图像, (横坐标, 0), (横坐标, 高度), 颜色, 粗细)

        # 绘制横线：贯穿左右
        计算机视觉_2.line(图像, (0, 纵坐标), (宽度, 纵坐标), 颜色, 粗细)

    def 更新画面(self) -> None:
        成功与否, 当前帧 = self.摄像头.read()
        if not 成功与否:
            return

        彩色图像 = 计算机视觉_2.cvtColor(
            current_frame := 当前帧, 计算机视觉_2.COLOR_BGR2RGB
        )

        检测结果 = self.面部检测器.process(彩色图像)

        if 检测结果.multi_face_landmarks:
            高度, 宽度, _ = 当前帧.shape

            for 面部地标 in 检测结果.multi_face_landmarks:
                额头坐标 = 面部地标.landmark[self.额头点编号]
                x坐标 = int(额头坐标.x * 宽度)
                y坐标 = int(额头坐标.y * 高度)

                # 检测是否移动
                是否移动 = hasattr(self, "前一横坐标") and (
                    x坐标 != self.前一横坐标 or y坐标 != self.前一纵坐标
                )

                # 更新前一帧坐标
                self.前一横坐标 = x坐标
                self.前一纵坐标 = y坐标

                # 控制台打印
                print(f"\033[1;32mDetected:\033[0m \033[1;37mTrue\033[0m")
                print(f"\033[1;34mX:\033[0m \033[1;37m{x坐标}\033[0m")
                print(f"\033[1;36mY:\033[0m \033[1;37m{y坐标}\033[0m")
                print(f"\033[1;35mMOVEMENT:\033[0m \033[1;31m{是否移动}\033[0m")

                # 屏幕文字信息
                字体 = 计算机视觉_2.FONT_HERSHEY_SIMPLEX
                起始位置 = 30
                行距 = 30
                信息列表 = [
                    f"Detected: True",
                    f"X: {x坐标}",
                    f"Y: {y坐标}",
                    f"MOVEMENT: {是否移动}",
                ]

                for i, 信息 in enumerate(信息列表):
                    计算机视觉_2.putText(
                        当前帧,
                        信息,
                        (10, 起始位置 + i * 行距),
                        字体,
                        0.7,
                        (0, 0, 0),
                        4,
                    )

                # 画十字 + 中心线
                self.画十字准星(当前帧, x坐标, y坐标)

        图像RGB = 计算机视觉_2.cvtColor(当前帧, 计算机视觉_2.COLOR_BGR2RGB)
        图像对象 = Image.fromarray(图像RGB)
        Tk图像 = ImageTk.PhotoImage(image=图像对象)

        self.显示标签.imgtk = Tk图像
        self.显示标签.configure(image=Tk图像)

        self.窗口.after(10, self.更新画面)

    def 画十字中心到目标(self, 图像, 目标横, 目标纵, 颜色=(0, 0, 255), 粗细=1) -> None:
        高度, 宽度, _ = 图像.shape
        中心横 = 宽度 // 2
        中心纵 = 高度 // 2
        计算机视觉_2.line(图像, (中心横, 中心纵), (目标横, 目标纵), 颜色, 粗细)

    def 关闭窗口(self) -> None:
        self.摄像头.release()
        self.窗口.destroy()

    def 画中央十字瞄准线(self, 图像, 颜色=(0, 0, 255), 粗细=1) -> None:
        高度, 宽度, _ = 图像.shape
        中心横 = 宽度 // 2
        中心纵 = 高度 // 2

        # 纵向全贯穿
        计算机视觉_2.line(图像, (中心横, 0), (中心横, 高度), 颜色, 粗细)

        # 横向全贯穿
        计算机视觉_2.line(图像, (0, 中心纵), (宽度, 中心纵), 颜色, 粗细)


if __name__ == "__main__":
    狙心介面()
