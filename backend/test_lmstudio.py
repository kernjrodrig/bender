#!/usr/bin/env python3
"""
Script de prueba para verificar la conectividad con LMStudio
"""

import asyncio
import httpx
import json

async def test_lmstudio_connection():
    """Prueba la conectividad con LMStudio"""
    url = "http://192.168.10.80:8089"
    
    print(f"🔍 Probando conexión con LMStudio en: {url}")
    
    try:
        async with httpx.AsyncClient() as client:
            # Probar endpoint de chat de LMStudio (formato OpenAI)
            print("💬 Probando endpoint /v1/chat/completions...")
            payload = {
                "model": "meta-llama-3-8b-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hola, responde solo 'OK' si me escuchas."
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.7,
                "stream": False
            }
            
            chat_response = await client.post(
                f"{url}/v1/chat/completions",
                json=payload,
                timeout=30.0
            )
            
            if chat_response.status_code == 200:
                chat_data = chat_response.json()
                print("✅ Conexión exitosa con LMStudio!")
                # LMStudio devuelve la respuesta en formato OpenAI
                respuesta = chat_data.get("choices", [{}])[0].get("message", {}).get("content", "Sin respuesta")
                print(f"🤖 Respuesta de prueba: {respuesta[:100]}...")
                print(f"📊 Status: {chat_response.status_code}")
                print(f"🔗 URL: {url}")
            else:
                print(f"❌ Error en chat: {chat_response.status_code}")
                print(f"📝 Respuesta: {chat_response.text}")
                
    except httpx.TimeoutException:
        print("⏰ Timeout: La conexión tardó demasiado")
    except httpx.ConnectError:
        print("🔌 Error de conexión: No se pudo conectar al servidor")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de conectividad con LMStudio...")
    asyncio.run(test_lmstudio_connection())
    print("\n✨ Pruebas completadas") 