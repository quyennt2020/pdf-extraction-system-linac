@echo off
echo ========================================
echo Medical Device PDF Processing System
echo ========================================
echo.

echo Step 1: Installing dependencies...
pip install python-dotenv
pip install -r requirements.txt
echo.

echo Step 2: Running setup test...
python test_setup.py
echo.

echo Step 3: Checking for PDF files...
dir "data\input_pdfs\*.pdf" /b 2>nul
if errorlevel 1 (
    echo No PDF files found in data\input_pdfs\
    echo Please place your PDF file there and run again.
    pause
    exit /b 1
)

echo.
echo Found PDF files:
for %%f in ("data\input_pdfs\*.pdf") do echo   - %%~nxf

echo.
echo Step 4: Ready to process PDF!
echo.
echo Choose an option:
echo 1. Process first PDF with 5 pages (quick test)
echo 2. Process first PDF with dashboard
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto quick_test
if "%choice%"=="2" goto dashboard_test
if "%choice%"=="3" goto end

:quick_test
for %%f in ("data\input_pdfs\*.pdf") do (
    echo Processing %%~nxf with 5 pages...
    python run_with_real_pdf.py "%%f" --max-pages 5
    goto end
)

:dashboard_test
for %%f in ("data\input_pdfs\*.pdf") do (
    echo Processing %%~nxf with dashboard...
    python run_with_real_pdf.py "%%f" --max-pages 10 --start-dashboard
    goto end
)

:end
echo.
echo Done! Check the results in data\real_pdf_results\
pause