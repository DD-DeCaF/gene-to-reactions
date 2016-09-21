#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask_script import Manager, Server
from flask_cors import CORS
from genotype_to_model.app import create_app

SETTINGS_OBJECT = os.environ.get('SETTINGS_OBJECT', 'genotype_to_model.settings.Production')
app = create_app(SETTINGS_OBJECT)

cors = CORS(resources={
    r"/*": {
        "origins": "*",
        "expose_headers": ('X-Total-Count',)
    }
})
cors.init_app(app)


if __name__ == "__main__":
    manager = Manager(app)
    manager.add_command("runserver", Server(host="0.0.0.0", port=8000, use_debugger=True, use_reloader=True))
    manager.run()
