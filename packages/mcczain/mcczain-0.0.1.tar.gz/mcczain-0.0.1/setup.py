from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'A simple streaming package'
LONG_DESCRIPTION = 'A package that allows building simple streams of video, audio, and camera data.'

setup(
    name="mcczain",
    version=VERSION,
    author="syed",
    author_email="syedadil093@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/plain",
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
