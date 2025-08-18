import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scCAMEL",
    version="0.45b",
    author="Yizhou Hu",
    author_email="yizhou.hu@ki.se",
    description="scCAMEL: single cell Cross- Annotation and Multimodal Estimation on Lineage trajectory;License: GPL version 3;Developed by: Yizhou Hu, Department of Laboratory Medicine, Karolinska Institutet;Tutorials and other informations in :https://sccamel.readthedocs.io/",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://sccamel.readthedocs.io/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS"],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
install_requires=[
        'arboreto','openpyxl','skorch','kneed','captum','scanpy'],
)