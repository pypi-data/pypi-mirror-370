from .descuentos import Descuentos
from .impuestos import Impuestos
from .precios import Precios

class GestorVentas:
    def __init__(self, precio_base, impuesto_porcentaje, descuento_porcentaje ):
        self.precio_base=precio_base
        self.impuesto=Impuestos(impuesto_porcentaje)
        self.descuento=Descuentos(descuento_porcentaje)

    def calcular_precio_final(self):
        impuesto_aplicado=self.impuesto.aplicar_impuestos(self.precio_base)
        descuento_aplicado=self.descuento.aplicar_descuento(self.precio_base)
        precio_final=Precios.calcular_precio_final(self.precio_base, impuesto_aplicado,descuento_aplicado)
        return round(precio_final, 2)

