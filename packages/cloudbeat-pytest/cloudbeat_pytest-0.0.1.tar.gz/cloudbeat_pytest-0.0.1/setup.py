import os
from setuptools import setup

PACKAGE = "cloudbeat-pytest"

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Framework :: Pytest',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Topic :: Software Development :: Quality Assurance',
    'Topic :: Software Development :: Testing',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
]

install_requires = [
    "attrs>=16.0.0",
    "pluggy>=0.4.0",
    "cloudbeat_common"
]

def get_readme(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def main():
    setup(
        name=PACKAGE,
        version="0.0.1",  # Hardcoded version here
        description="CloudBeat Pytest Kit",
        url="https://cloudbeat.io/",
        project_urls={
            "Source": "https://github.com/cloudbeat-io/cb-kit-python",
        },
        author="CBNR Cloud Solutions LTD",
        author_email="info@cloudbeat.io",
        license="Apache-2.0",
        classifiers=classifiers,
        keywords="cloudbeat testing reporting python pytest",
        # long_description=get_readme("README.md"),
        long_description_content_type="text/markdown",
        packages=["cloudbeat_pytest"],
        package_dir={"cloudbeat_pytest": 'src'},
        entry_points={"pytest11": ["cloudbeat_pytest = cloudbeat_pytest.plugin"]},
        py_modules=['cloudbeat_pytest'],
        python_requires='>=3.6',
        
        # COMMENTED OUT OLD CODE
        # setup_requires=["setuptools_scm"],
        # use_scm_version=prepare_version,
    )

if __name__ == '__main__':
    main()
