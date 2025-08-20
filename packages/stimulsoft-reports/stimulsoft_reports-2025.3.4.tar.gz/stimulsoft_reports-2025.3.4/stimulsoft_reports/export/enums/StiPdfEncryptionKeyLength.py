from enum import Enum


class StiPdfEncryptionKeyLength(Enum):
    """Enumeration which sets an encryption key length of the resulting pdf file."""

    BIT40 = 1
    """RC4 algorithm, 40 bit encryption key length (Acrobat 3)."""
    
    BIT128 = 2
    """RC4 algorithm, 128 bit encryption key length (Acrobat 5)."""
    
    BIT128_R4 = 3
    """AES algorithm, 128 bit encryption key length, revision 4 (Acrobat 7)."""
    
    BIT256_R5 = 4
    """AES algorithm, 256 bit encryption key length, revision 5 (Acrobat 9)."""
    
    BIT256_R6 = 5
    """AES algorithm, 256 bit encryption key length, revision 6 (Acrobat X)."""