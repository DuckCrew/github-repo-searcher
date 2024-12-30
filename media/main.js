const vscode = acquireVsCodeApi();

   function sendMessage() {
       const input = document.getElementById('messageInput');
       const message = input.value;
       input.value = ''; // Очистка поля ввода

       vscode.postMessage({
           command: 'sendMessage',
           text: message
       });
   }

   window.addEventListener('message', event => {
       const message = event.data; 

       switch (message.command) {
           case 'receiveMessage':
               const chatContainer = document.getElementById('chatContainer');
               const div = document.createElement('div');
               div.textContent = message.text;
               chatContainer.appendChild(div);
               break;
       }
   });
