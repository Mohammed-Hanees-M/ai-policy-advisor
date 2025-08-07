from typing import Dict, List, Optional
from datetime import datetime
import json
import os

class ChatMemory:
    def __init__(self, storage_path: str = "./.chat_memory"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
    def save_chat(
        self,
        chat_id: str,
        messages: List[Dict],
        metadata: Optional[Dict] = None
    ) -> None:
        """Saves chat to persistent storage"""
        filepath = os.path.join(self.storage_path, f"{chat_id}.json")
        data = {
            "meta": metadata or {},
            "messages": messages,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_chat(self, chat_id: str) -> Optional[Dict]:
        """Loads chat from storage"""
        filepath = os.path.join(self.storage_path, f"{chat_id}.json")
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def delete_chat(self, chat_id: str) -> bool:
        """Deletes a chat session"""
        filepath = os.path.join(self.storage_path, f"{chat_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    
    def list_chats(self) -> List[Dict]:
        """Lists all available chats"""
        chats = []
        for fname in os.listdir(self.storage_path):
            if fname.endswith('.json'):
                chat_id = fname[:-5]
                meta = self.load_chat(chat_id).get("meta", {})
                chats.append({
                    "id": chat_id,
                    "title": meta.get("title", chat_id),
                    "last_updated": meta.get("last_updated")
                })
        return sorted(chats, key=lambda x: x["last_updated"], reverse=True)

class KnowledgeGraph:
    """Advanced feature for connecting related concepts"""
    def __init__(self):
        self.graph = {}  # {concept: {related: [], sources: []}}
    
    def add_relationship(self, concept1: str, concept2: str, source: str) -> None:
        """Records relationships between concepts"""
        for concept in [concept1, concept2]:
            if concept not in self.graph:
                self.graph[concept] = {"related": [], "sources": []}
        
        if concept2 not in self.graph[concept1]["related"]:
            self.graph[concept1]["related"].append(concept2)
            self.graph[concept1]["sources"].append(source)