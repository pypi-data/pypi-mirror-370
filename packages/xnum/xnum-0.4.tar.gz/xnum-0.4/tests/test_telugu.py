from xnum import convert, NumeralSystem

TEST_CASE_NAME = "Telugu tests"
TELUGU_DIGITS = "౦౧౨౩౪౫౬౭౮౯"


def test_identity_conversion():
    assert convert(TELUGU_DIGITS, source=NumeralSystem.TELUGU, target=NumeralSystem.TELUGU) == TELUGU_DIGITS


def test_telugu_to_english1():
    assert convert(TELUGU_DIGITS, source=NumeralSystem.TELUGU, target=NumeralSystem.ENGLISH) == "0123456789"


def test_telugu_to_english2():
    assert convert(f"abc {TELUGU_DIGITS} abc", source=NumeralSystem.TELUGU, target=NumeralSystem.ENGLISH) == "abc 0123456789 abc"


def test_telugu_to_persian1():
    assert convert(TELUGU_DIGITS, source=NumeralSystem.TELUGU, target=NumeralSystem.PERSIAN) == "۰۱۲۳۴۵۶۷۸۹"


def test_telugu_to_persian2():
    assert convert(f"abc {TELUGU_DIGITS} abc", source=NumeralSystem.TELUGU, target=NumeralSystem.PERSIAN) == "abc ۰۱۲۳۴۵۶۷۸۹ abc"


def test_telugu_to_hindi1():
    assert convert(TELUGU_DIGITS, source=NumeralSystem.TELUGU, target=NumeralSystem.HINDI) == "०१२३४५६७८९"


def test_telugu_to_hindi2():
    assert convert(f"abc {TELUGU_DIGITS} abc", source=NumeralSystem.TELUGU, target=NumeralSystem.HINDI) == "abc ०१२३४५६७८९ abc"


def test_telugu_to_arabic_indic1():
    assert convert(TELUGU_DIGITS, source=NumeralSystem.TELUGU, target=NumeralSystem.ARABIC_INDIC) == "٠١٢٣٤٥٦٧٨٩"


def test_telugu_to_arabic_indic2():
    assert convert(f"abc {TELUGU_DIGITS} abc", source=NumeralSystem.TELUGU, target=NumeralSystem.ARABIC_INDIC) == "abc ٠١٢٣٤٥٦٧٨٩ abc"


def test_telugu_to_bengali1():
    assert convert(TELUGU_DIGITS, source=NumeralSystem.TELUGU, target=NumeralSystem.BENGALI) == "০১২৩৪৫৬৭৮৯"


def test_telugu_to_bengali2():
    assert convert(f"abc {TELUGU_DIGITS} abc", source=NumeralSystem.TELUGU, target=NumeralSystem.BENGALI) == "abc ০১২৩৪৫৬৭৮৯ abc"


def test_telugu_to_thai1():
    assert convert(TELUGU_DIGITS, source=NumeralSystem.TELUGU, target=NumeralSystem.THAI) == "๐๑๒๓๔๕๖๗๘๙"


def test_telugu_to_thai2():
    assert convert(f"abc {TELUGU_DIGITS} abc", source=NumeralSystem.TELUGU, target=NumeralSystem.THAI) == "abc ๐๑๒๓๔๕๖๗๘๙ abc"


def test_telugu_to_khmer1():
    assert convert(TELUGU_DIGITS, source=NumeralSystem.TELUGU, target=NumeralSystem.KHMER) == "០១២៣៤៥៦៧៨៩"


def test_telugu_to_khmer2():
    assert convert(f"abc {TELUGU_DIGITS} abc", source=NumeralSystem.TELUGU, target=NumeralSystem.KHMER) == "abc ០១២៣៤៥៦៧៨៩ abc"


def test_telugu_to_burmese1():
    assert convert(TELUGU_DIGITS, source=NumeralSystem.TELUGU, target=NumeralSystem.BURMESE) == "၀၁၂၃၄၅၆၇၈၉"


def test_telugu_to_burmese2():
    assert convert(f"abc {TELUGU_DIGITS} abc", source=NumeralSystem.TELUGU, target=NumeralSystem.BURMESE) == "abc ၀၁၂၃၄၅၆၇၈၉ abc"


def test_telugu_to_tibetan1():
    assert convert(TELUGU_DIGITS, source=NumeralSystem.TELUGU, target=NumeralSystem.TIBETAN) == "༠༡༢༣༤༥༦༧༨༩"


def test_telugu_to_tibetan2():
    assert convert(f"abc {TELUGU_DIGITS} abc", source=NumeralSystem.TELUGU, target=NumeralSystem.TIBETAN) == "abc ༠༡༢༣༤༥༦༧༨༩ abc"


def test_telugu_to_gujarati1():
    assert convert(TELUGU_DIGITS, source=NumeralSystem.TELUGU, target=NumeralSystem.GUJARATI) == "૦૧૨૩૪૫૬૭૮૯"


def test_telugu_to_gujarati2():
    assert convert(f"abc {TELUGU_DIGITS} abc", source=NumeralSystem.TELUGU, target=NumeralSystem.GUJARATI) == "abc ૦૧૨૩૪૫૬૭૮૯ abc"


def test_telugu_to_odia1():
    assert convert(TELUGU_DIGITS, source=NumeralSystem.TELUGU, target=NumeralSystem.ODIA) == "୦୧୨୩୪୫୬୭୮୯"


def test_telugu_to_odia2():
    assert convert(f"abc {TELUGU_DIGITS} abc", source=NumeralSystem.TELUGU, target=NumeralSystem.ODIA) == "abc ୦୧୨୩୪୫୬୭୮୯ abc"


def test_telugu_to_kannada1():
    assert convert(TELUGU_DIGITS, source=NumeralSystem.TELUGU, target=NumeralSystem.KANNADA) == "೦೧೨೩೪೫೬೭೮೯"


def test_telugu_to_kannada2():
    assert convert(f"abc {TELUGU_DIGITS} abc", source=NumeralSystem.TELUGU, target=NumeralSystem.KANNADA) == "abc ೦೧೨೩೪೫೬೭೮೯ abc"


def test_telugu_to_gurmukhi1():
    assert convert(TELUGU_DIGITS, source=NumeralSystem.TELUGU, target=NumeralSystem.GURMUKHI) == "੦੧੨੩੪੫੬੭੮੯"


def test_telugu_to_gurmukhi2():
    assert convert(f"abc {TELUGU_DIGITS} abc", source=NumeralSystem.TELUGU, target=NumeralSystem.GURMUKHI) == "abc ੦੧੨੩੪੫੬੭੮੯ abc"
