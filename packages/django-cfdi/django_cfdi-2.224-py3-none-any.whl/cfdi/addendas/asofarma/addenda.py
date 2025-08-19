from django.template.loader import render_to_string
from django.conf import settings


CAMPOS_ENCABEZADOS = (
    ("ordenCompra", "str"),
    ("folio", "str"),
    ("serie", "str"),
    ("noProveedor", "str"),
    ("tipoProveedor", "str"),
    ("otros", "str"),
    ("ivaDevengado", "str"),
    ("ivaAcreditable", "str"),
    ("noPartida", "str"),
)


def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/asofarma.xml", diccionario)
