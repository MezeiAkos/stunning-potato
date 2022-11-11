import requests
import json
import tinify
import ocrspace
import os
# TODO only use the wrapper


def get_text_from_images(url):
    tinify.key = "7GxQtrdRGLj9fMQ2H5cW7q4y9DpCkcLK"

    key = "K82057996588957"
    result = requests.get(f"https://api.ocr.space/parse/imageurl?apikey={key}&url={url}")
    result = result.content.decode()
    result = json.loads(result)
    if result["IsErroredOnProcessing"] is not True:
        parsed_results = result.get("ParsedResults")[0]
        text_detected = parsed_results.get("ParsedText")
        return text_detected
    else:
        print(f"{result['ErrorMessage']}, compressing")
        source = tinify.from_url(url)
        source.to_file("optimized.png")

        api = ocrspace.API(api_key=key)
        result = api.ocr_file("optimized.png")
        os.remove("optimized.png")
        return result
# from: https://www.kaggle.com/code/naim99/ocr-text-recognition-ocr-space-api-tesseract, https://github.com/ErikBoesen/ocrspace
