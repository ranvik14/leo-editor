from typing import Any

def at_file_to_at_auto_command(event) -> None: ...
def view_pack_command(event) -> None: ...

class PersistenceDataController:
    c: Any
    at_persistence: Any
    def __init__(self, c) -> None: ...
    def clean(self) -> None: ...
    def update_before_write_foreign_file(self, root): ...
    def delete_at_data_children(self, at_data, root) -> None: ...
    def update_after_read_foreign_file(self, root) -> None: ...
    def restore_gnxs(self, at_gnxs, root) -> None: ...
    def create_outer_gnx_dict(self, root): ...
    def restore_gnx(self, d, gnx, root, unl) -> None: ...
    def create_uas(self, at_uas, root) -> None: ...
    def at_data_body(self, p): ...
    def expected_headline(self, p): ...
    def find_at_data_node(self, root): ...
    def find_at_gnxs_node(self, root): ...
    def find_at_persistence_node(self): ...
    def find_at_uas_node(self, root): ...
    def find_position_for_relative_unl(self, root, unl): ...
    def find_best_match(self, root, unl_list): ...
    def find_exact_match(self, root, unl_list): ...
    def find_representative_node(self, root, target): ...
    def foreign_file_name(self, p): ...
    def has_at_data_node(self, root): ...
    def has_at_gnxs_node(self, root): ...
    def has_at_uas_node(self, root): ...
    def has_at_persistence_node(self): ...
    def is_at_auto_node(self, p): ...
    def is_at_file_node(self, p): ...
    def is_cloned_outside_parent_tree(self, p): ...
    def is_foreign_file(self, p): ...
    def pickle(self, p): ...
    def unpickle(self, s): ...
    def drop_unl_parent(self, unl): ...
    def drop_unl_tail(self, unl): ...
    def relative_unl(self, p, root): ...
    def unl(self, p): ...
    def unl_tail(self, unl): ...
