import { JupyterFrontEnd, LabShell } from "@jupyterlab/application";
import { TOGGLE_AI_CHAT_MESSAGE } from "../constants";
import wcmatch from 'wildcard-match';
import { Panel } from "@lumino/widgets";


export class IngressPointService {
    constructor(private app: JupyterFrontEnd, private chatPanel: Panel) {}

    public async initialize(){
        window.addEventListener('message', this.messageListener);
    }

    private messageListener = async (event: MessageEvent): Promise<void> => {
        if(!this.isMessageOriginValid(event)) return;

        /**
         * When a Q toggle event is passed into the iframe from the parent,
         * this toggles visibility of the Q chat window.
         */
        if (event.data === TOGGLE_AI_CHAT_MESSAGE) {
            this.toggleQChat(this.app, this.chatPanel);
            return;
        }
    }

    private isMessageOriginValid(event: MessageEvent): boolean {
        const allowedDomainPatterns = [
            'https://**.v2.*.beta.app.*.aws.dev',
            'https://**.ui.*.aws.dev',
            'https://**.v2.*-gamma.*.on.aws',
            'https://**.datazone.*.on.aws',
            'https://**.sagemaker.*.on.aws',
            'https://**.sagemaker-gamma.*.on.aws',
        ];

        return allowedDomainPatterns.some((pattern) => wcmatch(pattern)(event.origin));
    }

    private toggleQChat(app: JupyterFrontEnd, chatPanel: Panel): void {
        const chatPanelId = chatPanel.id;

        if(!chatPanelId){
            throw new Error("Chat widget not found.")
        }
        if (app.shell instanceof LabShell) {
        const leftWidgets = Array.from(app.shell.widgets('left'));
        const rightWidgets = Array.from(app.shell.widgets('right'));
        // support finding widgets on left or right panel
        const widgets = [...leftWidgets, ...rightWidgets];
        const chatWidget = widgets.find((widget) => widget.id === chatPanelId);

        if (chatWidget) {
            if (chatWidget.isHidden) {
            app.shell.activateById(chatPanelId);
            } else {
            if (rightWidgets.find((widget) => widget.id === chatPanelId)) {
                app.shell.collapseRight();
            } else {
                app.shell.collapseLeft();
            }
            }
        }
        }
    }
}