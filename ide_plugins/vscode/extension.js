const vscode = require('vscode');
const axios = require('axios');

class OmniStackExtension {
    constructor(context) {
        this.context = context;
        this.apiClient = axios.create({
            baseURL: 'http://localhost:8000',
            timeout: 10000
        });
        
        // Register commands
        this.registerCommands();
        
        // Initialize features
        this.initializeFeatures();
    }
    
    registerCommands() {
        // Register analyze command
        let analyzeDisposable = vscode.commands.registerCommand(
            'omnistack.analyzeCode',
            () => this.analyzeCurrentFile()
        );
        
        // Register debug command
        let debugDisposable = vscode.commands.registerCommand(
            'omnistack.debugCode',
            () => this.debugCurrentFile()
        );
        
        this.context.subscriptions.push(analyzeDisposable, debugDisposable);
    }
    
    initializeFeatures() {
        // Initialize real-time analysis
        this.initializeRealTimeAnalysis();
        
        // Initialize code completion
        this.initializeCodeCompletion();
        
        // Initialize diagnostics
        this.initializeDiagnostics();
    }
    
    async analyzeCurrentFile() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }
        
        const document = editor.document;
        const code = document.getText();
        
        try {
            const response = await this.apiClient.post('/analyze', {
                code,
                project_files: await this.getProjectFiles(),
                context: await this.getFileContext()
            });
            
            this.showAnalysisResults(response.data);
        } catch (error) {
            vscode.window.showErrorMessage(
                `Analysis failed: ${error.message}`
            );
        }
    }
    
    async debugCurrentFile() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }
        
        const document = editor.document;
        const code = document.getText();
        
        try {
            const response = await this.apiClient.post('/debug', {
                code,
                context: await this.getFileContext()
            });
            
            this.showDebugResults(response.data.issues);
        } catch (error) {
            vscode.window.showErrorMessage(
                `Debugging failed: ${error.message}`
            );
        }
    }
    
    initializeRealTimeAnalysis() {
        vscode.workspace.onDidChangeTextDocument(async (event) => {
            const document = event.document;
            
            // Debounce analysis requests
            if (this.analysisTimeout) {
                clearTimeout(this.analysisTimeout);
            }
            
            this.analysisTimeout = setTimeout(async () => {
                try {
                    const response = await this.apiClient.post('/analyze', {
                        code: document.getText(),
                        project_files: await this.getProjectFiles(),
                        context: await this.getFileContext()
                    });
                    
                    this.updateDiagnostics(document, response.data);
                } catch (error) {
                    console.error('Real-time analysis failed:', error);
                }
            }, 1000);
        });
    }
    
    initializeCodeCompletion() {
        const provider = vscode.languages.registerCompletionItemProvider(
            ['javascript', 'typescript', 'python'],
            {
                provideCompletionItems: async (document, position) => {
                    const linePrefix = document
                        .lineAt(position)
                        .text.substr(0, position.character);
                    
                    if (linePrefix.trim().length === 0) {
                        return undefined;
                    }
                    
                    try {
                        // Get AI-powered completions
                        const response = await this.apiClient.post('/complete', {
                            code: document.getText(),
                            line: linePrefix,
                            position: {
                                line: position.line,
                                character: position.character
                            }
                        });
                        
                        return this.createCompletionItems(response.data);
                    } catch (error) {
                        console.error('Completion failed:', error);
                        return undefined;
                    }
                }
            }
        );
        
        this.context.subscriptions.push(provider);
    }
    
    initializeDiagnostics() {
        this.diagnosticCollection = vscode.languages
            .createDiagnosticCollection('omnistack');
        this.context.subscriptions.push(this.diagnosticCollection);
    }
    
    async getProjectFiles() {
        const files = await vscode.workspace.findFiles(
            '**/*.{js,ts,py}',
            '**/node_modules/**'
        );
        return files.map(file => file.fsPath);
    }
    
    async getFileContext() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return {};
        }
        
        return {
            fileName: editor.document.fileName,
            languageId: editor.document.languageId,
            selection: editor.selection
        };
    }
    
    showAnalysisResults(results) {
        const panel = vscode.window.createWebviewPanel(
            'omnistack.analysis',
            'OmniStack Analysis Results',
            vscode.ViewColumn.Two,
            {}
        );
        
        panel.webview.html = this.getAnalysisResultsHtml(results);
    }
    
    showDebugResults(issues) {
        this.diagnosticCollection.clear();
        
        const diagnostics = issues.map(issue => {
            const range = new vscode.Range(
                issue.line_number - 1,
                0,
                issue.line_number - 1,
                100
            );
            
            return new vscode.Diagnostic(
                range,
                `${issue.message}\nSuggestion: ${issue.suggestion}`,
                this.getSeverity(issue.severity)
            );
        });
        
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            this.diagnosticCollection.set(
                editor.document.uri,
                diagnostics
            );
        }
    }
    
    getSeverity(severity) {
        switch (severity.toLowerCase()) {
            case 'error':
                return vscode.DiagnosticSeverity.Error;
            case 'warning':
                return vscode.DiagnosticSeverity.Warning;
            default:
                return vscode.DiagnosticSeverity.Information;
        }
    }
    
    getAnalysisResultsHtml(results) {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    .score { font-size: 24px; margin-bottom: 20px; }
                    .section { margin-bottom: 20px; }
                    .issue { margin-bottom: 10px; }
                </style>
            </head>
            <body>
                <div class="score">
                    Code Quality Score: ${results.code_quality_score.toFixed(2)}
                </div>
                
                <div class="section">
                    <h2>Potential Issues</h2>
                    ${results.potential_issues.map(issue => `
                        <div class="issue">
                            <strong>${issue.severity}:</strong> ${issue.message}
                        </div>
                    `).join('')}
                </div>
                
                <div class="section">
                    <h2>Optimization Suggestions</h2>
                    ${results.optimization_suggestions.map(opt => `
                        <div class="issue">
                            ${opt.message}
                        </div>
                    `).join('')}
                </div>
            </body>
            </html>
        `;
    }
    
    createCompletionItems(completions) {
        return completions.map(completion => {
            const item = new vscode.CompletionItem(
                completion.label,
                vscode.CompletionItemKind.Snippet
            );
            item.detail = completion.detail;
            item.documentation = completion.documentation;
            item.insertText = completion.insertText;
            return item;
        });
    }
}

function activate(context) {
    new OmniStackExtension(context);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
