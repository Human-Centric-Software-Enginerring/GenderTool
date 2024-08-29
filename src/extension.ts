// import * as vscode from 'vscode';
// import { exec } from 'child_process';

// export function activate(context: vscode.ExtensionContext) {
//   const provider = new GenderToolViewProvider(context.extensionUri);

//   context.subscriptions.push(
//     vscode.window.registerWebviewViewProvider(GenderToolViewProvider.viewType, provider)
//   );

//   // Run the Python scripts when the extension is activated
//   runPythonScripts();
// }

// class GenderToolViewProvider implements vscode.WebviewViewProvider {
//   public static readonly viewType = 'genderToolView';

//   private _view?: vscode.WebviewView;

//   constructor(
//     private readonly _extensionUri: vscode.Uri,
//   ) { }

//   public resolveWebviewView(
//     webviewView: vscode.WebviewView,
//     context: vscode.WebviewViewResolveContext,
//     _token: vscode.CancellationToken,
//   ) {
//     this._view = webviewView;

//     webviewView.webview.options = {
//       enableScripts: true,
//       localResourceRoots: [
//         this._extensionUri
//       ]
//     };

//     webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

//     webviewView.webview.onDidReceiveMessage(
//       message => {
//         switch (message.command) {
//           case 'openLink':
//             vscode.env.openExternal(vscode.Uri.parse(message.link));
//             return;
//         }
//       }
//     );
//   }

//   private _getHtmlForWebview(webview: vscode.Webview): string {
//     const nonce = getNonce();

//     const stylesUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'styles.css'));
//     const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'script.js'));

//     return `<!DOCTYPE html>
//     <html lang="en">
//     <head>
//         <meta charset="UTF-8">
//         <meta name="viewport" content="width=device-width, initial-scale=1.0">
//         <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource}; script-src 'nonce-${nonce}';">
//         <title>Gender Tool</title>
//         <link href="${stylesUri}" rel="stylesheet">
//     </head>
//     <body>
//         <h1>YOUR STATS</h1>
//         <hr>
//         <div class="stat-row">
//             <span class="arrow">→</span>
//             <span class="stat-label">Lines of Code</span>
//             <span class="stat-value" id="linesOfCode">0</span>
//         </div>
//         <div class="stat-row">
//             <span class="arrow">→</span>
//             <span class="stat-label">Primary Contribution</span>
//             <span class="info-icon" id="primaryContributionInfo">ⓘ</span>
//             <div class="toggle-container">
//                 <input id="primaryContributionToggle" type="checkbox" class="toggle-input">
//                 <label for="primaryContributionToggle" class="toggle-label">
//                     <span class="toggle-text left">DRIVER</span>
//                     <span class="toggle-text right">NAVIGATOR</span>
//                 </label>
//             </div>
//         </div>
//         <div class="stat-row">
//             <span class="arrow">→</span>
//             <span class="stat-label">Communication Style</span>
//             <span class="info-icon" id="communicationStyleInfo">ⓘ</span>
//             <div class="toggle-container">
//                 <input id="communicationStyleToggle" type="checkbox" class="toggle-input">
//                 <label for="communicationStyleToggle" class="toggle-label">
//                     <span class="toggle-text left">VERBAL</span>
//                     <span class="toggle-text right">NONVERBAL</span>
//                 </label>
//             </div>
//         </div>
//         <div class="stat-row">
//             <span class="arrow">→</span>
//             <span class="stat-label">Partner is trying to be</span>
//             <span class="info-icon" id="partnerTryingInfo">ⓘ</span>
//             <div class="toggle-container">
//                 <input id="partnerTryingToggle" type="checkbox" class="toggle-input">
//                 <label for="partnerTryingToggle" class="toggle-label">
//                     <span class="toggle-text left">FRIENDLY</span>
//                     <span class="toggle-text right">WORKING</span>
//                 </label>
//             </div>
//         </div>
//         <div class="stat-row">
//             <span class="arrow">→</span>
//             <span class="stat-label">Your Interruptions</span>
//             <span class="stat-value" id="interruptionCount">##</span>
//         </div>
//         <div id="popup" class="popup">
//             <div class="popup-content">
//                 <span class="close-btn">✕</span>
//                 <div class="popup-icon">💡</div>
//                 <p id="popupText"></p>
//                 <p class="why-link">Why?</p>
//                 <p class="click-info">Clicking on the above will open a browser link.</p>
//             </div>
//         </div>

