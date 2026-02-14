Set WshShell = CreateObject("WScript.Shell")

' 1. Tell the script WHERE your folder is
WshShell.CurrentDirectory = "C:\Users\Your_Path\remote"

' 2. Run it silently using pythonw
' If this fails, try changing "pythonw" to "python" just to see the error
WshShell.Run "pythonw app.py", 0

Set WshShell = Nothing