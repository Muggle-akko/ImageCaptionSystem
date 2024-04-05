import streamlit as st
from PIL import Image
import requests
import io
from io import BytesIO
from PIL import ImageDraw
from PIL import ImageFont
import captionGenerate
from googletrans import Translator
from st_pages import Page, Section, show_pages, add_page_title, hide_pages

# 标题
st.markdown("<h1 style='text-align: center;'>图像字幕生成系统</h1>", unsafe_allow_html=True)

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

#页面功能控制
show_pages(
    [
        Page("App.py", "图像字幕生成", "🖼️"),
        Page("VideoApp.py", "视频情节概览", "🎞️︎",in_section=True),
        Page("About.py", "关于", "💻", in_section=True),
    ])

# 检查 caption_generated 变量是否在会话状态中，如果不存在则设置为 False
if 'caption_generated' not in st.session_state:
    st.session_state.caption_generated = False

# URL输入框
url_input = st.text_input("🔗 请输入图片URL，并按回车键确认:")
if (url_input != "") and (url_input != None):
    response = requests.get(url_input)
    image = Image.open(BytesIO(response.content))
    st.image(image, caption='图片上传成功！')


# 检查图片格式函数
def check_image_format(image):
    try:
        img = Image.open(io.BytesIO(image))
        img.verify()
        return True
    except Exception as e:
        return False


# 导入本地图片按钮
uploaded_file = st.file_uploader("📤 或者，您可以点击右侧按钮导入本地图片:", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 使用本地上传的图片
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption='图片上传成功！')
    except:
        st.error("图片上传失败，请上传有效的图片格式！")

# 显示测试用的默认字幕
#default_captions = ["正在投出棒球的男人", "穿着棒球服的男人在球场上", "一个带着鸭舌帽男人在投球"]
default_captions = []
# 默认字体列表
default_fonts = {"黑体": "simhei.ttf", "微软雅黑": "msyhbd.ttc", "楷体": "simkai.ttf", "新宋体": "simsun.ttc"}


# 定义生成图片字幕的函数
def generate_captioned_image(image, caption, font_size, font_color):
    draw = ImageDraw.Draw(image)  # 创建图像绘制对象
    font = ImageFont.truetype(chosen_font_path, font_size)  # 指定字体和大小，使用 Arial 字体

    # 设置字体样式，将十六进制颜色值转换为 RGB 元组
    font_color = tuple(int(font_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))

    # 在图片下方添加字幕
    text_width, text_height = draw.textsize(caption, font=font)  # 获取字幕文本的宽度和高度
    image_width, image_height = image.size  # 获取图片的宽度和高度

    # 计算字幕文本的位置，使其位于图片中心的下方
    text_position = ((image_width - text_width) // 2, image_height - text_height - 10)

    # 绘制字幕文本
    draw.text(text_position, caption, font=font, fill=font_color)

#语言选择
LanguageOptions = st.multiselect(
     '💬 请选择生成字幕的语言（默认只生成英文）：',
     ('中文', 'English'))
#模型选择
ModelOptions = st.multiselect(
     '💡 请选择生成字幕的模型（默认只选择模型A，后面是其准确率）：',
     ('模型A，✔️73.4%', '模型B，✔️70.6%','模型C，✔️71.1%'))

# 导入图片后执行
if st.button("生成图像字幕"):
    if 'image' in locals():
        if not st.session_state.caption_generated:
            # 调用生成字幕的函数并获取结果
            with st.spinner(text="🖌️ 正在生成字幕，请稍等..."):
                # 初始化 CaptionGenerator 实例 todo:不要每次生成都初始化一次
                checkpoint_paths = []  # 模型的checkpoint路径列表
                if '模型A，✔️73.4%' in ModelOptions:
                    checkpoint_paths.append('checkpointA.pth')
                if '模型B，✔️70.6%' in ModelOptions:
                    checkpoint_paths.append('checkpointB.pth')
                if '模型C，✔️71.1%' in ModelOptions:
                    checkpoint_paths.append('checkpointC.pth')
                #默认加载模型A
                if len(ModelOptions) == 0:
                    checkpoint_paths.append('checkpointA.pth')

                caption_generator = captionGenerate.CaptionGenerator(checkpoint_paths)
                result = caption_generator.generate_caption(image)

                #判断用户选择了生成哪种语言的字幕
                if '中文' in LanguageOptions:
                    for caption_item in result:
                        # 使用翻译api将生成的字幕翻译为中文
                        translator = Translator()
                        translated_result = translator.translate(caption_item, src='en', dest='zh-cn').text
                        # 添加翻译后的结果到默认字幕列表中
                        default_captions.append(translated_result)
                if 'English' in LanguageOptions:
                    for caption_item in result:
                        default_captions.append(caption_item)
                #用户没选择，默认生成英文
                if len(LanguageOptions) == 0:
                    for caption_item in result:
                        default_captions.append(caption_item)

                # 将生成的字幕存到session中
                st.session_state.default_captions = default_captions[:]

                # 设置标志变量为 True，表示已生成字幕,防止页面重加载一直生成，同时显示字幕编辑选单
                st.session_state.caption_generated = True

            st.success("字幕生成成功！")
    else:
        st.warning("请上传图片后再操作！")

# 显示字幕编辑选单
if st.session_state.caption_generated:
        chosen_caption = st.selectbox("🖼️ 请选择一条图片字幕以嵌入到图片中：", options=st.session_state.default_captions)
        chosen_font = st.selectbox("🗛 选择字体:", options=default_fonts)
        chosen_font_path = default_fonts[chosen_font]

        # 字体样式选项
        font_size = st.slider("🗚 选择字体大小:", min_value=10, max_value=50, step=2, value=25)
        font_color = st.color_picker("🎨 选择字体颜色:", "#000000")
        if st.button("嵌入字幕到图片"):
            st.empty()  # 清空输出
            generate_captioned_image(image, chosen_caption, font_size, font_color)
            st.image(image, caption='已更新为嵌入图像字幕后的图像！')