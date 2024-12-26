import pyecharts.charts
import pypinyin
import streamlit as st
import streamlit_echarts as st_echarts
import requests
from bs4 import BeautifulSoup
import jieba
from pyecharts.charts import Funnel
from pyecharts.charts import Bar, WordCloud, Map, Boxplot
# steamlit中嵌入pyechats前端代码
import streamlit.components.v1 as components
from pyecharts import options as opts
# 汉字转拼音
from pypinyin import pinyin, Style
# import gopup as gp
import re # 正则表达式库
# from nltk.corpus import stopwords # 停用词库

def remove_stopwords(text):
    # stop_words = set(stopwords.words('english'))
    stop_words = {'my', 'not', 'couldn', "mustn't", 'and', 'why', "weren't", 'its', 'same', 'hasn', 'again', 'being', "you'd", 'hers', 'don', "wasn't", 'more', "isn't", 'when', 'ma', 'were', 't', 'by', 're', "couldn't", 'we', 'that', "hadn't", 'she', 'down', 's', 'themselves', 'each', 'because', 'having', "you're", 'herself', 'a', 'those', 'them', 'above', 'how', 'only', 'shouldn', 've', 'itself', 'be', 'out', 'up', 'until', 'whom', 'yours', 'did', 'our', 'through', 'below', 'won', "won't", 'nor', 'now', 'off', 'while', "should've", 'wouldn', 'll', 'needn', "mightn't", 'didn', 'hadn', 'an', "wouldn't", 'from', 'in', 'all', 'yourselves', 'both', 'after', 'he', 'few', "you've", 'at', 'these', 'him', "aren't", "haven't", 'his', 'has', 'you', 'myself', 'aren', 'with', 'it', 'will', 'any', "shan't", 'than', 'some', 'haven', 'mustn', "shouldn't", 'theirs', 'been', 'their', 'about', 'on', "you'll", 'm', 'into', 'himself', 'yourself', 'doesn', 'are', 'such', 'your', 'against', 'to', 'mightn', 'doing', 'further', 'over', 'as', 'they', 'during', 'so', 'there', 'between', 'which', 'once', 'me', 'had', 'here', 'under', 'most', 'can', 'but', 'before', 'wasn', "that'll", 'd', 'just', "she's", "it's", 'other', 'have', 'no', 'i', "didn't", 'her', "don't", 'ours', 'very', 'the', 'should', 'too', "needn't", 'if', 'of', 'was', 'isn', 'own', 'what', 'where', 'ourselves', 'or', 'this', 'ain', 'then', 'for', 'weren', 'do', 'who', 'is', "hasn't", "doesn't", 'shan', 'am', 'o', 'y', 'does'}
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)

# 使用正则表达式去掉标点符号
def remove_punctuations(text):
    # 使用正则表达式去掉标点符号
    cleaned_text = re.sub(r'[^\w\s]', '', text)
    return cleaned_text

def crawlingFn(url):
    # 发送GET请求并获取响应
    response = requests.get(url)
    # 确定编码
    encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
    # 使用BeautifulSoup解析响应文本
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding=encoding)
    # 获取文本内容
    text_content = soup.text
    # 对文本内容清洗
    text_content = remove_punctuations(text_content)
    text_content = remove_stopwords(text_content)
    return text_content
