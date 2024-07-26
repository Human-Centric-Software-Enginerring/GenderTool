import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  const provider = new GenderToolViewProvider(context.extensionUri);

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(GenderToolViewProvider.viewType, provider)
  );
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
  }

  private _getHtmlForWebview(webview: vscode.Webview) {
    return `<!DOCTYPE html>
      <html lang="en">
      <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Gender Tool</title>
      </head>
      <body>
          <h1>Gender Tool</h1>
          <p>This is the Gender Tool sidebar.</p>
      </body>
      </html>`;
  }
}

export function deactivate() {}