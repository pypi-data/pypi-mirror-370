from setuptools import setup, find_packages

setup(
    name="flaskkits_boilerplate",
    version="0.1.3",
    description="Starter kit Flask modern dengan struktur rapi, integrasi Tailwind CSS, dan perintah CLI sederhana.",
    url="https://github.com/lahadiyani/flaskkit",
    author="Hadiani",
    author_email="lahadiyani@gmail.com",
    license="MIT",

    packages=find_packages(),
    include_package_data=True,
    package_data={
        "flaskkits_boilerplate": [
            "starter/Jsvanilla-tailwind/**/*",
        ],
    },
    install_requires=[
        "Flask",
        "Flask-SQLAlchemy",
        "pymysql",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "flaskkit=flaskkits_boilerplate.cli:main",
        ],
    },
)