
from setuptools import setup, find_packages

setup(
    name='django-chelseru',
    version='1.0.6',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=5.1.6',
        'djangorestframework==3.15.2',
        'djangorestframework_simplejwt==5.5.0',
        'channels==4.2.2',
        'channels_redis==4.2.1',
        'daphne==4.1.2',
        'zeep==4.3.1',
        'user-agents==2.2.0'
    ],
    author='Sobhan Bahman|Rashnu',
    author_email='bahmanrashnu@gmail.com',
    description='Authentication system, online and real-time chat, SMS system for Iranian SMS services.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://pipdjango.chelseru.com',
    project_urls={
        "Documentation": "https://github.com/Chelseru/django-chelseru-lour/",
        "Telegram Group": "https://t.me/bahmanpy",
        "Telegram Channel": "https://t.me/ChelseruCom",
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
    keywords="djangochelseruchat djangochat drfchat online-chat online real-time chat iran chelseru lor lur bahman rashnu lour sms djangoauth auth ywt otpauth otp authentication djangootp djangoiransms iransms djangosms djangokavenegar djangomelipayamak sobhan چت  سبحان بهمن رشنو چلسرو جنگو پایتون لر لور آنلاین ریل تایم",
)
