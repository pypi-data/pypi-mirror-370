"""
 import unittest módulo estándar de Python que se usa para escribir
 y ejecutar pruebas automáticas. Sirve para verificar que tu código funciona correctamente, 
 incluso cuando haces cambios en el futuro.
"""
import unittest
from aplicacion_ventas.gestor_ventas import GestorVentas
from aplicacion_ventas.excepciones import ImpuestoInvalidoError, DescuentoInvalidoError

class TestGestorVentas(unittest.TestCase):

    def test_calculo_precio_final(self):
        gestor=GestorVentas(100.0, 0.05, 0.10)
        self.assertEqual(gestor.calcular_precio_final(), 95.0) #assetEqual revisa si dos valores son iguales
    
    def test_impuesto_invalido(self):
        with self.assertRaises(ImpuestoInvalidoError): #assertraises verifica que la excepcion se valide de forma correcta
            GestorVentas(100.0, 1.5, 0.10)

    def test_descuento_invalido(self):
        with self.assertRaises(DescuentoInvalidoError):
            GestorVentas(100.00, 0.05, 1.5)

if __name__=="__main__":
    unittest.main()
        
