from setuptools import setup, find_packages

setup(
    name="accuknox-llm-defense",
    version="0.1.1",
    author="Yash Sanjay Kulkarni",
    author_email="yashkulkarni2023@gmail.com",
    description="Python SDK for AccuKnox LLM Defence API",
    packages=find_packages(),
    install_requires=[
        "requests>=2.20.0",
        "pyjwt>=2.3.0"
    ],
    python_requires=">=3.7",
    url="https://github.com/yourusername/accuknox-llm-defense",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
