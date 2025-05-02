try:
    import math
    import time
    import random
    import os
    import cv2 as 计算机视觉_2
    import mediapipe as 媒体管道
    import numpy as 数组处理库
    from tkinter import Tk, Label
    from PIL import Image, ImageTk
    from PIL import ImageFont, ImageDraw
except ImportError:
    print("请先安装必要的库：pip3 install opencv-python mediapipe tkinter pillow")
    exit()


class 狙心界面:
    def __init__(self) -> None:
        super(狙心界面, self).__init__()

        self.移动累计 = 0  # 记录移动强度
        self.心率 = 60  # 初始心率

        self.前一横坐标 = None
        self.前一纵坐标 = None

        self.窗口 = Tk()
        self.窗口.title("狙心 · 中文编程")

        # 初始化人脸网格检测器
        self.面部网格模块 = 媒体管道.solutions.face_mesh
        self.面部检测器 = self.面部网格模块.FaceMesh(
            static_image_mode=False, max_num_faces=1, refine_landmarks=True
        )

        # FaceMesh 中额头中点的地标编号
        self.额头点编号 = 10

        self.显示标签 = Label(self.窗口)
        self.显示标签.pack()

        self.摄像头 = 计算机视觉_2.VideoCapture(0)
        self.更新画面()
        self.窗口.protocol("WM_DELETE_WINDOW", self.关闭窗口)
        self.窗口.mainloop()

    def 画中文文本(self, 图像, 文本, 位置, 字号=30, 颜色=(255, 0, 0)) -> None:
        # 获取当前脚本的目录
        当前目录 = os.path.dirname(os.path.realpath(__file__))

        # 计算字体文件的路径（assets/font.ttf）
        字体路径 = os.path.join(
            当前目录, "..", "assets", "NotoSansSC-VariableFont_wght.ttf"
        )

        # 转换为 PIL 的图像格式
        图像_pil = Image.fromarray(
            计算机视觉_2.cvtColor(图像, 计算机视觉_2.COLOR_BGR2RGB)
        )

        draw = ImageDraw.Draw(图像_pil)

        # 加载字体（确保路径正确）
        字体 = ImageFont.truetype(字体路径, 字号, encoding="utf-8")

        # 绘制中文文本
        draw.text(位置, 文本, font=字体, fill=颜色[::-1])  # RGB 转为 BGR

        # 转换回 OpenCV 格式
        return 计算机视觉_2.cvtColor(
            数组处理库.array(图像_pil), 计算机视觉_2.COLOR_RGB2BGR
        )

    def 画十字准星(self, 图像, 横坐标, 纵坐标, 颜色=(0, 0, 255), 粗细=3) -> None:
        高度, 宽度, _ = 图像.shape

        # 绘制竖线：贯穿上下
        计算机视觉_2.line(图像, (横坐标, 0), (横坐标, 高度), 颜色, 粗细)

        # 绘制横线：贯穿左右
        计算机视觉_2.line(图像, (0, 纵坐标), (宽度, 纵坐标), 颜色, 粗细)

        # 在交点处画一个圆圈，点缀中轴线
        半径 = 10
        计算机视觉_2.circle(图像, (横坐标, 纵坐标), 半径, 颜色, -1)  # -1 表示填充圆圈

    def 画心跳动画(self, 图像, 心率):
        # 右下角心电图动画
        高度, 宽度, _ = 图像.shape
        区域宽度 = 200
        区域高度 = 60
        起始横 = 宽度 - 区域宽度 - 20
        起始纵 = 高度 - 区域高度 - 20

        # 绘制半透明背景矩形
        覆盖层 = 图像.copy()
        cv2 = 计算机视觉_2
        计算机视觉_2.rectangle(
            覆盖层,
            (起始横, 起始纵),
            (起始横 + 区域宽度, 起始纵 + 区域高度),
            (30, 30, 30),
            -1,
        )
        透明度 = 0.4
        计算机视觉_2.addWeighted(覆盖层, 透明度, 图像, 1 - 透明度, 0, 图像)

        # 绘制心电波形
        点集 = []
        当前时间 = time.time()

        for i in range(区域宽度):
            # 心率决定波形频率
            频率 = 心率 / 60.0
            # 简单正弦+尖峰模拟心电波
            相位 = (当前时间 * 频率 * 2 * math.pi) + (i / 区域宽度) * 2 * math.pi
            y值 = int(区域高度 / 2 - 15 * math.sin(相位))

            # 加入“心跳”尖峰
            if 40 < (i % 60) < 50:
                y值 -= int(20 * math.exp(-(((i % 60) - 45) ** 2) / 10))
            点集.append((起始横 + i, 起始纵 + y值 + 区域高度 // 2))
        for j in range(1, len(点集)):
            计算机视觉_2.line(图像, 点集[j - 1], 点集[j], (0, 0, 255), 2)

        图像 = self.画中文文本(
            图像,
            f"心率: {心率} 次/分",
            (起始横 + 10, 起始纵 + 区域高度 - 30),
            字号=28,
            颜色=(0, 0, 255),
        )

        # 绘制爱心图标
        中心点 = (起始横 + 区域宽度 - 30, 起始纵 + 20)
        计算机视觉_2.circle(图像, (中心点[0] - 7, 中心点[1]), 7, (0, 0, 255), -1)
        计算机视觉_2.circle(图像, (中心点[0] + 7, 中心点[1]), 7, (0, 0, 255), -1)
        爱心点 = 数组处理库.array(
            [
                [中心点[0] - 14, 中心点[1]],
                [中心点[0], 中心点[1] + 18],
                [中心点[0] + 14, 中心点[1]],
            ],
            数组处理库.int32,
        )
        计算机视觉_2.fillPoly(图像, [爱心点], (0, 0, 255))

    def 更新画面(self) -> None:
        成功, 当前帧 = self.摄像头.read()
        if not 成功:
            return

        彩色图像 = 计算机视觉_2.cvtColor(当前帧, 计算机视觉_2.COLOR_BGR2RGB)

        检测结果 = self.面部检测器.process(彩色图像)

        if 检测结果.multi_face_landmarks:
            高度, 宽度, _ = 当前帧.shape

            for 面部地标 in 检测结果.multi_face_landmarks:
                额头坐标 = 面部地标.landmark[self.额头点编号]
                横坐标 = int(额头坐标.x * 宽度)
                纵坐标 = int(额头坐标.y * 高度)

                # 检测是否移动
                是否移动 = hasattr(self, "前一横坐标") and (
                    横坐标 != self.前一横坐标 or 纵坐标 != self.前一纵坐标
                )

                # 计算移动距离并更新心率
                移动距离 = 0
                if self.前一横坐标 is not None and self.前一纵坐标 is not None:
                    移动距离 = abs(横坐标 - self.前一横坐标) + abs(
                        纵坐标 - self.前一纵坐标
                    )
                self.移动累计 = min(self.移动累计 * 0.9 + 移动距离, 1000)  # 衰减+累加
                self.心率 = int(60 + min(self.移动累计 * 0.1, 100))  # 60~160

                # 更新前一帧坐标
                self.前一横坐标 = 横坐标
                self.前一纵坐标 = 纵坐标

                # 控制台打印
                print(f"\033[1;32m检测到头部:\033[0m \033[1;37m是\033[0m")
                print(f"\033[1;34m横坐标:\033[0m \033[1;37m{横坐标}\033[0m")
                print(f"\033[1;36m纵坐标:\033[0m \033[1;37m{纵坐标}\033[0m")
                print(f"\033[1;35m是否移动:\033[0m \033[1;31m{是否移动}\033[0m")

                # 屏幕文字信息
                起始位置 = 30
                行距 = 30
                信息列表 = [
                    f"检测到头部: 是",
                    f"横坐标: {横坐标}",
                    f"纵坐标: {纵坐标}",
                    f"是否移动: {是否移动}",
                ]

                随机星星 = [
                    (random.randint(0, 宽度), random.randint(0, 高度))
                    for _ in range(20)
                ]
                for x, y in 随机星星:
                    计算机视觉_2.circle(当前帧, (x, y), 2, (255, 255, 255), -1)

                for i, 信息 in enumerate(信息列表):
                    当前帧 = self.画中文文本(
                        当前帧,
                        信息,
                        (10, 起始位置 + i * 行距),
                        字号=28,
                        颜色=(0, 0, 0),
                    )

                # 画十字准星
                self.画十字准星(当前帧, 横坐标, 纵坐标)

        # 无论是否检测到人脸都绘制心跳动画
        self.画心跳动画(当前帧, self.心率)

        图像RGB = 计算机视觉_2.cvtColor(当前帧, 计算机视觉_2.COLOR_BGR2RGB)
        图像对象 = Image.fromarray(图像RGB)
        Tk图像 = ImageTk.PhotoImage(image=图像对象)

        self.显示标签.imgtk = Tk图像
        self.显示标签.configure(image=Tk图像)

        self.窗口.after(5, self.更新画面)

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
    狙心界面()
