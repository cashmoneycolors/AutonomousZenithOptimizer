#!/usr/bin/env python3
"""
VOLSTÄNDIGE SYSTEM-INTEGRATION - Alle 50 Module einbinden
"""
import os
import sys
import importlib.util
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

class ModuleIntegrator:
    """Integriert alle verfügbaren Module"""

    def __init__(self):
        self.modules = {}
        self.loaded_count = 0
        self.failed_count = 0

    def find_all_modules(self):
        """Findet alle .py Module"""
        modules_dir = Path('python_modules')
        found_modules = []

        if modules_dir.exists():
            for file_path in modules_dir.glob('*.py'):
                if not file_path.name.startswith('__'):
                    found_modules.append(file_path)

        return found_modules

    def load_module_safe(self, module_path):
        """Lädt ein Modul sicher"""
        try:
            module_name = module_path.stem
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.modules[module_name] = module
                self.loaded_count += 1
                logger.info(f"✅ Geladen: {module_name}")
                return True
        except Exception as e:
            self.failed_count += 1
            logger.warning(f"❌ Fehler bei {module_path.name}: {e}")

        return False

    def integration_full_system(self):
        """Vollständige Systemintegration"""
        logger.info("🚀 STARTE VOLSTÄNDIGE SYSTEM-INTEGRATION")
        logger.info("="*50)

        # Alle Module finden
        module_files = self.find_all_modules()
        logger.info(f"📊 {len(module_files)} Python-Module gefunden")

        # Jedes Modul laden
        for module_file in module_files:
            logger.info(f"🔄 Lade {module_file.name}...")
            self.load_module_safe(module_file)

        logger.info("="*50)
        logger.info(f"📊 INTEGRATION ABGESCHLOSSEN:")
        logger.info(f"✅ Erfolgreich: {self.loaded_count}")
        logger.info(f"❌ Fehlgeschlagen: {self.failed_count}")
        logger.info(f"📈 Gesamt: {len(self.modules)}")
        logger.info("="*50)

        return self.modules

def main():
    integrator = ModuleIntegrator()
    loaded_modules = integrator.integration_full_system()

    print(f"\n🌟 AUTONOMOUS ZENITH OPTIMIZER - MODUL-INTEGRATION FERTIG!")
    print(f"📊 {len(loaded_modules)} von 50 verfügbaren Modulen erfolgreich integriert")
    print(f"💡 System bereit für maximale Profit-Optimierung!")

    return loaded_modules

if __name__ == "__main__":
    main()
