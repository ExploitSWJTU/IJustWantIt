import re
import time
import requests
import muggle_ocr


course_list_re = re.compile(r'<tr>[\s\S]+?<\/tr>')
course_url_re = re.compile(r'window\.location=\'\.\.(.+?)\'')
confirm_url_re = re.compile(r'editStudentCourseSysListConfirm\(.+?\'([0-9A-F]{16})\',\'(.+?)\',\'(.+?)\'\)')

# For change course only
class JWC:
    def __init__(self, username, password, query, target):
        self.s = requests.Session()
        self.base_url = 'http://jwc.swjtu.edu.cn'
        self.username = username
        self.password = password
        self.query = query
        self.target = target

    def login(self):
        sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)
        while True:
            captcha = self.s.get(self.base_url+'/vatuu/GetRandomNumberToJPEG').content
            ranstring = sdk.predict(captcha)

            data = {
                'username': self.username,
                'password': self.password,
                'ranstring': ranstring,
            }
            r = self.s.post(self.base_url+'/vatuu/UserLoginAction', headers={'Referer': 'http://jwc.swjtu.edu.cn/service/login.html'}, data=data)
            print(r.json())
            if r.json()['loginStatus'] != '-2':
                break

        self.s.post(self.base_url+'/vatuu/UserLoadingAction')

    def get_course_list(self):
        r = self.s.get(self.base_url+'/vatuu/CourseStudentAction?setAction=studentCourseSysList&viewType=editCourse')
        return r.text

    def query_course(self):
        for course in course_list_re.findall(self.get_course_list()):
            if self.query in course:
                r = self.s.get(self.base_url+course_url_re.search(course).group(1))
                for course in course_list_re.findall(r.text):
                    if self.target in course:
                        try:
                            return confirm_url_re.search(course).groups()
                        except AttributeError:
                            return '', '', ''

    def change_course(self):
        list_id, course_code, teach_id = self.query_course()
        if not list_id:
            print('Not available')
            return
        r = self.s.get(self.base_url+'/vatuu/CourseStudentAction?setAction=editStudentCourseList&listId={}&courseCode={}&teachId={}&tt={}'.format(list_id, course_code, teach_id, int(time.time()*1000)))
        print(r.text)

if __name__ == '__main__':
    jwc = JWC('username', 'password', 'query', 'target')
    jwc.login()
    jwc.change_course()
