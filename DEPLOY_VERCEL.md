Deploying this Django project to Vercel

1. Ensure `requirements.txt` contains all dependencies (Django, gunicorn, Pillow, python-decouple).

2. Exclude local environment and database (we added `.vercelignore` to skip `.venv`, `db.sqlite3`, and `media/`).

3. `vercel.json` is configured to use `myproject/wsgi.py` as the WSGI app.

4. Recommended environment variables to set in Vercel dashboard:
   - `DJANGO_SETTINGS_MODULE` = `myproject.settings` (optional since wsgi sets it)
   - `SECRET_KEY` = (set a production secret)
   - `DEBUG` = `False`
   - Configure any DB or storage credentials as appropriate.

5. Static/media files: Vercel is serverless — serve static files with an external provider (S3, Cloudflare R2) or use WhiteNoise and ensure `collectstatic` writes to a folder that is served. For quick testing, DEBUG can be True and media stored in repo (not recommended).

6. Deploy steps:
   - Install Vercel CLI and login: `npm i -g vercel` then `vercel login`
   - From the repo root run: `vercel` and follow prompts. Use existing project or create new.

7. Troubleshooting:
   - If build fails with "No module named 'django'", ensure `requirements.txt` is committed and not ignored. Vercel installs packages during build.
   - Check Build Logs in Vercel dashboard for pip install output.

