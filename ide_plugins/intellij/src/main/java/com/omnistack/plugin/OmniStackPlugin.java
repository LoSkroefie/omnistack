package com.omnistack.plugin;

import com.intellij.openapi.project.Project;
import com.intellij.openapi.editor.Editor;
import com.intellij.openapi.editor.Document;
import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.actionSystem.CommonDataKeys;
import com.intellij.openapi.command.WriteCommandAction;
import com.intellij.psi.PsiFile;
import com.intellij.psi.PsiElement;
import com.intellij.psi.util.PsiUtilBase;
import com.intellij.openapi.diagnostic.Logger;
import com.intellij.openapi.ui.Messages;
import com.intellij.util.ui.UIUtil;

import java.util.concurrent.CompletableFuture;
import java.util.List;
import java.util.Map;
import org.jetbrains.annotations.NotNull;

public class OmniStackPlugin extends AnAction {
    private static final Logger LOG = Logger.getInstance(OmniStackPlugin.class);
    private final OmniStackService service;
    private final AnalysisManager analysisManager;
    
    public OmniStackPlugin() {
        super("Analyze with OmniStack AI");
        this.service = new OmniStackService();
        this.analysisManager = new AnalysisManager();
    }
    
    @Override
    public void actionPerformed(@NotNull AnActionEvent e) {
        Project project = e.getProject();
        Editor editor = e.getData(CommonDataKeys.EDITOR);
        PsiFile psiFile = e.getData(CommonDataKeys.PSI_FILE);
        
        if (project == null || editor == null || psiFile == null) {
            return;
        }
        
        analyzeCode(project, editor, psiFile);
    }
    
    private void analyzeCode(
        Project project,
        Editor editor,
        PsiFile psiFile
    ) {
        String code = editor.getDocument().getText();
        CompletableFuture.supplyAsync(() -> service.analyzeCode(code))
            .thenAccept(analysis -> {
                UIUtil.invokeLaterIfNeeded(() -> {
                    showAnalysisResults(project, editor, analysis);
                });
            })
            .exceptionally(throwable -> {
                LOG.error("Analysis failed", throwable);
                UIUtil.invokeLaterIfNeeded(() -> {
                    Messages.showErrorDialog(
                        project,
                        "Analysis failed: " + throwable.getMessage(),
                        "OmniStack AI Error"
                    );
                });
                return null;
            });
    }
    
    private void showAnalysisResults(
        Project project,
        Editor editor,
        Map<String, Object> analysis
    ) {
        AnalysisResultsPanel panel = new AnalysisResultsPanel(
            project,
            editor,
            analysis
        );
        panel.show();
    }
    
    @Override
    public void update(@NotNull AnActionEvent e) {
        Project project = e.getProject();
        Editor editor = e.getData(CommonDataKeys.EDITOR);
        PsiFile psiFile = e.getData(CommonDataKeys.PSI_FILE);
        
        e.getPresentation().setEnabledAndVisible(
            project != null && editor != null && psiFile != null
        );
    }
}

class OmniStackService {
    private static final String API_ENDPOINT = "http://localhost:8000";
    private final HttpClient httpClient;
    
    public OmniStackService() {
        this.httpClient = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_2)
            .build();
    }
    
    public Map<String, Object> analyzeCode(String code) {
        // Implement API call to OmniStack backend
        return Map.of(
            "quality_score", 0.85,
            "suggestions", List.of("Suggestion 1", "Suggestion 2"),
            "optimizations", List.of("Optimization 1", "Optimization 2")
        );
    }
}

class AnalysisManager {
    private final Map<String, Analysis> analysisCache;
    
    public AnalysisManager() {
        this.analysisCache = new ConcurrentHashMap<>();
    }
    
    public void cacheAnalysis(String fileId, Analysis analysis) {
        analysisCache.put(fileId, analysis);
    }
    
    public Analysis getCachedAnalysis(String fileId) {
        return analysisCache.get(fileId);
    }
}

class Analysis {
    private final double qualityScore;
    private final List<String> suggestions;
    private final List<String> optimizations;
    
    public Analysis(
        double qualityScore,
        List<String> suggestions,
        List<String> optimizations
    ) {
        this.qualityScore = qualityScore;
        this.suggestions = suggestions;
        this.optimizations = optimizations;
    }
    
    public double getQualityScore() {
        return qualityScore;
    }
    
    public List<String> getSuggestions() {
        return suggestions;
    }
    
    public List<String> getOptimizations() {
        return optimizations;
    }
}
