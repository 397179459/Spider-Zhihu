# @Author: wanglei03
# @Time: 2021-5-6 21:25:19
# @Method: 实现指定问题和答案的ID爬取图片
import json
import logging
import os
import random
import re
import socket
import time
import urllib.request

import threadpool
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.NOTSET)
socket.setdefaulttimeout(60)
# 2021-5-9 01:53:54 保存文件夹时增加当前的时间戳
NOW_TIME = time.strftime('%Y%m%d%H%M', time.localtime())

QUESTION_CHINESE = ''
AUTHOR_CHINESE = ''

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]
UA = random.choice(USER_AGENTS)


# 通过 请求url 返回json内容
def url_json(_url):
    _request = urllib.request.Request(url=_url, headers={"user-agent": UA})
    response = urllib.request.urlopen(_request)
    # 打开url请求（如同打开本地文件一样）
    with response as f:
        return json.loads(f.read().decode('utf-8'))


def url_question(question_id, limit=1, offset=0, sort_way='default'):
    '''
    通过问题的 URL 获取 json 内容. limit 是每次获取的增量，offset是浏览的起始值，
    因为后面是按照逐个回答建立文件夹，所以此处的 limit 建议设置为1，
    sortWay是排序方式，默认是按照热度排序，如果想按照时间排序，传参的时候需要指定sortWay是 created
    '''
    question_url = 'https://www.zhihu.com/api/v4/questions/' + str(question_id) + \
                   '/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics%3Bdata%5B%2A%5D.settings.table_of_content.enabled' \
                   '&limit=' + str(limit) + '&offset=' + str(offset) + '&platform=desktop&sort_by=' + sort_way
    return url_json(question_url)


def soup_img_url(j, html_content):
    '''
    2021-5-9 02:43:34 重大更新
    测试的时候发现其实获取json中的content内容后，也是可以解析成soup对象的，那么就代表可以跟解析指定答案的HTML一样，用bf获取图片地址，
    而且还可以把这一模块抽取出来，便于代码复用
    '''
    soup = BeautifulSoup(html_content, 'html.parser')
    try:
        img_url_item = soup.find_all('img', class_="origin_image zh-lightbox-thumb lazy")
        img_url_list_bf = []
        for x in img_url_item:
            img_url_list_bf.append(x.get('data-original'))
        '''
        下面的图片是可能会漏掉的，所以我们再找一遍另一个class的，
        暂时是在一个测试用例中发现的 https://www.zhihu.com/question/338323696/answer/1836142615 
        如果有别的漏掉的图片，可以再联系
        如果是问题的形式，采用正则去解析是不行的，它会把那些小图也解析出来，去重也是去不掉的
        '''
        img_url_item_o = soup.find_all('img', class_='content_image lazy')
        for y in img_url_item_o:
            img_url_list_bf.append(y.get('data-actualsrc'))
        logging.info(f'========第 {j + 1} 个答案用 bf4 解析到 {len(img_url_list_bf)} 张图片=========')

        if j == -1:
            question_name_s = soup.find(class_="QuestionHeader-title").get_text()  # 问题中文名
            writer_name_s = soup.find(itemprop="author").meta['content']  # 作者
            return img_url_list_bf, question_name_s, writer_name_s
        else:
            return img_url_list_bf
    except:
        os._exit(0)


# 通过答案的 URL 用 BeautifulSoup4 获取图片
def url_answer(j, question_id, answer_id):
    answer_url = 'https://www.zhihu.com/question/' + str(question_id) + '/answer/' + str(answer_id)
    _request = urllib.request.Request(answer_url)
    response = urllib.request.urlopen(_request)
    content = response.read()
    info_list = soup_img_url(j, content)
    question_name = info_list[1]
    writer_name = info_list[2]
    QUESTION_CHINESE = re_only_chinese(question_name)
    AUTHOR_CHINESE = re_only_chinese(writer_name)
    return info_list[0]


# 根据图片地址下载图片，这里的 i 主要是用来文件命名
def download_pic(i, img_url):
    folder_or_file = 0
    if folder_or_file:
        suffix = '\\{}.jpg'.format(i + 1)
    else:
        suffix = '\\{}-aid-{}-{}-{}.jpg'.format(j + 1, my_answer_id, author_chinese, i + 1)
    file_name = absolute_dir + suffix
    try:
        urllib.request.urlretrieve(img_url, file_name)
        logging.info('第 {} 张下载完成 {}'.format(i + 1, file_name))
    except:
        logging.warning("链接失效，图片无法下载")


# 多线程下载列表中的url
def thread_pool_download(img_url_list, question_id, answer_id, absolute_dir):
    # 定义线程池数量
    pool = threadpool.ThreadPool(10)
    '''
    makeRequests 方法第二个参数必须是 iter 对象，
    然后我们的download_pic函数是用到了 下标（用来保存文件名）和url 2个参数，所以这里必须这样遍历一遍
    或者这里你可以把url转成文件名也可以，download_pic 函数只传 url 1个参数的话，就不用这一步遍历了
    '''
    _data = [((index, x), None) for index, x in enumerate(img_url_list)]
    th_request = threadpool.makeRequests(download_pic, _data)
    for req in th_request:
        pool.putRequest(req)
    pool.wait()
    logging.info(
        f'https://www.zhihu.com/question/{question_id}/answer/{answer_id}  中 {len(img_url_list)} 张图片下载完成')
    logging.info('保存路径为   {}'.format(absolute_dir))


