class StiLicenseStatic:

### Fields

    __licenseKey: str = None
    __licenseFile: str = None


### License

    @staticmethod
    def setKey(key: str) -> None:
        """Sets the license key in Base64 format."""

        StiLicenseStatic.__licenseKey = key

    @staticmethod
    def setFile(file: str) -> None:
        """Sets the path or URL to the license key file."""

        StiLicenseStatic.__licenseFile = file
        