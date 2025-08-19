from setuptools import setup, find_packages

setup(
    name="sirp_test",  # Name of the library
    version="1.0.2",
    author="Muhammad Waqar Anwar",
    author_email="waqar@sirp.io",
    description="Test library for Sirp",
    package_dir={"": "src"},  # Tell setuptools packages are in src/
    packages=find_packages(where="src"),
    include_package_data=True,
    zip_safe=False,
    package_data={
        "sirp_test": ["*.so"],  # Include the .so binary
    },
)