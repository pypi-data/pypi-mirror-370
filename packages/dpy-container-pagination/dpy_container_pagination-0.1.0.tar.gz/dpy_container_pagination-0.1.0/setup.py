from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="dpy-container-pagination",
    version="0.1.0",
    description="Easily create pagination for your containers.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    py_modules=["Paginator"],
    package_dir={'': "src"},
    url="https://github.com/Migan178/dpy-container-pagination",
    author="Migan178",
    author_email="me@migan.co.kr",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed',
    ]
)
