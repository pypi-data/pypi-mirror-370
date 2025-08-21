import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xldashboard",
    version="0.1.3",
    author="xlartas",
    author_email="ivanhvalevskey@gmail.com",
    description="More beautiful/customizable admin dashboard for Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Artasov/xldashboard",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=4.0,<5.3",
        "django-jazzmin>=3.0.1",
        "pyperclip>=1.8.0",
        "aiohttp>=3.8.0",
        "celery>=5.0.0",
    ],
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 4",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5",
        "Framework :: Django :: 5.1",
        "Framework :: Django :: 5.2",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires='>=3.8',
    keywords='dashboard django app apps jazzmin xldashboard utils admin beautiful funcs features',
    project_urls={
        'Source': 'https://github.com/Artasov/xldashboard ',
        'Tracker': 'https://github.com/Artasov/xldashboard /issues',
    },
)
