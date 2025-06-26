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
Luego, redacta una descripción más larga (máximo 20 palabras) que explique lo que es, qué puntos de dolor resuelve y por qué lo necesitaría.
Tanto el título como la descripción que sean atractivos para hacer ver a la persona que lo lee que es una gran oferta. 
Si el producto tiene tallas, o es una talla concreta, indícalo en la descripción.
Utiliza sesgos psicológicos de ventas y técnicas de neuromarketing.
No repitas el mismo texto en ambos campos. Si no tienes claro el tipo de artículo o producto que es, no inventes, que el título y la descripción entonces 
sean genéricos, que no de pie a confusión, simplemente puedes decir que es una gran oferta, limitada y da sensación de urgencia.
Puedes usar emojis si crees realmente que pueden mejorar la presentación y dar claridad a la oferta.

Devuelve también el precio que se encuentra en el mensaje.
Devuelve también el precio original en caso de que se encuentre en el mensaje. Si no, o tienes dudas, déjalo vacío.

Si existe alguna información extra como la talla, el género o alguna información complementaria que puede ser importante conocer, puedes devolverlo también.

Formato:
_title: <aquí el título>
_description: <aquí la descripción>
_price: <aquí el precio>
_old_price: <aquí el precio original>
_more_info: <aquí la información extra, si la hay, si no, vacío>
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        text = response.choices[0].message.content
        print(f"generated text={response.choices[0].message.content}")

        # lines = text.strip().split("\n")
        # title = next((line.replace("_title:", "").strip() for line in lines if line.startswith("_title:")), "")
        # description = next((line.replace("_description:", "").strip() for line in lines if line.startswith("_description:")), "")
        # price = next((line.replace("_price:", "").strip() for line in lines if line.startswith("_price:")), "")

        lines = text.strip().splitlines()
        title = ""
        description = ""
        price = ""
        old_price = None
        more_info = None

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("_title:"):
                title = line.replace("_title:", "").strip()
                if not title and i + 1 < len(lines):
                    title = lines[i + 1].strip()
                    i += 1
            elif line.startswith("_description:"):
                description = line.replace("_description:", "").strip()
                if not description and i + 1 < len(lines):
                    description = lines[i + 1].strip()
                    i += 1
            elif line.startswith("_price:"):
                price = line.replace("_price:", "").strip()
                if not price and i + 1 < len(lines):
                    price = lines[i + 1].strip()
                    i += 1
            elif line.startswith("_old_price:"):
                old_price = line.replace("_old_price:", "").strip()
                if not old_price and i + 1 < len(lines):
                    old_price = lines[i + 1].strip()
                    i += 1
            elif line.startswith("_more_info:"):
                more_info = line.replace("_more_info:", "").strip()
                if not more_info and i + 1 < len(lines):
                    more_info = lines[i + 1].strip()
                    i += 1
            i += 1

        return {
            "title": title,
            "description": description,
            "price": price,
            "old_price": old_price,
            "more_info": more_info
        }
    except Exception as e:
        print(f"❌ Error generating text with OpenAI: {e}")
        return {"title": "", "description": "", "price": ""}
    

def test_generate(content: str) -> dict:
    # Get original message and publish like this...
    # Just for testing

    extracted = extract_description_and_prices(content)

    #print(f"TEXT GENERATION TEST={content}")
    #print(f"TEXT GENERATION TEST EXTRACTED={extracted}")

    return {
        "title": "Artículo en Venta. OFERTÓN!!!",
        "description": extracted['description'],
        "price": extracted['current_price'],
        "old_price": extracted['previous_price'],
        "more_info": "Unisex, talla XL"
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
        "current_price": price_now,
        "previous_price": 99.95 if price_before is None else price_before
    }