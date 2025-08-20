from enum import Enum


class PaperKind(Enum):
    
    CUSTOM = 0
    """The paper size is defined by the user."""

    LETTER = 1
    """Letter paper (8.5 in. by 11 in.)."""

    LEGAL = 5
    """Legal paper (8.5 in. by 14 in.)."""

    A4 = 9
    """A4 paper (210 mm by 297 mm)."""

    C_SHEET = 24
    """C paper (17 in. by 22 in.)."""

    D_SHEET = 25
    """D paper (22 in. by 34 in.)."""

    E_SHEET = 26
    """E paper (34 in. by 44 in.)."""

    LETTER_SMALL = 2
    """Letter small paper (8.5 in. by 11 in.)."""

    TABLOID = 3
    """Tabloid paper (11 in. by 17 in.)."""

    LEDGER = 4
    """Ledger paper (17 in. by 11 in.)."""

    STATEMENT = 6
    """Statement paper (5.5 in. by 8.5 in.)."""

    EXECUTIVE = 7
    """Executive paper (7.25 in. by 10.5 in.)."""

    A3 = 8
    """A3 paper (297 mm by 420 mm)."""

    A4_SMALL = 10
    """A4 small paper (210 mm by 297 mm)."""

    A5 = 11
    """A5 paper (148 mm by 210 mm)."""

    B4 = 12
    """B4 paper (250 mm by 353 mm)."""

    B5 = 13
    """B5 paper (176 mm by 250 mm)."""

    FOLIO = 14
    """Folio paper (8.5 in. by 13 in.)."""

    QUARTO = 15
    """Quarto paper (215 mm by 275 mm)."""

    STANDARD_10X14 = 16
    """Standard paper (10 in. by 14 in.)."""

    STANDARD_11X17 = 17
    """Standard paper (11 in. by 17 in.)."""

    NOTE = 18
    """Note paper (8.5 in. by 11 in.)."""

    NUMBER_9_ENVELOPE = 19
    """#9 envelope (3.875 in. by 8.875 in.)."""

    NUMBER_10_ENVELOPE = 20
    """#10 envelope (4.125 in. by 9.5 in.)."""

    NUMBER_11_ENVELOPE = 21
    """#11 envelope (4.5 in. by 10.375 in.)."""

    NUMBER_12_ENVELOPE = 22
    """#12 envelope (4.75 in. by 11 in.)."""

    NUMBER_14_ENVELOPE = 23
    """#14 envelope (5 in. by 11.5 in.)."""

    DL_ENVELOPE = 27
    """DL envelope (110 mm by 220 mm)."""

    C5_ENVELOPE = 28
    """C5 envelope (162 mm by 229 mm)."""

    C3_ENVELOPE = 29
    """C3 envelope (324 mm by 458 mm)."""

    C4_ENVELOPE = 30
    """C4 envelope (229 mm by 324 mm)."""

    C6_ENVELOPE = 31

    C65_ENVELOPE = 32
    """C65 envelope (114 mm by 229 mm)."""

    B4_ENVELOPE = 33
    """B4 envelope (250 mm by 353 mm)."""

    B5_ENVELOPE = 34
    """B5 envelope (176 mm by 250 mm)."""

    B6_ENVELOPE = 35
    """B6 envelope (176 mm by 125 mm)."""

    ITALY_ENVELOPE = 36
    """Italy envelope (110 mm by 230 mm)."""

    MONARCH_ENVELOPE = 37
    """Monarch envelope (3.875 in. by 7.5 in.)."""

    PERSONAL_ENVELOPE = 38
    """6 3/4 envelope (3.625 in. by 6.5 in.)."""

    US_STANDARD_FANFOLD = 39
    """US standard fanfold (14.875 in. by 11 in.)."""

    GERMAN_STANDARD_FANFOLD = 40
    """German standard fanfold (8.5 in. by 12 in.)."""

    GERMAN_LEGAL_FANFOLD = 41
    """German legal fanfold (8.5 in. by 13 in.)."""

    ISO_B4 = 42
    """ISO B4 (250 mm by 353 mm)."""

    JAPANESE_POSTCARD = 43
    """Japanese postcard (100 mm by 148 mm)."""

    STANDARD_9X11 = 44
    """Standard paper (9 in. by 11 in.)."""

    STANDARD_10X11 = 45
    """Standard paper (10 in. by 11 in.)."""

    STANDARD_15X11 = 46
    """Standard paper (15 in. by 11 in.)."""

    INVITE_ENVELOPE = 47
    """Invitation envelope (220 mm by 220 mm)."""

    LETTER_EXTRA = 50
    """
    Letter extra paper (9.275 in. by 12 in.). This value is specific to the PostScript
    driver and is used only by Linotronic printers in order to conserve paper.
    """

    LEGAL_EXTRA = 51
    """
    Legal extra paper (9.275 in. by 15 in.). This value is specific to the PostScript
    driver and is used only by Linotronic printers in order to conserve paper.
    """

    TABLOID_EXTRA = 52
    """
    Tabloid extra paper (11.69 in. by 18 in.). This value is specific to the PostScript
    driver and is used only by Linotronic printers in order to conserve paper.
    """

    A4_EXTRA = 53
    """
    A4 extra paper (236 mm by 322 mm). This value is specific to the PostScript driver 
    and is used only by Linotronic printers to help save paper.
    """

    LETTER_TRANSVERSE = 54
    """Letter transverse paper (8.275 in. by 11 in.)."""

    A4_TRANSVERSE = 55
    """A4 transverse paper (210 mm by 297 mm)."""

    LETTER_EXTRA_TRANSVERSE = 56
    """Letter extra transverse paper (9.275 in. by 12 in.)."""

    A_PLUS = 57
    """SuperA/SuperA/A4 paper (227 mm by 356 mm)."""

    B_PLUS = 58
    """SuperB/SuperB/A3 paper (305 mm by 487 mm)."""

    LETTER_PLUS = 59
    """Letter plus paper (8.5 in. by 12.69 in.)."""

    A4_PLUS = 60
    """A4 plus paper (210 mm by 330 mm)."""

    A5_TRANSVERSE = 61
    """A5 transverse paper (148 mm by 210 mm)."""

    B5_TRANSVERSE = 62
    """JIS B5 transverse paper (182 mm by 257 mm)."""

    A3_EXTRA = 63
    """A3 extra paper (322 mm by 445 mm)."""

    A5_EXTRA = 64
    """A5 extra paper (174 mm by 235 mm)."""

    B5_EXTRA = 65
    """ISO B5 extra paper (201 mm by 276 mm)."""

    A2 = 66
    """A2 paper (420 mm by 594 mm)."""

    A3_TRANSVERSE = 67
    """A3 transverse paper (297 mm by 420 mm)."""

    A3_EXTRA_TRANSVERSE = 68
    """A3 extra transverse paper (322 mm by 445 mm)."""

    JAPANESE_DOUBLE_POSTCARD = 69
    """Japanese double postcard (200 mm by 148 mm). Requires Windows 98, Windows NT 4.0, or later."""

    A6 = 70
    """A6 paper (105 mm by 148 mm). Requires Windows 98, Windows NT 4.0, or later."""

    JAPANESE_ENVELOPE_KAKU_NUMBER_2 = 71
    """Japanese Kaku #2 envelope. Requires Windows 98, Windows NT 4.0, or later."""

    JAPANESE_ENVELOPE_KAKU_NUMBER_3 = 72
    """Japanese Kaku #3 envelope. Requires Windows 98, Windows NT 4.0, or later."""

    JAPANESE_ENVELOPE_CHOU_NUMBER_3 = 73
    """Japanese Chou #3 envelope. Requires Windows 98, Windows NT 4.0, or later."""

    JAPANESE_ENVELOPE_CHOU_NUMBER_4 = 74
    """Japanese Chou #4 envelope. Requires Windows 98, Windows NT 4.0, or later."""

    LETTER_ROTATED = 75
    """Letter rotated paper (11 in. by 8.5 in.)."""

    A3_ROTATED = 76
    """A3 rotated paper (420 mm by 297 mm)."""

    A4_ROTATED = 77
    """A4 rotated paper (297 mm by 210 mm). Requires Windows 98, Windows NT 4.0, or later."""

    A5_ROTATED = 78
    """A5 rotated paper (210 mm by 148 mm). Requires Windows 98, Windows NT 4.0, or later."""

    B4_JIS_ROTATED = 79
    """JIS B4 rotated paper (364 mm by 257 mm). Requires Windows 98, Windows NT 4.0, or later."""

    B5_JIS_ROTATED = 80
    """JIS B5 rotated paper (257 mm by 182 mm). Requires Windows 98, Windows NT 4.0, or later."""

    JAPANESE_POSTCARD_ROTATED = 81
    """Japanese rotated postcard (148 mm by 100 mm). Requires Windows 98, Windows NT 4.0, or later."""

    JAPANESE_DOUBLE_POSTCARD_ROTATED = 82
    """Japanese rotated double postcard (148 mm by 200 mm). Requires Windows 98, Windows NT 4.0, or later."""

    A6_ROTATED = 83
    """A6 rotated paper (148 mm by 105 mm). Requires Windows 98, Windows NT 4.0, or later."""

    JAPANESE_ENVELOPE_KAKU_NUMBER_2_ROTATED = 84
    """Japanese rotated Kaku #2 envelope. Requires Windows 98, Windows NT 4.0, or later."""

    JAPANESE_ENVELOPE_KAKU_NUMBER_3_ROTATED = 85
    """Japanese rotated Kaku #3 envelope. Requires Windows 98, Windows NT 4.0, or later."""

    JAPANESE_ENVELOPE_CHOU_NUMBER_3_ROTATED = 86
    """Japanese rotated Chou #3 envelope. Requires Windows 98, Windows NT 4.0, or later."""

    JAPANESE_ENVELOPE_CHOU_NUMBER_4_ROTATED = 87
    """Japanese rotated Chou #4 envelope. Requires Windows 98, Windows NT 4.0, or later."""

    B6_JIS = 88
    """JIS B6 paper (128 mm by 182 mm). Requires Windows 98, Windows NT 4.0, or later."""

    B6_JIS_ROTATED = 89
    """JIS B6 rotated paper (182 mm by 128 mm). Requires Windows 98, Windows NT 4.0, or later."""

    STANDARD_12X11 = 90
    """Standard paper (12 in. by 11 in.). Requires Windows 98, Windows NT 4.0, or later."""

    JAPANESE_ENVELOPE_YOU_NUMBER_4 = 91
    """Japanese You #4 envelope. Requires Windows 98, Windows NT 4.0, or later."""

    JAPANESE_ENVELOPE_YOU_NUMBER_4_ROTATED = 92
    """Japanese You #4 rotated envelope. Requires Windows 98, Windows NT 4.0, or later."""

    PRC_16K = 93
    """16K paper (146 mm by 215 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_32K = 94
    """32K paper (97 mm by 151 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_32K_BIG = 95
    """32K big paper (97 mm by 151 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_1 = 96
    """#1 envelope (102 mm by 165 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_2 = 97
    """#2 envelope (102 mm by 176 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_3 = 98
    """#3 envelope (125 mm by 176 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_4 = 99
    """#4 envelope (110 mm by 208 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_5 = 100
    """#5 envelope (110 mm by 220 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_6 = 101
    """#6 envelope (120 mm by 230 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_7 = 102
    """#7 envelope (160 mm by 230 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_8 = 103
    """#8 envelope (120 mm by 309 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_9 = 104
    """#9 envelope (229 mm by 324 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOP_ENUMBER_10 = 105
    """#10 envelope (324 mm by 458 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_16K_ROTATED = 106
    """16K rotated paper (146 mm by 215 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_32K_ROTATED = 107
    """32K rotated paper (97 mm by 151 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_32K_BIG_ROTATED = 108
    """32K big rotated paper (97 mm by 151 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_1_ROTATED = 109
    """#1 rotated envelope (165 mm by 102 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_2_ROTATED = 110
    """#2 rotated envelope (176 mm by 102 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_3_ROTATED = 111
    """#3 rotated envelope (176 mm by 125 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_4_ROTATED = 112
    """#4 rotated envelope (208 mm by 110 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_5_ROTATED = 113
    """Envelope #5 rotated envelope (220 mm by 110 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_6_ROTATED = 114
    """#6 rotated envelope (230 mm by 120 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_7_ROTATED = 115
    """#7 rotated envelope (230 mm by 160 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_8_ROTATED = 116
    """#8 rotated envelope (309 mm by 120 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_9_ROTATED = 117
    """#9 rotated envelope (324 mm by 229 mm). Requires Windows 98, Windows NT 4.0, or later."""

    PRC_ENVELOPE_NUMBER_10_ROTATED = 118
    """#10 rotated envelope (458 mm by 324 mm). Requires Windows 98, Windows NT 4.0, or later."""
