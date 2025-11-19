#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - AUTOMATIC BACKUP SYSTEM
Automatische Sicherung aller Mining-Session-Daten
"""
import os
import json
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
import threading
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AutoBackupSystem:
    """Automatisches Backup-System für Mining-Daten"""

    def __init__(self):
        self.backup_dir = "backups"
        self.session_file = "mining_session_1_export.json"
        self.backup_interval = 3600  # 1 Stunde
        self.max_backups = 50  # Maximale Anzahl Backups behalten
        self.is_running = False
        self.backup_thread = None

        # Backup-Verzeichnis erstellen
        os.makedirs(self.backup_dir, exist_ok=True)

        print("🔄 AUTO BACKUP SYSTEM INITIALIZED")
        print(f"📁 Backup-Verzeichnis: {self.backup_dir}")
        print(f"⏰ Backup-Intervall: {self.backup_interval} Sekunden")

    def start_auto_backup(self):
        """Startet automatisches Backup-System"""
        if self.is_running:
            print("Auto-Backup läuft bereits")
            return

        self.is_running = True
        self.backup_thread = threading.Thread(target=self._backup_loop, daemon=True)
        self.backup_thread.start()

        print("✅ AUTO BACKUP SYSTEM GESTARTET")

        # Sofortiges erstes Backup
        self.create_backup()

    def stop_auto_backup(self):
        """Stoppt automatisches Backup-System"""
        if not self.is_running:
            return

        self.is_running = False
        if self.backup_thread:
            self.backup_thread.join(timeout=5)

        print("⏹️ AUTO BACKUP SYSTEM GESTOPPT")

    def create_backup(self, custom_name: str = None) -> str:
        """Erstellt manuelles Backup"""
        if not os.path.exists(self.session_file):
            print(f"⚠️ Session-Datei nicht gefunden: {self.session_file}")
            return None

        # Backup-Name generieren
        if custom_name:
            backup_name = f"{custom_name}.json"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"mining_session_backup_{timestamp}.json"

        backup_path = os.path.join(self.backup_dir, backup_name)

        try:
            # Session-Daten kopieren
            shutil.copy2(self.session_file, backup_path)

            # Backup-Info hinzufügen
            backup_info = {
                'backup_created': datetime.now().isoformat(),
                'original_file': self.session_file,
                'backup_type': 'manual' if custom_name else 'automatic'
            }

            # Backup-Info in separater Datei speichern
            info_file = backup_path.replace('.json', '_info.json')
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2)

            print(f"💾 BACKUP ERSTELLT: {backup_name}")
            self._cleanup_old_backups()

            return backup_path

        except Exception as e:
            print(f"❌ Backup-Fehler: {e}")
            return None

    def list_backups(self) -> list:
        """Listet alle verfügbaren Backups auf"""
        if not os.path.exists(self.backup_dir):
            return []

        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.json') and 'backup' in file:
                file_path = os.path.join(self.backup_dir, file)
                file_size = os.path.getsize(file_path)
                modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                backups.append({
                    'filename': file,
                    'path': file_path,
                    'size': file_size,
                    'modified': modified_time,
                    'size_mb': file_size / (1024 * 1024)
                })

        # Nach Änderungsdatum sortieren (neueste zuerst)
        backups.sort(key=lambda x: x['modified'], reverse=True)
        return backups

    def restore_backup(self, backup_filename: str) -> bool:
        """Stellt Backup wieder her"""
        backup_path = os.path.join(self.backup_dir, backup_filename)

        if not os.path.exists(backup_path):
            print(f"❌ Backup nicht gefunden: {backup_filename}")
            return False

        try:
            # Backup in Session-Datei kopieren
            shutil.copy2(backup_path, self.session_file)
            print(f"🔄 BACKUP WIEDERHERGESTELLT: {backup_filename}")
            return True

        except Exception as e:
            print(f"❌ Wiederherstellungs-Fehler: {e}")
            return False

    def get_backup_stats(self) -> dict:
        """Gibt Backup-Statistiken zurück"""
        backups = self.list_backups()

        if not backups:
            return {'total_backups': 0, 'total_size_mb': 0, 'oldest_backup': None, 'newest_backup': None}

        total_size = sum(b['size'] for b in backups)

        return {
            'total_backups': len(backups),
            'total_size_mb': total_size / (1024 * 1024),
            'oldest_backup': backups[-1]['modified'],
            'newest_backup': backups[0]['modified'],
            'average_size_mb': total_size / len(backups) / (1024 * 1024)
        }

    def _backup_loop(self):
        """Hauptschleife für automatisches Backup"""
        while self.is_running:
            try:
                time.sleep(self.backup_interval)
                if self.is_running:  # Nochmal prüfen falls gestoppt wurde
                    self.create_backup()
            except Exception as e:
                print(f"Backup-Loop Fehler: {e}")
                time.sleep(60)  # Bei Fehler 1 Minute warten

    def _cleanup_old_backups(self):
        """Räumt alte Backups auf"""
        backups = self.list_backups()

        if len(backups) > self.max_backups:
            # Älteste Backups löschen
            to_delete = backups[self.max_backups:]

            for backup in to_delete:
                try:
                    os.remove(backup['path'])
                    # Info-Datei auch löschen
                    info_file = backup['path'].replace('.json', '_info.json')
                    if os.path.exists(info_file):
                        os.remove(info_file)

                    print(f"🗑️ ALTES BACKUP GELÖSCHT: {backup['filename']}")
                except Exception as e:
                    print(f"❌ Cleanup-Fehler für {backup['filename']}: {e}")

# Globale Instanz
auto_backup_system = AutoBackupSystem()

# Standalone-Funktionen
def start_auto_backup():
    """Startet automatisches Backup"""
    auto_backup_system.start_auto_backup()

def stop_auto_backup():
    """Stoppt automatisches Backup"""
    auto_backup_system.stop_auto_backup()

def create_manual_backup(name: str = None):
    """Erstellt manuelles Backup"""
    return auto_backup_system.create_backup(name)

def list_available_backups():
    """Listet verfügbare Backups"""
    return auto_backup_system.list_backups()

def restore_from_backup(filename: str):
    """Stellt Backup wieder her"""
    return auto_backup_system.restore_backup(filename)

def get_backup_statistics():
    """Gibt Backup-Statistiken"""
    return auto_backup_system.get_backup_stats()

if __name__ == "__main__":
    print("CASH MONEY COLORS ORIGINAL (R) - AUTO BACKUP SYSTEM")
    print("=" * 60)

    # Test des Backup-Systems
    print("🧪 Teste Backup-System...")

    # Statistiken anzeigen
    stats = get_backup_statistics()
    print(f"📊 Backup-Statistiken:")
    print(f"   Total Backups: {stats['total_backups']}")
    print(f"   Total Size: {stats['total_size_mb']:.2f} MB")

    # Verfügbare Backups auflisten
    backups = list_available_backups()
    if backups:
        print(f"📁 Verfügbare Backups ({len(backups)}):")
        for i, backup in enumerate(backups[:5]):  # Erste 5 anzeigen
            print(f"   {i+1}. {backup['filename']} ({backup['size_mb']:.2f} MB) - {backup['modified']}")
    else:
        print("📁 Keine Backups verfügbar")

    # Manuelles Backup erstellen
    print("\n💾 Erstelle manuelles Backup...")
    backup_path = create_manual_backup("test_backup")
    if backup_path:
        print(f"✅ Backup erstellt: {backup_path}")

    print("\n✅ AUTO BACKUP SYSTEM BEREIT!")
    print("Verwende start_auto_backup() für kontinuierliche Sicherung")
