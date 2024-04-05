import streamlit as st


# 添加自定义 CSS 样式以更改网页背景颜色
st.markdown(
    """
    <style>
    body {
        background-color: #FAF0E6; /* 米白色 */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
### ⭐关于

你好，我是合肥工业大学宣城校区的巫佳聪，这个项目是我的毕业设计，主要用于为用户上传的图片生成符合图像内容的字幕描述，
并且用户可以个性化一些相关的参数.同时该项目还提供将用户上传的视频进行提取片段，分别生成字幕以达到概括影片内容的功
能，有任何使用上的问题请联系作者邮箱：artRAM@163.com ，祝您使用愉快！

### 🍞模型训练

- 使用Transformer模型进行训练，训练源码引用自github上🔗 <a href="https://github.com/saahiluppal/catr" >catr的开源项目</a>
- 训练数据集来自于COCO2017，训练数据等将后续补充...

### 🛠️技术推荐

- streamlit, 一款好用的轻量化python前端框架
- st_pages, streamlit支持的多页面管理包

""", unsafe_allow_html=True)

