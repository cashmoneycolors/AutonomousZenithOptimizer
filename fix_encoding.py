#!/usr/bin/env python3
"""
AZO ENCODING FIX - Windows Compatibility Script
Repariert Unicode-Encoding-Probleme für Windows-Kompatibilität
"""

import os
import sys
import codecs

def fix_unicode_issues():
    """Behebt alle Unicode-Encoding-Probleme in Python-Modulen"""

    # Setze stdout encoding auf UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    modules_to_fix = [
        'python_modules/config_manager.py',
        'python_modules/market_integration.py',
        'python_modules/risk_manager.py',
        'python_modules/algorithm_switcher.py',
        'python_modules/temperature_optimizer.py',
        'python_modules/predictive_maintenance.py'
    ]

    emoji_replacements = {
        '🔑': '[KEY]',
        '✅': '[OK]',
        '⚙️': '[CFG]',
        '📁': '[DIR]',
        '🔧': '[TOOL]',
        '🪙': '[COIN]',
        '📊': '[STATS]',
        '💰': '[MONEY]',
        '⚠️': '[WARN]',
        '❌': '[ERROR]',
        '🚨': '[ALERT]',
        '🔄': '[CYCLE]',
        '🛡️': '[SHIELD]',
        '📝': '[LOG]',
        '🌡️': '[TEMP]',
        '🧠': '[AI]',
        '⛏️': '[MINING]',
        '🔬': '[LAB]',
        '⬛': '[STOP]',
        '🚀': '[LAUNCH]',
        '❄️': '[COLD]',
        '⚡': '[POWER]',
        '🔥': '[HOT]',
        '📱': '[MOBILE]',
        '🖥️': '[DESKTOP]',
        '🦾': '[ROBOT]',
        '💎': '[DIAMOND]',
        '🎉': '[CELEBRATE]',
        '🧪': '[TEST]',
        '📦': '[PACKAGE]',
        '🔍': '[SEARCH]',
        '🗂️': '[FOLDER]',
        '🔔': '[BELL]',
        '📈': '[CHART]',
        '📋': '[CLIPBOARD]',
        '🗜️': '[ARCHIVE]',
        '🔒': '[LOCK]',
        '🔓': '[UNLOCK]',
        '📡': '[NETWORK]',
        '💾': '[SAVE]',
        '🚪': '[EXIT]',
        '⚠️': '[WARNING]',
        '🔥': '[CRITICAL]'
    }

    print("🔧 Fixing Unicode encoding issues...")

    for module_file in modules_to_fix:
        if not os.path.exists(module_file):
            print(f"File not found: {module_file}")
            continue

        print(f"Fixing: {module_file}")

        try:
            with open(module_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Ersetze Emojis mit ASCII-Alternativen
            for emoji, replacement in emoji_replacements.items():
                content = content.replace(emoji, replacement)

            # Speichere die korrigierte Version
            with open(module_file, 'w', encoding='utf-8') as f:
                f.write(content)

