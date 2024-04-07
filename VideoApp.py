import streamlit as st
import cv2
import os
from PIL import Image
from captionGenerate import CaptionGenerator  # 假设你有用于生成字幕的模块


def videoProcess(path):
    '''读取mp4文件并进行分割'''
    cam = cv2.VideoCapture(path)
    try:
        # 创建名为data的文件夹
        if not os.path.exists('Images'):
            os.makedirs('Images')
            print('created successfully ')

    # 如果未创建，则引发错误
    except OSError:
        print('Error: Creating directory of data')

    # 定义保存图片函数
    # image:要保存的图片名字
    # addr；图片地址与相片名字的前部分
    # num: 相片，名字的后缀。int 类型
    def save_image(image, addr, num):
        address = addr + str(num) + '.jpg'
        cv2.imwrite(address, image)

    # reading from frame
    ret, frame = cam.read()  # ret为布尔值 frame保存着视频中的每一帧图像 是个三维矩阵
    i = 0
    timeF = 60  # 设置要保存图像的间隔 60为每隔60帧保存一张图像
    j = 0
    while ret:
        i = i + 1
        # 如果视频仍然存在，继续创建图像
        if i % timeF == 0:
            # 呈现输出图片的数量
            j = j + 1
            save_image(frame, './Images/', j)
            print('save image:', j)
        ret, frame = cam.read()
        # 一旦完成释放所有的空间和窗口
    cam.release()
    cv2.destroyAllWindows()


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

    if uploaded_video is not None:
        st.video(uploaded_video)

        # 为视频生成字幕
        captions = generate_captions(uploaded_video)

        # 显示带有字幕的图像
        # for frame, caption in captions:
        #     st.image(frame, caption=caption)
        for frame in captions:
            st.image(frame)

if __name__ == "__main__":
    main()