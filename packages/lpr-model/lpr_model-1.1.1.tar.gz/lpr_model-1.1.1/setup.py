from setuptools import setup, find_packages

setup(
    name="lpr_model",                  # 包名
    version="1.1.1",                   # 版本
    packages=find_packages(),          # 自动发现包
    install_requires=[
        "torch>=2.7.0",
        "transformers>=4.32.0",
        "esm>=0.5.0"                   # 你的依赖
    ],
    python_requires=">=3.8",
    include_package_data=True,
    description="A custom LPR model for lipid-binding Protein prediction",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://huggingface.co/Noora68/lpr-0.4B",
    author="FeitongDong",
    author_email="one@ldu.edu.cn",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