def textFn():
    st.title('欢迎使用网页词频可视化工具! 👋')
    input_url = st.text_input("Enter URL:")
    if input_url.strip() == "":
        return
    else:
        text = crawlingFn(input_url)
        words = jieba.lcut(text)  # 使用精确模式对文本进行分词
        word_counts = {}
        # 获取词频字典
        for word in words:
            if len(word) == 1:
                continue
            else:
                word_counts[word] = word_counts.get(word, 0) + 1
        # 添加交互过滤低频词的功能
        min_freq = st.slider("设置最低词频阈值", 0, max(word_counts.values()), 0)
        filtered_word_counts = {word: freq for word, freq in word_counts.items() if freq >= min_freq}
        # 字典按值从大到小取前20个
        word_counts_20 = dict(sorted(filtered_word_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        return word_counts_20
def page_home():
    # 这是主页面
    word_counts_20 = textFn()
    if word_counts_20:
        bar = Bar()
        val = list(map(int, word_counts_20.values()))
        wordList = list(word_counts_20.keys())
        bar.add_xaxis(wordList)
        bar.add_yaxis("关键词", val)
        # 设置 x 轴标签旋转角度为 45 度
        bar.set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
        )
        # 使用 st_echarts.st_pyecharts() 方法将图表渲染到 Streamlit 中
        st_echarts.st_pyecharts(bar)
def page_ciyun():
    # 词云数据
    word_counts = textFn()
    if word_counts:
        # 字典按值从大到小取前20个
        word_counts_20 = dict(sorted(word_counts.items(), key=lambda x: x[1], reverse=True))
        wordcloud = WordCloud()
        wordcloud.add(
            "",
            list(word_counts_20.items()),
            word_size_range=[20, 100]
        )
        wordcloud.set_global_opts(title_opts=opts.TitleOpts(title="WordCloud Chart"))
        st_echarts.st_pyecharts(wordcloud)
def page_pie():
    # 饼状图页面
    word_counts_20 = textFn()  # 调用 textFn() 函数获取前20个高频词及其出现次数的字典。
    if word_counts_20:
        # 图表创建部分
        # 将字典转换为列表中的元组形式，
        # 每个元组代表一个单词和它对应的计数 (word, count)。
        word_list = [(x,y) for x,y in word_counts_20.items()]
        # 创建一个新的饼状图对象，使用 Pyecharts 库的 Pie 类
        pie = pyecharts.charts.Pie()
        # 添加数据（系列名字，绘制的数据，饼图内径、外径）
        pie.add("",word_list, radius=["40%", "55%"])
        # 设置全局配置项，不显示标题
        pie.set_global_opts(title_opts=opts.TitleOpts(title=""))
        st_echarts.st_pyecharts(pie)
        # st_echarts插件渲染显示饼图，st_pyecharts方法用于在Streamlit应用中展示Pyecharts 图表。
def page_broken():
    # 这是折线图
    word_counts_20 = textFn()
    if word_counts_20:
        val = list(map(int, word_counts_20.values()))
        wordList = list(word_counts_20.keys())
        line = pyecharts.charts.Line()
        line.add_xaxis(wordList)
        line.add_yaxis("关键词",val)
        # 设置 x 轴标签旋转角度为 45 度
        line.set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
        )
        st_echarts.st_pyecharts(line)
def page_point():
    # 这是散点图
    word_counts_20 = textFn()
    if word_counts_20:
        val = list(map(int, word_counts_20.values()))
        wordList = list(word_counts_20.keys())
        size_data = [10, 20, 30, 40, 50, 60]
        es = pyecharts.charts.EffectScatter()
        es.add_xaxis(wordList)
        es.add_yaxis("关键词",val,symbol_size=size_data)
        # 设置 x 轴标签旋转角度为 45 度
        es.set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
        )
        st_echarts.st_pyecharts(es)
def page_box():
    # 这是箱型图
    word_counts_20 = textFn()
    if word_counts_20:
        val = list(map(int, word_counts_20.values()))
        vals = list()
        for i in val:
            temp = [x for x in range(int(i/2-2),int(i/2+3))]
            vals.append(temp)
        wordList = list(word_counts_20.keys())
        # 创建箱形图
        box_plot = Boxplot()
        box_plot.add_xaxis(wordList)
        box_plot.add_yaxis("关键词", vals)
        box_plot.set_global_opts(title_opts=opts.TitleOpts(title="箱形图示例"))
        htmlcode = box_plot.render_embed()  # 嵌入式渲染
        components.html(htmlcode, width=1000, height=600)
def page_funnel():
    # 漏斗图页面
    # 字典按值从大到小取前20个
    word_counts_20 = textFn()
    if word_counts_20:
        # [()]
        word_list = [(x, y) for x, y in word_counts_20.items()]
        funnel = (
            Funnel()
            .add(
                series_name="",
                data_pair=word_list,
                gap=-2  # 设置漏斗之间的间隙，单位为像素
            )
            .set_colors(["#FFD700", "#FFA500", "#FF4500", "#FF6347", "#FF8C00"])  # 设置漏斗图颜色
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))  # 设置标签格式
            # .set_global_opts(title_opts=opts.TitleOpts(title="Funnel Chart"))
        )
        st_echarts.st_pyecharts(funnel)


def main():
    # 设置初始页面为Home
    session_state = st.session_state
    session_state['page'] = '条形图'
    # 导航栏
    page = st.sidebar.selectbox('导航栏', ['条形图', '词云','饼状图','折线图','散点图','箱型图','漏斗图'])

    if page == '条形图':
        # 在Home页面中显示数据和功能组件
        page_home()
    elif page == '词云':
        # 在About页面中显示数据和功能组件
        page_ciyun()
    elif page == '饼状图':
        # 在About页面中显示数据和功能组件
        page_pie()
    elif page == '折线图':
        page_broken()
    elif page == '散点图':
        page_point()
    elif page == '箱型图':
        page_box()
    elif page == '漏斗图':
        page_funnel()


if __name__ == '__main__':
    main()