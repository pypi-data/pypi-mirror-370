from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


@dataclass
class Entity:
    id: int
    name: str
    display: str
    url: str


@dataclass
class EntityWithSlug(Entity):
    slug: str


@dataclass
class Label:
    value: str
    label: str


@dataclass
class DeviceType:
    id: int
    manufacturer: EntityWithSlug
    model: str
    slug: str


@dataclass
class IpFamily:
    value: int
    label: str


@dataclass
class DeviceIp:
    id: int
    display: str
    address: str
    family: IpFamily  # after 4.0 "family" has new structure, int -> dict


@dataclass
class Circuit:
    id: int
    url: str
    display: str
    cid: str


@dataclass
class InterfaceCable:
    id: int
    label: str
    display: str
    url: str


@dataclass
class LinkPeer:
    id: int
    display: str
    url: str
    cable: InterfaceCable
    device: Entity | None = None
    term_side: str | None = None
    circuit: Circuit | None = None


@dataclass
class InterfaceType:
    value: str
    label: str


@dataclass
class InterfaceConnectedEndpoint(Entity):
    device: Entity | None = None
    cable: InterfaceCable | None = None


@dataclass
class InterfaceMode:
    value: str
    label: str


@dataclass
class InterfaceVlan(Entity):
    vid: int


@dataclass
class Interface(Entity):
    cable: InterfaceCable | None
    cable_end: str
    device: Entity
    label: str
    link_peers: list[LinkPeer]
    link_peers_type: str | None
    enabled: bool
    type: InterfaceType
    description: str
    connected_endpoints: list[InterfaceConnectedEndpoint] | None
    mode: InterfaceMode | None
    untagged_vlan: InterfaceVlan | None
    tagged_vlans: list[InterfaceVlan] | None
    created: datetime
    last_updated: datetime
    vrf: Entity | None
    mgmt_only: bool
    lag: Entity | None
    mtu: int | None
    tags: list[EntityWithSlug]
    speed: int | None
    custom_fields: dict[str, Any]
    count_ipaddresses: int
    count_fhrp_groups: int


@dataclass
class ConsolePort(Entity):
    cable: InterfaceCable | None
    device: Entity
    label: str
    type: InterfaceType
    description: str
    link_peers: list[LinkPeer] | None
    link_peers_type: str | None
    connected_endpoints: list[InterfaceConnectedEndpoint] | None
    created: datetime
    last_updated: datetime


@dataclass
class Device(Entity):
    url: str
    display: str  # renamed in 3.x from display_name
    device_type: DeviceType
    role: EntityWithSlug  # device_role is depricated after 4.0
    tenant: EntityWithSlug | None
    platform: EntityWithSlug | None
    serial: str
    asset_tag: str | None
    site: EntityWithSlug
    rack: Entity | None
    position: float | None
    face: Label | None
    status: Label
    primary_ip: DeviceIp | None
    primary_ip4: DeviceIp | None
    primary_ip6: DeviceIp | None
    tags: list[EntityWithSlug]
    custom_fields: dict[str, Any]
    created: datetime
    last_updated: datetime
    comments: None | str
    cluster: Entity | None
    config_context: dict[str, Any] | None
    config_template: dict[str, Any] | None


@dataclass
class IpAddrAssignedObject(Entity):
    device: Entity | None = None
    virtual_machine: Entity | None = None


@dataclass
class IpAddress:
    id: int
    assigned_object_id: int | None
    assigned_object: IpAddrAssignedObject | None
    display: str
    family: IpFamily
    address: str
    status: Label
    role: Label | None
    tags: list[EntityWithSlug]
    created: datetime
    last_updated: datetime
    tenant: EntityWithSlug | None
    vrf: Entity | None


class CableType(str, Enum):
    AOC = "aoc"
    CAT3 = "cat3"
    CAT5 = "cat5"
    CAT5E = "cat5e"
    CAT6 = "cat6"
    CAT6A = "cat6a"
    CAT7 = "cat7"
    CAT7A = "cat7a"
    CAT8 = "cat8"
    COAXIAL = "coaxial"
    DAC_ACTIVE = "dac-active"
    DAC_PASSIVE = "dac-passive"
    MMF = "mmf"
    MMF_OM1 = "mmf-om1"
    MMF_OM2 = "mmf-om2"
    MMF_OM3 = "mmf-om3"
    MMF_OM4 = "mmf-om4"
    MMF_OM5 = "mmf-om5"
    MRJ21_TRUNK = "mrj21-trunk"
    POWER = "power"
    SMF = "smf"
    SMF_OS1 = "smf-os1"
    SMF_OS2 = "smf-os2"
    VALUE_23 = ""


@dataclass
class GenericObject:
    object_type: str
    object_id: int


@dataclass
class Cable:
    id: int
    url: str
    display: str
    created: None | datetime
    last_updated: None | datetime
    custom_fields: dict[str, Any]
    tags: list[EntityWithSlug]
    type: CableType | None = None
    a_terminations: None | list[GenericObject] = None
    b_terminations: None | list[GenericObject] = None
    status: None | Label = None
    tenant: Entity | None = None
    label: None | str = None
    color: None | str = None
    length: None | float = None
    length_unit: Label | None = None
    description: None | str = None
    comments: None | str = None


@dataclass
class NewCable:
    custom_fields: dict[str, Any] | None = None
    tags: list[EntityWithSlug] | None = None
    type: CableType | None = None
    a_terminations: None | list[GenericObject] = None
    b_terminations: None | list[GenericObject] = None
    status: None | Label = None
    tenant: Entity | None = None
    label: None | str = None
    color: None | str = None
    length: None | float = None
    length_unit: Label | None = None
    description: None | str = None
    comments: None | str = None


@dataclass
class ItemToDelete:
    id: int


@dataclass
class Prefix:
    id: int
    prefix: str
    site: Entity | None
    vrf: Entity | None
    tenant: Entity | None
    vlan: Entity | None
    role: Entity | None
    status: Label
    is_pool: bool
    custom_fields: dict[str, Any]
    created: datetime
    description: str
    last_updated: datetime


@dataclass
class FHRPGroupBrief:
    id: int
    group_id: int
    display: str
    protocol: str
    description: str


@dataclass
class FHRPGroup(FHRPGroupBrief):
    name: str
    auth_type: str | None
    auth_key: str
    tags: list[EntityWithSlug]
    custom_fields: dict[str, Any]
    ip_addresses: list[DeviceIp]
    comments: str | None = None


@dataclass
class FHRPGroupAssignmentBrief:
    id: int
    display: str
    priority: int

    interface_type: str | None
    interface_id: int | None
    group: FHRPGroupBrief
