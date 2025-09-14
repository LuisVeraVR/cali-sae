#!/usr/bin/env python3
"""
Script para generar el hash SHA-256 de contraseñas
Úsalo para calcular el hash correcto de cualquier contraseña
"""

import hashlib

def generate_password_hash(password):
    """Generar hash SHA-256 de una contraseña"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

if __name__ == "__main__":
    # Contraseñas a probar
    passwords = [
        "FacturasElectronicas2024",
        "facturas2024",
        "FACTURAS2024", 
        "Facturas123",
        "admin123"
    ]
    
    print("=" * 60)
    print("GENERADOR DE HASH DE CONTRASEÑAS")
    print("=" * 60)
    
    for pwd in passwords:
        hash_value = generate_password_hash(pwd)
        print(f"Contraseña: '{pwd}'")
        print(f"Hash SHA-256: {hash_value}")
        print("-" * 60)
    
    # Permitir entrada personalizada
    print("\nIngresa una contraseña personalizada (o presiona Enter para salir):")
    while True:
        custom_pwd = input("Contraseña: ").strip()
        if not custom_pwd:
            break
        
        custom_hash = generate_password_hash(custom_pwd)
        print(f"Hash para '{custom_pwd}': {custom_hash}")
        print()
