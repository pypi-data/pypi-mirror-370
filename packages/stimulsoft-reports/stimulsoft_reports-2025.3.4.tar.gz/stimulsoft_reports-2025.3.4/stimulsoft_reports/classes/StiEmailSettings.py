class StiEmailSettings:
    
    fromAddr: str = None
    """Email address of the sender."""

    name: str = None
    """Name and surname of the sender."""

    toAddr: str = None
    """Email address of the recipient."""

    subject: str = None
    """Email Subject."""

    message: str = None
    """Text of the Email."""

    attachmentName: str = None
    """Attached file name."""

    charset = 'utf-8'
    """Charset for the message."""

    host: str = None
    """Address of the SMTP server."""

    port = 465
    """Port of the SMTP server."""

    secure = 'SSL'
    """The secure connection prefix - 'SSL' or 'TLS'."""

    login: str = None
    """Login (Username or Email)."""

    password: str = None
    """Password."""

    cc = []
    """The array of 'cc' addresses."""

    bcc = []
    """The array of 'bcc' addresses."""