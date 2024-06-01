import io

from flask import Flask
from flask import send_file

import generate.generator

app = Flask(__name__)
app.debug = True

@app.route("/")
async def hello_world():
    image_binary = io.BytesIO()
    panel_img = await generate.generate.generate_panel(template=2)
    panel_img.save(image_binary, 'PNG')
    image_binary.seek(0)
    return send_file(image_binary, mimetype='image/png')

