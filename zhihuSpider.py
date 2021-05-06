import json
import logging
import os
import re
import urllib.request
import socket
import random
import threadpool
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.NOTSET)
socket.setdefaulttimeout(60)

'''
通过问题的 URL 获取 json 内容. limit 是每次获取的增量，offset是浏览的起始值，
因为后面是按照逐个回答建立文件夹，所以此处的 limit 建议设置为1，
sortWay是排序方式，默认是按照热度排序，如果想按照时间排序，传参的时候需要指定sortWay是 created
'''


def url_question(questionId, limit=1, offset=0, sortWay='default'):
    question_url = 'https://www.zhihu.com/api/v4/questions/' + str(questionId) + \
                   '/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics%3Bdata%5B%2A%5D.settings.table_of_content.enabled' \
                   '&limit=' + str(limit) + '&offset=' + str(offset) + '&platform=desktop&sort_by=' + sortWay
    return url_json(question_url)


# 通过 请求url 返回json内容
def url_json(myUrl):
    user_agents = [
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
    ua = random.choice(user_agents)
    request = urllib.request.Request(url=myUrl, headers={"user-agent": ua})
    response = urllib.request.urlopen(request)
    # 打开url请求（如同打开本地文件一样）
    with response as f:
        return json.loads(f.read().decode('utf-8'))


# 通过正则找到json内容中的图片地址，原图是保存在属性 data-original 中
def re_get_img_url(myJsonText):
    pattern = re.compile('data-original="(.*?)"')
    img_url_list_re = pattern.findall(str(myJsonText))
    img_url_only_list = sorted(set(img_url_list_re), key=img_url_list_re.index)
    logging.info(
        '=====================第 {} 个答案用 正则 解析到 {} 张图片====================='.format(j + 1, len(img_url_only_list)))
    return img_url_only_list


# 通过答案的 URL 用 BeautifulSoup4 获取图片
def url_answer(questionId, answerId):
    answer_url = 'https://www.zhihu.com/question/' + str(questionId) + '/answer/' + str(answerId)
    request = urllib.request.Request(answer_url)
    response = urllib.request.urlopen(request)
    content = response.read()
    soup = BeautifulSoup(content, 'html.parser')
    try:
        question_name = soup.find(class_="QuestionHeader-title").get_text()  # 问题中文名
        writer_name = soup.find(itemprop="author").meta['content']  # 作者
        global QUESTION_CHINESE
        global AUTHOR_CHINESE
        QUESTION_CHINESE = re_only_chinese(question_name)
        AUTHOR_CHINESE = re_only_chinese(writer_name)
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
        logging.info('用 beautifulSoup4 解析到 {} 张图片'.format(len(img_url_list_bf)))
        return img_url_list_bf
    except:
        logging.error('未找到任何图片，点击 https://www.zhihu.com/question/{}/answer/{} 检查路径'.format(question_id, answer_id))
        os._exit(-1)


# 根据图片地址下载图片，这里的 i 主要是用来文件命名
def download_pic(i, imgUrl):
    if folder_or_file:
        suffix = '\\{}.jpg'.format(i + 1)
    else:
        suffix = '\\{}-aid-{}-{}-{}.jpg'.format(j + 1, my_answer_id, author_chinese, i + 1)
    file_name = absolute_dir + suffix
    try:
        # logging.info("正在下载第 {} 张图片......".format(i+1))
        urllib.request.urlretrieve(imgUrl, file_name)
        logging.info('第 {} 张下载完成 {}'.format(i + 1, file_name))
    except:
        logging.warning("链接失效，图片无法下载")


# 从字符串中只匹配中文
def re_only_chinese(s):
    pattern = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]")
    ret = pattern.sub("", s)
    # 虽然文件名长度限制长达200多，但是为了易读性，我们还是设置一下截取的长度，毕竟已经有问题和答案ID
    return ret[:20]


# 多线程下载列表中的url
def thread_pool_download(imgUrlList):
    # 定义线程池数量
    pool = threadpool.ThreadPool(15)
    """
    makeRequests 方法第二个参数必须是 iter 对象，
    然后我们的download_pic函数是用到了 下标（用来保存文件名）和url 2个参数，所以这里必须这样遍历一遍
    或者这里你可以把url转成文件名也可以，download_pic 函数只传 url 1个参数的话，就不用这一步遍历了
    """
    data = [((index, x), None) for index, x in enumerate(imgUrlList)]
    th_request = threadpool.makeRequests(download_pic, data)
    for req in th_request:
        pool.putRequest(req)
    pool.wait()
    logging.info(
        'https://www.zhihu.com/question/{}/answer/{}  中 {} 张图片下载完成'.format(question_id, answer_id or my_answer_id,
                                                                           img_num))
    logging.info('保存路径为   {}'.format(absolute_dir))


