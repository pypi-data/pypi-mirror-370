from setuptools import setup, find_packages

setup(
    name='cw_sdk',
    version='0.2.1',
    author='Manuel Traverso',
    author_email='mtraverso@customswatch.com',
    description='Utils para SharePoint y Graph API para Customs Watch',
    packages=find_packages(),
    install_requires=[
        'msal',
        'requests'
    ],
    python_requires='>=3.8',
    license='MIT',  # ✅ Este campo es el correcto para setup.py
    url='https://github.com/customswatch/cw_sdk',
    project_urls={
        "Repository": "https://github.com/customswatch/cw_sdk"
    }
)
