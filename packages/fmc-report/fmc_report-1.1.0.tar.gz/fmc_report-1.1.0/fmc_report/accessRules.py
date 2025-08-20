from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class Zone:
    id: str
    name: str
    subType: str
    type: str

@dataclass
class Network:
    id: str
    name: str
    overridable: bool
    type: str

@dataclass
class Port:
    id: str
    name: str
    overridable: bool
    protocol: str
    type: str

@dataclass
class Application:
    id: str
    name: str
    type: str

@dataclass
class URLCategory:
    id: str
    name: str
    type: str

@dataclass
class URLCategoryWithReputation:
    category: URLCategory
    type: str

@dataclass
class SecurityGroupTag:
    id: str
    name: str
    type: str

@dataclass
class NetworkGroup:
    id: str
    name: str
    overridable: bool
    type: str

@dataclass
class Metadata:
    accessPolicy: Dict[str, str]
    category: str
    domain: Dict[str, str]
    ruleIndex: int
    section: str
    timestamp: int

@dataclass
class Links:
    self: str

@dataclass
class VariableSet:
    id: str
    name: str
    type: str

@dataclass
class AccessRule:
    action: str
    applications: Dict[str, List[Application]]
    destinationDynamicObjects: Dict
    destinationNetworks: Dict[str, List[Network]]
    destinationPorts: Dict[str, List[Port]]
    destinationZones: Dict[str, List[Zone]]
    enableSyslog: bool
    enabled: bool
    id: str
    links: Links
    logBegin: bool
    logEnd: bool
    logFiles: bool
    metadata: Metadata
    name: str
    sendEventsToFMC: bool
    sourceDynamicObjects: Dict
    sourceNetworks: Dict[str, List[Network]]
    # sourceNetworkGroups: Dict[str, List[NetworkGroup]]
    sourcePorts: Dict[str, List[Port]]
    sourceSecurityGroupTags: Dict[str, List[SecurityGroupTag]]
    sourceZones: Dict[str, List[Zone]]
    type: str
    urls: Dict[str, List[URLCategoryWithReputation]]
    variableSet: VariableSet
    vlanTags: Dict

def create_access_rule(
    action: str,
    id: str,
    name: str,
    enabled: bool,
    links: Links,
    metadata: Metadata,
    variable_set: VariableSet,
    applications: Optional[Dict[str, List[Application]]] = None,
    destination_dynamic_objects: Optional[Dict] = None,
    destination_networks: Optional[Dict[str, List[Network]]] = None,
    destination_ports: Optional[Dict[str, List[Port]]] = None,
    destination_zones: Optional[Dict[str, List[Zone]]] = None,
    source_dynamic_objects: Optional[Dict] = None,
    source_networks: Optional[Dict[str, List[Network]]] = None,
    # source_network_groups: Optional[Dict[str, List[NetworkGroup]]] = None,
    source_ports: Optional[Dict[str, List[Port]]] = None,
    source_security_group_tags: Optional[Dict[str, List[SecurityGroupTag]]] = None,
    source_zones: Optional[Dict[str, List[Zone]]] = None,
    urls: Optional[Dict[str, List[URLCategoryWithReputation]]] = None,
    enable_syslog: bool = False,
    log_begin: bool = False,
    log_end: bool = False,
    log_files: bool = False,
    send_events_to_fmc: bool = False,
    vlan_tags: Optional[Dict] = None
) -> AccessRule:
    return AccessRule(
        action=action,
        applications=applications or {},
        destinationDynamicObjects=destination_dynamic_objects or {},
        destinationNetworks=destination_networks or {},
        destinationPorts=destination_ports or {},
        destinationZones=destination_zones or {},
        enableSyslog=enable_syslog,
        enabled=enabled,
        id=id,
        links=links,
        logBegin=log_begin,
        logEnd=log_end,
        logFiles=log_files,
        metadata=metadata,
        name=name,
        sendEventsToFMC=send_events_to_fmc,
        sourceDynamicObjects=source_dynamic_objects or {},
        sourceNetworks=source_networks or {},
        # sourceNetworkGroups=source_network_groups or {},
        sourcePorts=source_ports or {},
        sourceSecurityGroupTags=source_security_group_tags or {},
        sourceZones=source_zones or {},
        type="AccessRule",
        urls=urls or {},
        variableSet=variable_set,
        vlanTags=vlan_tags or {}
    )


def create_access_rules_from_dicts(dicts: List[Dict]) -> List[AccessRule]:
    access_rules = []

    for dictionary in dicts:
        links = Links(self=dictionary.get('links', {}).get('self'))
        metadata = Metadata(
            accessPolicy=dictionary.get('metadata', {}).get('accessPolicy'),
            category=dictionary.get('metadata', {}).get('category'),
            domain=dictionary.get('metadata', {}).get('domain'),
            ruleIndex=dictionary.get('metadata', {}).get('ruleIndex'),
            section=dictionary.get('metadata', {}).get('section'),
            timestamp=dictionary.get('metadata', {}).get('timestamp')
        )
        variable_set = VariableSet(
            id=dictionary.get('variableSet', {}).get('id'),
            name=dictionary.get('variableSet', {}).get('name'),
            type=dictionary.get('variableSet', {}).get('type')
        )

        access_rule = create_access_rule(
            action=dictionary.get('action'),
            id=dictionary.get('id'),
            name=dictionary.get('name'),
            enabled=dictionary.get('enabled'),
            links=links,
            metadata=metadata,
            variable_set=variable_set,
            applications=dictionary.get('applications', {}),
            destination_dynamic_objects=dictionary.get('destinationDynamicObjects', {}),
            destination_networks=dictionary.get('destinationNetworks', {}),
            destination_ports=dictionary.get('destinationPorts', {}),
            destination_zones=dictionary.get('destinationZones', {}),
            source_dynamic_objects=dictionary.get('sourceDynamicObjects', {}),
            source_networks=dictionary.get('sourceNetworks', {}),
            # source_network_groups=dictionary.get('sourceNetworkGroups', {}),
            source_ports=dictionary.get('sourcePorts', {}),
            source_security_group_tags=dictionary.get('sourceSecurityGroupTags', {}),
            source_zones=dictionary.get('sourceZones', {}),
            urls=dictionary.get('urls', {}),
            enable_syslog=dictionary.get('enableSyslog', False),
            log_begin=dictionary.get('logBegin', False),
            log_end=dictionary.get('logEnd', False),
            log_files=dictionary.get('logFiles', False),
            send_events_to_fmc=dictionary.get('sendEventsToFMC', False),
            vlan_tags=dictionary.get('vlanTags', {})
        )

        access_rules.append(access_rule)

    return access_rules
