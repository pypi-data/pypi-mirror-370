from contentgrid_application_client import hal_form_type_check


def test_hal_from_type_check():
    number = 12
    boolean = True
    string = "test"
    url = "https://b93ccecf-3466-44c0-995e-2620a8c66ac3.eu-west-1.contentgrid.cloud/skills/b4d84ca3-b436-4522-a1c3-71aaaf6f73ce"
    datetime = "2024-03-20T16:48:59.904Z"

    assert hal_form_type_check["text"](string)
    assert hal_form_type_check["datetime"](datetime)
    assert hal_form_type_check["checkbox"](boolean)
    assert hal_form_type_check["number"](number)
    assert hal_form_type_check["url"](url)

    assert not hal_form_type_check["text"](number)
    assert not hal_form_type_check["number"](string)
    assert not hal_form_type_check["checkbox"]("true")
    assert not hal_form_type_check["datetime"]("2024-03-20")
