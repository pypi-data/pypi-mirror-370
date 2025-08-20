from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rb-commons",
    version="0.7.13",
    author="Abdulvoris",
    author_email="erkinovabdulvoris101@gmail.com",
    description="Commons of project and simplified orm based on sqlalchemy.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RoboSell-organization/rb-commons",  # Replace with your repo URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
    install_requires=[
        "annotated-types==0.7.0",
        "greenlet==3.1.1",
        "pydantic>=1.7.4,<3.0.0",
        "PyJWT==2.10.1",
        "python-dotenv==1.0.1",
        "SQLAlchemy==2.0.36",
        "fastapi>=0.115.6,<0.120.0",
        "aio-pika==9.5.5"
    ],
)