if __name__ == '__main__':
    # 采用问题和答案 ID 下载，必须都输入
    question_id = '424555505'
    answer_id = ''
    # 问题ID列表，多份快乐，如果不想单独设置每个回答下的下载数量， 修改 want_answer_num = answer_counts 即为下载全部
    # question_id_l = [366062253, 338323696, 424555505, 350939352]  # 我乱打的几个ID，兄弟们自己不要当真（狗头）
    question_id_l = [366062253, 350939352, 338323696, ]

    # 判断用户是否输入了 question_id 和 answer id， 如果输入了，就采用 BeautifulSoup4 的方法解析 html ，而非解析json
    if question_id and answer_id:
        logging.info(
            '正在使用 beautifulSoup4 方式解析 https://www.zhihu.com/question/{}/answer/{}'.format(question_id, answer_id))
        img_url_list = url_answer(question_id, answer_id)
        # 判断 BeautifulSoup4 解析之后的列表，基本上是不可能为空的，因为是直接通过answerid的，如果为空，提示用户检查此答案下是否有图片
        if img_url_list:
            # 这几步都是创建路径
            path = os.getcwd()
            new_path = str(path) + '-qid-' + question_id + '-' + QUESTION_CHINESE
            absolute_dir = new_path + '\\' + 'aid-{}-{}'.format(answer_id, AUTHOR_CHINESE)
            # 因为下面用到了 download_pic，函数，所以这里必须定义成文件夹形式保存
            folder_or_file = 1
            if not os.path.exists(absolute_dir):
                os.makedirs(absolute_dir)
            # 获取总共多少张图片
            img_num = len(img_url_list)
            thread_pool_download(img_url_list)
            # 最原始的逐个下载，没有多线程
            # for i in range(40):
            #     download_pic(i, img_url_list[i])
        else:
            logging.warning(
                '此答案下没有任何图片，点击 https://www.zhihu.com/question/{}/answer/{} 查看'.format(question_id, answer_id))

    elif question_id_l:
        for question_id in question_id_l:
            question_id = str(question_id)
            logging.info('正在使用 json + re 方式解析 https://www.zhihu.com/question/{}'.format(question_id))
            json_text_tmp = url_question(question_id)
            answer_counts = json_text_tmp['paging']['totals']  # 答案总数量
            question_name = json_text_tmp['data'][0]['question']['title']  # 问题中文名
            logging.info('@@@@@@@@@@@@@@ 问题 @@@@@@@@@@@ {} 下有 # {} 个回答'.format(question_name, answer_counts))
            '''
            前多少个回答，默认是按照热度排序，一般设置成 50 或者 100，依照答案数量而定，
            一般也就前面点赞的还可以，群众的眼睛是雪亮的，私认为热度前 100 足够了
            现在知乎老是有整流大师，搜集各种回答，所以前几名一般都是他们，不建议设置前 5
            '''
            # want_answer_num = int(input("请输入需要下载前多少个答案的数量（不输入默认 100 ）：") or 100)
            want_answer_num = 4  # 测试使用
            # want_answer_num = answer_counts   # 不想单独选的，每个问题全部下载，但是会特别费时，一般福利问题都几百上千个回答
            for j in range(want_answer_num):
                json_text = url_question(questionId=question_id, offset=j)
                answer_text = json_text['data'][0]['content']
                img_url_list_tmp = re_get_img_url(answer_text)
                my_answer_id = json_text['data'][0]['id']  # 答案id
                author = json_text['data'][0]['author']['name']  # 作者
                if img_url_list_tmp:
                    question_chinese = re_only_chinese(question_name)
                    author_chinese = re_only_chinese(author)
                    path = os.getcwd()
                    new_path = str(path) + '-qid-' + question_id + '-' + question_chinese
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
                        '第 {} 个答案下没有任何图片，点击 https://www.zhihu.com/question/{}/answer/{} 查看'.format(j + 1, question_id,
                                                                                                   my_answer_id))
                # 必须放到最后判断，因为最后一个答案的 flag 是true，如果放到最开始判断的话，就会漏掉最后一个答案
                end_flag = json_text['paging']['is_end']
                if end_flag:
                    break
            logging.info('############# 问题 ########### {} 下载完毕'.format(question_name))
    else:
        logging.warning('请检查  question_id, answer_id, question_id_l 参数是否正确输入')

    logging.info('!!!!!!!!!!!!!  执行完毕，谢谢使用  !!!!!!!!!!!!!!!')

    # t1 = time.time()
    # totaltime = t1 - t0
    # print("use time : ", totaltime)
