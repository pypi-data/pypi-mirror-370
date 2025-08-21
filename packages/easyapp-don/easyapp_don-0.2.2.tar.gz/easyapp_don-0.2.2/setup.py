from setuptools import setup,find_packages
with open("README.txt","r",encoding="utf-8") as file:
    r = file.read()
setup(name="easyapp_don",
      version="0.2.2",
      author="LvYanHua",
      description="A simple tool for building apps—even easier than Kivy and KivyMD!",
      packages=find_packages(),
      python_requires=">=3.7",
      install_requires=["kivy>=2.3.0",
                        "kivymd>=1.2.0"],
      package_data={"easyapp_don":["images/*"],
                    "easyapp_don.supermarket":["images/*"],
                    "easyapp_don.image":["images/*"],
                    "easyapp_don.supermarket.indexbooks":["images/*"]},
      author_email="at034000@qq.com",
      long_description=str(r),
      license="MIT")