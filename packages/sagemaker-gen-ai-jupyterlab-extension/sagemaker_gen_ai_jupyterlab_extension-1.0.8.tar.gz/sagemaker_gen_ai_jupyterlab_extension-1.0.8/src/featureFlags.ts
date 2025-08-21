import { postToWebView } from './webview';

export const setChatFeatureFlags = (featureFlags: string[]) => {
  const featureFlagParams = featureFlags.reduce(
    (acc, flag) => {
      acc[flag] = true;
      return acc;
    },
    {} as Record<string, boolean>
  );

  postToWebView({
    command: 'chatOptions',
    params: featureFlagParams
  });
};
