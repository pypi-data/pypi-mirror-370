from xnum import convert, NumeralSystem

TEST_CASE_NAME = "Gujarati tests"
GUJARATI_DIGITS = "૦૧૨૩૪૫૬૭૮૯"


def test_identity_conversion():
    assert convert(GUJARATI_DIGITS, source=NumeralSystem.GUJARATI, target=NumeralSystem.GUJARATI) == GUJARATI_DIGITS


def test_gujarati_to_english1():
    assert convert(GUJARATI_DIGITS, source=NumeralSystem.GUJARATI, target=NumeralSystem.ENGLISH) == "0123456789"


def test_gujarati_to_english2():
    assert convert(f"abc {GUJARATI_DIGITS} abc", source=NumeralSystem.GUJARATI, target=NumeralSystem.ENGLISH) == "abc 0123456789 abc"


def test_gujarati_to_persian1():
    assert convert(GUJARATI_DIGITS, source=NumeralSystem.GUJARATI, target=NumeralSystem.PERSIAN) == "۰۱۲۳۴۵۶۷۸۹"


def test_gujarati_to_persian2():
    assert convert(f"abc {GUJARATI_DIGITS} abc", source=NumeralSystem.GUJARATI, target=NumeralSystem.PERSIAN) == "abc ۰۱۲۳۴۵۶۷۸۹ abc"


def test_gujarati_to_hindi1():
    assert convert(GUJARATI_DIGITS, source=NumeralSystem.GUJARATI, target=NumeralSystem.HINDI) == "०१२३४५६७८९"


def test_gujarati_to_hindi2():
    assert convert(f"abc {GUJARATI_DIGITS} abc", source=NumeralSystem.GUJARATI, target=NumeralSystem.HINDI) == "abc ०१२३४५६७८९ abc"


def test_gujarati_to_arabic_indic1():
    assert convert(GUJARATI_DIGITS, source=NumeralSystem.GUJARATI, target=NumeralSystem.ARABIC_INDIC) == "٠١٢٣٤٥٦٧٨٩"


def test_gujarati_to_arabic_indic2():
    assert convert(f"abc {GUJARATI_DIGITS} abc", source=NumeralSystem.GUJARATI, target=NumeralSystem.ARABIC_INDIC) == "abc ٠١٢٣٤٥٦٧٨٩ abc"


def test_gujarati_to_bengali1():
    assert convert(GUJARATI_DIGITS, source=NumeralSystem.GUJARATI, target=NumeralSystem.BENGALI) == "০১২৩৪৫৬৭৮৯"


def test_gujarati_to_bengali2():
    assert convert(f"abc {GUJARATI_DIGITS} abc", source=NumeralSystem.GUJARATI, target=NumeralSystem.BENGALI) == "abc ০১২৩৪৫৬৭৮৯ abc"


def test_gujarati_to_thai1():
    assert convert(GUJARATI_DIGITS, source=NumeralSystem.GUJARATI, target=NumeralSystem.THAI) == "๐๑๒๓๔๕๖๗๘๙"


def test_gujarati_to_thai2():
    assert convert(f"abc {GUJARATI_DIGITS} abc", source=NumeralSystem.GUJARATI, target=NumeralSystem.THAI) == "abc ๐๑๒๓๔๕๖๗๘๙ abc"


def test_gujarati_to_khmer1():
    assert convert(GUJARATI_DIGITS, source=NumeralSystem.GUJARATI, target=NumeralSystem.KHMER) == "០១២៣៤៥៦៧៨៩"


def test_gujarati_to_khmer2():
    assert convert(f"abc {GUJARATI_DIGITS} abc", source=NumeralSystem.GUJARATI, target=NumeralSystem.KHMER) == "abc ០១២៣៤៥៦៧៨៩ abc"


def test_gujarati_to_burmese1():
    assert convert(GUJARATI_DIGITS, source=NumeralSystem.GUJARATI, target=NumeralSystem.BURMESE) == "၀၁၂၃၄၅၆၇၈၉"


def test_gujarati_to_burmese2():
    assert convert(f"abc {GUJARATI_DIGITS} abc", source=NumeralSystem.GUJARATI, target=NumeralSystem.BURMESE) == "abc ၀၁၂၃၄၅၆၇၈၉ abc"


def test_gujarati_to_tibetan1():
    assert convert(GUJARATI_DIGITS, source=NumeralSystem.GUJARATI, target=NumeralSystem.TIBETAN) == "༠༡༢༣༤༥༦༧༨༩"


def test_gujarati_to_tibetan2():
    assert convert(f"abc {GUJARATI_DIGITS} abc", source=NumeralSystem.GUJARATI, target=NumeralSystem.TIBETAN) == "abc ༠༡༢༣༤༥༦༧༨༩ abc"


def test_gujarati_to_odia1():
    assert convert(GUJARATI_DIGITS, source=NumeralSystem.GUJARATI, target=NumeralSystem.ODIA) == "୦୧୨୩୪୫୬୭୮୯"


def test_gujarati_to_odia2():
    assert convert(f"abc {GUJARATI_DIGITS} abc", source=NumeralSystem.GUJARATI, target=NumeralSystem.ODIA) == "abc ୦୧୨୩୪୫୬୭୮୯ abc"


def test_gujarati_to_telugu1():
    assert convert(GUJARATI_DIGITS, source=NumeralSystem.GUJARATI, target=NumeralSystem.TELUGU) == "౦౧౨౩౪౫౬౭౮౯"


def test_gujarati_to_telugu2():
    assert convert(f"abc {GUJARATI_DIGITS} abc", source=NumeralSystem.GUJARATI, target=NumeralSystem.TELUGU) == "abc ౦౧౨౩౪౫౬౭౮౯ abc"


def test_gujarati_to_kannada1():
    assert convert(GUJARATI_DIGITS, source=NumeralSystem.GUJARATI, target=NumeralSystem.KANNADA) == "೦೧೨೩೪೫೬೭೮೯"


def test_gujarati_to_kannada2():
    assert convert(f"abc {GUJARATI_DIGITS} abc", source=NumeralSystem.GUJARATI, target=NumeralSystem.KANNADA) == "abc ೦೧೨೩೪೫೬೭೮೯ abc"


def test_gujarati_to_gurmukhi1():
    assert convert(GUJARATI_DIGITS, source=NumeralSystem.GUJARATI, target=NumeralSystem.GURMUKHI) == "੦੧੨੩੪੫੬੭੮੯"


def test_gujarati_to_gurmukhi2():
    assert convert(f"abc {GUJARATI_DIGITS} abc", source=NumeralSystem.GUJARATI, target=NumeralSystem.GURMUKHI) == "abc ੦੧੨੩੪੫੬੭੮੯ abc"