//         <h1>PARTNER'S STATS</h1>
//         <hr>
//         <div class="stat-row">
//             <span class="arrow">→</span>
//             <span class="stat-label">Lines of Code</span>
//             <span class="stat-value" id="linesOfCode2">0</span>
//         </div>
//         <div class="stat-row">
//             <span class="arrow">→</span>
//             <span class="stat-label">Primary Contribution</span>
//             <span class="info-icon" id="primaryContributionInfo">ⓘ</span>
//             <div class="toggle-container">
//                 <input id="primaryContributionToggle2" type="checkbox" class="toggle-input">
//                 <label for="primaryContributionToggle2" class="toggle-label">
//                     <span class="toggle-text left">DRIVER</span>
//                     <span class="toggle-text right">NAVIGATOR</span>
//                 </label>
//             </div>
//         </div>
//         <div class="stat-row">
//             <span class="arrow">→</span>
//             <span class="stat-label">Communication Style</span>
//             <span class="info-icon" id="communicationStyleInfo">ⓘ</span>
//             <div class="toggle-container">
//                 <input id="communicationStyleToggle2" type="checkbox" class="toggle-input">
//                 <label for="communicationStyleToggle2" class="toggle-label">
//                     <span class="toggle-text left">VERBAL</span>
//                     <span class="toggle-text right">NONVERBAL</span>
//                 </label>
//             </div>
//         </div>
//         <script nonce="${nonce}" src="${scriptUri}"></script>
//     </body>
//     </html>`;
//   }
// }

// function getNonce() {
//     let text = '';
//     const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
//     for (let i = 0; i < 32; i++) {
//         text += possible.charAt(Math.floor(Math.random() * possible.length));
//     }
//     return text;
// }

// function runPythonScripts() {
//     exec('python D:/HCI_Research/GenderTool/Tool/recognition/test.py', (error, stdout, stderr) => {
//         if (error) {
//             console.error(`Error executing test1.py: ${error.message}`);
//             return;
//         }
//         if (stderr) {
//             console.error(`Stderr from test1.py: ${stderr}`);
//             return;
//         }
//         console.log(`Output from test1.py: ${stdout}`);
//     });
// }

// export function deactivate() {}

import * as vscode from 'vscode';
import { exec } from 'child_process';

export function activate(context: vscode.ExtensionContext) {
  const provider = new GenderToolViewProvider(context.extensionUri);

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(GenderToolViewProvider.viewType, provider)
  );

  // Run the Python scripts when the extension is activated
  runPythonScripts();
}

class GenderToolViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = 'genderToolView';

  private _view?: vscode.WebviewView;

  constructor(
    private readonly _extensionUri: vscode.Uri,
  ) { }

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken,
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [
        this._extensionUri
      ]
    };

    webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

    webviewView.webview.onDidReceiveMessage(
      message => {
        switch (message.command) {
          case 'openLink':
            vscode.env.openExternal(vscode.Uri.parse(message.link));
            return;
          case 'runTest2':
            console.log(`Received command to run test2.py with session ID: ${message.sessionId}`);
            this.runTest2Script(message.sessionId);
            return;
        }
      }
    );
  }

  private runTest2Script(sessionId: string) {
    const scriptPath = 'D:/HCI_Research/GenderTool/Tool/recognition/test2.py';
    const command = `python "${scriptPath}" "${sessionId}"`;
    //change webview once it is submitted
    if (this._view) {
        this._view.webview.postMessage({ command: 'showProgress' });
    }
    exec(command, (error, stdout, stderr) => {
        if (error) {
            vscode.window.showErrorMessage(`Failed to run test2.py: ${error.message}`);
            return;
        }
        if (stderr) {
            console.warn(`Warnings from test2.py: ${stderr}`);
        }
        vscode.window.showInformationMessage(`test2.py output: ${stdout}`);
        // notify the webview when the process is complete
        if (this._view) {
            this._view.webview.postMessage({ command: 'sessionCompleted' });
        }
    });
  }

  private _getHtmlForWebview(webview: vscode.Webview): string {
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
    exec('python D:/HCI_Research/GenderTool/Tool/recognition/test.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing test1.py: ${error.message}`);
            return;
        }
        if (stderr) {
            console.error(`Stderr from test1.py: ${stderr}`);
            return;
        }
        console.log(`Output from test1.py: ${stdout}`);
    });
}

export function deactivate() {}

