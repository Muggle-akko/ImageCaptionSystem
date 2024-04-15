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
import hashlib

#百度翻译API调用
def translate_with_baidu(text, source_language='en', target_language='zh'):
    # 这里填入百度翻译API应用信息
    app_id = '20240406002016043'
    app_key = 'b2UhlL_ZcDSSClFhWlcC'

    url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    payload = {
        'q': text,
        'from': source_language,
        'to': target_language,
        'appid': app_id,
        'salt': 'random_salt',  # 随机数
        'sign': '',  # 签名
    }
    sign_str = app_id + text + 'random_salt' + app_key
    payload['sign'] = hashlib.md5(sign_str.encode()).hexdigest()

    response = requests.post(url, data=payload)
    translation = response.json()
    if 'error_code' in translation:
        print("Translation Error:", translation['error_code'])
        return None
    elif 'trans_result' in translation:
        return translation['trans_result'][0]['dst']
    else:
        return None

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

    frames_to_capture = 6  # 要截取的帧数
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
def generate_captioned_image(image, caption, font_size, font_color, chosen_position):
    draw = ImageDraw.Draw(image)  # 创建图像绘制对象
    chosen_font_path = "simhei.ttf"
    font = ImageFont.truetype(chosen_font_path, font_size)

    # 设置字体样式，将十六进制颜色值转换为 RGB 元组
    font_color = tuple(int(font_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))

    # 在图片下方添加字幕
    text_width, text_height = draw.textsize(caption, font=font)  # 获取字幕文本的宽度和高度
    image_width, image_height = image.size  # 获取图片的宽度和高度

    # 计算字幕文本的位置，使其位于图片中心的下方
    text_position = ((image_width - text_width) // 2, image_height - text_height - chosen_position)

    # 绘制字幕文本
    draw.text(text_position, caption, font=font, fill=font_color)

def video_predict():
    # 初始化 CaptionGenerator 实例
    checkpoint_paths = []  # 模型的checkpoint路径列表
    checkpoint_paths.append('checkpointA.pth')

    # 初始化数据
    caption_generator = captionGenerate.CaptionGenerator(checkpoint_paths)
    # 用于存放图片概述的列表
    generate_captions = []
    #用于存放原切片的列表
    images_origin = []
    # 用于存放处理后图片的列表
    images_to_show = []


    for filename in os.listdir("Frames"):
        # 拼接文件的完整路径
        file_path = os.path.join("Frames", filename)

        # 检查文件是否为图片文件
        if os.path.isfile(file_path) and filename.lower().endswith((".jpg", ".jpeg", ".png")):
            # 读取图像
            image_path = file_path
            image = Image.open(image_path)
            # 将上传的原始图片存到session中
            images_origin.append(image)
            st.session_state.images_origin = images_origin[:]

            result = caption_generator.generate_caption(image)

            for caption_item in result:
                # 使用翻译api将生成的字幕翻译为中文
                translated_result = translate_with_baidu(caption_item, source_language='en', target_language='zh')
                generate_captions.append(translated_result)
                # 将生成的字幕存到session中
                st.session_state.generate_captions = generate_captions[:]

                #设置字体参数
                font_size = 50
                font_color = "#000000"
                temp_image = image.copy()
                chosen_position = 70
                generate_captioned_image(temp_image, translated_result, font_size, font_color, chosen_position)
                # 将处理后的图片添加到待展示的图片列表中
                images_to_show.append(temp_image)
                if len(images_to_show) == 6:
                    st.image(images_to_show, width=350)
                    images_to_show = []


# Streamlit 应用程序
def main():
    st.title("视频故事概括")
    st.markdown("---")

    # 检查 caption_generated 变量是否在会话状态中，如果不存在则设置为 False
    if 'VideoCaption_generated' not in st.session_state:
        st.session_state.VideoCaption_generated = False

    #用于存放图片概述切片的列表
    images_origin = []

    # 默认字体列表
    default_fonts = {"黑体": "simhei.ttf", "微软雅黑": "msyhbd.ttc", "楷体": "simkai.ttf", "新宋体": "simsun.ttc"}

    vid_upload = st.file_uploader("📤 上传视频文件 (.mp4)", type=["mp4"])


    if vid_upload != None and not st.session_state.VideoCaption_generated:

        # 调用生成字幕的函数并获取结果
        with st.spinner(text="🖌️ 正在加载视频，请稍等..."):
            video_bytes = vid_upload.read()
            # 播放视频
            with open("temp_video.mp4", "wb") as f:
                f.write(video_bytes)
            # 获取视频文件的本地路径
            video_path = "temp_video.mp4"
            st.video(video_bytes)
            # 调用其他函数，并将视频路径作为参数传递
        with st.spinner(text="🖌️ 正在将视频切片，请稍等..."):
            videoProcess(video_path)
        with st.spinner(text="🖌️ 正在为切片生成概述，请稍等..."):
            video_predict()
            # 设置标志变量为 True，表示已生成字幕,防止页面重加载一直生成，同时显示字幕编辑选单
            st.session_state.VideoCaption_generated = True
            # 删除切帧的临时文件夹路径
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

    #用户自定义文字样式模块
    if st.session_state.VideoCaption_generated:
        # 字体样式选项
        chosen_font = st.selectbox("🗛 选择字体:", options=default_fonts)
        chosen_font_path = default_fonts[chosen_font]
        font_size = st.slider("🗚 选择字体大小:", min_value=10, max_value=100, step=2, value=25)
        chosen_position = st.slider("📝 调整文字位置:", min_value=10, max_value=500, step=5, value=50)
        font_color = st.color_picker("🎨 选择字体颜色:", "#000000")
        chosen_captions = st.session_state.generate_captions
        images_to_show = []
        if st.button("修改文字样式"):
            st.empty()  # 清空输出
            for index, images in enumerate(st.session_state.images_origin):
                if index < len(chosen_captions):
                    chosen_caption = chosen_captions[index]
                else:
                    chosen_caption = "字幕出错，请联系开发者"  # 防止读取错误程序终止的情况
                temp_image = images.copy()
                generate_captioned_image(temp_image, chosen_caption, font_size, font_color, chosen_position)
                images_to_show.append(temp_image)
                if len(images_to_show) == 6:
                    st.image(images_to_show, width=350)
                    images_to_show = []

if __name__ == "__main__":
    main()