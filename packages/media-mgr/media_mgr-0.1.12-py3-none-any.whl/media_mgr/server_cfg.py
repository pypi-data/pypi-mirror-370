#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- Server Config
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

from quickcolor.color_def import color

from corecfg.multi_entity import MultiEntityCoreCfg

from ipaddress import IPv4Network

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

class ServerType():
    plex = f'{color.CYELLOW2}plex{color.CEND}'
    worker = f'{color.CBLUE2}worker{color.CEND}'

serverTypeLkup = {
        'plex' : ServerType.plex,
        'worker' : ServerType.worker,
        }

# ------------------------------------------------------------------------------------------------------

def get_available_server_types():
    return serverTypeLkup.keys()

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def is_ipv4_address_valid(ipv4AddrToChk: str = "192.168.1.1", debug: bool = False):
    try:
        network = IPv4Network(ipv4AddrToChk)
        if debug:
            print(f'Specified IPV4 address ' + \
                    f'{color.CYELLOW2}{ipv4AddrToCheck}{color.CEND}' + \
                    f' is {color.CGREEN2}valid{color.CEND}!')
        return True
    except ValueError:
        if debug:
            print(f'{color.CYELLOW2}{ipv4AddrToCheck}{color.CEND} is ' + \
                    f'{color.CRED2}not{color.CEND} a valid IPv4 address!')
        return False

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

class ServerConfig(MultiEntityCoreCfg):

    # --------------------------------------------------------------------------------------------------
    def __init__(self, verbose: bool = False, debug: bool = False):
        self._verbose = verbose
        self._debug = debug
        if debug:
            print(f'{color.CCYAN2}Initializing {type(self).__name__}! {color.CWHITE2}id: {str(id(self))}{color.CEND}')

        super(ServerConfig, self).__init__(cfgFileName = 'server_config.json', debug = debug)

        cfgMetadataInit = { 'label' : 'Server Cfg', 'maxLabelLen' : 30 }
        categoryMetadataInit = {
                'ipv4' : { 'color' : color.CWHITE2, 'maxLen' : 20 },
                'serverType' : { 'color' : color.CBLUE2, 'maxLen' : 20 },
                }
        if cfgMetadataInit != self.get_cfg_metadata() or categoryMetadataInit != self.get_category_metadata():
            if debug:
                print(f'Initializing {type(self).__name__} metadata for cfg and categories!')
            self.initialize_metadata(cfgMetadata=cfgMetadataInit, categoryMetadata=categoryMetadataInit)

    # --------------------------------------------------------------------------------------------------
    def register_server(self, serverName: str, ipv4: str, serverType: str):
        if not is_ipv4_address_valid(ipv4AddrToChk = ipv4):
            raise ValueError(f"Specified ({ipv4}) is not a valid IPV4 address!")

        if serverType not in serverTypeLkup.keys():
            raise ValueError(f'{serverType} is not a recognized server type! ' + \
                    f'Try one of these: {serverTypeLkup.keys()}')

        tupleList = {}
        tupleList['ipv4'] = ipv4
        tupleList['serverType'] = serverType

        allItems = self.get_all_configured_items()
        if tupleList in allItems.values():
            print(f'{color.CRED2}Error: {color.CWHITE}Tuple {color.CBLUE2}' + \
                    f'{str(tupleList.values())}{color.CWHITE} is already configured!{color.CEND}')
            return

        self.update_item(itemLabel = serverName, newTuple = tupleList)

    # --------------------------------------------------------------------------------------------------
    def unregister_server(self, serverName: str):
        allItems = self.get_all_configured_items()
        if serverName not in allItems.keys():
            print(f'{color.CRED2}Error: {color.CWHITE}Media server label ' + \
                    f'{color.CBLUE2}{serverName}{color.CWHITE}' + \
                    f' is not registered in server config!{color.CEND}')
            return

        print(f'{color.CVIOLET2}\n   -- removing Media server label {color.CYELLOW}{serverName}{color.CVIOLET2}' + \
                f' containing \n      {color.CWHITE2}{str(allItems[serverName])}{color.CEND}')

        self.remove_item(itemLabel = serverName)

    # --------------------------------------------------------------------------------------------------
    def get_server_list(self):
        allItems = self.get_all_configured_items()
        return allItems.items()

    # --------------------------------------------------------------------------------------------------
    def get_server_name_list(self):
        allItems = self.get_all_configured_items()
        return allItems.keys()

    # --------------------------------------------------------------------------------------------------
    def get_server_address(self, serverLabel: str):
        itemData = self.get_cfg_data_for_item_label(itemLabel = serverLabel)
        return itemData['ipv4']

    # --------------------------------------------------------------------------------------------------
    def get_server_type(self, serverLabel: str):
        itemData = self.get_cfg_data_for_item_label(itemLabel = serverLabel)
        return itemData['serverType']

    # --------------------------------------------------------------------------------------------------
    def get_server_type_for_ipv4(self, ipv4: str):
        allItems = self.get_all_configured_items()
        for item, itemData in allItems.items():
            if ipv4 == itemData['ipv4']:
                return itemData['serverType']

        raise ValueError('Specified IPV4 is not part of server config!')

    # --------------------------------------------------------------------------------------------------
    def get_server_ipv4_list(self, serverType: str | None = None) -> list:
        ipv4List = []
        allItems = self.get_all_configured_items()
        for item, itemData in allItems.items():
            if not serverType or serverType in itemData['serverType']:
                ipv4List.append(itemData['ipv4'])

        return ipv4List

    # --------------------------------------------------------------------------------------------------
    def show_server_config(self):
        MultiEntityCoreCfg.show_full_config(self)

    # --------------------------------------------------------------------------------------------------
    def show_server_config_labels(self):
        MultiEntityCoreCfg.show_available_item_labels(self)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

