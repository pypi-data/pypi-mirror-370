from django.template.loader import render_to_string
from django.conf import settings

CAMPOS_ENCABEZADOS = (
    ("oc", "str"),
)

def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/zobele.xml", diccionario)
