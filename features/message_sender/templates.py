from typing import Dict, Any
import disnake

def validate_template(data: Dict[str, Any]) -> bool:
	"""Проверяет валидность JSON шаблона"""
	if not isinstance(data, dict):
		return False
	
	if "embeds" in data:
		if not isinstance(data["embeds"], list):
			return False
		
		for embed in data["embeds"]:
			try:
				disnake.Embed.from_dict(embed)
			except:
				return False
	
	return True