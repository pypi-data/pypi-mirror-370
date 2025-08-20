from enum import Enum


class StiDbfCodePages(Enum):
    """Enumeration for setting Code Pages."""

    DEFAULT = 0
    """A parameter indicating that the code page of the exported document will not be specified."""

    USDOS = 437
    """A code page of the exported document is U.S. MS-DOS. Code page number 437."""
    
    MAZOVIA_DOS = 620
    """A code page of the exported document is Mazovia (Polish) MS-DOS. Code page number 620."""
    
    GREEK_DOS = 737
    """A code page of the exported document is Greek MS-DOS (437G). Code page number 737."""
    
    INTERNATIONAL_DOS = 850
    """A code page of the exported document is International MS-DOS. Code page number 850."""

    EASTERN_EUROPEAN_DOS = 852
    """A code page of the exported document is Eastern European MS-DOS. Code page number 852."""
    
    ICELANDIC_DOS = 861
    """A code page of the exported document is Icelandic MS-DOS. Code page number 861."""

    NORDIC_DOS = 865
    """A code page of the exported document is Nordic MS-DOS. Code page number 865."""

    RUSSIAN_DOS = 866
    """A code page of the exported document is Russian MS-DOS. Code page number 866."""
    
    KAMENICKY_DOS = 895
    """A code page of the exported document is Kamenicky (Czech) MS-DOS. Code page number 895."""
    
    TURKISH_DOS = 857
    """A code page of the exported document is Turkish MS-DOS. Code page number 857."""

    EASTERN_EUROPEAN_WINDOWS = 1250
    """A code page of the exported document is EasternEuropean MS-DOS. Code page number 1250."""

    RUSSIAN_WINDOWS = 1251
    """A code page of the exported document is Russian Windows. Code page number 1251."""

    WINDOWS_ANSI = 1252
    """A code page of the exported document is Windows ANSI. Code page number 1252."""

    GREEK_WINDOWS = 1253
    """A code page of the exported document is Greek Windows. Code page number 1253."""

    TURKISH_WINDOWS = 1254
    """A code page of the exported document is Turkish Windows. Code page number 1254."""
    
    STANDARD_MACINTOSH = 10000
    """A code page of the exported document is Standard Macintosh. Code page number 10000."""

    GREEK_MACINTOSH = 10006
    """A code page of the exported document is Greek Macintosh. Code page number 10006."""
    
    RUSSIAN_MACINTOSH = 10007
    """A code page of the exported document is Russian Macintosh. Code page number 10007."""
    
    EASTERN_EUROPEAN_MACINTOSH = 10029
    """A code page of the exported document is Eastern European Macintosh. Code page number 10029."""