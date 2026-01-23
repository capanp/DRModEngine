# Dungeon Rampage Mod Engine
<p align="center">
  <img width="150" height="150" alt="DRModEngine-icon" src="https://github.com/user-attachments/assets/9cff6b1d-2c49-4401-87fe-4b16eee8f70c" />
</p>
<h3>An automated, portable mod loader for Dungeon Rampage.</h3>

This tool allows users to inject ActionScript (.as) code and assets into the game dynamically. It utilizes DLL Hijacking for seamless integration with Steam and JPEXS (FFDec) for realtime SWF modification.

### 🌟 Key Features
* Zero-Config Installation: Just drag and drop into the game folder.
* Auto-Update Support: Automatically detects game updates (via MD5 hash), creates a new clean backup, and re-applies mods. No manual work required.
* Smart Caching: If no mods are changed, the engine skips injection for instant game startup.
* Embedded Runtime: Comes with a stripped-down Java JRE and FFDec. Users do not need to install Python or Java.
* Conflict Handling: Uses a "Last-Loaded-Wins" strategy for conflicting scripts.

### 📂 Installation
Download the latest release.
1. Open your game directory (e.g., Steam\steamapps\common\DungeonRampage).
2. Copy the contents of the archive (version.dll, mods/, and DRModEngine/) into the game folder.
3. Launch the game via Steam as usual.

Directory Structure:
```
Dungeon Rampage/
├── DungeonBustersProject.swf   (Original Game File)
├── version.dll                 (Loader Proxy)
├── mods/                       <-- PUT YOUR .AS FILES HERE
└── DRModEngine/                (Core Engine Files)
    └── inject/                 (Default Api Files)
    └── Launcher.exe
```

