import os
from pathlib import Path

# Installed CLI keeps models and generated files in the chosen workspace,
# never inside site-packages. Override when launching from another folder.
ROOT=Path(os.environ.get('KAOMOJI_REPLY_HOME',str(Path.cwd()))).resolve()
