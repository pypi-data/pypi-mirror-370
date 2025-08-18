from xnum import convert, NumeralSystem

TEST_CASE_NAME = "Khmer tests"
KHMER_DIGITS = "០១២៣៤៥៦៧៨៩"


def test_identity_conversion():
    assert convert(KHMER_DIGITS, source=NumeralSystem.KHMER, target=NumeralSystem.KHMER) == KHMER_DIGITS


def test_khmer_to_english1():
    assert convert(KHMER_DIGITS, source=NumeralSystem.KHMER, target=NumeralSystem.ENGLISH) == "0123456789"


def test_khmer_to_english2():
    assert convert(f"abc {KHMER_DIGITS} abc", source=NumeralSystem.KHMER,
                   target=NumeralSystem.ENGLISH) == "abc 0123456789 abc"


def test_khmer_to_persian1():
    assert convert(KHMER_DIGITS, source=NumeralSystem.KHMER, target=NumeralSystem.PERSIAN) == "۰۱۲۳۴۵۶۷۸۹"


def test_khmer_to_persian2():
    assert convert(f"abc {KHMER_DIGITS} abc", source=NumeralSystem.KHMER, target=NumeralSystem.PERSIAN) == "abc ۰۱۲۳۴۵۶۷۸۹ abc"


def test_khmer_to_hindi1():
    assert convert(KHMER_DIGITS, source=NumeralSystem.KHMER, target=NumeralSystem.HINDI) == "०१२३४५६७८९"


def test_khmer_to_hindi2():
    assert convert(f"abc {KHMER_DIGITS} abc", source=NumeralSystem.KHMER,
                   target=NumeralSystem.HINDI) == "abc ०१२३४५६७८९ abc"


def test_khmer_to_arabic_indic1():
    assert convert(KHMER_DIGITS, source=NumeralSystem.KHMER, target=NumeralSystem.ARABIC_INDIC) == "٠١٢٣٤٥٦٧٨٩"


def test_khmer_to_arabic_indic2():
    assert convert(f"abc {KHMER_DIGITS} abc", source=NumeralSystem.KHMER,
                   target=NumeralSystem.ARABIC_INDIC) == "abc ٠١٢٣٤٥٦٧٨٩ abc"


def test_khmer_to_bengali1():
    assert convert(KHMER_DIGITS, source=NumeralSystem.KHMER, target=NumeralSystem.BENGALI) == "০১২৩৪৫৬৭৮৯"


def test_khmer_to_bengali2():
    assert convert(f"abc {KHMER_DIGITS} abc", source=NumeralSystem.KHMER,
                   target=NumeralSystem.BENGALI) == "abc ০১২৩৪৫৬৭৮৯ abc"


def test_khmer_to_thai1():
    assert convert(KHMER_DIGITS, source=NumeralSystem.KHMER, target=NumeralSystem.THAI) == "๐๑๒๓๔๕๖๗๘๙"


def test_khmer_to_thai2():
    assert convert(f"abc {KHMER_DIGITS} abc", source=NumeralSystem.KHMER,
                   target=NumeralSystem.THAI) == "abc ๐๑๒๓๔๕๖๗๘๙ abc"


def test_khmer_to_burmese1():
    assert convert(KHMER_DIGITS, source=NumeralSystem.KHMER, target=NumeralSystem.BURMESE) == "၀၁၂၃၄၅၆၇၈၉"


def test_khmer_to_burmese2():
    assert convert(f"abc {KHMER_DIGITS} abc", source=NumeralSystem.KHMER,
                   target=NumeralSystem.BURMESE) == "abc ၀၁၂၃၄၅၆၇၈၉ abc"


def test_khmer_to_tibetan1():
    assert convert(KHMER_DIGITS, source=NumeralSystem.KHMER, target=NumeralSystem.TIBETAN) == "༠༡༢༣༤༥༦༧༨༩"


def test_khmer_to_tibetan2():
    assert convert(f"abc {KHMER_DIGITS} abc", source=NumeralSystem.KHMER,
                   target=NumeralSystem.TIBETAN) == "abc ༠༡༢༣༤༥༦༧༨༩ abc"


def test_khmer_to_gujarati1():
    assert convert(KHMER_DIGITS, source=NumeralSystem.KHMER, target=NumeralSystem.GUJARATI) == "૦૧૨૩૪૫૬૭૮૯"


def test_khmer_to_gujarati2():
    assert convert(f"abc {KHMER_DIGITS} abc", source=NumeralSystem.KHMER,
                   target=NumeralSystem.GUJARATI) == "abc ૦૧૨૩૪૫૬૭૮૯ abc"


def test_khmer_to_odia1():
    assert convert(KHMER_DIGITS, source=NumeralSystem.KHMER, target=NumeralSystem.ODIA) == "୦୧୨୩୪୫୬୭୮୯"


def test_khmer_to_odia2():
    assert convert(f"abc {KHMER_DIGITS} abc", source=NumeralSystem.KHMER,
                   target=NumeralSystem.ODIA) == "abc ୦୧୨୩୪୫୬୭୮୯ abc"


def test_khmer_to_telugu1():
    assert convert(KHMER_DIGITS, source=NumeralSystem.KHMER, target=NumeralSystem.TELUGU) == "౦౧౨౩౪౫౬౭౮౯"


def test_khmer_to_telugu2():
    assert convert(f"abc {KHMER_DIGITS} abc", source=NumeralSystem.KHMER,
                   target=NumeralSystem.TELUGU) == "abc ౦౧౨౩౪౫౬౭౮౯ abc"


def test_khmer_to_kannada1():
    assert convert(KHMER_DIGITS, source=NumeralSystem.KHMER, target=NumeralSystem.KANNADA) == "೦೧೨೩೪೫೬೭೮೯"


def test_khmer_to_kannada2():
    assert convert(f"abc {KHMER_DIGITS} abc", source=NumeralSystem.KHMER,
                   target=NumeralSystem.KANNADA) == "abc ೦೧೨೩೪೫೬೭೮೯ abc"


def test_khmer_to_gurmukhi1():
    assert convert(KHMER_DIGITS, source=NumeralSystem.KHMER, target=NumeralSystem.GURMUKHI) == "੦੧੨੩੪੫੬੭੮੯"


def test_khmer_to_gurmukhi2():
    assert convert(f"abc {KHMER_DIGITS} abc", source=NumeralSystem.KHMER, target=NumeralSystem.GURMUKHI) == "abc ੦੧੨੩੪੫੬੭੮੯ abc"
