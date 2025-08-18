from xnum import convert, NumeralSystem

TEST_CASE_NAME = "Burmese tests"
BURMESE_DIGITS = "၀၁၂၃၄၅၆၇၈၉"


def test_identity_conversion():
    assert convert(BURMESE_DIGITS, source=NumeralSystem.BURMESE, target=NumeralSystem.BURMESE) == BURMESE_DIGITS


def test_burmese_to_english1():
    assert convert(BURMESE_DIGITS, source=NumeralSystem.BURMESE, target=NumeralSystem.ENGLISH) == "0123456789"


def test_burmese_to_english2():
    assert convert(f"abc {BURMESE_DIGITS} abc", source=NumeralSystem.BURMESE,
                   target=NumeralSystem.ENGLISH) == "abc 0123456789 abc"


def test_burmese_to_persian1():
    assert convert(BURMESE_DIGITS, source=NumeralSystem.BURMESE, target=NumeralSystem.PERSIAN) == "۰۱۲۳۴۵۶۷۸۹"


def test_burmese_to_persian2():
    assert convert(f"abc {BURMESE_DIGITS} abc", source=NumeralSystem.BURMESE,
                   target=NumeralSystem.PERSIAN) == "abc ۰۱۲۳۴۵۶۷۸۹ abc"


def test_burmese_to_hindi1():
    assert convert(BURMESE_DIGITS, source=NumeralSystem.BURMESE, target=NumeralSystem.HINDI) == "०१२३४५६७८९"


def test_burmese_to_hindi2():
    assert convert(f"abc {BURMESE_DIGITS} abc", source=NumeralSystem.BURMESE,
                   target=NumeralSystem.HINDI) == "abc ०१२३४५६७८९ abc"


def test_burmese_to_arabic_indic1():
    assert convert(BURMESE_DIGITS, source=NumeralSystem.BURMESE, target=NumeralSystem.ARABIC_INDIC) == "٠١٢٣٤٥٦٧٨٩"


def test_burmese_to_arabic_indic2():
    assert convert(f"abc {BURMESE_DIGITS} abc", source=NumeralSystem.BURMESE,
                   target=NumeralSystem.ARABIC_INDIC) == "abc ٠١٢٣٤٥٦٧٨٩ abc"


def test_burmese_to_bengali1():
    assert convert(BURMESE_DIGITS, source=NumeralSystem.BURMESE, target=NumeralSystem.BENGALI) == "০১২৩৪৫৬৭৮৯"


def test_burmese_to_bengali2():
    assert convert(f"abc {BURMESE_DIGITS} abc", source=NumeralSystem.BURMESE,
                   target=NumeralSystem.BENGALI) == "abc ০১২৩৪৫৬৭৮৯ abc"


def test_burmese_to_thai1():
    assert convert(BURMESE_DIGITS, source=NumeralSystem.BURMESE, target=NumeralSystem.THAI) == "๐๑๒๓๔๕๖๗๘๙"


def test_burmese_to_thai2():
    assert convert(f"abc {BURMESE_DIGITS} abc", source=NumeralSystem.BURMESE,
                   target=NumeralSystem.THAI) == "abc ๐๑๒๓๔๕๖๗๘๙ abc"


def test_burmese_to_khmer1():
    assert convert(BURMESE_DIGITS, source=NumeralSystem.BURMESE, target=NumeralSystem.KHMER) == "០១២៣៤៥៦៧៨៩"


def test_burmese_to_khmer2():
    assert convert(f"abc {BURMESE_DIGITS} abc", source=NumeralSystem.BURMESE,
                   target=NumeralSystem.KHMER) == "abc ០១២៣៤៥៦៧៨៩ abc"


def test_burmese_to_tibetan1():
    assert convert(BURMESE_DIGITS, source=NumeralSystem.BURMESE, target=NumeralSystem.TIBETAN) == "༠༡༢༣༤༥༦༧༨༩"


def test_burmese_to_tibetan2():
    assert convert(f"abc {BURMESE_DIGITS} abc", source=NumeralSystem.BURMESE,
                   target=NumeralSystem.TIBETAN) == "abc ༠༡༢༣༤༥༦༧༨༩ abc"


def test_burmese_to_gujarati1():
    assert convert(BURMESE_DIGITS, source=NumeralSystem.BURMESE, target=NumeralSystem.GUJARATI) == "૦૧૨૩૪૫૬૭૮૯"


def test_burmese_to_gujarati2():
    assert convert(f"abc {BURMESE_DIGITS} abc", source=NumeralSystem.BURMESE,
                   target=NumeralSystem.GUJARATI) == "abc ૦૧૨૩૪૫૬૭૮૯ abc"


def test_burmese_to_odia1():
    assert convert(BURMESE_DIGITS, source=NumeralSystem.BURMESE, target=NumeralSystem.ODIA) == "୦୧୨୩୪୫୬୭୮୯"


def test_burmese_to_odia2():
    assert convert(f"abc {BURMESE_DIGITS} abc", source=NumeralSystem.BURMESE,
                   target=NumeralSystem.ODIA) == "abc ୦୧୨୩୪୫୬୭୮୯ abc"


def test_burmese_to_telugu1():
    assert convert(BURMESE_DIGITS, source=NumeralSystem.BURMESE, target=NumeralSystem.TELUGU) == "౦౧౨౩౪౫౬౭౮౯"


def test_burmese_to_telugu2():
    assert convert(f"abc {BURMESE_DIGITS} abc", source=NumeralSystem.BURMESE,
                   target=NumeralSystem.TELUGU) == "abc ౦౧౨౩౪౫౬౭౮౯ abc"


def test_burmese_to_kannada1():
    assert convert(BURMESE_DIGITS, source=NumeralSystem.BURMESE, target=NumeralSystem.KANNADA) == "೦೧೨೩೪೫೬೭೮೯"


def test_burmese_to_kannada2():
    assert convert(f"abc {BURMESE_DIGITS} abc", source=NumeralSystem.BURMESE,
                   target=NumeralSystem.KANNADA) == "abc ೦೧೨೩೪೫೬೭೮೯ abc"


def test_burmese_to_gurmukhi1():
    assert convert(BURMESE_DIGITS, source=NumeralSystem.BURMESE, target=NumeralSystem.GURMUKHI) == "੦੧੨੩੪੫੬੭੮੯"


def test_burmese_to_gurmukhi2():
    assert convert(f"abc {BURMESE_DIGITS} abc", source=NumeralSystem.BURMESE, target=NumeralSystem.GURMUKHI) == "abc ੦੧੨੩੪੫੬੭੮੯ abc"
