import json
from pathlib import Path
from typing import Dict


DEFAULT_SKILL_NAMES: Dict[str, str] = {
    "13,255,0": "惩击",
    "0,255,64": "治疗之触",
    "0,255,140": "清晰术",
    "0,255,217": "护星术",
    "0,255,255": "野性成长",
    "13,255,255": "滋养",
    "64,255,0": "愈合",
    "140,255,0": "回春术",
    "217,255,0": "生命绽放",
    "255,255,0": "驱散",
    "255,217,0": "联结治疗",
    "255,140,0": "野性印记",
    "255,64,0": "星火术",
    "255,0,0": "愤怒",
    "255,0,64": "月火术",
    "255,0,140": "精灵火",
    "255,0,217": "台风",
    "217,0,255": "纠缠根须",
    "140,0,255": "自然之力",
    "89,255,0": "自然防御",
}


class SkillNameManager:
    """技能名称管理器"""

    def __init__(self, config_path: str = "skill_names.json"):
        self.config_path = Path(config_path)
        self.skills: Dict[str, dict] = {}
        self._load_config()

    def _load_config(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.skills = data.get("skills", {})
            except (json.JSONDecodeError, IOError):
                self.skills = self._default_config()
        else:
            self.skills = self._default_config()

    def _default_config(self) -> Dict[str, dict]:
        return {
            color_key: {"name": name, "enabled": True}
            for color_key, name in DEFAULT_SKILL_NAMES.items()
        }

    def get_name(self, color_key: str) -> str:
        return self.skills.get(color_key, {}).get("name", "未知")

    def set_name(self, color_key: str, name: str):
        if color_key in self.skills:
            self.skills[color_key]["name"] = name
            self._save_config()

    def get_all_skills(self) -> Dict[str, dict]:
        return self.skills.copy()

    def reset_all(self):
        self.skills = self._default_config()
        self._save_config()

    def _save_config(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(
                    {"version": 1, "skills": self.skills},
                    f,
                    ensure_ascii=False,
                    indent=2
                )
        except IOError as e:
            print(f"保存技能名称配置失败: {e}")