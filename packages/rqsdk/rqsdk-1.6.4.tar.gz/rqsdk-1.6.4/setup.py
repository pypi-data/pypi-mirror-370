# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

import versioneer

version_map = {}
version_map["rqdatac"] = {
    "wcwidth",
    "tabulate <= 0.8.10; python_version <= '3.6'",
    "tabulate >= 0.9.0; python_version >= '3.7'",
    "requests",
    "pyopenssl>22.0.0; python_version >= '3.7'",  #  cryptography 的版本由 pyopenssl 来指定
    # 高版本的 cryptography 在 python3.9/windows 下可能会遇到 ImportError: https://stackoverflow.com/questions/78853596/how-to-solve-importerror-dll-load-failed-while-importing-rust
    "cryptography==41.0.7; python_version == '3.9'",
    "cryptography==2.9.2; python_version <= '3.6'",  # python 3.6.0 有点过分,pip更新报错，cryptography版本太高也报错
    "click>=7.0",
    "pyjwt==1.7.1",
    "patsy>=0.5.1",
    "statsmodels>=0.12.1",
    "scipy <= 1.7.3; python_version <= '3.7'",
    "scipy >= 1.8.0, <= 1.10.1; python_version >= '3.8' and python_version <= '3.11'",
    "scipy >= 1.11.2; python_version >= '3.12'",  # 低版本在python 3.12 下无法正常安装
    "numpy>=1.19.5; python_version <= '3.6'",
    "numpy>=1.20.0; python_version == '3.7'",
    "numpy>=1.23.0; python_version >= '3.8'",  # numpy 1.23.0 修改了类型大小
    "numpy>=2.0.0; python_version >= '3.12'",  # Python 3.12 及以上版本使用 numpy 2.0+
    "pandas >= 1.3.1",
    "pandas>=2.2.0; platform_system=='Linux' and python_version>='3.12'", # Linux 系统的 Python 3.12 环境无法安装较低版本的 pandas
    "python-rapidjson <= 1.5; python_version <= '3.6'",  # rapidjson 1.6 开始不再提供 python 3.6 的 whl 包
    "rqdatac>=3.2.8",  # 3.2.8 版本开始引入 REITs 数据
    "rqdatac_fund==1.0.*,>=1.0.18"
}
version_map["rqfactor"] = version_map["rqdatac"] | {
    "ta-lib>=0.4.38",
    "rqfactor==1.3.*,>=1.3.1",
}
version_map["rqoptimizer"] = version_map["rqdatac"] | {
    "ecos==2.0.10",
    "scs>=2.1.4",
    "cvxpy==1.1.18 ; python_version == '3.6'",
    "cvxpy==1.2.0 ; python_version >= '3.7' and python_version <= '3.11'",
    "cvxpy>=1.6.0 ; python_version >= '3.12'",
    "osqp==0.6.2.post5 ; python_version <= '3.10'",
    "osqp>=0.6.2.post8 ; python_version >= '3.11'",
    "rqoptimizer>=1.2.17",
}
version_map["rqalpha_plus"] = version_map["rqfactor"] | {
    "rqalpha==5.6.*,>=5.6.2",
    "rqalpha-mod-option==1.2.*,>=1.2.3",
    "rqalpha-mod-optimizer2==1.0.*,>=1.0.9",
    "rqalpha-mod-convertible==1.2.*,>=1.2.19",
    "rqalpha-mod-ricequant-data==2.5.*,>=2.5.0",
    "rqalpha-mod-rqfactor==1.0.*,>=1.0.11",
    "rqalpha-mod-spot==1.0.*,>=1.0.11",
    "rqalpha-mod-fund==0.0.*,>=0.0.16",
    "rqalpha-mod-incremental==0.0.*,>=0.0.9",
    "rqalpha-mod-ams==1.3.*,>= 1.3.3",
    "rqalpha-plus==4.3.*,>=4.3.3",
    "rqrisk==1.0.*,>=1.0.9",
    "h5py>=3.0.0",
    "hdf5plugin",
    "matplotlib>=3.1.0",
}
version_map["rqpattr"] = version_map["rqdatac"] | {
    "rqpattr>=0.0.2"
}

extras_require = {k: list(v) for k, v in version_map.items()}

with open('README.md', encoding="utf8") as f:
    readme = f.read()

with open('HISTORY.md', encoding="utf8") as f:
    history = f.read()

setup(
    name="rqsdk",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Ricequant Native SDK",
    long_description="",
    author="Ricequant",
    author_email="public@ricequant.com",
    keywords="rqsdk",
    url="https://www.ricequant.com/",
    include_package_data=True,
    packages=find_packages(include=["rqsdk", "rqsdk.*"]),
    install_requires=extras_require["rqdatac"],
    python_requires=">=3.6.1",
    extras_require=extras_require,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "rqsdk = rqsdk:entry_point"
        ]
    },
)
