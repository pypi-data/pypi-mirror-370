import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    #Application name and details
     name='trex_program',
     description="TRex Program package",
     long_description=long_description,
     long_description_content_type="text/markdown",  
     url="https://bitbucket.org/lokjac/trex-program",
     version='1.6.8',
     
     #Author details
     author="Jack Lok",
     author_email="sglok77@gmail.com",
     
     #packages=setuptools.find_packages(),
     packages=setuptools.find_packages(),
     
     #include additional files
     #package_data = {
     #   # If any package contains *.txt or *.rst files, include them:
     #   '': ['*.*'],
     #},
     
     include_package_data=True,
     
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     install_requires=[            
          'trex-lib',
          'trex-model',
      ],
 )

