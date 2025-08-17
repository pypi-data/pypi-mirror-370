from setuptools import setup, find_packages

setup(
    name="dakit",                 
    version="0.0.1",               
    author="Hongda Zhang",
    author_email="1324904307@qq.com",
    description="A toolkit for data processing",  
    long_description=open("README.md").read(),   
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dakit",  
    packages=find_packages(),       
    classifiers=[                   
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",        
    install_requires=[              
        "numpy>=1.18.0",
        "pandas>=1.0.0",
    ],
    extras_require={                
        "dev": ["pytest", "black"]
    }
)
