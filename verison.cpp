#include <windows.h>
#include <process.h>

// --- PYTHON LAUNCHER'I ÇALIŞTIRMA FONKSİYONU ---
void RunLauncher() {
    // Burada senin Python'dan çevirdiğin EXE'yi çalıştıracağız.
    // system() komutu konsol açabilir, o yüzden CreateProcess daha temizdir ama
    // şimdilik basit olması için WinExec kullanabiliriz.
    
    // "Launcher.exe" senin Python scriptinin derlenmiş halidir.
    // Oyunun klasöründe olmalı.
    WinExec("DRModEngine\\Launcher.exe", SW_SHOW); 
}

// --- DLL GİRİŞ NOKTASI ---
BOOL APIENTRY DllMain(HMODULE hModule,
                      DWORD  ul_reason_for_call,
                      LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
        // Oyun DLL'i yüklediği AN burası çalışır.
        // Oyunun ana kodları daha başlamadan araya giriyoruz.
        
        // Launcher'ı ayrı bir thread'de başlatıyoruz ki oyunu dondurmasın.
        CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)RunLauncher, NULL, 0, NULL);
        break;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}