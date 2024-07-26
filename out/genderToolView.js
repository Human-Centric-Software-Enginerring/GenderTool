"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GenderToolViewProvider = void 0;
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
            localResourceRoots: [this._extensionUri]
        };
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
    }
    _getHtmlForWebview(webview) {
        return `<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Gender Tool</title>
    </head>
    <body>
      <h1>Hello from Gender Tool!</h1>
    </body>
    </html>`;
    }
}
exports.GenderToolViewProvider = GenderToolViewProvider;
//# sourceMappingURL=genderToolView.js.map