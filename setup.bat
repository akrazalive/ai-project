@echo off
echo === Setting up Job Search App ===

echo.
echo [1/4] Installing Python dependencies...
cd backend
pip install -r requirements.txt

echo.
echo [2/4] Running database migrations...
python manage.py migrate

echo.
echo [3/4] Creating admin user...
python manage.py shell -c "from django.contrib.auth import get_user_model; U=get_user_model(); U.objects.filter(username='admin').exists() or U.objects.create_superuser('admin','admin@example.com','admin123')"

echo.
echo [4/4] Installing frontend dependencies...
cd ..\frontend
npm install

echo.
echo === Setup complete! ===
echo Run 'run.bat' to start the app.
echo Admin login: username=admin  password=admin123
cd ..
