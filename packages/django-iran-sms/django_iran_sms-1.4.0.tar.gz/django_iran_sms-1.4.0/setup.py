
from setuptools import setup, find_packages

setup(
    name='django-iran-sms',
    version='1.4.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django-chelseru',
    ],
    author='Sobhan Bahman Rashnu',
    author_email='bahmanrashnu@gmail.com',
    description='A Django package for seamless integration with Iranian SMS services like ParsianWebCo , Kavenegar and Melipayamak.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://pipdjango.chelseru.com/',
    project_urls={
        "Documentation": "https://github.com/Chelseru/django-chelseru-lour/",
        "Telegram Group": "https://t.me/bahmanpy",
        "Telegram Channel": "https://t.me/djangochelseru",
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
    keywords="djangoiransms djangosms drfsms drfiransms chelseru lor lur bahman rashnu sobhan bahman bahman rashnu melipayamak parsianwebco sms جنگو پیامک ملی اایران کاوه نگار python kavenegar kave negar meli payamak",
)
