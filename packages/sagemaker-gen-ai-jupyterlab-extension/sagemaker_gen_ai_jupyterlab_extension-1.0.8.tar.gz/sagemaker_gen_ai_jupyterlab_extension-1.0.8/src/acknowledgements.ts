type AcknowledgementCommand = 'chatPromptOptionAcknowledged' | 'disclaimerAcknowledged';

/**
 * @description stores user acknowledgements in local browser storage. 
 * disclaimerAcknowledged: if true, user has acknowledged the Amazon Q Developer use disclaimer.
 * located at the bottom of the chat experience
 * chatPromptOptionAcknowledged: if true, user has closed the agentic chat intro
 * alert. 
 */
export const storeAcknowledgements = (command: AcknowledgementCommand) => {
    if(command === 'disclaimerAcknowledged'){
        localStorage.setItem('disclaimerAcknowledged', 'true');
    }

    if(command === 'chatPromptOptionAcknowledged'){
        localStorage.setItem('chatPromptOptionAcknowledged', 'true');
    }
}