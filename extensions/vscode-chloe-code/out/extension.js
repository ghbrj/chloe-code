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
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
function activate(context) {
    const config = vscode.workspace.getConfiguration('chloeCode');
    const generateCmd = vscode.commands.registerCommand('chloeCode.generate', async () => {
        const prompt = await vscode.window.showInputBox({ placeHolder: 'Entrez votre requête de génération de code' });
        if (!prompt) {
            return;
        }
        const endpoint = config.get('endpoint') ?? 'http://localhost:8000/v1';
        try {
            const resp = await axios_1.default.post(`${endpoint}/infer`, { prompt });
            const code = resp.data.code ?? '';
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                editor.edit(editBuilder => editBuilder.insert(editor.selection.active, code));
                vscode.window.showInformationMessage('Code généré et inséré.');
            }
        }
        catch (err) {
            vscode.window.showErrorMessage(`Erreur d’inférence : ${err.message}`);
        }
    });
    const updateModelCmd = vscode.commands.registerCommand('chloeCode.updateModel', async () => {
        const endpoint = config.get('endpoint') ?? 'http://localhost:8000/v1';
        try {
            await axios_1.default.post(`${endpoint}/update-model`);
            vscode.window.showInformationMessage('Modèle mis à jour.');
        }
        catch (err) {
            vscode.window.showErrorMessage(`Erreur de mise à jour du modèle : ${err.message}`);
        }
    });
    // Enregistrement des commandes
    context.subscriptions.push(generateCmd, updateModelCmd);
}
function deactivate() { }
//# sourceMappingURL=extension.js.map