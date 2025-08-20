from setuptools import setup, find_packages

setup(
    name="vectocore",  # 패키지 이름
    version="1.1.1",  # 패키지 버전
    author="hd-ai-lab",  # 작성자 이름
    author_email="store_admin@hyundaifuturenet.co.kr",  # 작성자 이메일
    description="A simple vector core library",  # 패키지 설명
    long_description=open("README.md").read(),  # 패키지 설명 (README.md)
    long_description_content_type="text/markdown",  # 설명 파일 형식
    url="https://www.vectocore.com/",  # 프로젝트 URL
    packages=find_packages(),  # 자동으로 패키지 찾기
    classifiers=[  # 패키지 분류 정보
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "json_autocomplete"],
    python_requires=">=3.6",  # 필요한 파이썬 버전
)
