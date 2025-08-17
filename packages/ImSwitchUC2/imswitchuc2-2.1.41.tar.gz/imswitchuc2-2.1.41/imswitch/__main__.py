import importlib
import traceback
import logging
import argparse
import os

import imswitch
def main(is_headless:bool=None, default_config:str=None, http_port:int=None, socket_port:int=None, ssl:bool=None, config_folder:str=None,
         data_folder: str=None, scan_ext_data_folder:bool=None, ext_drive_mount:str=None):
    '''
    is_headless: bool => start with or without qt
    default_config: str => path to the config file
    http_port: int => port number (default: 8001)
    socket_port: int => port number (default: 8002)
    ssl: bool => use ssl (default: True)
    config_folder: str => path to the config folder (default: None, pointing to Documents/ImSwitch)
    data_folder: str => path to the data folder (default: None, pointing to Documents/ImSwitchConfig)
    scan_ext_data_folder: bool => if True, we will scan the ext_drive_mount for usb drives and use this for data storage
    ext_drive_mount: str => path to the external drive mount point (default: None, optionally pointing to e.g. /Volumes or /media)



    To start imswitch in headless using the arguments, you can call the main file with the following arguments:
        python main.py --headless or
        python -m imswitch --headless 1 --config-file example_virtual_microscope.json --config-folder /Users/bene/Downloads --scan-ext-drive-mount true --ext-data-folder ~/Downloads --ext-drive-mount /Volumes
    '''
    try:
        try: # Google Colab does not support argparse
            parser = argparse.ArgumentParser(description='Process some integers.')

            # specify if run in headless mode
            parser.add_argument('--headless', dest='headless', default=False, action='store_true',
                                help='run in headless mode')

            # specify config file name - None for default
            parser.add_argument('--config-file', dest='config_file', type=str, default=None,
                                help='specify run with config file')

            # specify http port
            parser.add_argument('--http-port', dest='http_port', type=int, default=8001,
                                help='specify http port')

            # specify socket port
            parser.add_argument('--socket-port', dest='socket_port', type=int, default=8002,
                                help='specify socket port')
            # specify ssl
            parser.add_argument('--no-ssl', dest='ssl', default=True, action='store_false',
                                help='specify ssl')

            # specify the config folder (e.g. if running from a different location / container)
            parser.add_argument('--config-folder', dest='config_folder', type=str, default=None,
                                help='specify config folder')

            parser.add_argument('--ext-data-folder', dest='data_folder', type=str, default=None,
                                help='point to a folder to store the data. This is the default location for the data folder. If not specified, the default location will be used.')

            parser.add_argument('--scan-ext-drive-mount', dest='scan_ext_data_folder', default=False, action='store_true',
                                help='scan the external mount (linux only) if we have a USB drive to save to')

            parser.add_argument('--ext-drive-mount', dest='ext_drive_mount', type=str, default=None,
                                help='specify the external drive mount point (e.g. /Volumes or /media)')



            args = parser.parse_args()

            imswitch.IS_HEADLESS = args.headless            # if True, no QT will be loaded
            imswitch.__httpport__ = args.http_port          # e.g. 8001
            imswitch.__ssl__ = args.ssl                     # if True, ssl will be used (e.g. https)
            imswitch.__socketport__ = args.socket_port      # e.g. 8002

            if type(args.config_file)==str and args.config_file.find("json")>=0:  # e.g. example_virtual_microscope.json
                imswitch.DEFAULT_SETUP_FILE = args.config_file
            if args.config_folder and os.path.isdir(args.config_folder):
                imswitch.DEFAULT_CONFIG_PATH = args.config_folder # e.g. /Users/USER/ in case an alternative path is used
            if args.data_folder and os.path.isdir(args.data_folder):
                imswitch.DEFAULT_DATA_PATH = args.data_folder # e.g. /Users/USER/ in case an alternative path is used
            if args.scan_ext_data_folder:
                imswitch.SCAN_EXT_DATA_FOLDER = args.scan_ext_data_folder
            if args.ext_drive_mount:
                imswitch.EXT_DRIVE_MOUNT = args.ext_drive_mount

        except Exception as e:
            print(e)
            pass
        # override settings if provided as argument
        if is_headless is not None:
            print("We use the user-provided headless flag: " + str(is_headless))
            imswitch.IS_HEADLESS = is_headless
        if default_config is not None:
            print("We use the user-provided configuration file: " + default_config)
            imswitch.DEFAULT_SETUP_FILE = default_config
        if http_port is not None:
            print("We use the user-provided http port: " + str(http_port))
            imswitch.__httpport__ = http_port
        if socket_port is not None:
            print("We use the user-provided socket port: " + str(socket_port))
            imswitch.__socketport__ = socket_port
        if ssl is not None:
            print("We use the user-provided ssl: " + str(ssl))
            imswitch.__ssl__ = ssl
        if config_folder is not None:
            print("We use the user-provided configuration path: " + config_folder)
            imswitch.DEFAULT_CONFIG_PATH = config_folder
        if data_folder is not None:
            print("We use the user-provided data path: " + data_folder)
            imswitch.DEFAULT_DATA_PATH = data_folder
        if scan_ext_data_folder is not None:
            print("We use the user-provided scan_ext_data_folder: " + str(scan_ext_data_folder))
            imswitch.SCAN_EXT_DATA_FOLDER = scan_ext_data_folder
        if ext_drive_mount is not None:
            print("We use the user-provided ext_drive_mount: " + str(ext_drive_mount))
            imswitch.EXT_DRIVE_MOUNT = ext_drive_mount

        # FIXME: !!!! This is because the headless flag is loaded after commandline input
        from imswitch.imcommon import prepareApp, launchApp
        from imswitch.imcommon.controller import ModuleCommunicationChannel, MultiModuleWindowController
        from imswitch.imcommon.model import modulesconfigtools, pythontools, initLogger

        logger = initLogger('main')
        logger.info(f'Starting ImSwitch {imswitch.__version__}')
        logger.info(f'Headless mode: {imswitch.IS_HEADLESS}')
        logger.info(f'Config file: {imswitch.DEFAULT_SETUP_FILE}')
        logger.info(f'Config folder: {imswitch.DEFAULT_CONFIG_PATH}')
        logger.info(f'Data folder: {imswitch.DEFAULT_DATA_PATH}')

        # TODO: check if port is already in use
        
        if imswitch.IS_HEADLESS:
            app = None
        else:
            app = prepareApp()
        enabledModuleIds = modulesconfigtools.getEnabledModuleIds()

        if 'imscripting' in enabledModuleIds:
            if imswitch.IS_HEADLESS:
                enabledModuleIds.remove('imscripting')
            else:
                # Ensure that imscripting is added last
                enabledModuleIds.append(enabledModuleIds.pop(enabledModuleIds.index('imscripting')))

        if 'imnotebook' in enabledModuleIds:
            # Ensure that imnotebook is added last
            try:
                enabledModuleIds.append(enabledModuleIds.pop(enabledModuleIds.index('imnotebook')))
            except ImportError:
                logger.error('QtWebEngineWidgets not found, disabling imnotebook')
                enabledModuleIds.remove('imnotebook')

        modulePkgs = [importlib.import_module(pythontools.joinModulePath('imswitch', moduleId))
                    for moduleId in enabledModuleIds]

        # connect the different controllers through the communication channel
        moduleCommChannel = ModuleCommunicationChannel()

        # only create the GUI if necessary
        if not imswitch.IS_HEADLESS:
            from imswitch.imcommon.view import MultiModuleWindow, ModuleLoadErrorView
            multiModuleWindow = MultiModuleWindow('ImSwitch')
            multiModuleWindowController = MultiModuleWindowController.create(
                multiModuleWindow, moduleCommChannel
            )
            multiModuleWindow.show(showLoadingScreen=True)
            app.processEvents()  # Draw window before continuing
        else:
            multiModuleWindow = None
            multiModuleWindowController = None

        # Register modules
        for modulePkg in modulePkgs:
            moduleCommChannel.register(modulePkg)

        # Load modules
        moduleMainControllers = dict()

        for i, modulePkg in enumerate(modulePkgs):
            moduleId = modulePkg.__name__
            moduleId = moduleId[moduleId.rindex('.') + 1:]  # E.g. "imswitch.imcontrol" -> "imcontrol"

            # The displayed module name will be the module's __title__, or alternatively its ID if
            # __title__ is not set
            moduleName = modulePkg.__title__ if hasattr(modulePkg, '__title__') else moduleId
            # we load all the controllers, managers and widgets here:
            try:
                view, controller = modulePkg.getMainViewAndController(
                    moduleCommChannel=moduleCommChannel,
                    multiModuleWindowController=multiModuleWindowController,
                    moduleMainControllers=moduleMainControllers
                )
                logger.info(f'initialize module {moduleId}')

            except Exception as e:
                logger.error(f'Failed to initialize module {moduleId}')
                logger.error(e)
                logger.error(traceback.format_exc())
                moduleCommChannel.unregister(modulePkg)
                if not imswitch.IS_HEADLESS:
                    from imswitch.imcommon.view import ModuleLoadErrorView
                    multiModuleWindow.addModule(moduleId, moduleName, ModuleLoadErrorView(e))
            else:
                # Add module to window
                if not imswitch.IS_HEADLESS:
                    multiModuleWindow.addModule(moduleId, moduleName, view)
                moduleMainControllers[moduleId] = controller

                # in case of the imnotebook, spread the notebook url
                if moduleId == 'imnotebook':
                    imswitch.jupyternotebookurl = controller.webaddr

                # Update loading progress
                if not imswitch.IS_HEADLESS:
                    multiModuleWindow.updateLoadingProgress(i / len(modulePkgs))
                    app.processEvents()  # Draw window before continuing
        logger.info(f'init done')
        launchApp(app, multiModuleWindow, moduleMainControllers.values())
    except Exception as e:
        logging.error(traceback.format_exc())


if __name__ == '__main__':
    main()

# Copyright (C) 2020-2024 ImSwitch developers
# This file is part of ImSwitch.
#
# ImSwitch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ImSwitch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
