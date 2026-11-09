"""Run Chrome checks against a temporary DB copy and stop the QA server afterwards."""
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

with tempfile.TemporaryDirectory(prefix="myportofolio-qa-") as folder:
    database = Path(folder) / "db.sqlite3"
    if (ROOT / "db.sqlite3").exists():
        shutil.copy2(ROOT / "db.sqlite3", database)
    os.environ["DJANGO_SETTINGS_MODULE"] = "scripts.qa_settings"
    os.environ["PORTFOLIO_QA_DATABASE"] = str(database)
    import django
    django.setup()
    from django.core.management import call_command
    from django.contrib.auth.models import Group, User
    from main.models import Experience, Project
    call_command("migrate", verbosity=0, interactive=False)
    for username, owner in [("qa-owner", True), ("qa-visitor", False), ("qa-editor", False)]:
        user, _ = User.objects.get_or_create(username=username)
        user.set_password("temporary-browser-qa")
        user.is_superuser = user.is_staff = owner
        user.save()
        user.groups.clear()
        if username == "qa-editor":
            user.groups.add(Group.objects.get_or_create(name="Editor")[0])
    if not Project.objects.exists():
        Project.objects.create(title="QA Seed", category="design", image_url="/static/img/monte.png",
            short_description="QA seed project", full_description="QA project detail", tags="Django")
    if not Experience.objects.exists():
        Experience.objects.create(title="QA Designer", location="UI", category="part-time",
            description="QA seed experience", started_at="2026-01-01")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    with open(Path(folder) / "server.log", "w") as log:
        server = subprocess.Popen([sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}", "--noreload", "--insecure"], stdout=log, stderr=log)
        try:
            for _ in range(100):
                try:
                    if urlopen(base + "/project/", timeout=1).status == 200:
                        break
                except OSError:
                    time.sleep(.1)
            else:
                raise RuntimeError("QA server did not start")
            env = {**os.environ, "QA_URL": base, "QA_PASSWORD": "temporary-browser-qa"}
            browser_scripts = ["scripts/qa_browser.cjs"]
            if "--assignment-6" in sys.argv:
                browser_scripts.append("scripts/qa_ia6_browser.cjs")
            for script in browser_scripts:
                subprocess.run([os.environ.get("NODE_BINARY", "node"), script], env=env, check=True)
        finally:
            server.terminate()
            server.wait(timeout=10)
