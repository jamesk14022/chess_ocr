from setuptools import setup, find_packages

setup(
    name='chess_ocr',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'openai==1.3.3',
        'numpy==1.22.4',
        'opencv_python==4.8.0.76',
        'pandas==1.3.5',
        'Pillow==9.0.0',
        'pytesseract==0.3.10'
    ],
)
