from setuptools import setup, find_packages # Import find_packages

setup(
    name='fx-shared-models',
    version='0.2.81', # Incremented version after adding shared_models/__init__.py
    packages=find_packages(include=['shared_models', 'shared_models.*']),  # Find packages under the shared_models directory
    install_requires=[
        'Django>=4.2',  # Match the version from requirements.txt if possible
        'django-environ>=0.10.0',
        'djangorestframework>=3.14.0', # Added dependency
        'pytz', # Added dependency (often needed with Django)
        'django-encrypted-model-fields>=0.6.0', # Added dependency for encrypted fields (Specify a minimum version if known)
    ],
    python_requires='>=3.8',
    author='FX Backend',
    author_email='fxbackend@gmail.com',
    description='Shared models for FX Backend',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/fxbackend/fx-shared-models',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django',
    ],
    include_package_data=True,
)
