from xnum import convert, NumeralSystem

TEST_CASE_NAME = "Hindi tests"
HINDI_DIGITS = "०१२३४५६७८९"


def test_identity_conversion():
    assert convert(HINDI_DIGITS, source=NumeralSystem.HINDI, target=NumeralSystem.HINDI) == HINDI_DIGITS


def test_hindi_to_english1():
    assert convert(HINDI_DIGITS, source=NumeralSystem.HINDI, target=NumeralSystem.ENGLISH) == "0123456789"


def test_hindi_to_english2():
    assert convert(f"abc {HINDI_DIGITS} abc", source=NumeralSystem.HINDI,
                   target=NumeralSystem.ENGLISH) == "abc 0123456789 abc"


def test_hindi_to_persian1():
    assert convert(HINDI_DIGITS, source=NumeralSystem.HINDI, target=NumeralSystem.PERSIAN) == "۰۱۲۳۴۵۶۷۸۹"


def test_hindi_to_persian2():
    assert convert(f"abc {HINDI_DIGITS} abc", source=NumeralSystem.HINDI,
                   target=NumeralSystem.PERSIAN) == "abc ۰۱۲۳۴۵۶۷۸۹ abc"


def test_hindi_to_arabic_indic1():
    assert convert(HINDI_DIGITS, source=NumeralSystem.HINDI, target=NumeralSystem.ARABIC_INDIC) == "٠١٢٣٤٥٦٧٨٩"


def test_hindi_to_arabic_indic2():
    assert convert(f"abc {HINDI_DIGITS} abc", source=NumeralSystem.HINDI,
                   target=NumeralSystem.ARABIC_INDIC) == "abc ٠١٢٣٤٥٦٧٨٩ abc"


def test_hindi_to_bengali1():
    assert convert(HINDI_DIGITS, source=NumeralSystem.HINDI, target=NumeralSystem.BENGALI) == "০১২৩৪৫৬৭৮৯"


def test_hindi_to_bengali2():
    assert convert(f"abc {HINDI_DIGITS} abc", source=NumeralSystem.HINDI,
                   target=NumeralSystem.BENGALI) == "abc ০১২৩৪৫৬৭৮৯ abc"


def test_hindi_to_thai1():
    assert convert(HINDI_DIGITS, source=NumeralSystem.HINDI, target=NumeralSystem.THAI) == "๐๑๒๓๔๕๖๗๘๙"


def test_hindi_to_thai2():
    assert convert(f"abc {HINDI_DIGITS} abc", source=NumeralSystem.HINDI,
                   target=NumeralSystem.THAI) == "abc ๐๑๒๓๔๕๖๗๘๙ abc"


def test_hindi_to_khmer1():
    assert convert(HINDI_DIGITS, source=NumeralSystem.HINDI, target=NumeralSystem.KHMER) == "០១២៣៤៥៦៧៨៩"


def test_hindi_to_khmer2():
    assert convert(f"abc {HINDI_DIGITS} abc", source=NumeralSystem.HINDI,
                   target=NumeralSystem.KHMER) == "abc ០១២៣៤៥៦៧៨៩ abc"


def test_hindi_to_burmese1():
    assert convert(HINDI_DIGITS, source=NumeralSystem.HINDI, target=NumeralSystem.BURMESE) == "၀၁၂၃၄၅၆၇၈၉"


def test_hindi_to_burmese2():
    assert convert(f"abc {HINDI_DIGITS} abc", source=NumeralSystem.HINDI,
                   target=NumeralSystem.BURMESE) == "abc ၀၁၂၃၄၅၆၇၈၉ abc"


def test_hindi_to_tibetan1():
    assert convert(HINDI_DIGITS, source=NumeralSystem.HINDI, target=NumeralSystem.TIBETAN) == "༠༡༢༣༤༥༦༧༨༩"


def test_hindi_to_tibetan2():
    assert convert(f"abc {HINDI_DIGITS} abc", source=NumeralSystem.HINDI,
                   target=NumeralSystem.TIBETAN) == "abc ༠༡༢༣༤༥༦༧༨༩ abc"


def test_hindi_to_gujarati1():
    assert convert(HINDI_DIGITS, source=NumeralSystem.HINDI, target=NumeralSystem.GUJARATI) == "૦૧૨૩૪૫૬૭૮૯"


def test_hindi_to_gujarati2():
    assert convert(f"abc {HINDI_DIGITS} abc", source=NumeralSystem.HINDI,
                   target=NumeralSystem.GUJARATI) == "abc ૦૧૨૩૪૫૬૭૮૯ abc"


def test_hindi_to_odia1():
    assert convert(HINDI_DIGITS, source=NumeralSystem.HINDI, target=NumeralSystem.ODIA) == "୦୧୨୩୪୫୬୭୮୯"


def test_hindi_to_odia2():
    assert convert(f"abc {HINDI_DIGITS} abc", source=NumeralSystem.HINDI,
                   target=NumeralSystem.ODIA) == "abc ୦୧୨୩୪୫୬୭୮୯ abc"


def test_hindi_to_telugu1():
    assert convert(HINDI_DIGITS, source=NumeralSystem.HINDI, target=NumeralSystem.TELUGU) == "౦౧౨౩౪౫౬౭౮౯"


def test_hindi_to_telugu2():
    assert convert(f"abc {HINDI_DIGITS} abc", source=NumeralSystem.HINDI,
                   target=NumeralSystem.TELUGU) == "abc ౦౧౨౩౪౫౬౭౮౯ abc"


def test_hindi_to_kannada1():
    assert convert(HINDI_DIGITS, source=NumeralSystem.HINDI, target=NumeralSystem.KANNADA) == "೦೧೨೩೪೫೬೭೮೯"


def test_hindi_to_kannada2():
    assert convert(f"abc {HINDI_DIGITS} abc", source=NumeralSystem.HINDI,
                   target=NumeralSystem.KANNADA) == "abc ೦೧೨೩೪೫೬೭೮೯ abc"


def test_hindi_to_gurmukhi1():
    assert convert(HINDI_DIGITS, source=NumeralSystem.HINDI, target=NumeralSystem.GURMUKHI) == "੦੧੨੩੪੫੬੭੮੯"


def test_hindi_to_gurmukhi2():
    assert convert(f"abc {HINDI_DIGITS} abc", source=NumeralSystem.HINDI, target=NumeralSystem.GURMUKHI) == "abc ੦੧੨੩੪੫੬੭੮੯ abc"
