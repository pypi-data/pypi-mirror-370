from setuptools import setup, find_packages

# อ่าน long description จาก README.md (ถ้ามี)
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "The OneChat Python library provides an interface for sending messages, broadcasting messages to multiple users, sending location information, sending stickers, and sending files through the OneChat API."  # fallback text

setup(
    name="one-chat-api",  # ชื่อ package
    version="0.3.2",  # เวอร์ชันของ package
    description="The OneChat Python library provides an interface for sending messages, broadcasting messages to multiple users, sending location information, sending stickers, and sending files through the OneChat API.",
    long_description=long_description,  # รายละเอียดยาว
    long_description_content_type="text/markdown",  # ประเภทของเนื้อหาคำอธิบายยาว
    author="Pargorn Ruasijan (xNewz)",  # ชื่อของผู้พัฒนา
    author_email="contact@pargorn.com",  # อีเมลของผู้พัฒนา
    packages=find_packages(),  # หาชื่อ package ที่อยู่ในโฟลเดอร์
    install_requires=[
        "requests",  # ไลบรารีที่จำเป็น
    ],
    python_requires=">=3.6",  # ระบุเวอร์ชันของ Python ที่รองรับ
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
