from setuptools import setup, find_packages

setup(
    name="BotUi",
    version="0.1.0",
    packages=find_packages(include=["BotUi", "BotUi.*"]),
    install_requires=[
        "selenium",
        "opencv-python",
        "pillow",
        "pydantic",
        "pyyaml",
        "pytesseract",
        "rapidocr-onnxruntime",
        "webdriver-manager",
    ],
    python_requires=">=3.10",
)
