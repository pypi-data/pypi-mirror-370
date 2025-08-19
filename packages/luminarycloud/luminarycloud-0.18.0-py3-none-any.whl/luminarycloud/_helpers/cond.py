# Copyright 2024 Luminary Cloud, Inc. All Rights Reserved.
# type: ignore

import json
from dataclasses import dataclass, field
from itertools import pairwise
from collections import defaultdict
from collections.abc import Iterable, Mapping, Iterator
from typing import Any, Optional, TypeVar
from uuid import UUID, uuid4

from google.protobuf.any_pb2 import Any as AnyProto
from google.protobuf.descriptor import Descriptor, FieldDescriptor
from google.protobuf.json_format import MessageToDict

import luminarycloud._proto.condition.condition_pb2 as conditionpb
import luminarycloud._proto.options.options_pb2 as optionspb
from luminarycloud._proto.client.simulation_pb2 import SimulationParam


class ParamMap:
    """
    Provides maps to get the FieldDescriptor for every "param" (see param_registry.py) by name
    or by numner (tag/field number, which is supposed to unique) in the given param group.
    """

    by_name: dict[str, FieldDescriptor]
    by_number: dict[int, FieldDescriptor]

    def __init__(self, param_group: AnyProto):
        self.by_name = dict()
        self.by_number = dict()
        self._build(param_group.DESCRIPTOR)

    def _build(self, param_group_desc: Optional[Descriptor]):
        if param_group_desc is not None:
            if param_group_desc.containing_type is not None:  # to detect map/Entry types
                return self._build(param_group_desc.fields_by_name["value"].message_type)
            for field in param_group_desc.fields:
                if field.name in self.by_name:
                    continue
                if not str.startswith(field.full_name, "luminary.proto.client"):
                    continue
                self.by_name[field.name] = field
                self.by_number[field.number] = field
                self._build(field.message_type)


K = TypeVar("K")
V = TypeVar("V")


class ContextFrame(Mapping[K, V]):
    """
    A utility class which implements a Mapping (i.e. dict) interface as a... graph(?) of context frames.

    Writes only write to this frame, while reads look at this frame and then each of its ancestor
    frames, returning only the first hit. Returns None if there is no hit.
    """

    __id: UUID
    __parent_frames: list["ContextFrame"]
    __current_frame: dict[type[K], type[V]]

    def __init__(self):
        self.__id = uuid4()
        self.__current_frame = dict()
        self.__parent_frames = []

    def new_frame(self) -> "ContextFrame":
        """Creates a new frame on top of this frame"""
        __next_frame = ContextFrame()
        __next_frame.__parent_frames = [self]
        return __next_frame

    def entangle(self, other: "ContextFrame") -> None:
        """
        Entangles this frame with another frame.

        Essentially, becomes a secondary parent of the other frame, and vice versa. This creates a
        cycle but reads won't revisit frames. Might seem weird, but it's necessary.
        """
        self.__parent_frames.append(other)
        other.__parent_frames.append(self)

    def __setitem__(self, key: type[K], value: type[V]) -> None:
        self.__current_frame[key] = value

    def __getitem__(self, key: type[K]) -> Optional[type[V]]:
        return self.__getitem_helper(key, set())

    def __getitem_helper(self, key: type[K], closed: set[str]) -> Optional[type[V]]:
        if key in self.__current_frame:
            return self.__current_frame[key]
        for frame in self.__parent_frames:
            if frame.__id in closed:
                continue
            closed.add(frame.__id)

            found = frame.__getitem_helper(key, closed)
            if found is not None:
                return found
        return None

    def __iter__(self) -> Iterator[tuple[type[K], type[V]]]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


@dataclass(kw_only=True)
class Node:
    """
    Represents actual data in an instance of client params. Unlike just the "param", a node has a
    value and a parent.

    To help with evaluating conds, it also keeps track of whether it is active/inactive and has a
    context that can be used to resolve relative references to other nodes.
    """

    name: str = ""
    "Param name or key name (depending on whether this is a map or message value)"
    value: Any = None
    parent: Optional["Node"] = None
    children: list["Node"] = field(default_factory=list)

    is_active: Optional[bool] = None
    context: ContextFrame[str | int, "Node"] = field(default_factory=ContextFrame)


