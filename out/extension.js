"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const child_process_1 = require("child_process");
const ws_1 = __importDefault(require("ws"));
function activate(context) {
    const provider = new GenderToolViewProvider(context.extensionUri);
    context.subscriptions.push(vscode.window.registerWebviewViewProvider(GenderToolViewProvider.viewType, provider));
    // Run the Python scripts when the extension is activated
    provider.runPythonScripts(); // Updated to use the class method
}
class GenderToolViewProvider {
    _extensionUri;
    static viewType = 'genderToolView';
    _view;
    ws; // WebSocket instance
    constructor(_extensionUri) {
        this._extensionUri = _extensionUri;
    }
    resolveWebviewView(webviewView, context, _token) {
        this._view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [
                this._extensionUri
            ]
        };
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        webviewView.webview.onDidReceiveMessage(message => {
            switch (message.command) {
                case 'openLink':
                    vscode.env.openExternal(vscode.Uri.parse(message.link));
                    return;
                case 'runTest2':
                    console.log(`Received command to run client.py with session ID: ${message.sessionId}`);
                    this.runTest2Script(message.sessionId);
                    return;
                case 'updateData':
                    console.log('Line 53: Received updateData command:', message.users_data);
                    break;
                case 'endSession':
                    console.log('Received command to end session');
                    this.sendEndSessionMessageToServer();
                    break;
            }
        });
    }
    sendEndSessionMessageToServer() {
        if (this.ws && this.ws.readyState === ws_1.default.OPEN) {
            vscode.window.showInformationMessage(`Ending Session`);
            this.ws.send('Endsession');
            console.log('Sent "Endsession" message to the server');
        }
        else {
            console.error('WebSocket is not open. Cannot send "Endsession" message.');
        }
    }
    runTest2Script(sessionId) {
        const scriptPath = 'D:/HCI_Research/GenderTool/Tool/client/client.py';
        const command = `python "${scriptPath}" "${sessionId}"`;
        if (this._view) {
            this._view.webview.postMessage({ command: 'showProgress' });
        }
        (0, child_process_1.exec)(command, (error, stdout, stderr) => {
            if (error) {
                vscode.window.showErrorMessage(`Failed to run client.py: ${error.message}`);
                return;
            }
            if (stderr) {
                console.warn(`Warnings from client.py: ${stderr}`);
            }
            console.log(`Output from client.py: ${stdout}`);
        });
    }
    refreshWebview() {
        if (this._view && this._view.webview) {
            this._view.webview.html = this._getHtmlForWebview(this._view.webview);
        }
    }
    _getHtmlForWebview(webview) {
        const nonce = getNonce();
        const stylesUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'styles.css'));
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'script.js'));
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src vscode-resource: https:; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}'; connect-src ws://localhost:8765;">
            <title>Gender Tool</title>
            <link href="${stylesUri}" rel="stylesheet">
        </head>
        <body>
            <div class="session-id-container">
                <label for="sessionIdInput" class="session-id-label">Enter Session ID:</label>
                <input type="text" id="sessionIdInput" class="session-id-input" placeholder="Session ID">
                <button id="runTest2Btn" class="submit-button">Submit</button>
            </div>
            <div id="progressMessage" class="progress-message hidden">
                <div class="loading-icon"></div>
                <p>Session started, reports will be displayed soon!</p>
            </div>
            <div id="userStats" class="user-stats hidden">
                <h1>Your Stats</h1>
                <p> You worked primarily as <span id="user1PrimaryContribution"></span></p>
                <p>Communication Style: <span id="user1CommunicationStyle"></span></p>
                <p>Self Efficacy: <span id="user1SelfEfficacy"></span></p>
                <p>Interruptions: <span id="user1Interruptions"></span></p>
                <p>Leadership Style: <span id="user1Leasdership"></span></p>
                <p>Rapport: <span id="user1Rapport"></span></p>
                <h1>Partner's Stats</h1>
                <p>Primary Contribution: <span id="user2PrimaryContribution"></span></p>
                <p>Communication Style: <span id="user2CommunicationStyle"></span></p>
                <p>Self Efficacy: <span id="user2SelfEfficacy"></span></p>
                <p>Rapport: <span id="user2Rapport"></span></p>
                <h1>Session Stats</h1>
                <p>Total Lines of Code: <span id="sessionLOC"></span></p>
                <button id="endSession" class="end-button">End Session</button>
            </div>
            <div id="finalStats" class="final-stats hidden">
                <h1>Final Stats</h1>
                <h1>Your Stats</h1>
                <p> You worked primarily as <span id="user1FinalRole"></span></p>
                <p>Communication Style: <span id="user1FinalComm"></span></p>
                <p>Self Efficacy: <span id="user1FinalEfficacy"></span></p>
                <p>Interruptions: <span id="user1FinalInterr"></span></p>
                <p>Leadership Style: <span id="user1FinalLeadership"></span></p>
                <p>Rapport: <span id="user1FinalRapport"></span></p>
                <h1>Partner's Stats</h1>
                <p>Primary Contribution: <span id="user2FinalRole"></span></p>
                <p>Communication Style: <span id="user2FinalComm"></span></p>
                <p>Self Efficacy: <span id="user2FinalEfficacy"></span></p>
                <p>Rapport: <span id="user2FinalRapport"></span></p>
                <h1>Session Stats</h1>
                <p>Total Lines of Code: <span id="sessionFinalLOC"></span></p>
            </div>
            <script nonce="${nonce}" src="${scriptUri}"></script>
        </body>
        </html>`;
    }
    runPythonScripts() {
        // Start the WebSocket server
        (0, child_process_1.exec)('python D:/HCI_Research/GenderTool/Tool/server/ws_server.py', (error, stdout, stderr) => {
            if (error) {
                console.error(`Error executing ws_server.py: ${error.message}`);
                return;
            }
            if (stderr) {
                console.error(`Error in ws_server.py: ${stderr}`);
            }
            console.log(`Output from ws_server.py: ${stdout}`);
        });
        // Delay to ensure WebSocket server is up and running
        setTimeout(() => {
            // Establish WebSocket connection to receive data from server
            try {
                this.ws = new ws_1.default('ws://localhost:8000/ws');
                //this.ws = new WebSocket('ws://localhost:8765');
                this.ws.onopen = () => {
                    console.log('WebSocket connection established successfully with frontend.');
                    this.ws?.send(JSON.stringify({
                        type: "text",
                        message: "Hello Server"
                    }));
                    vscode.window.showInformationMessage('WebSocket connection established successfully!');
                };
                this.ws.onmessage = (event) => {
                    console.log('Received data from server:', event.data.toString());
                    vscode.window.showInformationMessage(`Received from server: ${event.data}`);
                    try {
                        const parsedData = JSON.parse(event.data.toString());
                        console.log('Parsed Data:', parsedData);
                        if (parsedData.status === 'intervalData' && this._view) {
                            this._view.webview.postMessage({ command: 'updateData', users_data: parsedData.interval_data });
                        }
                        // Check if the message contains final data
                        if (parsedData.status === 'finalData' && this._view) {
                            console.log('final data received');
                            this._view.webview.postMessage({ command: 'finalStats', final_data: parsedData.final_data });
                        }
                    }
                    catch (e) {
                        console.error('Error parsing message:', e);
                    }
                };
                this.ws.onerror = (error) => {
                    console.error('Frontend WebSocket Error:', error.message || 'Unknown error');
                    vscode.window.showErrorMessage('Frontend WebSocket Connection Error: ' + error.message);
                };
                this.ws.onclose = () => {
                    console.log('WebSocket connection closed.');
                };
            }
            catch (error) {
                console.error('Error initializing WebSocket:', error);
            }
        }, 2000); // Delay for 2 seconds
    }
}
function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
function deactivate() { }
//# sourceMappingURL=extension.js.map