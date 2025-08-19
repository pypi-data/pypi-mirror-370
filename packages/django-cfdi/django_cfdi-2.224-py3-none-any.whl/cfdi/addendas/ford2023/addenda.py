from django.template.loader import render_to_string
from django.conf import settings

CAMPOS_ENCABEZADOS = (
    ("Purchaseorder", "str"),
    ("asn1", "str"),
    ("asn2", "str"),
    ("asn3", "str"),
    ("vendorcode", "str"),
    ("plant", "str"),
)

def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/ford2023.xml", diccionario)
