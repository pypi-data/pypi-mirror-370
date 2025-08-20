from setuptools import setup, find_packages

setup(
    name='sthg_ontology_base',
    version='0.0.19',
    packages=find_packages(include=['sthg_ontology_base*']),
    description='ontology base',
    # long_description=open('sthg_base_common/README.md').read(),
    long_description_content_type='text/markdown',
    author='DongQing',
    author_email='maoyouyu@163.com',
    url='https://github.com/yourusername/your_package_name',
    install_requires=[
        # 依赖项列表
        "PyMySQL >=1.1.1",  # 数据库驱动:ml-citation{ref="3,4" data="citationList"}
        "SQLAlchemy >=1.4.44",  #sqlalchemy:ml-citation{ref="3,4" data="citationList"}
    ],
    classifiers=[
        # 包分类列表，例如：
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
)
