import streamlit as st
import cv2
import os
from PIL import Image
import captionGenerate
import requests
import io
from io import BytesIO
from PIL import ImageDraw
from PIL import ImageFont
from st_pages import Page, Section, show_pages, add_page_title, hide_pages
import mysql.connector
from mysql.connector import Error
import time

def videoProcess(path):
    '''读取mp4文件并进行分割'''
    cam = cv2.VideoCapture(path)
    try:
        # 创建名为data的文件夹
        if not os.path.exists('Frames'):
            os.makedirs('Frames')
            print('成功创建切帧文件夹')

    # 如果未创建，则引发错误
    except OSError:
        print('Error: 创建切帧文件夹时错误！')

    # 定义保存图片函数
    # image:要保存的图片名字
    # addr；图片地址与相片名字的前部分
    # num: 相片，名字的后缀。int 类型
    def save_image(image, addr, num):
        address = addr + str(num) + '.jpg'
        cv2.imwrite(address, image)

    # 获取视频的总帧数
    total_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))

    frames_to_capture = 3  # 要截取的帧数
    interval = total_frames // frames_to_capture  # 计算截取帧的间隔

    i = 0
    frame_index = 0
    while i < frames_to_capture:
        # 设置视频的帧索引
        cam.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cam.read()
        if not ret:
            break  # 如果无法读取帧，停止循环
        save_image(frame, './Frames/', i + 1)
        i += 1
        # 更新下一个要读取的帧的索引
        frame_index += interval

    cam.release()
    cv2.destroyAllWindows()

# 定义嵌入图片字幕的函数
def generate_captioned_image(image, caption, font_size, font_color):
    draw = ImageDraw.Draw(image)  # 创建图像绘制对象
    chosen_font_path = "simhei.ttf"
    font = ImageFont.truetype(chosen_font_path, font_size)

    # 设置字体样式，将十六进制颜色值转换为 RGB 元组
    font_color = tuple(int(font_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))

    # 在图片下方添加字幕
    text_width, text_height = draw.textsize(caption, font=font)  # 获取字幕文本的宽度和高度
    image_width, image_height = image.size  # 获取图片的宽度和高度

    # 计算字幕文本的位置，使其位于图片中心的下方
    text_position = ((image_width - text_width) // 2, image_height - text_height - 70)

    # 绘制字幕文本
    draw.text(text_position, caption, font=font, fill=font_color)

def video_predict():
    st.markdown('#### 视频描述:')

    # 初始化 CaptionGenerator 实例
    checkpoint_paths = []  # 模型的checkpoint路径列表
    checkpoint_paths.append('checkpointA.pth')

    # 初始化 Captions
    captions = []

    for filename in os.listdir("Frames"):
        # 拼接文件的完整路径
        file_path = os.path.join("Frames", filename)

        # 检查文件是否为图片文件
        if os.path.isfile(file_path) and filename.lower().endswith((".jpg", ".jpeg", ".png")):
            # 读取图像
            image_path = file_path
            image = Image.open(image_path)
            caption_generator = captionGenerate.CaptionGenerator(checkpoint_paths)
            result = caption_generator.generate_caption(image)
            for caption_item in result:
                font_size = 22
                font_color = "#FFFFFF"
                generate_captioned_image(image, caption_item, font_size, font_color)
                st.image(image,width = 500)


# Streamlit 应用程序
def main():
    st.title("视频故事概括")
    st.markdown("---")

    vid_upload = st.file_uploader("📤 上传视频文件 (.mp4)", type=["mp4"])

    if vid_upload != None:
        video_bytes = vid_upload.read()
        # 播放视频
        with open("temp_video.mp4", "wb") as f:
            f.write(video_bytes)
        # 获取视频文件的本地路径
        video_path = "temp_video.mp4"
        st.video(video_bytes)
        # 调用其他函数，并将视频路径作为参数传递
        videoProcess(video_path)
        video_predict()

        # 删除切帧的文件夹路径
        folder_path = 'Frames'
        try:
            # 清空文件夹内的内容
            files = os.listdir(folder_path)
            for file in files:
                file_path = os.path.join(folder_path, file)
                os.remove(file_path)
             # 删除文件夹及其内容
            os.rmdir(folder_path)
            print("切帧文件夹删除成功")
        except OSError as e:
            print(f"切帧删除文件夹失败: {e}")

if __name__ == "__main__":
    main()