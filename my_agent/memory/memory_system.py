# -*- coding: utf-8 -*-
# 记忆系统基类


import os
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List
from abc import ABC, abstractmethod
from core.config import settings
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


def _normalize_text(text: str) -> str:
    """格式化文本：小写 且 合并空白符"""
    return " ".join(str(text or "").lower().split())

class MemoryMode(Enum):
    """记忆存储格式"""
    NOTES = "note"  # 每条记忆是最小的、不可再分的实时
    ENHANCED_NOTES = "enhanced_note"  # 每条记忆包含完整上下文段落
    JSON_CARDS = "json_card"  # 嵌套结构（类别->子类别->键值对）
    ADVANCED_JSON_CARDS = "advanced_json_card"  # 额外信息：叙事背景（backstory）、主体身份（person）、与用户的关系（relationship）和时间戳


@dataclass
class MemoryNote:
    """记忆笔记"""
    note_id: str
    content: str
    session_id: str

    # 上下文信息
    created_at: str
    updated_at: str
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """将记忆笔记转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryNote":
        """从字典创建记忆笔记"""
        return cls(**data)


@dataclass
class MemoryCard:
    """Json格式记忆卡片"""
    category: str
    subcategory: str
    key: str
    value: str
    session_id: str
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        """将记忆卡片转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryCard":
        """从字典创建记忆卡片"""
        return cls(**data)


class BaseMemorySystem(ABC):
    """记忆系统基类"""

    def __init__(self, user_id: str):
        """
        初始化记忆系统
        
        Args:
            user_id (str): 用户ID
            log (bool, optional): 是否开启日志记录. Defaults to False
        """
        self.user_id = user_id
        self.memory_file = os.path.join(settings.memory.storage_dir, f"{user_id}.json")

    @abstractmethod
    def load_memory(self):
        """加载记忆"""
        pass

    @abstractmethod
    def save_memory(self):
        """保存记忆"""
        pass

    @abstractmethod
    def add_memory(self, content: Any, session_id: str, **kwargs):
        """添加记忆"""
        pass

    @abstractmethod
    def update_memory(self, memory_id: str, session_id: str, content: Any, **kwargs):
        """更新记忆"""
        pass

    @abstractmethod
    def delete_memory(self, memory_id: str):
        """删除记忆"""
        pass

    @abstractmethod
    def search_memory(self, query: str) -> List[Any]:
        """搜索记忆"""
        pass

    @abstractmethod
    def get_context_format(self) -> str:
        """获取所有记忆内容格式化为LLM上下文"""
        pass


