**== PROJECT ARCHITECTURE ==**



&nbsp; -- Directories and Files --			 -- Description --

.

├── docs.md					*Documentation*

├── readme.md					*High level readme (installation)*

├── pvevti\_development\_guide.md			*This file!*

├── LICENSE					*License file*

├── pyproject.toml				*Project file containing build instructions*

├── *dist*					*The directory containing wheels and tarballs to be uploaded*

│   ├── pvevti-VERSION-py3-none-any.whl		*Example wheel*

│   └── pvevti-VERSION.tar.gz			*Example tarball*

└── *src*						*Source directory*

&nbsp;   └── *pvevti*					*pvevti directory*

&nbsp;       ├── \_\_init\_\_.py				*Python for pre-import and diagnostics*

&nbsp;       ├── csvutil.py				*CSV Utilities module*

&nbsp;       ├── genutil.py				*General Utilities module*

        ├── mf4util.py				*MF4 Utilities module*

        ├── pdfutil.py				*PDF Utilities module*

        ├── jsonutil.py				*JSON Utilities module*

&nbsp;       ├── prefs.json				*Base Preferences file* 

        └── *\_\_pycache\_\_*				*Directory containing temp files*





**== API KEYS ==**

An API key is a unique identifier that allows you to upload to the dist without any login credentials. Do not share!

The two distributions reflect a typical development cycle of a test branch (frequent updates) and a main branch (infrequent stable updates). pvevti doesn't subscribe to this type of development, since it is not a production-ready library. Consequently, only the main branch is used (even though the testing branch can be used).



*Testing Distribution (test.pypi.org)*

pypi-AgENdGVzdC5weXBpLm9yZwIkOTAzN2NlNmItZDY5Mi00OGViLWE3OTAtNjM4ZGQyYjA3YzNhAAIqWzMsImVmOTc0YjNiLWNjNWItNDVkMi04ZDJmLTA5MDNjZTVhZWYzZSJdAAAGILuL6n2Qe8AzjNRs3HK6Op\_dxW45ulJ5WL2WQo4ZQPj3



*Real Distribution (pypi.org) <- use this one!*

pypi-AgEIcHlwaS5vcmcCJDFmNTNmNDU2LWNhZGUtNGVlNy1hOTM4LTc1NDMzNDNhNWUwOAACKlszLCJmZTc1OWE5MC1mZjdlLTRjYjItODliMC1mOTA2MjI0YzA1ZDQiXQAABiBUch5nJcv2U-yuQW7btSsS84AmUZn-TeRNpqpMqoG5Mw





**== COMMANDS ==**

Run these in order to build, upload, and install pvevti.



*py -m build*

  Must be run while the current working directory is the same as the project directory -- i.e. C:\\...\\pvevti

  Builds the project into distributable formats (tarball and wheel).



*py -m twine upload --repository pypi dist/\* --verbose*

  Uploads the built wheels and tarballs to the main branch. Again, run from the project directory.

&nbsp; When prompted, enter the *pypi.org* API key.

  Exclude --verbose if you don't want to see a boatload of text.

&nbsp; It will re-upload existing files. For example, if you have built and uploaded 8.18.0 in the past, the wheel and tarball will remain in *./dist/* and continue to be reuploaded until you delete the associated wheel and tarball.



*pip install pvevti --upgrade*

  Upgrade the existing on-machine installation of pvevti from the uploaded version on pypi.

  If run too soon after upload, it will simply reinstall the old version. If that happens, just try again.





**== COMMON BUILD ISSUES ==**

These are the most frequent issues when trying to build and upload to the dist.

 1. Invalid API key, with some question about 'special characters'

      Try pasting the API key using *Ctrl+Shift+V* instead of *Ctrl+V*.

 2. Upload failed, with a versioning issue

      Once a file is uploaded with a version (8.19.0), a new build cannot be uploaded with the same version.

      Make sure the version in *pyproject.toml* is unique and reflected in *\_\_init.py\_\_*.

