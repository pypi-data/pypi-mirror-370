from django.template.loader import render_to_string
from django.conf import settings

CAMPOS_DETALLE = (
    ("no_identificacion", "str"),
    ("orden_compra", "str"),
)

def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/veritiv.xml", diccionario)