class CondHelper:

    def __init__(self):
        self.params = ParamMap(SimulationParam)
        self.nodes_by_surface: dict[str, list[Node]] = defaultdict(
            list
        )  # nodes with surface references

    def prune(self, tree: dict[str, Any]) -> dict[str, Any]:
        """
        Takes a dict of client parameters and returns a pruned tree, with inactive nodes and empty
        values removed.
        """
        # Scan entire tree to register all nodes.
        root_node = Node(is_active=True)
        self._scan_tree(tree, root_node)

        physics_nodes_by_id = self._physics_nodes_by_id(root_node)
        material_nodes_by_id = self._material_nodes_by_id(root_node)

        # Entangle physics and material nodes
        self._entangle_fluid_and_heat_physics(physics_nodes_by_id)
        self._entangle_physics_and_material_nodes(tree, physics_nodes_by_id, material_nodes_by_id)
        self._entangle_surface_nodes()

        # Finally, prune, using our registered nodes to evaluate conds.
        return self._prune_helper(root_node)

    def _scan_tree(
        self,
        tree: dict[str, Any],
        parent_node: Optional[Node],
    ) -> None:
        """
        From the root, traverses the tree to register all nodes. Whenever we go down into a
        "repeated" or "map" fields we push a new frame onto the context.
        """
        context = parent_node.context
        for key, value in tree.items():
            param = self.params.by_name.get(key, None)
            if param is None:
                continue  # ignore non-params

            node = Node(
                name=key,
                parent=parent_node,
                value=value,
                is_active=None,
                context=context,
            )
            parent_node.children.append(node)
            context[param.name] = node
            context[param.number] = node

            # Keep track of nodes with surface references
            if is_surface_reference(param):
                for surface in value:  # NOTE: just going to assume it's a list of surfaces
                    self.nodes_by_surface[surface].append(parent_node)

            if param.message_type is None or isinstance(value, str):
                continue

            # Recurse into message types
            if param.label == FieldDescriptor.LABEL_REPEATED:
                # map types show up as REPEATED in descriptor
                if isinstance(value, dict) and len(value) > 0:
                    for k, v in value.items():
                        new_node = Node(
                            name=k,
                            value=v,
                            is_active=True,
                            context=context.new_frame(),
                        )  # new frame
                        node.children.append(new_node)
                        self._scan_tree(v, new_node)
                elif isinstance(value, Iterable) and len(value) > 0:
                    for v in value:
                        new_node = Node(
                            value=v,
                            is_active=True,
                            context=context.new_frame(),
                        )  # new frame
                        node.children.append(new_node)
                        self._scan_tree(v, new_node)
            else:
                self._scan_tree(value, node)

    def _entangle_fluid_and_heat_physics(self, physics_nodes_by_id: dict[str, Node]) -> None:
        """
        Entangles fluid and heat physics nodes.
        """
        fluid_node = None
        heat_node = None
        for node in physics_nodes_by_id.values():
            if "fluid" in node.value:
                fluid_node = node
            elif "heat" in node.value:
                heat_node = node
        if fluid_node is not None and heat_node is not None:
            fluid_node.context.entangle(heat_node.context)

    def _entangle_physics_and_material_nodes(
        self,
        root: dict[str, Any],
        physics_nodes_by_id: dict[str, Node],
        material_nodes_by_id: dict[str, Node],
    ) -> None:
        """
        Entangles physics and material nodes that have a relationship with the same volume.
        """
        for physics_node in physics_nodes_by_id.values():
            physics_id = physics_node.value["physics_identifier"]["id"]
            material_id = self._get_material_id_by_physics_id(root, physics_id)
            if not material_id:
                continue
            material_node = material_nodes_by_id[material_id]
            physics_node.context.entangle(material_node.context)

    def _entangle_surface_nodes(self) -> None:
        """
        Entangles any nodes that reference the same surface.
        """
        for node_group in self.nodes_by_surface.values():
            for a, b in pairwise(node_group):
                a.context.entangle(b.context)

    def _prune_helper(self, root_node: Node) -> dict[str, Any]:
        """
        Prunes the tree, using nodes to resolve conds.
        """
        pruned_tree = dict()
        for node in root_node.children:
            name, value = node.name, node.value
            param = self.params.by_name.get(name, None)

            if param is None or name == "surface_name":  # "surface_name" appears twice in the tree
                pruned_tree[name] = value
                continue

            if self._is_node_active(node):
                if param.message_type is None or not str.startswith(
                    param.message_type.full_name, "luminary.proto.client"
                ):
                    if not (isinstance(value, Iterable) and len(value) == 0):
                        pruned_tree[name] = value
                elif param.label == FieldDescriptor.LABEL_REPEATED:
                    # map types show up as REPEATED in descriptor, so we need to distinguish
                    if isinstance(value, dict) and len(value) > 0:
                        pruned_tree[name] = {n.name: self._prune_helper(n) for n in node.children}
                    elif isinstance(value, Iterable) and len(value) > 0:
                        pruned_tree[name] = [self._prune_helper(n) for n in node.children]
                else:
                    pruned_value = self._prune_helper(node)
                    if len(pruned_value) > 0:  # prune empty dicts
                        pruned_tree[name] = pruned_value
        return pruned_tree

    def _physics_nodes_by_id(self, root_node: Node) -> dict[str, Node]:
        """
        Gets a map of physics nodes by their id.
        """
        nodes_by_physics_id = dict()
        for node in root_node.children:
            if node.name == "physics":
                for physics_node in node.children:
                    physics_id = physics_node.value["physics_identifier"]["id"]
                    nodes_by_physics_id[physics_id] = physics_node
        return nodes_by_physics_id

    def _material_nodes_by_id(self, root_node: Node) -> dict[str, Node]:
        """
        Gets a map of material nodes by their id.
        """
        nodes_by_material_id = dict()
        for node in root_node.children:
            if node.name == "material_entity":
                for material_node in node.children:
                    material_id = material_node.value["material_identifier"]["id"]
                    nodes_by_material_id[material_id] = material_node
        return nodes_by_material_id

    def _get_material_id_by_physics_id(
        self, root: dict[str, Any], physics_id: str
    ) -> dict[str, Any] | None:
        volume_id = self._get_volume_id_by_physics_id(root, physics_id)
        if volume_id is None:
            return None
        return self._get_material_id_by_volume_id(root, volume_id)

    def _get_volume_id_by_physics_id(self, root: dict[str, Any], physics_id: str) -> str | None:
        entity_relationships = root.get("entity_relationships")
        if not entity_relationships:
            return None
        for link in entity_relationships.get("volume_physics_relationship", []):
            if link.get("physics_identifier", {}).get("id") == physics_id:
                return link.get("volume_identifier", {}).get("id")
        return None

    def _get_material_id_by_volume_id(self, root: dict[str, Any], volume_id: str) -> str | None:
        entity_relationships = root.get("entity_relationships")
        if not entity_relationships:
            return None
        for link in entity_relationships.get("volume_material_relationship", []):
            if link.get("volume_identifier", {}).get("id") == volume_id:
                return link.get("material_identifier", {}).get("id")
        return None

    def _is_node_active(self, node: Node) -> bool:
        """
        Checks if a node is active.

        Checks the parent first, and then the conds. Only does this once.
        """
        if node.is_active is None:
            if node.parent is not None:
                if not self._is_node_active(node.parent):
                    node.is_active = False
                    return False
            cond = get_cond(self.params.by_name[node.name])
            node.is_active = self._check_cond(cond, node.context)
        return node.is_active

    def _check_cond(
        self, cond: conditionpb.Condition, context: ContextFrame[str | int, Node]
    ) -> bool:
        type = cond.WhichOneof("typ")
        if type is None:
            return True
        if type == "choice":
            return self._check_choice(cond.choice, context)
        elif type == "boolean":
            return self._check_boolean(cond.boolean, context)
        elif type == "allof":
            return all(self._check_cond(c, context) for c in cond.allof.cond)
        elif type == "anyof":
            return any(self._check_cond(c, context) for c in cond.anyof.cond)
        elif type == "not":
            return not self._check_cond(getattr(cond, "not").cond, context)
        elif type == "tag":
            return self._check_tag(cond.tag, context)
        elif type == "false":
            return (
                True  # CondFalse is generally used to control visibility in UI and can be ignored
            )
        return False

    def _check_choice(
        self, cond_choice: conditionpb.Choice, context: ContextFrame[str | int, Node]
    ) -> bool:
        name = cond_choice.param_name
        node = context[name]
        if node is None:
            return 0 == cond_choice.tag
        return self._is_node_active(node) and node.value == cond_choice.name

    def _check_boolean(
        self, cond_boolean: conditionpb.TrueFalse, context: ContextFrame[str | int, Node]
    ) -> bool:
        tag = cond_boolean.param_name_tag
        node = context[tag]
        if node is None:
            return False
        return self._is_node_active(node) and bool(node.value)

    def _check_tag(self, cond_tag: conditionpb.Tag, context: ContextFrame[str | int, Node]) -> bool:
        name = cond_tag.tag_name
        node = context[name]
        return (node is not None) and self._is_node_active(node)


def params_to_dict(sim_params: SimulationParam) -> dict[str, Any]:
    tree = MessageToDict(
        sim_params,
        preserving_proto_field_name=True,
    )
    helper = CondHelper()
    return helper.prune(tree)


def params_to_str(sim_params: SimulationParam) -> str:
    return json.dumps(params_to_dict(sim_params), indent=4)


def get_cond(param: FieldDescriptor) -> conditionpb.Condition:
    return param.GetOptions().Extensions[optionspb.cond]


def get_default(param: FieldDescriptor) -> Any:
    dfl = param.GetOptions().Extensions[optionspb.default_value]
    type = dfl.WhichOneof("typ")
    if type == "boolval":
        return dfl.boolval
    elif type == "choice":
        return dfl.choice
    elif type == "intval":
        return dfl.intval
    elif type == "strval":
        return dfl.strval
    elif type == "real":
        return dfl.real
    elif type == "vector3":
        return dfl.vector3
    return None


def is_surface_reference(param: FieldDescriptor) -> bool:
    return param.GetOptions().Extensions[optionspb.is_geometry_surfaces]
