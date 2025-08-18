#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- Media Config
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

from quickcolor.color_def import color

from corecfg.multi_entity import MultiEntityCoreCfg

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

class MediaCategory():
    movie = f'{color.CYELLOW2}movie{color.CEND}'
    show = f'{color.CBLUE2}show{color.CEND}'
    special = f'{color.CCYAN2}specials{color.CEND}'
    standup = f'{color.CRED2}standup{color.CEND}'
    sport = f'{color.CGREEN}sports{color.CEND}'
    concert = f'{color.CVIOLET2}concert{color.CEND}'

mediaCategoryLkup = {
        'movie' : MediaCategory.movie,
        'show' : MediaCategory.show,
        'special' : MediaCategory.special,
        'standup' : MediaCategory.standup,
        'sport' : MediaCategory.sport,
        'concert' : MediaCategory.concert,
        }

colorTypeLkup = {
        'red' : color.CRED,
        'bold red' : color.CRED2,
        'yellow' : color.CRED,
        'bold yellow' : color.CYELLOW2,
        'blue' : color.CBLUE,
        'bold blue' : color.CBLUE2,
        'green' : color.CGREEN,
        'bold green' : color.CGREEN2,
        'cyan' : color.CCYAN,
        'bold cyan' : color.CCYAN2,
        'violet' : color.CVIOLET,
        'bold violet' : color.CVIOLET2,
        'white' : color.CWHITE,
        'bold white' : color.CWHITE2,
        }
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

class MediaConfig(MultiEntityCoreCfg):

    # --------------------------------------------------------------------------------------------------
    def __init__(self, verbose: bool = False, debug: bool = False):
        self._verbose = verbose
        self._debug = debug
        if debug:
            print(f'{color.CCYAN2}Initializing {type(self).__name__}! {color.CWHITE2}id: {str(id(self))}{color.CEND}')

        super(MediaConfig, self).__init__(cfgFileName = 'media_config.json', debug = debug)

        cfgMetadataInit = { 'label' : 'Media Cfg', 'maxLabelLen' : 30 }
        categoryMetadataInit = {
                'category' : { 'color' : color.CBLUE2, 'maxLen' : 20 },
                'color' : { 'color' : color.CWHITE, 'maxLen' : 20 },
                }
        if cfgMetadataInit != self.get_cfg_metadata() or categoryMetadataInit != self.get_category_metadata():
            if debug:
                print(f'Initializing {type(self).__name__} metadata for cfg and categories!')
            self.initialize_metadata(cfgMetadata=cfgMetadataInit, categoryMetadata=categoryMetadataInit)

    # --------------------------------------------------------------------------------------------------
    def register_media_category(self, pathLabel: str, category: str, dirColor: str):
        if category not in mediaCategoryLkup.keys():
            raise ValueError(f"Media category ({category}) is not recognized! Try one of these: {mediaCategoryLkup.keys()}")

        if dirColor not in colorTypeLkup.keys():
            raise ValueError(f"Path color ({dirColor}) is not recognized! Try one of these: {colorTypeLkup.keys()}")

        tupleList = {}
        tupleList['category'] = category
        tupleList['color'] = dirColor

        '''
        allItems = self.get_all_configured_items()
        if tupleList in allItems.values():
            print(f'{color.CRED2}Error: {color.CWHITE}Tuple {color.CBLUE2}' + \
                    f'{str(tupleList.values())}{color.CWHITE} is already configured!{color.CEND}')
            return
        '''

        self.update_item(itemLabel = pathLabel, newTuple = tupleList)

    # --------------------------------------------------------------------------------------------------
    def unregister_media_category(self, pathLabel: str):
        allItems = self.get_all_configured_items()
        if pathLabel not in allItems.keys():
            print(f'{color.CRED2}Error: {color.CWHITE}Media cfg label ' + \
                    f'{color.CBLUE2}{pathLabel}{color.CWHITE}' + \
                    f' is not registered in media config!{color.CEND}')
            return

        print(f'{color.CVIOLET2}\n   -- removing Media cfg label {color.CYELLOW}{pathLabel}{color.CVIOLET2}' + \
                f' containing \n      {color.CWHITE2}{str(allItems[pathLabel])}{color.CEND}')

        self.remove_item(itemLabel = pathLabel)

    # --------------------------------------------------------------------------------------------------
    def get_configured_entries(self):
        allItems = self.get_all_configured_items()
        return allItems.keys()

    # --------------------------------------------------------------------------------------------------
    def get_color_label(self, pathLabel: str):
        allItems = self.get_all_configured_items()
        if pathLabel in allItems.keys():
            itemData = self.get_cfg_data_for_item_label(itemLabel = pathLabel)
        else:
            itemData = None
        if not itemData:
            return None, None
        return itemData['color'], colorTypeLkup[itemData['color']]

    # --------------------------------------------------------------------------------------------------
    def show_media_config(self):
        MultiEntityCoreCfg.show_full_config(self)

    # --------------------------------------------------------------------------------------------------
    def show_media_config_labels(self):
        MultiEntityCoreCfg.show_available_item_labels(self)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

