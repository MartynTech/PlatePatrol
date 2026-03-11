# Build Notes

## Why the `.exe` is not in the PR
Some git hosting providers reject binary files in pull requests (for example with errors like **"Binary files are not supported"**).
To keep PRs reviewable and compatible, this repo does **not** commit the built executable.

## Build on Windows
Run on a Windows machine in the repository root:

```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name PlatePatrolGUI gui_app.py
```

Your executable will be generated at:

- `dist/PlatePatrolGUI.exe`

## How to share the executable
Use one of these instead of committing the binary into the PR:

1. **GitHub Release asset** (recommended)
   - Create a tag/release and upload `dist/PlatePatrolGUI.exe` as an asset.
2. **CI artifact**
   - Build in CI and upload the `.exe` as a workflow artifact.
3. **External file storage**
   - Share via cloud storage and link it in the PR.
