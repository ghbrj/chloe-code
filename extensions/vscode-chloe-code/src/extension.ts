import * as vscode from 'vscode';
import axios from 'axios';

export function activate(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('chloeCode');

    const generateCmd = vscode.commands.registerCommand('chloeCode.generate', async () => {
        const prompt = await vscode.window.showInputBox({ placeHolder: 'Entrez votre requête de génération de code' });
        if (!prompt) { return; }

        const endpoint = config.get<string>('endpoint') ?? 'http://localhost:8000/v1';
        try {
            const resp = await axios.post(`${endpoint}/infer`, { prompt });
            const code = resp.data.code ?? '';
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                editor.edit(editBuilder => editBuilder.insert(editor.selection.active, code));
                vscode.window.showInformationMessage('Code généré et inséré.');
            }
        } catch (err:any) {
            vscode.window.showErrorMessage(`Erreur d’inférence : ${err.message}`);
        }
    });

    const updateModelCmd = vscode.commands.registerCommand('chloeCode.updateModel', async () => {
        const endpoint = config.get<string>('endpoint') ?? 'http://localhost:8000/v1';
        try {
            await axios.post(`${endpoint}/update-model`);
            vscode.window.showInformationMessage('Modèle mis à jour.');
        } catch (err:any) {
            vscode.window.showErrorMessage(`Erreur de mise à jour du modèle : ${err.message}`);
        }
    });

    // Enregistrement des commandes
    context.subscriptions.push(generateCmd, updateModelCmd);
}

export function deactivate() {}
