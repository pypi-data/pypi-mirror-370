from typing import Dict, Any, Union


class RefManager:
    def __init__(self):
        self.refs_dict: Dict[int, Dict[Union[str, int], Any]] = {}
        self.max_allocated_id = 1

    def create_ref(self, project_id: int, obj: Any):
        ref_id = self.max_allocated_id
        if project_id not in self.refs_dict:
            self.refs_dict[project_id] = {}
        self.refs_dict[project_id][ref_id] = obj
        self.max_allocated_id += 1
        return ref_id

    def create_ref_with_key(self, project_id: int, key: str, obj: Any):
        if project_id not in self.refs_dict:
            self.refs_dict[project_id] = {}
        self.refs_dict[project_id][key] = obj

    def get_object(self, project_id: int, ref_id: Union[str, int]):
        if project_id not in self.refs_dict:
            raise Exception(f"Project with project_id: {project_id} not found")
        return self.refs_dict[project_id].get(ref_id, None)

    def delete_refs(self, project_id: int):
        self.refs_dict[project_id].pop(project_id, None)
