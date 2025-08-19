# import codecs
# import os
from setuptools import setup, find_packages

# these things are needed for the README.md show on pypi
# here = os.path.abspath(os.path.dirname(__file__))
#
# with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
#     long_description = "\n" + fh.read()


VERSION = '1.3.10'
DESCRIPTION = 'ailuoge'
LONG_DESCRIPTION = '增加了批量上传函数的是否打印参数'

# Setting up
setup(
    name="ailuoge",
    version=VERSION,
    author="ailuoge",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python','ailuoge'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)