# 从字符串中只匹配中文
def re_only_chinese(s):
    pattern = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]")
    ret = pattern.sub("", s)
    # 虽然文件名长度限制长达200多，但是为了易读性，我们还是设置一下截取的长度，毕竟已经有问题和答案ID
    return ret[:20]


def get_by_answer_list(answer_l):
    for x in answer_l:
        question_id = x['q_id']
        answer_id = x['a_id']
        logging.info(
            f'正在使用 beautifulSoup4 方式解析 https://www.zhihu.com/question/{str(question_id)}/answer/{str(answer_id)}')
        # 因为 soup_img_url 函数在回答中要用到循环，所以这里指定一个j，也相当于一个 flag 标志位
        j = -1
        img_url_list = url_answer(j, question_id, answer_id)
        # 判断 BeautifulSoup4 解析之后的列表，基本上是不可能为空的，因为是直接通过answerid的，如果为空，提示用户检查此答案下是否有图片
        if img_url_list:
            # 这几步都是创建路径
            path = os.getcwd()
            new_path = str(path) + '-qid-' + question_id + '-' + QUESTION_CHINESE + '-' + NOW_TIME
            absolute_dir = new_path + '\\' + 'aid-{}-{}'.format(answer_id, AUTHOR_CHINESE)
            if not os.path.exists(absolute_dir):
                os.makedirs(absolute_dir)
            thread_pool_download(img_url_list,  question_id, answer_id, absolute_dir)
        else:
            logging.warning(
                f'此答案下没有任何图片，点击 https://www.zhihu.com/question/{question_id}/answer/{answer_id} 查看')


def get_by_question_list(question_id_l):
    for question_id in question_id_l:
        question_id = str(question_id)
        logging.info('正在使用 json + bf 方式解析 https://www.zhihu.com/question/{}'.format(question_id))
        json_text_tmp = url_question(question_id)
        answer_counts = json_text_tmp['paging']['totals']  # 答案总数量
        question_name = json_text_tmp['data'][0]['question']['title']  # 问题中文名
        logging.info(
            'Start....@@@@@@@@@@@@@@ 问题 @@@@@@@@@@@ {} 下有 # {} 个回答'.format(question_name, answer_counts))
        '''
        前多少个回答，默认是按照热度排序，一般设置成 50 或者 100，依照答案数量而定，
        一般也就前面点赞的还可以，群众的眼睛是雪亮的，私认为热度前 100 足够了
        现在知乎老是有整流大师，搜集各种回答，所以前几名一般都是他们，不建议设置前 5
        '''
        # want_answer_num = int(input("请输入需要下载前多少个答案的数量（不输入默认 100 ）：") or 100)
        want_answer_num = 5  # 测试使用
        # want_answer_num = answer_counts   # 不想单独选的，每个问题全部下载，但是会特别费时，一般福利问题都几百上千个回答
        for j in range(want_answer_num):
            json_text = url_question(questionId=question_id, offset=j)
            answer_content = json_text['data'][0]['content']
            # img_url_list_tmp = re_get_img_url(answer_text)  # 废弃的正则找图方法
            img_url_list_tmp = soup_img_url(answer_content)
            my_answer_id = json_text['data'][0]['id']  # 答案id
            author = json_text['data'][0]['author']['name']  # 作者
            if img_url_list_tmp:
                question_chinese = re_only_chinese(question_name)
                author_chinese = re_only_chinese(author)
                path = os.getcwd()
                new_path = str(path) + '-qid-' + question_id + '-' + question_chinese + '-' + NOW_TIME
                # 选择是否保存成文件夹  1  还是 按照一个文件下不同文件名区分  0
                folder_or_file = 0
                if folder_or_file:
                    absolute_dir = new_path + '\\' + '{}-aid-{}-{}'.format(j + 1, my_answer_id, author_chinese)
                else:
                    absolute_dir = new_path
                if not os.path.exists(absolute_dir):
                    os.makedirs(absolute_dir)
                # 获取总共多少张图片
                img_num = len(img_url_list_tmp)
                thread_pool_download(img_url_list_tmp)
            else:
                logging.warning(
                    '第 {} 个答案下没有任何图片，点击 https://www.zhihu.com/question/{}/answer/{} 查看'.format(j + 1,
                                                                                                              question_id,
                                                                                                              my_answer_id))
            # 必须放到最后判断，因为最后一个答案的 flag 是true，如果放到最开始判断的话，就会漏掉最后一个答案
            end_flag = json_text['paging']['is_end']
            if end_flag:
                break
        logging.info('Done....############# 问题 ########### {} 下载完毕'.format(question_name))


def run():
    answer_list = [{'q_id': 288424573, 'a_id': 3064929266},
                   {'q_id': 288424573, 'a_id': 928479462},
                   ]
    if answer_list:
        get_by_answer_list(answer_list)

    # 问题ID列表，多份快乐，如果不想单独设置每个回答下的下载数量， 修改 want_answer_num = answer_counts 即为下载全部
    # question_id_l = [366062253, 338323696, 424555505, 350939352]  # 我乱打的几个ID，兄弟们自己不要当真（狗头）
    # question_list = [316722332, 397912593, ]
    question_list = []
    if question_list:
        get_by_question_list(question_list)


if __name__ == '__main__':
    run()
    logging.info('!!!!!!!!!!!!!  执行完毕，谢谢使用  !!!!!!!!!!!!!!!')
