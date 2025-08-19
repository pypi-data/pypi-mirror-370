import setuptools 

setuptools.setup(
    name="ClickMouse",
    version="0.1.0",
    author="xystudio",
    author_email="173288240@qq.com", 
    description="基于Python的鼠标连点工具",
    url="https://github.com/xystudio/pyClickMouse",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["mouse", "click", "automation", "clickmouse"], 
    python_requires='>=3.10',
    install_requires=['pyautogui'],
    entry_points={
        "console_scripts": [
            "clickmouse = clickmouse.__main__:main",
        ]
    }, 
)
