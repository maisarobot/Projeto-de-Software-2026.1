import os
import sys
from dotenv import load_dotenv

# Troque SEU_USUARIO pelo seu usuário do PythonAnywhere
project_home = "/home/SEU_USUARIO/Projeto-de-Software-2026.1"

if project_home not in sys.path:
    sys.path.insert(0, project_home)

load_dotenv(os.path.join(project_home, ".env"))

from main import app as application
