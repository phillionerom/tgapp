import re

from openai import OpenAI

from config import AI_ENABLED, OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def generate(content: str) -> dict:
    return ai_generate(content) if AI_ENABLED else test_generate(content)


def ai_generate(content: str) -> dict:
    prompt = f"""
Contenido del producto:
{content}

Escribe un título breve y atractivo para este producto (máximo 10 palabras).
Luego, redacta una descripción más larga (máximo 30 palabras) que explique lo que es, qué puntos de dolor resuelve y por qué lo necesitaría.
Tanto el título como la descripción que sean atractivos para hacer ver a la persona que lo lee que es una gran oferta. 
Si el producto tiene tallas, o es una talla concreta, indícalo en la descripción.
Utiliza sesgos psicológicos de ventas y técnicas de neuromarketing.
No repitas el mismo texto en ambos campos. Si no tienes claro el tipo de artículo o producto que es, no inventes, que el título y la descripción entonces 
sean genéricos, que no de pie a confusión, simplemente puedes decir que es una gran oferta, limitada y da sensación de urgencia.

Devuelve también el precio que se encuentra en el mensaje.
Devuelve también el precio original en caso de que se encuentre en el mensaje. Si no, o tienes dudas, déjalo vacío.
Para los precios devuelve sólo el importe, no incluyas la moneda.

Si existe alguna información extra como la talla, el género o alguna información complementaria que puede ser importante conocer, puedes devolverlo también, 
siempre y cuando no aparezca ya esa información en el título o en la descripción que vas a generar, o sea el propio enlace del producto.
En caso de que no consideres nada que cumpla las premisas anteriores, NO ES NECESARIO devolver nada en ese campo. Omite la información irrelevante.
No generes ningún valor por defecto indeterminado tipo: N/A o cosas así, en tal caso, déjalo en blanco.

Si indica la existencia de algún cupón para obtener un mejor precio, devuelve ese código de cupón en la respuesta.

Si en el mensaje encuentras más de un producto, devuelve sólo la información para el primer producto que hayas encontrado. Omite toda información
perteneciente o relativa a los productos posteriores al primero que encuentres en el mensaje, ten esto muy en cuenta.

MUY IMPORTANTE: Omite toda mención al canal de origen del mensaje, sólo queremos información relevante al propio producto.

Formato:
_title: <aquí el título>
_description: <aquí la descripción>
_price: <aquí el precio>
_old_price: <aquí el precio original>
_more_info: <aquí la información extra, excepto de cupones, si la hay, si no, vacío>
_coupon: <aquí el código del cupón, si lo tiene, si no, vacío>
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        text = response.choices[0].message.content
        print(f"generated text={response.choices[0].message.content}")

        lines = text.strip().splitlines()

        field_map = {
            "_title:": "title",
            "_description:": "description",
            "_price:": "price",
            "_old_price:": "old_price",
            "_more_info:": "more_info",
            "_coupon:": "coupon"
        }

        data = {
            "title": "",
            "description": "",
            "price": "",
            "old_price": "",
            "more_info": "",
            "coupon": ""
        }

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            for key, field in field_map.items():
                if line.startswith(key):
                    value = line[len(key):].strip()
                    # Evitar que se tome otra cabecera como valor accidental
                    if not value and (i + 1) < len(lines):
                        next_line = lines[i + 1].strip()
                        if not any(next_line.startswith(k) for k in field_map):
                            value = next_line
                            i += 1
                    data[field] = value
                    break
            i += 1

        return {
            "title": data["title"],
            "description": data["description"],
            "price": safe_parse_float(data["price"]),
            "old_price": safe_parse_float(data["old_price"]),
            "more_info": data["more_info"] or None,
            "coupon": data["coupon"] or None
        }
    except Exception as e:
        print(f"❌ Error generating text with OpenAI: {e}")
        return None
    

def test_generate(content: str) -> dict:
    # Get original message and publish like this...
    # Just for testing

    extracted = extract_description_and_prices(content)

    #print(f"TEXT GENERATION TEST={content}")
    #print(f"TEXT GENERATION TEST EXTRACTED={extracted}")

    return {
        "title": "Artículo en Venta. OFERTÓN!!!",
        "description": extracted['description'],
        "price": safe_parse_float(extracted['current_price']),
        "old_price": safe_parse_float(extracted['previous_price']),
        "more_info": "Unisex, talla XL",
        "coupon": "X123ABC"
    }

# This method should go in every parser, just to fit the message structure
def extract_description_and_prices(text: str) -> dict:
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]

    # Encuentra primera línea que parezca descripción
    description = next((line for line in lines if not line.startswith("#") and not line.lower().startswith(("talla", "hombre", "mujer", "https://", "🧿", "✅", "❌"))), "")

    price_now = None
    # más tolerancia para precios con o sin decimales
    match_now = re.search(r"(?i)(pvp\s*)?ahora[^\d]*(\d+[.,]?\d{0,2})", text)
    if match_now:
        try:
            price_now = float(match_now.group(2).replace(",", "."))
        except ValueError:
            price_now = None

    price_before = None
    match_before = re.search(r"(?i)(antes|previo)[^\d]*(\d+[.,]?\d{0,2})", text)
    if match_before:
        try:
            price_before = float(match_before.group(2).replace(",", "."))
        except ValueError:
            price_before = None

    return {
        "description": description,
        "current_price": 25.99 if price_now is None else price_now,
        "previous_price": 99.95 if price_before is None else price_before
    }

def safe_parse_float(value: str | float | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, float):
        return value
    try:
        # Elimina símbolos de moneda y cambia la coma por punto decimal
        cleaned = value.replace("€", "").replace(",", ".").strip()
        return float(cleaned)
    except (ValueError, TypeError, AttributeError):
        return None