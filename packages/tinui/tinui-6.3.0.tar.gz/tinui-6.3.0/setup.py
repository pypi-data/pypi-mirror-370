import setuptools

with open("README.md", "r",encoding='utf-8') as f:
  long_description = f.read()

setuptools.setup(name='tinui',  # 包名
      version='6.3.0',  # 版本号
      description='使用tkinter.Canvas绘制现代UI组件',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Smart-Space',
      author_email='smart-space@qq.com',
      url='https://github.com/Smart-Space/TinUI',
      python_requires='>=3.6',
      license='GPL License',
      packages=setuptools.find_packages(),
      include_package_data = True,
      classifiers=[
          'Intended Audience :: Developers',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries'
      ],
      )