class NotesMemorySystem(BaseMemorySystem):
    """笔记记忆系统"""

    def __init__(self, user_id: str):
        self.notes: List[MemoryNote] = []
        super().__init__(user_id)


    def load_memory(self):
        """加载记忆"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("type") == MemoryMode.NOTES.value:
                    self.notes = [MemoryNote.from_dict(note) for note in data.get("notes", [])]
                    logger.info(f"成功加载 {len(self.notes)} 条笔记")
                else:
                    logger.error(f"用户 {self.user_id} 记忆文件格式错误: {data.get('type')}")
        else:
            self.notes = []
            logger.info(f"用户 {self.user_id} 没有记忆文件")

    def save_memory(self):
        """保存笔记"""
        try:
            os.makedirs(os.path.dirname(self.memory_file) or ".", exist_ok=True)
            with open(self.memory_file, "w", encoding="utf-8") as f:
                data = {
                    "user_id": self.user_id,
                    "type": MemoryMode.NOTES.value,
                    "updated_at": datetime.now().isoformat(),
                    "notes": [note.to_dict() for note in self.notes]
                }
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存笔记时出错: {e}")

    def add_memory(self, content: str, session_id: str, tags: list[str] = None):
        """添加笔记"""
        note = MemoryNote(
            note_id=str(uuid.uuid4()),
            content=content,
            session_id=session_id,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            tags=tags or []
        )
        self.notes.append(note)
        # 限制记忆条数。 按更新时间排序，保留最新条
        if len(self.notes) > settings.memory.max_items:
            self.notes.sort(key=lambda x: x.updated_at)
            self.notes.pop(0)
            logger.info(f"笔记添加：用户 {self.user_id} 记忆条数超过最大限制，已删除旧笔记")
        self.save_memory()
        return note.note_id

    def update_memory(self, memory_id: str, content: str, session_id: str, tags: list[str] = None):
        """更新笔记"""
        for note in self.notes:
            if note.note_id == memory_id:
                note.content = content
                note.session_id = session_id
                if tags is not None:
                    note.tags = tags
                note.updated_at = datetime.now().isoformat()
                self.save_memory()
                return True
        logger.error(f"笔记更新：用户 {self.user_id} 未找到ID为 {memory_id} 的笔记")
        return False

    def delete_memory(self, memory_id: str):
        """删除笔记"""
        for note in self.notes:
            if note.note_id == memory_id:
                self.notes.remove(note)
                self.save_memory()
                return True
        logger.error(f"笔记删除：用户 {self.user_id} 未找到ID为 {memory_id} 的笔记")
        return False

    def search_memory(self, query: str) -> List[MemoryNote]:
        """搜索笔记。 简单的文本搜索, 内容和标签同时匹配"""
        query_lower = query.lower()
        results = [note for note in self.notes if query_lower in note.content.lower() or any(query_lower in tag.lower() for tag in note.tags)]
        return results

    def get_context_format(self) -> str:
        """将所有笔记内容转化为LLM上下文格式"""
        if not self.notes:
            return "无内容"

        context = "User Memory Notes:\n\n"
        for i, note in enumerate(self.notes, start=1):
            context += f"Note {i} (ID: {note.note_id}, Session: {note.session_id}):\n"
            context += f"  Content: {note.content}\n"
            if note.tags:
                context += f"  Tags: {', '.join(note.tags)}\n"
            context += f"  Updated: {note.updated_at}\n\n"
        return context

    def consolidate_memories(self, resolve_conflicts: bool = True) -> Dict[str, Any]:
        """
        笔记的去重和冲突解决
        冲突解决策略：
            按第一个标签进行分组，每个分组内 内容不一致时，保留最近更新的，删除其他笔记
        """
        # 处理报告
        report: Dict[str, Any] = {
            "duplicates_removed": 0,
            "merged_notes": [],
            "conflict_resolved": [],
            "initial_count": len(self.notes),
            "final_count": 0,
        }

        # 1. 去重
        by_content: Dict[str, MemoryNote] = {}
        deduped: List[MemoryNote] = []
        for note in self.notes:
            norm = _normalize_text(note.content)
            existing = by_content.get(norm)
            if existing is None:
                by_content[norm] = note
                deduped.append(note)
                continue
            # 重复内容，保留最新的
            keeper, dropped = (existing, note) if existing.updated_at >= note.updated_at else (note, existing)
            keeper.tags = sorted(set(keeper.tags) | set(dropped.tags)) # 合并标签
            if keeper is note:      # 替换引用
                idx = deduped.index(existing)
                deduped[idx] = keeper
                by_content[norm] = keeper
            report["duplicates_removed"] += 1
            report["merged_notes"].append(keeper.content)

        # 2. 冲突处理。 直接比较格式化文本内容
        if resolve_conflicts:
            groups: Dict[str, List[MemoryNote]] = {}
            singletons: List[MemoryNote] = []
            for note in deduped:
                attr = note.tags[0] if note.tags else None
                if attr is None:
                    singletons.append(note)
                else:
                    groups.setdefault(attr, []).append(note)

            kept: List[MemoryNote] = list(singletons)
            for attr, notes in groups.items():
                distinct = {_normalize_text(note.content) for note in notes}
                if len(notes) == 1 or len(distinct) == 1:
                    # 仅一条笔记，不会冲突
                    kept.append(notes)
                    continue
                winner = max(notes, key=lambda note: note.updated_at)       # 保留 最近更新的
                superseded = [note for note in notes if note is not winner] # 要移除的
                kept.append(winner)
                report["conflict_resolved"].append({
                    "attr": attr,
                    "kept": winner.content,
                    "superseded": [note.content for note in superseded],
                })

            deduped = kept

        changed = len(deduped) != len(kept)
        self.notes = deduped
        report["final_count"] = len(self.notes)
        if changed:
            self.save_memory()
        return report


class JsonCardsMemorySystem(BaseMemorySystem):
    """Json格式记忆卡片系统"""

    def __init__(self, user_id: str):
        # 三层嵌套 类别→子类别→键值对
        self.cards: Dict[str, Dict[str, Dict[str, Any]]] = {}
        super().__init__(user_id)

    def load_memory(self):
        """从文件加载记忆卡片"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data["type"] == MemoryMode.JSON_CARDS.value:
                    self.cards = data.get("memory_cards", {})
                    logger.info(f"成功加载 {len(self.cards)} 条记忆卡片")
                else:
                    self.cards = {}
                    logger.error(f"用户 {self.user_id} 记忆文件格式错误: {data.get('type')}")
        else:
            self.cards = {}
            logger.info(f"用户 {self.user_id} 没有记忆卡片文件")

    def save_memory(self):
        """将记忆卡片保存到文件"""
        try:
            os.makedirs(os.path.dirname(self.memory_file) or ".", exist_ok=True)
            with open(self.memory_file, "w", encoding="utf-8") as f:
                data = {
                    "user_id": self.user_id,
                    "type": MemoryMode.JSON_CARDS.value,
                    "updated_at": datetime.now().isoformat(),
                    "memory_cards": self.cards
                }
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存记忆卡片到文件失败: {e}")

    def add_memory(self, content: Dict[str, Any], session_id: str, **kwargs):
        """添加记忆卡片.  结构为三层嵌套：类别→子类别→键值对"""
        category = content.get("category", "general")
        subcategory = content.get("subcategory", "info")
        key = content.get("key", str(uuid.uuid4()))
        value = content.get("value")

        self.cards.setdefault(category, {}).setdefault(subcategory, {})[key] = {
            "value": value,
            "session_id": session_id,
            "updated_at": datetime.now().isoformat(),
        }
        self.save_memory()
        return f"{category}.{subcategory}.{key}"

    def update_memory(self, memory_id: str, session_id: str, content: Dict[str, Any], **kwargs):
        """更新记忆卡片"""
        parts = memory_id.split(".")
        if len(parts) != 3:
            return False
        
        category, subcategory, key = parts
        if category in self.cards and subcategory in self.cards[category] and key in self.cards[category][subcategory]:
            self.cards[category][subcategory][key]["value"] = {
                "value": content.get("value"),
                "session_id": session_id,
                "updated_at": datetime.now().isoformat(),
            }
            self.save_memory()
            return True
        return False

    def delete_memory(self, memory_id):
        """删除记忆卡片"""
        parts = memory_id.split(".")
        if len(parts) != 3:
            return
        
        category, subcategory, key = parts
        if category in self.cards and subcategory in self.cards[category] and key in self.cards[category][subcategory]:
            del self.cards[category][subcategory][key]

            # 清理空字典
            if not self.cards[category][subcategory]:
                del self.cards[category][subcategory]
            if not self.cards[category]:
                del self.cards[category]
            self.save_memory()

    def search_memory(self, query):
        """搜索记忆卡片"""
        query_lower = query.lower()
        results = []
        for category, subcategory_cards in self.cards.items():
            for subcategory, key_cards in subcategory_cards.items():
                for key, card in key_cards.items():
                    memory_path = f"{category}.{subcategory}.{key}"
                    value_str = str(card.get("value", "")).lower()
                    if (query_lower in category.lower() or
                        query_lower in subcategory.lower() or
                        query_lower in key.lower() or
                        query_lower in value_str):

                        results.append((memory_path, card))
        return results

    def get_context_format(self):
        """所有记忆卡片内容以LLM上下文格式返回"""
        if not self.cards:
            return "无内容"
        context = "User Memory Cards(JSON):\n\n"
        context += json.dumps(self.cards, ensure_ascii=False, indent=2)
        return context
        


