### 知乎图片下载爬虫-zhihuSpider

> @ 2021-5-9 02:48:17 重大更新：
>
> - 废除 `re_get_img_url` 函数
>
> - 测试的时候发现其实获取json中的content内容后，也是可以解析成soup对象的，那么就代表可以跟解析指定答案的HTML一样，用bf获取图片地址，而且还可以把这一模块抽取出来，便于代码复用
>
> - 
>   保存文件夹时增加当前的时间戳
>   
> 
> @ 2021-5-6 上传第一版，最近想下载一些知乎的图片，所以就做了这个，至于具体用来爬什么图片，兄弟们自己斟酌，身体要紧

#### [爬取的思路记录在这里](https://github.com/397179459/zhihuSpider/tree/master/analysis)

#### 目前实现的功能：

- 多线程下载图片，所以下载会比较无序，但是能保证都下载
- 默认的下载位置是爬虫文件夹的同级目录
- 支持 以文件夹归档和不同文件名保存图片
- 支持指定问题和答案ID下载图片，采用 `BeautifulSoup4`
- 支持问题ID列表，下载点赞前多少 `num` 的回答图片，具体的使用方法都写在代码注释中，采用`json`+`bf`

#### 待完成：

- 爬取指定用户下的回答，初步暂定也是按照用户答案的点赞数爬，不过目前好像还爬不到数据，知乎可能对爬用户比较敏感，在实现中
- 可能会升级成队列爬取，初学Python，正在研究中，改成队列，最大的问题是文件名怎么保持和现在的一样清晰
- 爬取知乎指定话题下的所有答案，最近发现某些回答都是包含相同话题标签的，所以就准备试下，唯一的区别是话题下包含了文章和回答2种类型的内容，正在coding

#### 用到的库

```python
import json
import logging
import os
import re
import urllib.request
import socket
import random
import threadpool
from bs4 import BeautifulSoup
import time
```

#### 如何使用：

- 如果采用第一种指定问题和答案ID下载，必须都输入，至于 `question_id` & `answer_id` ，你打开一个知乎答案的链接 https://www.zhihu.com/question/397912593/answer/1405924814  就明白了
- 如果采用第二种问题ID列表下载的方式，只用在列表中输入相应的ID即可

```python
if __name__ == '__main__':
    # 采用问题和答案 ID 下载，必须都输入
    question_id = ''
    answer_id = ''
    # 问题ID列表，多份快乐，如果不想单独设置每个回答下的下载数量， 修改 want_answer_num = answer_counts 即为下载全部
    # question_id_l = [366062253, 338323696, 424555505, 350939352]  # 我乱打的几个ID，兄弟们自己不要当真（狗头）
    question_id_l = [316722332, 397912593, ]
......
```

[![gJd158.jpg](https://z3.ax1x.com/2021/05/09/gJd158.jpg)](https://imgtu.com/i/gJd158)

##### 下面的讲解都是针对第二种问题列表下载的方式

- 这里的 `want_answer_num` 就是你想下载的数量

```python
'''
前多少个回答，默认是按照热度排序，一般设置成 50 或者 100，依照答案数量而定，
一般也就前面点赞的还可以，群众的眼睛是雪亮的，私认为热度前 100 足够了
现在知乎老是有整流大师，搜集各种回答，所以前几名一般都是他们，不建议设置前 5
'''
# want_answer_num = int(input("请输入需要下载前多少个答案的数量（不输入默认 100 ）：") or 100)
want_answer_num = 4  # 测试使用
# want_answer_num = answer_counts   # 不想单独选的，每个问题全部下载，但是会特别费时，一般福利问题都几百上千个回答
for j in range(want_answer_num):
......
```

- 这里的`folder_or_file` 参数是选择2种保存方式，1是对应每个回答保存成一个文件夹，0是所有图片都在一个根目录下，文件名来区别答案 ，推荐采用 1，看起来比较有条理

```python
# 选择是否保存成文件夹  1  还是 按照一个文件下不同文件名区分  0
folder_or_file = 0	
```

[![gJdYvj.png](https://z3.ax1x.com/2021/05/09/gJdYvj.png)](https://imgtu.com/i/gJdYvj)

- `folder_or_file = 0`

[![gJdlUf.jpg](https://z3.ax1x.com/2021/05/09/gJdlUf.jpg)](https://imgtu.com/i/gJdlUf)

- `folder_or_file = 1`

[![gJdevd.jpg](https://z3.ax1x.com/2021/05/09/gJdevd.jpg)](https://imgtu.com/i/gJdevd)