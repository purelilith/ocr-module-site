from extract import parse_fields, validate, detect_doc_type
from cleanup import clean_name

text = """СПРАВКА ОБ ОБУЧЕНИИ
ФИО студента: Соколов Олег Игоревич
Название вуза: Учебный университет «Меридиан»
Направление подготовки: 38.03.01 Экономика
Форма обучения: очная
Начало периода обучения: 01.09.2023
Окончание периода обучения: 31 августа 2026
Номер справки: ОБ-1006
Дата выдачи:
"""
print(detect_doc_type(text))
fields = parse_fields(text, "study_certificate")
fields["signature_present"] = True
fields["seal_present"] = False
print(fields)
print(validate("study_certificate", fields))
print(clean_name("и3ан"))