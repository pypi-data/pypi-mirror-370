class Precios:
    @staticmethod #decorador que sirve para los metodos estaicos, no dependen de una instancia particular dela clase, no pueden acceder a los atributos o metodos de la instacia
    def calcular_precio_final(precio_base, impuesto, descuento):
        return precio_base+impuesto-descuento
    
    
