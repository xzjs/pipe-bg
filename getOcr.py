import base64
import re
import requests
import threading

url = "http://hz.api.ydocr.com/ocr"

result_dic = {
    '任务名称': "",
    '起始井号': "",
    '终止井号': "",
    '检测人员': "",
    '检测日期': "",
    '管道材质': "",
    '检测方向': "",
    '检测地点': "",
    '管道类型': "",
    '管道直径': "",
    '距离': [],
    '位置': [],
}

result_dic2 = {
    '起始井号': "start_no",
    '终止井号': "end_no",
    '检测人员': "inspection_personnel",
    '检测日期': "detection_date",
    '管道材质': "material",
    '检测方向': "direction",
    '检测地点': "detection_site",
    '管道类型': "type",
    '管道直径': "diameter",
    '距离': "distance",
    '位置': "localization",
}

json_data = {
    "imageData": None,
    "secretID": "vw3isbnrk3xgnzess4dbx3jr",
    "signature": "kelcf4lh25ftu6z7y46qoai3",
    "signatureMethod": "secretKey",
}

lock = threading.Lock()
result_list = []
result_url = ['']*1000
width_threshold  = 500
height_threshold  = 80

def ocr_url(img):
    result = []
    json_data["imageData"] = base64.b64encode(img).decode('utf-8')
    res = requests.post(url, json=json_data)
    if res.status_code == 200:
        result = (eval(res.text))["data"]
    return result


def transform(dict):
    result = {}
    for key, value in dict.items():
        if key in result_dic2:
            result[result_dic2[key]] = value
    return result

def get_url(image,num):
    result_url[num] = ocr_url(image[num])

    key = '距离'
    for i in range(len(result_url[num])):
        is_match = re.match(key, result_url[num][i]['text'])
        if is_match:
            if result_url[num][i]['text'][len(key)] == '：':
                result_dic[key][num] = result_url[num][i]['text'][len(key)+1:]
            else:
                result_dic[key][num] = result_url[num][i]['text'][len(key):]
        if result_url[num][i]['polygon'][0][0] > width_threshold and result_url[num][i]['polygon'][0][1] < height_threshold:
            result_dic['位置'][num] = result_url[num][i]['text']
    with lock:
       result_list.extend(result_url[num])

       
def get_ocr_result(image):
    threads = []
    result_dic['位置'] = ['']*len(image)
    result_dic['距离'] = ['']*len(image)
    for i in range(len(image)):
        thread = threading.Thread(target=get_url,args=(image,i))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

    if len(result_list) > 0:
        for key in result_dic:
            max_confidence = 0
            max_num = 0
            if key != '距离' and key != '位置':
                for i in range(len(result_list)):
                    is_match = re.match(key, result_list[i]['text'])
                    if is_match:
                        if result_list[i]['confidence'] > max_confidence:
                            # 识别断开的情况
                            if len(result_list[i]['text']) < (len(key) + 2):
                                if result_list[i+1]['text'][0] == "：":
                                    result_list[i]['text'] = result_list[i]['text'] + \
                                        result_list[i+1]['text'][1:]
                                else:
                                    result_list[i]['text'] = result_list[i]['text'] + \
                                        result_list[i+1]['text']
                            ###
                            max_confidence = result_list[i]['confidence']
                            max_num = i
                if result_list[max_num]['text'][len(key)] == '：':
                    result_dic[key] = result_list[max_num]['text'][len(key)+1:]
                else:
                    result_dic[key] = result_list[max_num]['text'][len(key):]
    return transform(result_dic)