class AdvancedJsonCardsMemorySystem(BaseMemorySystem):
    """高级Json格式记忆卡片系统.  结构：categories -> memory_card_key -> memory card (任意 JSON 结构对象)"""

    def __init__(self, user_id: str):
        self.cards: Dict[str, Dict[str, Dict[str, Any]]] = {}
        super().__init__(user_id)

    def load_memory(self):
        """从文件加载记忆卡片"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data["type"] == MemoryMode.ADVANCED_JSON_CARDS.value:
                    self.cards = data.get("memory_cards", {})
                    logger.info(f"成功加载 {len(self.cards)} 条记忆卡片")
                else:
                    self.cards = {}
                    logger.error(f"用户 {self.user_id} 记忆文件格式错误: {data.get('type')}")
        else:
            self.cards = {}
            logger.info(f"用户 {self.user_id} 没有记忆卡片文件")
    
    def save_memory(self):
        """将记忆卡片保存到文件"""
        try:
            os.makedirs(os.path.dirname(self.memory_file) or ".", exist_ok=True)
            with open(self.memory_file, "w", encoding="utf-8") as f:
                data = {
                    "user_id": self.user_id,
                    "type": MemoryMode.JSON_CARDS.value,
                    "updated_at": datetime.now().isoformat(),
                    "memory_cards": self.cards
                }
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存记忆卡片到文件失败: {e}")

    def add_memory(self, content: Dict[str, Any], session_id: str, **kwargs):
        """
        添加记忆卡片

        Args:
            content (Dict[str, Any]): 记忆卡片内容，包含 category、card_key、card(JSON格式对象) 字段
            session_id (str): 会话ID，用于关联记忆卡片

        Returns:
            str: 记忆卡片路径，格式为 category.card_key
        """
        category = content.get("category", "general")
        card_key = content.get("card_key", str(uuid.uuid4()))
        card = content.get("card")

        # 添加元数据
        card['_metadata'] = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "session_id": session_id,
        }
        # 语义补充数据
        if 'backstory' not in card:
            card['backstory'] = kwargs.get("backstory", "") # 叙事背景
        if 'date_created' not in card:
            card['date_created'] = datetime.now().strftime(settings.timestamp_format) # 时间戳
        if 'person' not in card:
            card['person'] = kwargs.get("person", "Unknown") # 主体身份
        if 'relationship' not in card:
            card['relationship'] = kwargs.get("relationship", "Unknown") # 与主体的关系

        self.cards.setdefault(category, {}).setdefault(card_key, card)
        self.save_memory()
        return f"{category}.{card_key}"

    def update_memory(self, memory_id: str, session_id: str, content: Dict[str, Any], **kwargs):
        """更新记忆卡片"""
        parts = memory_id.split(".")
        if len(parts) != 2:
            return False
        
        category, card_key = parts
        if category in self.cards and card_key in self.cards[category]:
            old_card = self.cards[category][card_key]
            card = content.get("card", content)
            if '_metadata' in old_card:
                card['_metadata'] = old_card['_metadata']
            else:
                card['_metadata'] = {
                    "created_at": datetime.now().isoformat()
                }
            card['_metadata']['updated_at'] = datetime.now().isoformat()
            card['_metadata']['session_id'] = session_id
            self.cards[category][card_key] = card
            self.save_memory()
            return True
        return False

    def delete_memory(self, memory_id):
        """删除记忆卡片"""
        parts = memory_id.split(".")
        if len(parts) != 3:
            return
        
        category, subcategory, key = parts
        if category in self.cards and subcategory in self.cards[category] and key in self.cards[category][subcategory]:
            del self.cards[category][subcategory][key]

            # 清理空字典
            if not self.cards[category][subcategory]:
                del self.cards[category][subcategory]
            if not self.cards[category]:
                del self.cards[category]
            self.save_memory()

    def search_memory(self, query):
        """搜索记忆卡片"""
        query_lower = query.lower()
        results = []
        for category, subcategory_cards in self.cards.items():
            for subcategory, key_cards in subcategory_cards.items():
                for key, card in key_cards.items():
                    memory_path = f"{category}.{subcategory}.{key}"
                    value_str = str(card.get("value", "")).lower()
                    if (query_lower in category.lower() or
                        query_lower in subcategory.lower() or
                        query_lower in key.lower() or
                        query_lower in value_str):

                        results.append((memory_path, card))
        return results

    def get_context_format(self):
        """所有记忆卡片内容以LLM上下文格式返回"""
        if not self.cards:
            return "无内容"
        context = "User Memory Cards(JSON):\n\n"
        context += json.dumps(self.cards, ensure_ascii=False, indent=2)
        return context
    