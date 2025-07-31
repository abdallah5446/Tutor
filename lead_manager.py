import json
import os
from datetime import datetime
from typing import List, Dict, Any

class LeadManager:
    def __init__(self, data_file='data/leads.json'):
        self.data_file = data_file
        self.leads = self._load_leads()
    
    def _load_leads(self) -> List[Dict[str, Any]]:
        """Load leads from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_leads(self):
        """Save leads to JSON file"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.leads, f, indent=2, ensure_ascii=False)
    
    def add_leads(self, new_leads: List[Dict[str, Any]], source: str):
        """Add new leads from a specific source"""
        for lead in new_leads:
            lead['source'] = source
            lead['scraped_at'] = datetime.now().isoformat()
            
            # Check for duplicates based on title and URL
            if not self._is_duplicate(lead):
                self.leads.append(lead)
        
        self._save_leads()
    
    def _is_duplicate(self, new_lead: Dict[str, Any]) -> bool:
        """Check if a lead is duplicate based on title and URL"""
        for existing_lead in self.leads:
            if (existing_lead.get('title', '').lower() == new_lead.get('title', '').lower() and
                existing_lead.get('url', '') == new_lead.get('url', '')):
                return True
        return False
    
    def get_leads(self, source: str = '', keyword: str = '') -> List[Dict[str, Any]]:
        """Get leads with optional filtering"""
        filtered_leads = self.leads
        
        if source:
            filtered_leads = [lead for lead in filtered_leads if lead.get('source', '').lower() == source.lower()]
        
        if keyword:
            keyword_lower = keyword.lower()
            filtered_leads = [
                lead for lead in filtered_leads 
                if (keyword_lower in lead.get('title', '').lower() or 
                    keyword_lower in lead.get('description', '').lower())
            ]
        
        # Sort by scraped_at date (newest first)
        filtered_leads.sort(key=lambda x: x.get('scraped_at', ''), reverse=True)
        return filtered_leads
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the leads"""
        total_leads = len(self.leads)
        
        source_counts = {}
        for lead in self.leads:
            source = lead.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        # Get recent leads (last 24 hours)
        recent_leads = 0
        now = datetime.now()
        for lead in self.leads:
            try:
                scraped_time = datetime.fromisoformat(lead.get('scraped_at', ''))
                if (now - scraped_time).days < 1:
                    recent_leads += 1
            except:
                pass
        
        return {
            'total_leads': total_leads,
            'source_breakdown': source_counts,
            'recent_leads': recent_leads,
            'last_updated': self.get_last_updated()
        }
    
    def get_last_updated(self) -> str:
        """Get the timestamp of the most recent lead"""
        if not self.leads:
            return "Never"
        
        latest_time = max(lead.get('scraped_at', '') for lead in self.leads)
        try:
            dt = datetime.fromisoformat(latest_time)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "Unknown"
    
    def clear_old_leads(self, days: int = 7):
        """Remove leads older than specified days"""
        now = datetime.now()
        original_count = len(self.leads)
        
        self.leads = [
            lead for lead in self.leads
            if (now - datetime.fromisoformat(lead.get('scraped_at', ''))).days <= days
        ]
        
        removed_count = original_count - len(self.leads)
        if removed_count > 0:
            self._save_leads()
        
        return removed_count