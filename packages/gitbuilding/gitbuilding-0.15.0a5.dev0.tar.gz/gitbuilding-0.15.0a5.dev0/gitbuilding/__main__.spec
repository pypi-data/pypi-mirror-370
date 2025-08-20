# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
import os

a = Analysis(['__main__.py'],
             pathex=[os.getcwd()],
             binaries=[],
             datas=[('static','gitbuilding\\static'),
                    ('licenses','gitbuilding\\licenses'),
                    ('templates','gitbuilding\\templates')],
             hiddenimports=['encodings'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='gitbuilding',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          icon=os.path.abspath('static\\Logo\\favicon.ico'),
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='gitbuilding')
