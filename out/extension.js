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
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const child_process_1 = require("child_process");
function activate(context) {
    const provider = new GenderToolViewProvider(context.extensionUri);
    context.subscriptions.push(vscode.window.registerWebviewViewProvider(GenderToolViewProvider.viewType, provider));
    // Run the Python scripts when the extension is activated
    runPythonScripts();
}
class GenderToolViewProvider {
    _extensionUri;
    static viewType = 'genderToolView';
    _view;
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
            }
        });
    }
    runTest2Script(sessionId) {
        const scriptPath = 'D:/HCI_Research/GenderTool/Tool/client/client.py';
        const command = `python "${scriptPath}" "${sessionId}"`;
        //change webview once it is submitted
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
        });
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
        <meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src vscode-resource: https:; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
        <title>Gender Tool</title>
        <link href="${stylesUri}" rel="stylesheet">
    </head>
    <body>

        <!-- New section for entering session ID -->
        <div class="session-id-container">
    <label for="sessionIdInput" class="session-id-label">Enter Session ID:</label>
    <input type="text" id="sessionIdInput" class="session-id-input" placeholder="Session ID">
    <button id="runTest2Btn" class="submit-button">Submit</button>
        </div>

        <!-- Progress message container, initially hidden -->
    <div id="progressMessage" class="progress-message hidden">
        <div  class="loading-icon"></div>
        <p>Session started, reports will be displayed soon!!.</p>
    </div>

     <!-- User Stats Display -->
    <div id="userStats" class="user-stats hidden">
        <h1>Your Stats</h1>
        <p>Primary Contribution: <span id="user1PrimaryContribution"></span></p>
        <p>Communication Style: <span id="user1CommunicationStyle"></span></p>
        <p>Self Efficacy: <span id="user1SelfEfficacy"></span></p>
        <p>Interruptions: <span id="user1Interruptions"></span></p>

        <h1>Partner's Stats</h1>
        <p>Primary Contribution: <span id="user2PrimaryContribution"></span></p>
        <p>Communication Style: <span id="user2CommunicationStyle"></span></p>
        <p>Self Efficacy: <span id="user2SelfEfficacy"></span></p>
    </div>

        <script nonce="${nonce}" src="${scriptUri}"></script>
    </body>
    </html>`;
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
function runPythonScripts() {
    (0, child_process_1.exec)('python D:/HCI_Research/GenderTool/Tool/server/ws_server.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing ws_server.py: ${error.message}`);
            return;
        }
        if (stderr) {
            console.error(`Stderr from ws_server.py: ${stderr}`);
            return;
        }
        console.log(`Output from ws_server.py: ${stdout}`);
    });
}
function deactivate() { }
//# sourceMappingURL=extension.js.map