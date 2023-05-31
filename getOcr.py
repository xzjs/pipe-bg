import base64
import os
import re
import requests

url = "http://hz.api.ydocr.com/ocr"
headers = {'Content-Type': 'application/json'}

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
}

json_data = {
    "imageData": None,
    "secretID": "vw3isbnrk3xgnzess4dbx3jr",
    "signature": "kelcf4lh25ftu6z7y46qoai3",
    "signatureMethod": "secretKey",
}

def ocr_url(img):
    result = []
    json_data["imageData"] = base64.b64encode(img).decode('utf-8')
    res = requests.post(url, json=json_data)
    if res.status_code == 200:
        result = (eval(res.text))["data"]
    return result


def get_ocr_result(image):
    result_list = []
    for i in range(len(image)):
        result = ocr_url(image[i])
        result_list.extend(result)
    if len(result_list) > 0:
        for key in result_dic:
            max_confidence = 0
            max_num = 0
            for i in range(len(result_list)):
                is_match= re.match(key,result_list[i]['text'])
                if is_match:
                    if result_list[i]['confidence'] > max_confidence:
                        ### 识别断开的情况
                        if len(result_list[i]['text']) < (len(key) + 2):
                            if result_list[i+1]['text'][0] == "：":
                                result_list[i]['text'] = result_list[i]['text']  +  result_list[i+1]['text'][1:]
                            else:
                                result_list[i]['text'] = result_list[i]['text']  +  result_list[i+1]['text']
                        ###
                        max_confidence = result_list[i]['confidence']
                        max_num = i
            if result_list[max_num]['text'][len(key)] == '：': 
                result_dic[key] = result_list[max_num]['text'][len(key)+1:]
            else:
                result_dic[key] = result_list[max_num]['text'][len(key):]
    return result_dic

if __name__ == '__main__':
   folder = "data/"
   image_name_list = [os.path.join(num) for num in os.listdir(folder) if num[-3:] in ['jpg','png','gif','peg']]
   image_list = []
   for i in image_name_list:
       image_dir = os.path.join(folder,i)
       img = open(image_dir,"rb").read()
       image_list.append(img)
       
   ocr_result  = get_ocr_result(image_list)
   print(ocr_result)


