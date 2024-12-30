import * as vscode from 'vscode';
import axios from 'axios';

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(vscode.commands.registerCommand('extension.openChat', () => {
    ChatPanel.createOrShow(context.extensionUri);
  }));
}

class ChatPanel {
  public static currentPanel: ChatPanel | undefined;
  private readonly _panel: vscode.WebviewPanel;
  private readonly _extensionUri: vscode.Uri;
  private chatHistory: string[] = [];  // Создаем массив для хранения истории чата

  public static createOrShow(extensionUri: vscode.Uri) {
    const column = vscode.window.activeTextEditor ? vscode.window.activeTextEditor.viewColumn : undefined;

    if (ChatPanel.currentPanel) {
      ChatPanel.currentPanel._panel.reveal(column);
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      'chatView',
      'Chat',
      column || vscode.ViewColumn.One,
      {
        enableScripts: true,
      }
    );

    ChatPanel.currentPanel = new ChatPanel(panel, extensionUri);

    ChatPanel.currentPanel.initializeChat();
  }

  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
    this._panel = panel;
    this._extensionUri = extensionUri;
    this._panel.webview.html = this._getHtmlForWebview();

    this._panel.webview.onDidReceiveMessage(
      async message => {
        switch (message.command) {
          case 'sendMessage':
            // this.chatHistory.push(`You: ${message.text}`);
            const response = await this.sendMessageToServer(message.text);
            this.chatHistory.push(`Server: ${response}`);
            this._updateChat();
            return;
        }
      },
      undefined,
    //   context.subscriptions
    );

    this._panel.onDidDispose(() => {
      ChatPanel.currentPanel = undefined;
    });
  }

  public async initializeChat() {
    try {
      const response = await axios.post('http://localhost:3000/init', {});
    //   this.chatHistory.push(`Server: ${response.data}`);
      this._updateChat();
    } catch (error) {
      console.error('Failed to initialize chat:', error);
      this.chatHistory.push(`Error: Unable to initialize chat.`);
      this._updateChat();
    }
  }

  private async sendMessageToServer(text: string): Promise<string> {
    this.chatHistory.push(`You: ${text}`);

    try {
      const response = await axios.post('http://localhost:3000/message', { message: text });
      return response.data.response;
    } catch (error) {
      console.error('Failed to send message:', error);
      return 'Error: Unable to send message.';
    }
  }

  private _updateChat() {
    // Отправляем обновленную историю чата на страницу веб-просмотра
    this._panel.webview.postMessage({ command: 'updateChat', history: this.chatHistory });
  }

  private _getHtmlForWebview() {
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Chat</title>
    </head>
    <body>
      <div>
        <textarea id="input" cols="30" rows="2" placeholder="Type a message..."></textarea>
        <button onclick="sendMessage()">Send</button>
      </div>
      <div id="messages"></div>

      <script>
        const vscode = acquireVsCodeApi();
        function sendMessage() {
          const inputBox = document.getElementById('input');
          const text = inputBox.value;
          if (text) {
            vscode.postMessage({ command: 'sendMessage', text: text });
            inputBox.value = '';
          }
        }
        window.addEventListener('message', event => {
          const message = event.data;
          const messageBox = document.getElementById('messages');
          if (message.command === 'updateChat') {
            messageBox.innerHTML ='';
            message.history.forEach((msg) => {
              const div = document.createElement('div');
              div.textContent = msg;
              messageBox.appendChild(div);
            });
          }
        });
      </script>
    </body>
    </html>`;
  }
}
