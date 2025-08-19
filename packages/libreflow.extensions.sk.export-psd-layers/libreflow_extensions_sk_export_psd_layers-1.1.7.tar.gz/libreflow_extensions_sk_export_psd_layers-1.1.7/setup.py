import setuptools
import versioneer
import os

readme = os.path.normpath(os.path.join(__file__, "..", "README.md"))
with open(readme, "r", encoding="utf-8") as fh:
    long_description = fh.read()

long_description += "\n\n"

changelog = os.path.normpath(os.path.join(__file__, "..", "CHANGELOG.md"))
with open(changelog, "r", encoding="utf-8") as fh:
    long_description += fh.read()


setuptools.setup(
    name="libreflow.extensions.sk.export_psd_layers",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Thomas Thiebaut",
    author_email="autor@les-fees-speciales.coop",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/lfs.coop/libreflow/libreflow_launcher",
    license="LGPLv3+",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
    keywords="kabaret libreflow",
    install_requires=["psd-tools"],
    python_requires=">=3.7",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    package_data={
        "": ["*.css", "*.png", "*.jsx"],
    },
)
