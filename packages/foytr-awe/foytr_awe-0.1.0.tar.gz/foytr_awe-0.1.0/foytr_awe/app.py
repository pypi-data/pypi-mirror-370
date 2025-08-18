# Foytr-awe: A Simple Python Web Framework
# هذا الكود يمثل نقطة بداية لمكتبة ويب بسيطة
# مثل Flask، مع نظام للمسارات ونظام للجلسات.

import http.cookies
import urllib.parse
from wsgiref.simple_server import make_server

# الكلاس الرئيسي لإطار العمل
class FoytrAwe:
    """
    إطار عمل ويب بسيط يشبه Flask.
    """
    def __init__(self):
        # قاموس لتخزين المسارات (الروابط) والوظائف المرتبطة بها
        self.routes = {}

    def route(self, path):
        """
        مُزين (decorator) لربط رابط URL بوظيفة معينة.
        على سبيل المثال: @app.route('/')
        """
        def decorator(f):
            self.routes[path] = f
            return f
        return decorator

    def __call__(self, environ, start_response):
        """
        هذه الوظيفة تجعل الكلاس يعمل كخادم ويب WSGI.
        تستقبل الطلب وتُعيد الاستجابة.
        """
        # الحصول على مسار الطلب من بيئة الخادم
        path = environ.get('PATH_INFO', '')
        
        # إدارة الجلسات (Sessions) باستخدام الكوكيز
        cookies = http.cookies.SimpleCookie(environ.get('HTTP_COOKIE', ''))
        session = {}

        # فك تشفير بيانات الجلسة من الكوكي إذا كانت موجودة
        if 'foytr_awe_session' in cookies:
            try:
                session_data = urllib.parse.parse_qs(cookies['foytr_awe_session'].value)
                for key, value in session_data.items():
                    # تأكد من أن القيمة ليست قائمة
                    session[key] = value[0] if len(value) == 1 else value
            except:
                pass

        # التحقق من وجود المسار في القائمة
        if path in self.routes:
            # تشغيل الوظيفة المرتبطة بالمسار وتمرير كائن الجلسة
            result = self.routes[path](session)
            response_body = result.encode('utf-8')

            # إعداد الاستجابة
            headers = [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response_body)))
            ]
            
            # تحديث كوكي الجلسة وإضافته إلى الهيدر
            session_cookie_out = http.cookies.SimpleCookie()
            session_cookie_out['foytr_awe_session'] = urllib.parse.urlencode(session)
            headers.append(('Set-Cookie', session_cookie_out['foytr_awe_session'].OutputString()))

            start_response('200 OK', headers)
            return [response_body]
        else:
            # في حالة عدم العثور على المسار، أرسل خطأ 404
            start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
            return [b'Not Found']

# -----------------------------------------------------------------------------
# مثال على استخدام مكتبة Foytr-awe
# -----------------------------------------------------------------------------

# 1. إنشاء كائن التطبيق
app = FoytrAwe()

# 2. تعريف المسارات
@app.route('/')
def index(session):
    # استخدام الجلسة للحصول على اسم المستخدم
    username = session.get('username', 'Guest')
    return f"<h1>مرحباً بك يا {username}!</h1><p>هذا هو مسارك الرئيسي.</p>"

@app.route('/login')
def login(session):
    # تحديث اسم المستخدم في الجلسة
    session['username'] = 'Ali'
    return "تم تسجيل دخولك باسم علي! <a href='/'>العودة للرئيسية</a>"

# 3. تشغيل الخادم
if __name__ == "__main__":
    # تشغيل الخادم على البورت 8000
    httpd = make_server('', 8000, app)
    print("Foytr-awe server running on http://localhost:8000/")
    httpd.serve_forever()
