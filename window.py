import tkinter as tk
import cv2
from tkinter import filedialog
from PIL import Image, ImageTk
import  main

# 模拟的getcarid接口，用于识别车牌号
def getcarid(image):
    return main.detect(image)


# 创建视频界面
def create_videogui(main_window):
    def select_video():
        # 打开文件对话框，让用户选择视频文件
        video_path = filedialog.askopenfilename(filetypes=[('Video Files', '*.mp4;*.swf;*.mkv;*.avi')])
        # 调用getcarid接口获取车牌号
        plate_number = getcarid(video_path)
        # 显示识别结果
        result_label.config(text='车牌号：' + plate_number)
        # 显示选择的视频
        play_video(video_path)

    # 播放视频
    def play_video(video_path):
        # 使用OpenCV读取视频文件
        cap = cv2.VideoCapture(video_path)

        def update_frame():
            nonlocal cap
            # 读取视频帧
            ret, frame = cap.read()
            if ret:
                # 将视频帧转换为PIL图像
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                # 创建图像对象
                photo = ImageTk.PhotoImage(image)
                # 在视频区域显示图像
                video_label.config(image=photo)
                video_label.image = photo

                # 控制视频帧率
                window.after(30, update_frame)
            else:
                # 视频播放结束
                cap.release()

        update_frame()
    def close_videogui():
        window.destroy()
        main_window.destroy()  # 销毁主界面
    # 创建窗口
    window = tk.Toplevel(main_window)
    window.title('视频界面')
    window.geometry("500x500")

    # 创建按钮、标签和视频区域
    select_button = tk.Button(window, text='选择视频', command=select_video)
    select_button.pack()

    close_button = tk.Button(window, text='关闭', command=close_videogui)
    close_button.grid(row=0, column=1, padx=10, pady=10)

    result_label = tk.Label(window, text='车牌号：')
    result_label.pack()

    video_label = tk.Label(window)
    video_label.pack()


# 创建图片界面
def create_picturegui(main_window):
    def display_image(ipath):
        # 打开图片文件
        image = Image.open(ipath)
        # 调整图片大小
        image = image.resize((300, 200), Image.ANTIALIAS)
        # 创建图片对象
        photo = ImageTk.PhotoImage(image)
        # 在图片区域显示图片
        image_label.config(image=photo)
        image_label.image = photo

    def select_image():
        # 打开文件对话框，让用户选择图片文件
        image_path = filedialog.askopenfilename(filetypes=[('Image Files', '*.jpg;*.png;*.jpeg;*.bmp')])
        # 调用getcarid接口获取车牌号
        plate_number = getcarid(image_path)
        # 显示识别结果
        result_label.config(text='车牌号：' + plate_number)
        # 显示选择的图片
        display_image(image_path)

    def close_picturegui():
        window.destroy()
        main_window.destroy()  # 销毁主界面

    # 创建窗口
    window = tk.Toplevel(main_window)
    window.title('图片界面')

    # 获取屏幕的宽度和高度
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 设置窗口的大小和位置
    window_width = 600
    window_height = 500
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 创建选择图片按钮
    select_button = tk.Button(window, text='选择图片', command=select_image)
    select_button.grid(row=0, column=0, padx=10, pady=10)
    # 创建关闭按钮
    close_button = tk.Button(window, text='关闭', command=close_picturegui)
    close_button.grid(row=0, column=2, padx=10, pady=10)
    # 创建标签
    result_label = tk.Label(window, text='车牌号：')
    result_label.grid(row=1, column=0, padx=10, pady=10)
    # 创建图片区域
    image_label = tk.Label(window)
    image_label.grid(row=2, column=1, padx=10, pady=10)




def create_mainbroad():
    new_window = tk.Tk()
    new_window.title('车牌号识别')

    # 获取屏幕的宽度和高度
    screen_width = new_window.winfo_screenwidth()
    screen_height = new_window.winfo_screenheight()

    # 设置窗口的大小和位置
    new_window_width = 400
    new_window_height = 300
    x = (screen_width - new_window_width) // 2
    y = (screen_height - new_window_height) // 2
    new_window.geometry(f"{new_window_width}x{new_window_height}+{x}+{y}")

    def open_videogui():
        create_videogui(new_window)
        new_window.withdraw()

    def open_picturegui():
        create_picturegui(new_window)
        new_window.withdraw()
    button1 = tk.Button(new_window, text='视频', command=open_videogui)
    button1.pack()

    button2 = tk.Button(new_window, text='图片', command=open_picturegui)
    button2.pack()

    close_button = tk.Button(new_window, text='关闭', command=new_window.destroy)
    close_button.pack()

    new_window.mainloop()


if __name__ == '__main__':
    create_mainbroad()
