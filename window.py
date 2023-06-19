import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import main


# getcarid接口，用于识别车牌号
def getcarid(image):
    return main.detect(image)


# 创建图片界面
def create_picturegui():
    def display_image(ipath):
        # 打开图片文件
        imagepicture = Image.open(ipath)
        # 调整图片大小
        imagepicture = imagepicture.resize((300, 200), Image.ANTIALIAS)
        # 创建图片对象
        photo = ImageTk.PhotoImage(imagepicture)
        # 在图片区域显示图片
        imagepicture_label.config(image=photo)
        imagepicture_label.image = photo

    def select_image():
        # 打开文件对话框，让用户选择图片文件
        image_path = filedialog.askopenfilename(filetypes=[('Image Files', '*.jpg;*.png;*.jpeg;*.bmp')])
        # 调用getcarid接口获取车牌号
        plate_number,color = getcarid(image_path)
        # 显示识别结果
        result_labelid.config(text='车牌号：' + plate_number)
        result_labelcolor.config(text='车牌颜色：' + color)
        # 显示选择的图片
        display_image(image_path)

    # 创建窗口
    window = tk.Tk()
    window.title('车牌号识别系统')

    # 获取屏幕的宽度和高度
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 打开图片文件
    imagebackground_path = "background.png"
    imagegui = Image.open(imagebackground_path)
    # 调整图片大小
    imagegui = imagegui.resize((600, 100), Image.ANTIALIAS)

    # 创建图片对象
    photo = ImageTk.PhotoImage(imagegui)

    # 创建Label组件并显示图片
    imagebackground_label = tk.Label(window, image=photo)
    imagebackground_label.grid()

    # 设置窗口的大小和位置
    window_width = 600
    window_height = 500
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 创建选择图片按钮
    select_button = tk.Button(window, text='选择图片', command=select_image, height=2, width=20)
    select_button.grid(row=0, column=0, padx=10, pady=10)
    # 创建字体对象并设置字体大小
    font = ("Helvetica", 14)
    # 创建车牌号标签
    result_labelid = tk.Label(window, text='车牌号：', font=font)
    result_labelid.grid(row=1, column=0, padx=10, pady=10)
    # 创建车牌颜色标签
    result_labelcolor = tk.Label(window, text='车牌颜色：', font=font)
    result_labelcolor.grid(row=2, column=0, padx=10, pady=10)

    # 创建图片区域
    imagepicture_label = tk.Label(window)
    imagepicture_label.grid(row=3, column=0, padx=10, pady=10)

    # 进入循环
    window.mainloop()
