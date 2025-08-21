import { ISettingRegistry } from '@jupyterlab/settingregistry/lib';
import { WebSocketHandler } from './webSocketHandler';

// this function subscribes to changes to Q settings and passes changes to the LSP server in real-time.
export const observeSettingsChanges = async ({
  socket,
  settingRegistry,
  pluginId
}: {
  socket: WebSocketHandler;
  settingRegistry: ISettingRegistry | null;
  pluginId: string;
}) => {
  settingRegistry?.load(pluginId).then(settings => {
    settings?.changed.connect(() => {
      socket.sendNotification({
        command: 'workspace/didChangeConfiguration',
        params: {}
      });
    });
  });
};
