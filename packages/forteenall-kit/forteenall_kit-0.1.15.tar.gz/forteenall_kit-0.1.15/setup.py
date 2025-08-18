import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="forteenall_kit",
version='0.1.15',
    author="Mahdi Nouri",
    author_email="algo.mahdi.nouri@gmail.com",
    description="all agents and AI",
    license="MIT",
    license_files=["LICENSE"],  # مسیر درست فایل لایسنس
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/algonouir/forteenall_kit",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
