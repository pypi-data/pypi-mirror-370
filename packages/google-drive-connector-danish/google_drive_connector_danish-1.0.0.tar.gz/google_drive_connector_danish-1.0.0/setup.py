from setuptools import setup, find_packages

setup(
    name="google_drive_connector_danish",
    version="1.0.0",
    author="Danish",
    author_email="tabnoone@gmail.com",
    description="A utility class to interact with Google Drive using OAuth 2.0 credentials.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    py_modules=["gdrive_connector"],
    python_requires=">=3.8",
    install_requires=[
        "google-api-python-client==2.179.0",
        "google-auth==2.40.3",
        "python-dotenv==1.1.1"
    ],
)
