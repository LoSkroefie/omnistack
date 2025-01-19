package com.omnistack.plugin;

import com.intellij.openapi.project.Project;
import com.intellij.openapi.editor.Editor;
import com.intellij.openapi.ui.DialogWrapper;
import com.intellij.ui.components.JBScrollPane;
import com.intellij.ui.components.JBTabbedPane;
import com.intellij.util.ui.JBUI;

import javax.swing.*;
import java.awt.*;
import java.util.Map;
import java.util.List;
import org.jetbrains.annotations.Nullable;

public class AnalysisResultsPanel extends DialogWrapper {
    private final Project project;
    private final Editor editor;
    private final Map<String, Object> analysis;
    
    public AnalysisResultsPanel(
        Project project,
        Editor editor,
        Map<String, Object> analysis
    ) {
        super(project);
        this.project = project;
        this.editor = editor;
        this.analysis = analysis;
        
        setTitle("OmniStack AI Analysis Results");
        init();
    }
    
    @Override
    protected @Nullable JComponent createCenterPanel() {
        JPanel mainPanel = new JPanel(new BorderLayout());
        mainPanel.setPreferredSize(new Dimension(600, 400));
        
        JBTabbedPane tabbedPane = new JBTabbedPane();
        
        // Quality Score Tab
        tabbedPane.addTab(
            "Quality Score",
            createQualityScorePanel()
        );
        
        // Suggestions Tab
        tabbedPane.addTab(
            "Suggestions",
            createSuggestionsPanel()
        );
        
        // Optimizations Tab
        tabbedPane.addTab(
            "Optimizations",
            createOptimizationsPanel()
        );
        
        mainPanel.add(tabbedPane, BorderLayout.CENTER);
        
        return mainPanel;
    }
    
    private JComponent createQualityScorePanel() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBorder(JBUI.Borders.empty(10));
        
        double qualityScore = (double) analysis.get("quality_score");
        JProgressBar progressBar = new JProgressBar(0, 100);
        progressBar.setValue((int) (qualityScore * 100));
        progressBar.setStringPainted(true);
        
        JLabel scoreLabel = new JLabel(
            String.format("Code Quality Score: %.2f", qualityScore)
        );
        
        panel.add(scoreLabel, BorderLayout.NORTH);
        panel.add(progressBar, BorderLayout.CENTER);
        
        return panel;
    }
    
    private JComponent createSuggestionsPanel() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBorder(JBUI.Borders.empty(10));
        
        @SuppressWarnings("unchecked")
        List<String> suggestions = (List<String>) analysis.get("suggestions");
        
        DefaultListModel<String> listModel = new DefaultListModel<>();
        suggestions.forEach(listModel::addElement);
        
        JList<String> suggestionsList = new JList<>(listModel);
        suggestionsList.setCellRenderer(new SuggestionCellRenderer());
        
        JBScrollPane scrollPane = new JBScrollPane(suggestionsList);
        panel.add(scrollPane, BorderLayout.CENTER);
        
        return panel;
    }
    
    private JComponent createOptimizationsPanel() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBorder(JBUI.Borders.empty(10));
        
        @SuppressWarnings("unchecked")
        List<String> optimizations = (List<String>) analysis.get("optimizations");
        
        DefaultListModel<String> listModel = new DefaultListModel<>();
        optimizations.forEach(listModel::addElement);
        
        JList<String> optimizationsList = new JList<>(listModel);
        optimizationsList.setCellRenderer(new OptimizationCellRenderer());
        
        JBScrollPane scrollPane = new JBScrollPane(optimizationsList);
        panel.add(scrollPane, BorderLayout.CENTER);
        
        return panel;
    }
}

class SuggestionCellRenderer extends DefaultListCellRenderer {
    @Override
    public Component getListCellRendererComponent(
        JList<?> list,
        Object value,
        int index,
        boolean isSelected,
        boolean cellHasFocus
    ) {
        JLabel label = (JLabel) super.getListCellRendererComponent(
            list, value, index, isSelected, cellHasFocus
        );
        
        label.setIcon(AllIcons.General.BalloonInformation);
        label.setBorder(JBUI.Borders.empty(5));
        
        return label;
    }
}

class OptimizationCellRenderer extends DefaultListCellRenderer {
    @Override
    public Component getListCellRendererComponent(
        JList<?> list,
        Object value,
        int index,
        boolean isSelected,
        boolean cellHasFocus
    ) {
        JLabel label = (JLabel) super.getListCellRendererComponent(
            list, value, index, isSelected, cellHasFocus
        );
        
        label.setIcon(AllIcons.General.Speed);
        label.setBorder(JBUI.Borders.empty(5));
        
        return label;
    }
}
