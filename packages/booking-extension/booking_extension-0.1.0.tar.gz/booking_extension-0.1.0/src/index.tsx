import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { IStatusBar } from '@jupyterlab/statusbar';
// import { IThemeManager } from '@jupyterlab/apputils';

import { diskWidget } from './components/DiskSpaceWidget';
import { showDiskNotifications } from './utils/showDiskNotifications';

/**
 * Initialization data for the booking_extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'booking_extension:plugin',
  description: '',
  autoStart: true,
  optional: [ISettingRegistry, IStatusBar],
  activate: (
    app: JupyterFrontEnd,
    settingRegistry: ISettingRegistry | null,
    statusBar: IStatusBar | null
  ) => {
    console.log('JupyterLab extension booking_extension is activated!');

    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log('booking_extension settings loaded:', settings.composite);
        })
        .catch(reason => {
          console.error(
            'Failed to load settings for booking_extension.',
            reason
          );
        });
    }

    if (statusBar != null) {
      statusBar.registerStatusItem(diskWidget.id, {
        item: diskWidget,
        align: 'left',
        rank: 2
      });
    }

    showDiskNotifications();
  }
};

export default plugin;
