
from setuptools import setup, find_packages

setup(
    name='django-chelseru-chat',
    version='1.3.3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django-chelseru',
    ],
    author='Sobhan Bahman Rashnu',
    author_email='bahmanrashnu@gmail.com',
    description='Real-time one-on-one chat system for Django projects, powered by WebSocket and JWT authentication.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://pipdjango.chelseru.com/',
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
    keywords="djangochelseruchat djangochat drfchat online-chat online real-time chat iran chelseru lor lur bahman rashnu sobhan چت  سبحان بهمن رشنو چلسرو جنگو پایتون لر لور آنلاین ریل تایم",
)
