import markdown
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    # return 'Hello, World :) !'

    with open(os.path.dirname(app.root_path) + '/README.md','r') as md_file:
        content = md_file.read()
        return markdown.markdown(content)

print ('__init__ ran.')