from django.template.loader import render_to_string
from django.conf import settings

CAMPOS_ENCABEZADOS = (
    ("ordenCompra", "int"),
    ("plantaEntrega", "str"),
    ("noLineaArticulo", "str"),
    ("noAcreedor", "int"),
    ("eMail", "str"),
)

def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/viscofan.xml", diccionario)