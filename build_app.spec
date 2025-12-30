# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/gui_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/remind-465308-775406c8a2f1.json', '.'),
        ('app/desktop_automation.py', '.'),
        ('app/desktop_automation_with_image.py', '.'),
    ],
    hiddenimports=[
        'gspread',
        'oauth2client',
        'selenium',
        'tkinter',
        'queue',
        'threading',
        'desktop_automation',
        'desktop_automation_with_image',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GoogleMessages_리마인드발송기',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 앱이므로 콘솔 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 아이콘 파일이 있으면 여기에 경로 추가
)
