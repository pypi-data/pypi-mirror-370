from django.template.loader import render_to_string
from django.conf import settings

CAMPOS_ENCABEZADOS = (
	("moneda", "str"),
	("id_factura", "str"),
)
CAMPOS_DETALLE = (
	("num_posicion", "str"),
	("num_oc", "str"),
    ("cantidad", "str"),
    ("valor_unitario", "str"),
    ("importe", "str"),
)

def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/zfsachs.xml", diccionario)
