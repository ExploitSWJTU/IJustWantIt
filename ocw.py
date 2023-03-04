import time
import requests
import muggle_ocr


class OCW:
    def __init__(self, username, password, course_id, add_type):
        self.s = requests.Session()
        self.base_url = 'https://ocw.swjtu.edu.cn'
        self.username = username
        self.password = password
        self.course_id = course_id
        self.add_type = add_type

    def choose_course(self):
        while True:
            captcha = self.s.get(self.base_url+'/yethan/GetRandomNumberToJPEG').content
            sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)
            ranstring = sdk.predict(image_bytes=captcha)

            data = {
                'username': self.username,
                'password': self.password,
                'ranstring': ranstring,
                'university': 10613
            }
            r = self.s.post(self.base_url+'/yethan/UserLoginAction', headers={'Referer': self.base_url+'/yethan/UserAction?setAction=userLogin'}, data=data)
            print(r.json())
            if r.json()['loginStatus'] != '-2':
                break

        self.s.post(self.base_url+'/yethan/UserLoadingAction')

        data = {
            'setAction': 'registerCourse',
            'courseId': self.course_id,
            'addType': self.add_type
        }

        while True:
            r = self.s.post(self.base_url+'/yethan/StudentAction', data=data)
            print(time.strftime('%H:%M', time.localtime(time.time())), r.text)

            if r.json()['statusCode'] == 'success':
                break
            time.sleep(60)

if __name__ == '__main__':
    OCW('username', 'password', 'course_id', 'add_type').choose_course()
