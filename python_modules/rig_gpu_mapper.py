#!/usr/bin/env python3
"""
CASH MONEY COLORS ORIGINAL (R) - RIG MAPPING CONFIGURATION
Mapping von Rig-IDs zu GPU-Indizes für Hardware-Steuerung
"""
import json
from typing import Dict, Optional
from pathlib import Path

class RigGPUMapper:
    """
    Verwaltet das Mapping zwischen Rig-IDs und GPU-Indizes
    Ermöglicht flexible Zuordnung von logischen Rigs zu physischen GPUs
    """
    
    def __init__(self, config_file: str = "rig_gpu_mapping.json"):
        self.config_file = config_file
        self.mapping: Dict[str, int] = {}
        self.load_mapping()
    
    def load_mapping(self) -> None:
        """Lädt Mapping aus Konfigurationsdatei"""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.mapping = data.get('rig_to_gpu', {})
                print(f"✅ Rig-Mapping geladen: {len(self.mapping)} Einträge")
            else:
                # Erstelle Standard-Mapping
                self.create_default_mapping()
        except Exception as e:
            print(f"⚠️  Fehler beim Laden des Mappings: {e}")
            self.create_default_mapping()
    
    def create_default_mapping(self) -> None:
        """Erstellt Standard-Mapping (Rig-ID → GPU-Index)"""
        self.mapping = {
            'RIG_001': 0,
            'RIG_002': 1,
            'RIG_003': 2,
            'RIG_004': 3,
            'TEST_RIG': 0,
            'DEMO_RIG': 0,
        }
        self.save_mapping()
        print(f"✅ Standard-Mapping erstellt: {len(self.mapping)} Einträge")
    
    def save_mapping(self) -> bool:
        """Speichert Mapping in Konfigurationsdatei"""
        try:
            data = {
                'version': '1.0',
                'description': 'Mapping von Rig-IDs zu GPU-Indizes',
                'rig_to_gpu': self.mapping
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Fehler beim Speichern des Mappings: {e}")
            return False
    
    def get_gpu_index(self, rig_id: str) -> int:
        """
        Gibt GPU-Index für eine Rig-ID zurück
        
        Args:
            rig_id: Rig-Identifikator (z.B. "RIG_001")
            
        Returns:
            GPU-Index (Standard: 0 falls nicht gefunden)
        """
        if rig_id in self.mapping:
            return self.mapping[rig_id]
        
        # Fallback: Versuche numerischen Index aus Rig-ID zu extrahieren
        if '_' in rig_id:
            parts = rig_id.split('_')
            try:
                # Versuche letzte Teil als Nummer zu interpretieren
                index = int(parts[-1])
                if 0 <= index <= 7:  # Maximal 8 GPUs
                    print(f"ℹ️  Auto-Mapping: {rig_id} → GPU {index}")
                    self.add_mapping(rig_id, index)
                    return index
            except ValueError:
                pass
        
        # Standard-Fallback
        print(f"⚠️  Kein Mapping für {rig_id}, verwende GPU 0")
        return 0
    
    def add_mapping(self, rig_id: str, gpu_index: int) -> bool:
        """
        Fügt neues Mapping hinzu
        
        Args:
            rig_id: Rig-Identifikator
            gpu_index: GPU-Index (0-7)
            
        Returns:
            True bei Erfolg
        """
        if not (0 <= gpu_index <= 7):
            print(f"❌ Ungültiger GPU-Index: {gpu_index} (erlaubt: 0-7)")
            return False
        
        self.mapping[rig_id] = gpu_index
        return self.save_mapping()
    
    def remove_mapping(self, rig_id: str) -> bool:
        """Entfernt Mapping für eine Rig-ID"""
        if rig_id in self.mapping:
            del self.mapping[rig_id]
            return self.save_mapping()
        return False
    
    def get_all_mappings(self) -> Dict[str, int]:
        """Gibt alle Mappings zurück"""
        return self.mapping.copy()
    
    def list_mappings(self) -> None:
        """Gibt alle Mappings auf der Konsole aus"""
        print("\n📋 Rig-GPU Mapping:")
        print("-" * 40)
        if not self.mapping:
            print("   (keine Mappings definiert)")
        else:
            for rig_id, gpu_index in sorted(self.mapping.items()):
                print(f"   {rig_id:<15} → GPU {gpu_index}")
        print("-" * 40 + "\n")


# Globale Instanz
_mapper_instance: Optional[RigGPUMapper] = None

def get_rig_mapper() -> RigGPUMapper:
    """Gibt die globale Mapper-Instanz zurück"""
    global _mapper_instance
    if _mapper_instance is None:
        _mapper_instance = RigGPUMapper()
    return _mapper_instance

def get_gpu_index_for_rig(rig_id: str) -> int:
    """Convenience-Funktion: Gibt GPU-Index für Rig-ID zurück"""
    mapper = get_rig_mapper()
    return mapper.get_gpu_index(rig_id)


if __name__ == "__main__":
    print("=" * 60)
    print("RIG-GPU MAPPER TEST")
    print("=" * 60)
    
    # Initialisiere Mapper
    mapper = RigGPUMapper()
    
    # Zeige Mappings
    mapper.list_mappings()
    
    # Test Mapping-Abfragen
    print("🧪 TEST MAPPING-ABFRAGEN:")
    test_rigs = ['RIG_001', 'RIG_002', 'UNKNOWN_RIG', 'TEST_RIG']
    for rig in test_rigs:
        gpu_idx = mapper.get_gpu_index(rig)
        print(f"   {rig} → GPU {gpu_idx}")
    
    # Test neues Mapping hinzufügen
    print("\n➕ TEST NEUES MAPPING:")
    mapper.add_mapping('NEW_RIG_001', 2)
    mapper.list_mappings()
    
    print("=" * 60)
    print("TEST ABGESCHLOSSEN")
    print("=" * 60)
