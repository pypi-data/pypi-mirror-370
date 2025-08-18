from xnum import convert, NumeralSystem

TEST_CASE_NAME = "Arabic-Indic tests"
ARABIC_INDIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"


def test_identity_conversion():
    assert convert(ARABIC_INDIC_DIGITS, source=NumeralSystem.ARABIC_INDIC,
                   target=NumeralSystem.ARABIC_INDIC) == ARABIC_INDIC_DIGITS


def test_arabic_indic_to_english1():
    assert convert(ARABIC_INDIC_DIGITS, source=NumeralSystem.ARABIC_INDIC, target=NumeralSystem.ENGLISH) == "0123456789"


def test_arabic_indic_to_english2():
    assert convert(f"abc {ARABIC_INDIC_DIGITS} abc", source=NumeralSystem.ARABIC_INDIC,
                   target=NumeralSystem.ENGLISH) == "abc 0123456789 abc"


def test_arabic_indic_to_persian1():
    assert convert(ARABIC_INDIC_DIGITS, source=NumeralSystem.ARABIC_INDIC, target=NumeralSystem.PERSIAN) == "۰۱۲۳۴۵۶۷۸۹"


def test_arabic_indic_to_persian2():
    assert convert(f"abc {ARABIC_INDIC_DIGITS} abc", source=NumeralSystem.ARABIC_INDIC,
                   target=NumeralSystem.PERSIAN) == "abc ۰۱۲۳۴۵۶۷۸۹ abc"


def test_arabic_indic_to_hindi1():
    assert convert(ARABIC_INDIC_DIGITS, source=NumeralSystem.ARABIC_INDIC, target=NumeralSystem.HINDI) == "०१२३४५६७८९"


def test_arabic_indic_to_hindi2():
    assert convert(f"abc {ARABIC_INDIC_DIGITS} abc", source=NumeralSystem.ARABIC_INDIC,
                   target=NumeralSystem.HINDI) == "abc ०१२३४५६७८९ abc"


def test_arabic_indic_to_bengali1():
    assert convert(ARABIC_INDIC_DIGITS, source=NumeralSystem.ARABIC_INDIC, target=NumeralSystem.BENGALI) == "০১২৩৪৫৬৭৮৯"


def test_arabic_indic_to_bengali2():
    assert convert(f"abc {ARABIC_INDIC_DIGITS} abc", source=NumeralSystem.ARABIC_INDIC,
                   target=NumeralSystem.BENGALI) == "abc ০১২৩৪৫৬৭৮৯ abc"


def test_arabic_indic_to_thai1():
    assert convert(ARABIC_INDIC_DIGITS, source=NumeralSystem.ARABIC_INDIC, target=NumeralSystem.THAI) == "๐๑๒๓๔๕๖๗๘๙"


def test_arabic_indic_to_thai2():
    assert convert(f"abc {ARABIC_INDIC_DIGITS} abc", source=NumeralSystem.ARABIC_INDIC,
                   target=NumeralSystem.THAI) == "abc ๐๑๒๓๔๕๖๗๘๙ abc"


def test_arabic_indic_to_khmer1():
    assert convert(ARABIC_INDIC_DIGITS, source=NumeralSystem.ARABIC_INDIC, target=NumeralSystem.KHMER) == "០១២៣៤៥៦៧៨៩"


def test_arabic_indic_to_khmer2():
    assert convert(f"abc {ARABIC_INDIC_DIGITS} abc", source=NumeralSystem.ARABIC_INDIC,
                   target=NumeralSystem.KHMER) == "abc ០១២៣៤៥៦៧៨៩ abc"


def test_arabic_indic_to_burmese1():
    assert convert(ARABIC_INDIC_DIGITS, source=NumeralSystem.ARABIC_INDIC, target=NumeralSystem.BURMESE) == "၀၁၂၃၄၅၆၇၈၉"


def test_arabic_indic_to_burmese2():
    assert convert(f"abc {ARABIC_INDIC_DIGITS} abc", source=NumeralSystem.ARABIC_INDIC,
                   target=NumeralSystem.BURMESE) == "abc ၀၁၂၃၄၅၆၇၈၉ abc"


def test_arabic_indic_to_tibetan1():
    assert convert(ARABIC_INDIC_DIGITS, source=NumeralSystem.ARABIC_INDIC, target=NumeralSystem.TIBETAN) == "༠༡༢༣༤༥༦༧༨༩"


def test_arabic_indic_to_tibetan2():
    assert convert(f"abc {ARABIC_INDIC_DIGITS} abc", source=NumeralSystem.ARABIC_INDIC,
                   target=NumeralSystem.TIBETAN) == "abc ༠༡༢༣༤༥༦༧༨༩ abc"


def test_arabic_indic_to_gujarati1():
    assert convert(
        ARABIC_INDIC_DIGITS,
        source=NumeralSystem.ARABIC_INDIC,
        target=NumeralSystem.GUJARATI) == "૦૧૨૩૪૫૬૭૮૯"


def test_arabic_indic_to_gujarati2():
    assert convert(f"abc {ARABIC_INDIC_DIGITS} abc", source=NumeralSystem.ARABIC_INDIC,
                   target=NumeralSystem.GUJARATI) == "abc ૦૧૨૩૪૫૬૭૮૯ abc"


def test_arabic_indic_to_odia1():
    assert convert(ARABIC_INDIC_DIGITS, source=NumeralSystem.ARABIC_INDIC, target=NumeralSystem.ODIA) == "୦୧୨୩୪୫୬୭୮୯"


def test_arabic_indic_to_odia2():
    assert convert(f"abc {ARABIC_INDIC_DIGITS} abc", source=NumeralSystem.ARABIC_INDIC,
                   target=NumeralSystem.ODIA) == "abc ୦୧୨୩୪୫୬୭୮୯ abc"


def test_arabic_indic_to_telugu1():
    assert convert(ARABIC_INDIC_DIGITS, source=NumeralSystem.ARABIC_INDIC, target=NumeralSystem.TELUGU) == "౦౧౨౩౪౫౬౭౮౯"


def test_arabic_indic_to_telugu2():
    assert convert(f"abc {ARABIC_INDIC_DIGITS} abc", source=NumeralSystem.ARABIC_INDIC,
                   target=NumeralSystem.TELUGU) == "abc ౦౧౨౩౪౫౬౭౮౯ abc"


def test_arabic_indic_to_kannada1():
    assert convert(ARABIC_INDIC_DIGITS, source=NumeralSystem.ARABIC_INDIC, target=NumeralSystem.KANNADA) == "೦೧೨೩೪೫೬೭೮೯"


def test_arabic_indic_to_kannada2():
    assert convert(f"abc {ARABIC_INDIC_DIGITS} abc", source=NumeralSystem.ARABIC_INDIC,
                   target=NumeralSystem.KANNADA) == "abc ೦೧೨೩೪೫೬೭೮೯ abc"


def test_arabic_indic_to_gurmukhi1():
    assert convert(
        ARABIC_INDIC_DIGITS,
        source=NumeralSystem.ARABIC_INDIC,
        target=NumeralSystem.GURMUKHI) == "੦੧੨੩੪੫੬੭੮੯"


def test_arabic_indic_to_gurmukhi2():
    assert convert(f"abc {ARABIC_INDIC_DIGITS} abc", source=NumeralSystem.ARABIC_INDIC, target=NumeralSystem.GURMUKHI) == "abc ੦੧੨੩੪੫੬੭੮੯ abc"
