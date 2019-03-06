pyinstaller --onefile treadmill.spec
echo y | move dist\Treadmill.exe .\
echo y | rmdir dist /s
echo y | rmdir build /s
pause