# Noterools: Not just Zotero Tools

<p align="center">中文文档 | <a href="README_EN.md">English</a></p>

一开始我只是想依照 [gwyn-hopkins](https://forums.zotero.org/discussion/comment/418013/#Comment_418013) 的代码写一份相应的 Python 实现，用于为 Zotero 的引用添加可跳转的超链接。但是随着论文的修改，我发现需要对论文的格式做越来越多的设置，代码实现的功能也越来越多。经过大量的重构以后，noterools 诞生。

## 这是什么?

目前 noterools 包含以下功能：

- 为 Zotero 参考文献表中的每个文献创建书签
- 为 Zotero 的引用设置跳转到相应文献的超链接，并设置超链接是否带下划线
- 为 Zotero 的引用设置字体颜色
- 将 Zotero 的参考文献表中，不能被正确设置为斜体的期刊名称和出版商设置为斜体
- 为正文中的交叉引用设置字体颜色和粗细
- 将参考文献表中，表示页码范围的`-` (Unicode为`002D`)修正为`–` (Unicode为`2013`)
- 为参考文献目录表中出现的链接添加超链接，并设置字体颜色以及是否带下划线
- **(实验性功能)** 帮助修改英文文献标题的大小写形式，支持三种形式：全部大写、所有单词首字母大写、仅句首首字母大写
- **(实验性功能)** 为 (Author, Date) 格式的文内引用添加上超链接（默认情况下只为 Date 添加）

## 效果图

![引用和参考文献表设置](./pics/noterools1.png)

![交叉引用设置](./pics/noterools2.png)

## 注意

- **该脚本仅能在 Windows 环境下运行**

## 如何使用

1. 使用 pip 安装 noterools
```bash
pip install noterools
```
2. 创建一个 Python 脚本并运行。以下是一个简单的示例

```python
from noterools import Word, add_cross_ref_style_hook, add_citation_cross_ref_hook

if __name__ == '__main__':
    word_file_path = r"E:\Documents\Word\test.docx"
    new_file_path = r"E:\Documents\Word\test_new.docx"

    with Word(word_file_path, save_path=new_file_path) as word:
        # 为顺序引用格式添加超链接
        add_citation_cross_ref_hook(word, is_numbered=True)

        # 为 (作者, 年份) 引用格式添加超链接，设置引用为蓝色。
        # 默认会将参考文献表中没有被正确设置为斜体的刊物名称或出版商设置为斜体
        # 默认情况下，只有年份部分会添加超链接，设置 full_citation_hyperlink=True 可以让整个引用(作者+年份)都添加超链接 (请注意，该特性还在开发测试中，可能会产生意外的结果)
        # add_citation_cross_ref_hook(word, is_numbered=False, full_citation_hyperlink=True)

        # 通过设置 color 的值，可以设置整个引用的颜色(不包含括号)
        # 0: 黑色
        # 16711680: 蓝色
        # 更多颜色请参考 Word 中的颜色枚举类型: https://learn.microsoft.com/en-us/office/vba/api/word.wdcolor
        # add_citation_cross_ref_hook(word, is_numbered=False, color=0)
        # 或者使用 RGB 值
        # add_cross_ref_style_hook(word, is_numbered=False, color="0, 0, 255")
        # 或者设为 Microsoft Word 中的“自动”，该颜色在浅色模式下为黑色，深色模式下为白色
        # add_cross_ref_style_hook(word, is_numbered=False, color="word_auto")

        # set_container_title_italic 用于控制是否修正参考文献表中没有正确设置为斜体的名称
        # 你可以通过将其设置为 False 来关闭这项功能
        # add_citation_cross_ref_hook(word, is_numbered=False, set_container_title_italic=False)

        # 为正文中以 Figure 开头的交叉引用字体设置蓝色和粗体
        add_cross_ref_style_hook(word, color=16711680, bold=True, key_word=["Figure"])

        # 修正 "-" 符号。
        # 如果想使用这项功能，你需要调用 zotero_init_client 函数初始化与 Zotero 通信的客户端。
        # 请参考 pyzotero 的文档获取你的 Zotero ID 和申请 API key。
        # https://pyzotero.readthedocs.io/en/latest/#getting-started-short-version
        # zotero_init_client(zotero_id="你的 Zotero ID", zotero_api_key="你的 Zotero API key")
        # add_update_dash_symbol_hook(word, "你的 ID", "你的 key")

        # 将英文标题改为全部大写
        # add_format_title_hook(word, upper_all_words=True)

        # 将英文标题改为首字母大写
        # add_format_title_hook(word, upper_first_char=True)

        # 将英文标题改为仅句首单词的首字母大写
        # add_format_title_hook(word, lower_all_words=True)

        # 改为仅句首单词的首字母大写时，你可以给出一个专有名词列表，noterools 会检测其中的专有名词，防止这些名词被错误设置为小写
        # word_list = ["UNet", "US", "China", "WRF"]
        # add_format_title_hook(word, lower_all_words=True, word_list=word_list)

        # 为参考文献目录表中出现的网址添加超链接
        # add_url_hyperlink_hook(word)

        # 自定义超链接的颜色以及是否添加下划线 (参数可选)
        # add_url_hyperlink_hook(word, color=16711680, no_under_line=False)
```
