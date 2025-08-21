import { URLExt } from "@jupyterlab/coreutils";
import { FLARE_IFRAME_ID } from "../constants";
import { ServerConnection } from "@jupyterlab/services";
import { Widget } from "@lumino/widgets";

export class FlareWidget extends Widget {
  constructor() {
    super();

    console.log('Creating Flare Widget');
    this.addClass('jp-FlareWidget');
    this.node.style.height = '100%';
    this.node.style.overflow = 'hidden';

    // Create container for the iframe
    const container = document.createElement('div');
    container.id = 'jp-FlareContainer';
    container.style.width = '100%';
    container.style.height = '100%';
    this.node.appendChild(container);
  }

  onAfterAttach() {
    console.log('Flare Widget attached');
    this.loadContent();
  }

  async loadContent() {
    const container = document.getElementById('jp-FlareContainer');
    if (!container) return;

    try {
      // Create iframe to load test-client.html
      const iframe = document.createElement('iframe');
      iframe.setAttribute(
        'sandbox',
        'allow-scripts allow-same-origin allow-forms allow-popups'
      );

      const settings = ServerConnection.makeSettings();
      const baseUrl = settings.baseUrl;
      iframe.src = URLExt.join(
        baseUrl,
        'sagemaker_gen_ai_jupyterlab_extension',
        'static',
        'client.html'
      );
      iframe.style.width = '100%';
      iframe.style.height = '100%';
      iframe.style.border = 'none';
      iframe.referrerPolicy = 'no-referrer';
      iframe.id = FLARE_IFRAME_ID;

      // Clear container and add iframe
      container.innerHTML = '';
      container.appendChild(iframe);
    } catch (error) {
      container.innerHTML = `<h2>Error Loading Amazon Q Chat</h2><p>${error}</p>`;
    }
  }
}