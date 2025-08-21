// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import * as path from "path";
import * as cp from "child_process";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind,
} from "vscode-languageclient/node";

let client: LanguageClient;

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
  // Use the console to output diagnostic information (console.log) and errors (console.error)
  // This line of code will only be executed once when your extension is activated
  console.log('Congratulationsx, your extension "gpython" is now active!');
  const pythonPath =
    vscode.workspace.getConfiguration("python").get<string>("pythonPath") ||
    "/Users/matiastoro/Documents/U/GPython/vsc_plugin/gpython/server/venv/bin/python3";

  let serverModule = context.asAbsolutePath(
    path.join("server", "my_language_server.py")
  );

  let serverOptions: ServerOptions = {
    run: { command: pythonPath, args: [serverModule] },
    debug: { command: pythonPath, args: [serverModule, "--debug"] },
  };

  let clientOptions: LanguageClientOptions = {
    documentSelector: [{ scheme: "file", language: "python" }],
    synchronize: {
      fileEvents: vscode.workspace.createFileSystemWatcher("**/*.py"),
    },
  };

  client = new LanguageClient(
    "PythonTypeChecker",
    "Python Type Checker",
    serverOptions,
    clientOptions
  );

  client.start();

  // The command has been defined in the package.json file
  // Now provide the implementation of the command with registerCommand
  // The commandId parameter must match the command field in package.json
  const disposable = vscode.commands.registerCommand(
    "gpython.helloWorld",
    () => {
      // The code you place here will be executed every time your command is executed
      // Display a message box to the user
      vscode.window.showInformationMessage("Hello World from GPython xx! ashu");
    }
  );

  context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
export function deactivate() {}
