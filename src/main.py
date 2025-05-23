try:
    import math
    import time
    import random
    import os
    import cv2 as 计算机视觉_2
    import mediapipe as 媒体管道
    import numpy as 数组处理库
    from tkinter import Tk, Label, Canvas
    from PIL import Image, ImageTk
    from PIL import ImageFont, ImageDraw
    import threading
    import queue
    import sounddevice as sd
    import numpy as np
except ImportError:
    print(
        "请先安装必要的库：pip3 install opencv-python mediapipe tkinter pillow sounddevice numpy"
    )
    exit()


class 终结者界面:
    def __init__(self) -> None:
        super(终结者界面, self).__init__()

        self.移动累计 = 0  # 记录移动强度
        self.心率 = 60  # 初始心率
        self.扫描线位置 = 0  # 扫描线初始位置
        self.扫描方向 = 1  # 扫描方向：1向下，-1向上
        self.目标锁定 = False  # 是否锁定目标
        self.系统启动时间 = time.time()  # 系统启动时间
        self.目标分析数据 = {}  # 目标分析数据
        self.威胁等级 = "低"  # 威胁等级评估

        self.前一横坐标 = None
        self.前一纵坐标 = None

        self.窗口 = Tk()
        self.窗口.title("终结者视觉系统 T-800")

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
        self.摄像头.set(计算机视觉_2.CAP_PROP_FRAME_WIDTH, 1200)
        self.摄像头.set(计算机视觉_2.CAP_PROP_FRAME_HEIGHT, 800)
        self.摄像头.set(计算机视觉_2.CAP_PROP_FPS, 15)
        self.更新画面()
        self.窗口.protocol("WM_DELETE_WINDOW", self.关闭窗口)
        self.窗口.mainloop()

    def 画中文文本(self, 图像, 文本, 位置, 字号=30, 颜色=(255, 0, 0)) -> None:
        当前目录 = os.path.dirname(os.path.realpath(__file__))
        字体路径 = os.path.join(
            当前目录, "..", "assets", "NotoSansSC-VariableFont_wght.ttf"
        )
        图像_pil = Image.fromarray(
            计算机视觉_2.cvtColor(图像, 计算机视觉_2.COLOR_BGR2RGB)
        )
        draw = ImageDraw.Draw(图像_pil)
        try:
            字体 = ImageFont.truetype(字体路径, 字号, encoding="utf-8")
        except OSError:
            print(f"字体文件未找到或无法打开: {字体路径}，将使用默认字体。")
            字体 = ImageFont.load_default()
        draw.text(位置, 文本, font=字体, fill=颜色[::-1])  # RGB 转为 BGR
        return 计算机视觉_2.cvtColor(
            数组处理库.array(图像_pil), 计算机视觉_2.COLOR_RGB2BGR
        )

    def 应用红色滤镜(self, 图像):
        """应用终结者红色视觉滤镜"""
        # 创建一个红色蒙版
        红色蒙版 = 数组处理库.zeros_like(图像)
        红色蒙版[:, :, 2] = 50  # 添加红色通道

        # 将原图转为灰度后再转为三通道
        灰度图 = 计算机视觉_2.cvtColor(图像, 计算机视觉_2.COLOR_BGR2GRAY)
        灰度图三通道 = 计算机视觉_2.cvtColor(灰度图, 计算机视觉_2.COLOR_GRAY2BGR)

        # 混合原图和红色蒙版
        结果 = 计算机视觉_2.addWeighted(灰度图三通道, 0.8, 红色蒙版, 0.3, 0)
        return 结果

    def 画目标锁定框(self, 图像, 横坐标, 纵坐标, 颜色=(0, 0, 255)):
        """绘制终结者风格的目标锁定框"""
        框大小 = 100
        线长 = 20
        厚度 = 2

        # 左上角
        计算机视觉_2.line(
            图像,
            (横坐标 - 框大小 // 2, 纵坐标 - 框大小 // 2),
            (横坐标 - 框大小 // 2 + 线长, 纵坐标 - 框大小 // 2),
            颜色,
            厚度,
        )
        计算机视觉_2.line(
            图像,
            (横坐标 - 框大小 // 2, 纵坐标 - 框大小 // 2),
            (横坐标 - 框大小 // 2, 纵坐标 - 框大小 // 2 + 线长),
            颜色,
            厚度,
        )

        # 右上角
        计算机视觉_2.line(
            图像,
            (横坐标 + 框大小 // 2, 纵坐标 - 框大小 // 2),
            (横坐标 + 框大小 // 2 - 线长, 纵坐标 - 框大小 // 2),
            颜色,
            厚度,
        )
        计算机视觉_2.line(
            图像,
            (横坐标 + 框大小 // 2, 纵坐标 - 框大小 // 2),
            (横坐标 + 框大小 // 2, 纵坐标 - 框大小 // 2 + 线长),
            颜色,
            厚度,
        )

        # 左下角
        计算机视觉_2.line(
            图像,
            (横坐标 - 框大小 // 2, 纵坐标 + 框大小 // 2),
            (横坐标 - 框大小 // 2 + 线长, 纵坐标 + 框大小 // 2),
            颜色,
            厚度,
        )
        计算机视觉_2.line(
            图像,
            (横坐标 - 框大小 // 2, 纵坐标 + 框大小 // 2),
            (横坐标 - 框大小 // 2, 纵坐标 + 框大小 // 2 - 线长),
            颜色,
            厚度,
        )

        # 右下角
        计算机视觉_2.line(
            图像,
            (横坐标 + 框大小 // 2, 纵坐标 + 框大小 // 2),
            (横坐标 + 框大小 // 2 - 线长, 纵坐标 + 框大小 // 2),
            颜色,
            厚度,
        )
        计算机视觉_2.line(
            图像,
            (横坐标 + 框大小 // 2, 纵坐标 + 框大小 // 2),
            (横坐标 + 框大小 // 2, 纵坐标 + 框大小 // 2 - 线长),
            颜色,
            厚度,
        )

        # 中心十字准星
        计算机视觉_2.line(图像, (横坐标 - 10, 纵坐标), (横坐标 + 10, 纵坐标), 颜色, 1)
        计算机视觉_2.line(图像, (横坐标, 纵坐标 - 10), (横坐标, 纵坐标 + 10), 颜色, 1)

        # 添加目标信息
        self.画中文文本(
            图像,
            "目标锁定",
            (横坐标 - 框大小 // 2, 纵坐标 - 框大小 // 2 - 30),
            字号=20,
            颜色=(0, 0, 255),
        )

        # 计算与中心的距离
        高度, 宽度, _ = 图像.shape
        中心横 = 宽度 // 2
        中心纵 = 高度 // 2
        距离 = int(math.sqrt((横坐标 - 中心横) ** 2 + (纵坐标 - 中心纵) ** 2))

        self.画中文文本(
            图像,
            f"距离: {距离}px",
            (横坐标 - 框大小 // 2, 纵坐标 + 框大小 // 2 + 10),
            字号=20,
            颜色=(0, 0, 255),
        )

    def 画扫描线(self, 图像):
        """绘制终结者风格的扫描线效果"""
        高度, 宽度, _ = 图像.shape

        # 更新扫描线位置
        self.扫描线位置 += 5 * self.扫描方向
        if self.扫描线位置 >= 高度:
            self.扫描方向 = -1
        elif self.扫描线位置 <= 0:
            self.扫描方向 = 1

        # 绘制红色扫描线
        计算机视觉_2.line(
            图像, (0, self.扫描线位置), (宽度, self.扫描线位置), (0, 0, 255), 1
        )

        # 添加扫描线上的红色小方块
        for i in range(0, 宽度, 50):
            if random.random() > 0.7:
                计算机视觉_2.rectangle(
                    图像,
                    (i, self.扫描线位置 - 2),
                    (i + random.randint(5, 20), self.扫描线位置 + 2),
                    (0, 0, 255),
                    -1,
                )

    def 画系统信息(self, 图像):
        """绘制终结者风格的系统信息"""
        高度, 宽度, _ = 图像.shape

        # 系统时间
        当前时间 = time.strftime("%H:%M:%S", time.localtime())
        运行时间 = int(time.time() - self.系统启动时间)

        # 伪造终结者风格的系统数据
        cpu温度 = f"{random.randint(45, 65)}°C"
        电池电量 = f"{random.randint(60, 100)}%"
        网络状态 = random.choice(["已连接", "弱信号", "断开"])
        目标编号 = f"ID-{random.randint(1000, 9999)}"
        系统警告 = random.choice(["无", "低电量", "高温", "异常信号"])

        # 左上角系统信息
        信息列表 = [
            f"T-800 视觉系统 v1.0",
            f"系统时间: {当前时间}",
            f"运行时间: {运行时间}s",
            f"扫描模式: 主动",
            f"威胁等级: {self.威胁等级}",
            f"CPU温度: {cpu温度}",
            f"电池电量: {电池电量}",
            f"网络状态: {网络状态}",
            f"目标编号: {目标编号}",
            f"系统警告: {系统警告}",
        ]

        # 绘制半透明背景
        覆盖层 = 图像.copy()
        计算机视觉_2.rectangle(覆盖层, (10, 10), (320, 270), (30, 30, 30), -1)
        透明度 = 0.6
        计算机视觉_2.addWeighted(覆盖层, 透明度, 图像, 1 - 透明度, 0, 图像)

        # 绘制信息（全部改为红色）
        for i, 信息 in enumerate(信息列表):
            图像 = self.画中文文本(
                图像, 信息, (20, 30 + i * 23), 字号=18, 颜色=(0, 0, 255)
            )

        # 右上角添加一些随机数据块，增强科技感
        数据块宽度 = 200
        计算机视觉_2.rectangle(
            覆盖层, (宽度 - 数据块宽度 - 10, 10), (宽度 - 10, 100), (30, 30, 30), -1
        )
        计算机视觉_2.addWeighted(覆盖层, 透明度, 图像, 1 - 透明度, 0, 图像)

        for i in range(5):
            随机数据 = "".join(random.choice("0123456789ABCDEF") for _ in range(16))
            图像 = self.画中文文本(
                图像,
                随机数据,
                (宽度 - 数据块宽度, 30 + i * 15),
                字号=15,
                颜色=(0, 0, 255),
            )

    def 画十字准星(self, 图像, 横坐标, 纵坐标, 颜色=(0, 0, 255), 粗细=3) -> None:
        高度, 宽度, _ = 图像.shape
        计算机视觉_2.line(图像, (横坐标, 0), (横坐标, 高度), 颜色, 粗细)
        计算机视觉_2.line(图像, (0, 纵坐标), (宽度, 纵坐标), 颜色, 粗细)
        半径 = 10
        计算机视觉_2.circle(图像, (横坐标, 纵坐标), 半径, 颜色, -1)

    def 画心跳动画(self, 图像, 心率):
        高度, 宽度, _ = 图像.shape
        区域宽度 = 200
        区域高度 = 60
        起始横 = 宽度 - 区域宽度 - 20
        起始纵 = 高度 - 区域高度 - 20

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

        点集 = []
        当前时间 = time.time()

        for i in range(区域宽度):
            频率 = 心率 / 60.0
            相位 = (当前时间 * 频率 * 2 * math.pi) + (i / 区域宽度) * 2 * math.pi
            y值 = int(区域高度 / 2 - 15 * math.sin(相位))

            if 40 < (i % 60) < 50:
                y值 -= int(20 * math.exp(-(((i % 60) - 45) ** 2) / 10))
            点集.append((起始横 + i, 起始纵 + y值 + 区域高度 // 2))
        for j in range(1, len(点集)):
            计算机视觉_2.line(图像, 点集[j - 1], 点集[j], (0, 0, 255), 2)

        图像 = self.画中文文本(
            图像,
            f"生命体征: {心率} BPM",
            (起始横 + 10, 起始纵 + 区域高度 - 30),
            字号=20,
            颜色=(0, 0, 255),
        )

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

    def 画旋转齿轮(self, 图像, 中心点, 半径, 颜色=(0, 0, 255), 粗细=2):
        """绘制旋转齿轮动画"""
        for 角度 in range(0, 360, 30):
            终点 = (
                int(中心点[0] + 半径 * math.cos(math.radians(角度))),
                int(中心点[1] + 半径 * math.sin(math.radians(角度))),
            )
            计算机视觉_2.line(图像, 中心点, 终点, 颜色, 粗细)

    def 画闪烁指示灯(self, 图像, 位置, 颜色=(0, 0, 255), 半径=5):
        """绘制闪烁指示灯"""
        if random.random() > 0.5:
            计算机视觉_2.circle(图像, 位置, 半径, 颜色, -1)

    def 画进度条(self, 图像, 位置, 长度, 进度, 颜色=(0, 0, 255), 高度=10):
        """绘制进度条"""
        计算机视觉_2.rectangle(
            图像, 位置, (位置[0] + 长度, 位置[1] + 高度), (50, 50, 50), -1
        )
        计算机视觉_2.rectangle(
            图像, 位置, (位置[0] + int(长度 * 进度), 位置[1] + 高度), 颜色, -1
        )

    def 更新画面(self) -> None:
        成功, 当前帧 = self.摄像头.read()
        if not 成功:
            return

        # 应用终结者红色视觉效果
        当前帧 = self.应用红色滤镜(当前帧)

        # 添加扫描线效果
        self.画扫描线(当前帧)

        # 添加系统信息
        self.画系统信息(当前帧)

        # 这里提前获取宽度和高度，避免后面未赋值
        高度, 宽度, _ = 当前帧.shape

        # 移除中央十字瞄准线
        # self.画中央十字瞄准线(当前帧, 颜色=(0, 255, 255), 粗细=1)

        彩色图像 = 计算机视觉_2.cvtColor(当前帧, 计算机视觉_2.COLOR_BGR2RGB)
        检测结果 = self.面部检测器.process(彩色图像)

        if 检测结果.multi_face_landmarks:
            高度, 宽度, _ = 当前帧.shape
            self.目标锁定 = True
            self.威胁等级 = random.choice(["低", "中", "高"])

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
                print("============================================")
                print(f"\033[1;32m目标检测:\033[0m \033[1;37m已锁定\033[0m")
                print(f"\033[1;34m坐标X:\033[0m \033[1;37m{横坐标}\033[0m")
                print(f"\033[1;36m坐标Y:\033[0m \033[1;37m{纵坐标}\033[0m")
                print(f"\033[1;35m目标移动:\033[0m \033[1;31m{是否移动}\033[0m")

                # 屏幕文字信息
                起始位置 = 高度 - 150
                行距 = 30
                信息列表 = [
                    f"目标状态: 已锁定",
                    f"坐标: X={横坐标} Y={纵坐标}",
                    f"移动状态: {'活动中' if 是否移动 else '静止'}",
                    f"威胁评估: {self.威胁等级}",
                ]

                # 绘制半透明背景
                覆盖层 = 当前帧.copy()
                计算机视觉_2.rectangle(
                    覆盖层, (10, 起始位置 - 30), (300, 起始位置 + 120), (30, 30, 30), -1
                )
                透明度 = 0.6
                计算机视觉_2.addWeighted(覆盖层, 透明度, 当前帧, 1 - 透明度, 0, 当前帧)

                for i, 信息 in enumerate(信息列表):
                    当前帧 = self.画中文文本(
                        当前帧,
                        信息,
                        (20, 起始位置 + i * 行距),
                        字号=20,
                        颜色=(0, 0, 255),
                    )

                # 画目标锁定框
                self.画目标锁定框(当前帧, 横坐标, 纵坐标, 颜色=(0, 0, 255))

                # 画红色十字准星跟随额头
                self.画十字准星(当前帧, 横坐标, 纵坐标, 颜色=(0, 0, 255), 粗细=2)

                # 从中心到目标画线
                中心横 = 宽度 // 2
                中心纵 = 高度 // 2

        else:
            self.目标锁定 = False
            self.威胁等级 = "未知"
            # 添加"搜索目标"文本（改为红色）
            当前帧 = self.画中文文本(
                当前帧,
                "搜索目标中...",
                (宽度 // 2 - 100, 高度 // 2 + 50),
                字号=30,
                颜色=(0, 0, 255),
            )

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

        # 添加终结者风格的瞄准框
        线长 = 15
        间隔 = 5

        # 左上
        计算机视觉_2.line(
            图像,
            (中心横 - 间隔 - 线长, 中心纵 - 间隔),
            (中心横 - 间隔, 中心纵 - 间隔),
            颜色,
            粗细,
        )
        计算机视觉_2.line(
            图像,
            (中心横 - 间隔, 中心纵 - 间隔 - 线长),
            (中心横 - 间隔, 中心纵 - 间隔),
            颜色,
            粗细,
        )

        # 右上
        计算机视觉_2.line(
            图像,
            (中心横 + 间隔, 中心纵 - 间隔),
            (中心横 + 间隔 + 线长, 中心纵 - 间隔),
            颜色,
            粗细,
        )
        计算机视觉_2.line(
            图像,
            (中心横 + 间隔, 中心纵 - 间隔 - 线长),
            (中心横 + 间隔, 中心纵 - 间隔),
            颜色,
            粗细,
        )

        # 左下
        计算机视觉_2.line(
            图像,
            (中心横 - 间隔 - 线长, 中心纵 + 间隔),
            (中心横 - 间隔, 中心纵 + 间隔),
            颜色,
            粗细,
        )
        计算机视觉_2.line(
            图像,
            (中心横 - 间隔, 中心纵 + 间隔),
            (中心横 - 间隔, 中心纵 + 间隔 + 线长),
            颜色,
            粗细,
        )

        # 右下
        计算机视觉_2.line(
            图像,
            (中心横 + 间隔, 中心纵 + 间隔),
            (中心横 + 间隔 + 线长, 中心纵 + 间隔),
            颜色,
            粗细,
        )
        计算机视觉_2.line(
            图像,
            (中心横 + 间隔, 中心纵 + 间隔),
            (中心横 + 间隔, 中心纵 + 间隔 + 线长),
            颜色,
            粗细,
        )

    def 采集音频(self):
        """采集麦克风音频数据并放入音频队列"""
        try:
            while True:
                音频数据 = sd.rec(
                    int(0.05 * 16000), samplerate=16000, channels=1, dtype="float32"
                )
                sd.wait()
                音频数据 = 音频数据.flatten()
                self.音频队列.put(音频数据)
        except Exception as e:
            print(f"音频采集异常: {e}")

    def 更新波形(self):
        # 从队列取最新音频数据
        while not self.音频队列.empty():
            self.音频波形 = self.音频队列.get()
        # 清空画布
        self.波形画布.delete("all")
        h = 80
        w = 400
        if self.音频波形 is not None and len(self.音频波形) > 0:
            # 归一化
            norm = np.abs(self.音频波形) / (np.max(np.abs(self.音频波形)) + 1e-6)
            points = []
            for i, v in enumerate(norm):
                x = i * w / len(norm)
                y = h / 2 - v * (h / 2 - 5)
                points.append((x, y))
            for i in range(len(points) - 1):
                self.波形画布.create_line(
                    points[i][0],
                    points[i][1],
                    points[i + 1][0],
                    points[i + 1][1],
                    fill="#ff0033",
                    width=2,
                )
        self.窗口.after(30, self.更新波形)


if __name__ == "__main__":
    终结者界面()
