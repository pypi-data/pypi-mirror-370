"""Web interface for iamx with improved UI."""

import json
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from ..core.analyzer import PolicyAnalyzer
from ..core.models import AnalysisConfig, Severity


class AnalysisRequest(BaseModel):
    """Request model for policy analysis."""
    policy_content: str
    fail_on: str = "critical"
    include_info: bool = False
    max_findings: int = 10


class AnalysisResponse(BaseModel):
    """Response model for policy analysis."""
    success: bool
    message: str
    result: Optional[dict] = None


def create_app() -> FastAPI:
    """Create the FastAPI application."""
    app = FastAPI(
        title="iamx - IAM Policy Explainer",
        description="Local-first IAM policy analyzer with deterministic risk detection",
        version="0.1.0",
    )
    
    @app.get("/", response_class=HTMLResponse)
    async def index():
        """Main page with improved UI."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>iamx - IAM Policy Explainer</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                    max-width: 1000px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    background-color: #f8f9fa;
                    scroll-behavior: smooth;
                }
                .main-content {
                    display: grid;
                    grid-template-columns: 2fr 1fr;
                    gap: 30px;
                    align-items: start;
                }
                
                .analysis-section { 
                    background: white; 
                    padding: 30px; 
                    border-radius: 12px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                
                .severity-guide {
                    background: white;
                    padding: 25px;
                    border-radius: 12px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    position: sticky;
                    top: 20px;
                }
                
                .severity-table table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                    font-size: 14px;
                }
                
                .severity-table th,
                .severity-table td {
                    padding: 8px 12px;
                    text-align: left;
                    border-bottom: 1px solid #e9ecef;
                }
                
                .severity-table th {
                    background: #f8f9fa;
                    font-weight: 600;
                }
                
                .severity-low { background: #d4edda; }
                .severity-medium { background: #fff3cd; }
                .severity-high { background: #f8d7da; }
                .severity-critical { background: #f5c6cb; }
                
                .example-grid {
                    display: grid;
                    grid-template-columns: 1fr;
                    gap: 15px;
                    margin-top: 15px;
                }
                
                .example-card {
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid;
                }
                
                .example-card h5 {
                    margin: 0 0 10px 0;
                    font-size: 14px;
                }
                
                .example-card ul {
                    margin: 0;
                    padding-left: 20px;
                    font-size: 13px;
                }
                
                .example-card li {
                    margin: 5px 0;
                }
                
                .example-card.critical {
                    background: #f8d7da;
                    border-left-color: #dc3545;
                }
                
                .example-card.high {
                    background: #fff3cd;
                    border-left-color: #ffc107;
                }
                
                .example-card.medium {
                    background: #e2e3e5;
                    border-left-color: #6c757d;
                }
                
                .example-card.low {
                    background: #d4edda;
                    border-left-color: #28a745;
                }
                
                .example-card code {
                    background: rgba(0,0,0,0.1);
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: monospace;
                }
                textarea { 
                    width: 100%; 
                    height: 250px; 
                    margin: 10px 0; 
                    padding: 15px;
                    border: 2px solid #e9ecef;
                    border-radius: 8px;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    font-size: 13px;
                    resize: vertical;
                    box-sizing: border-box;
                }
                button { 
                    background: #007cba; 
                    color: white; 
                    padding: 12px 24px; 
                    border: none; 
                    border-radius: 8px; 
                    cursor: pointer; 
                    font-size: 16px;
                    font-weight: 500;
                    transition: background-color 0.2s;
                }
                button:hover {
                    background: #005a8b;
                }
                .result { 
                    margin-top: 20px; 
                    padding: 20px; 
                    border-radius: 8px; 
                    border-left: 4px solid;
                }
                
                /* Color coding based on status */
                .result-passed { 
                    background: #d4f6d4; 
                    border-left-color: #28a745;
                    border: 1px solid #c3e6cb; 
                }
                .result-passed-medium { 
                    background: #fff3cd; 
                    border-left-color: #ffc107;
                    border: 1px solid #ffeaa7; 
                }
                .result-failed-critical { 
                    background: #f8d7da; 
                    border-left-color: #dc3545;
                    border: 1px solid #f5c6cb; 
                }
                .result-failed-high { 
                    background: #fff3cd; 
                    border-left-color: #ffc107;
                    border: 1px solid #ffeaa7; 
                }
                .error { 
                    background: #f8d7da; 
                    border-left-color: #dc3545;
                    border: 1px solid #f5c6cb; 
                }
                
                .summary-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }
                .summary-card {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    text-align: center;
                }
                .summary-card strong {
                    display: block;
                    font-size: 24px;
                    margin-bottom: 5px;
                }
                
                .findings-section {
                    margin-top: 20px;
                }
                .finding-item {
                    background: #f8f9fa;
                    margin: 10px 0;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid;
                }
                .finding-critical { border-left-color: #dc3545; }
                .finding-high { border-left-color: #ffc107; }
                .finding-medium { border-left-color: #17a2b8; }
                .finding-low { border-left-color: #6c757d; }
                
                .finding-title {
                    font-weight: bold;
                    margin-bottom: 8px;
                }
                .finding-description {
                    margin-bottom: 10px;
                    line-height: 1.5;
                }
                .finding-recommendation {
                    background: white;
                    padding: 10px;
                    border-radius: 4px;
                    margin-top: 10px;
                    font-style: italic;
                }
                
                pre {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    overflow-x: auto;
                    font-size: 12px;
                    max-height: 400px;
                    overflow-y: auto;
                    word-wrap: break-word;
                    white-space: pre-wrap;
                }
                
                .status-icon {
                    font-size: 20px;
                    margin-right: 8px;
                }
                
                h1 { color: #333; margin-bottom: 10px; }
                h2 { color: #555; margin-bottom: 15px; }
                h3 { color: #666; margin-bottom: 10px; }
                
                .loading {
                    text-align: center;
                    padding: 40px;
                    color: #6c757d;
                    animation: fadeIn 0.3s ease-in;
                }
                
                .loading-spinner {
                    display: inline-block;
                    width: 40px;
                    height: 40px;
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #007cba;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin-bottom: 15px;
                }
                
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                @keyframes slideIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                .result {
                    animation: slideIn 0.4s ease-out;
                }
                
                .summary-grid {
                    animation: fadeIn 0.5s ease-out 0.1s both;
                }
                
                .findings-section {
                    animation: fadeIn 0.5s ease-out 0.2s both;
                }
                
                .smooth-scroll {
                    scroll-behavior: smooth;
                }
            </style>
        </head>
        <body>
            <h1>🔍 iamx - IAM Policy Explainer</h1>
            <p style="color: #6c757d; margin-bottom: 30px;">Local-first IAM policy analyzer with deterministic risk detection</p>
            
            <div class="main-content">
                <div class="analysis-section">
                    <h2>Analyze IAM Policy</h2>
                    <p>Paste your IAM policy JSON below to analyze it for security risks:</p>
                    
                    <form id="analysisForm">
                        <textarea id="policyContent" placeholder="Paste your IAM policy JSON here...

Example:
{
  &quot;Version&quot;: &quot;2012-10-17&quot;,
  &quot;Statement&quot;: [
    {
      &quot;Effect&quot;: &quot;Allow&quot;,
      &quot;Action&quot;: &quot;s3:*&quot;,
      &quot;Resource&quot;: &quot;*&quot;
    }
  ]
}"></textarea>
                        <br>
                        <label style="margin: 10px 0; display: block;">
                            <input type="checkbox" id="includeInfo" style="margin-right: 8px;"> 
                            Include informational findings
                        </label>
                        <br>
                        <button type="submit">🔍 Analyze Policy</button>
                    </form>
                    
                    <div id="result"></div>
                </div>
                
                <div class="severity-guide">
                    <h3>🔍 Severity Guide</h3>
                    <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #2196f3;">
                        <h4 style="margin: 0 0 10px 0; color: #1976d2;">ℹ️ Analysis Limitations</h4>
                        <p style="margin: 0; font-size: 14px; line-height: 1.4;">
                            <strong>Static analysis cannot determine:</strong><br>
                            • Account ownership (cross-account access may be legitimate)<br>
                            • Business context (some "risky" patterns are necessary)<br>
                            • Actual permissions (depends on bucket policies, etc.)<br>
                            <em>Always review findings in context!</em>
                        </p>
                    </div>
                    <div class="severity-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>Risk Level</th>
                                    <th>Score Range</th>
                                    <th>Status</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr class="severity-low">
                                    <td>🟢 LOW</td>
                                    <td>0.0 - 3.0</td>
                                    <td>✅ PASS</td>
                                    <td>Minor issues, best practice violations</td>
                                </tr>
                                <tr class="severity-medium">
                                    <td>🟡 MEDIUM</td>
                                    <td>3.0 - 6.0</td>
                                    <td>✅ PASS</td>
                                    <td>Moderate risks, should be reviewed</td>
                                </tr>
                                <tr class="severity-high">
                                    <td>🟠 HIGH</td>
                                    <td>6.0 - 8.0</td>
                                    <td>❌ FAIL</td>
                                    <td>Significant security risks</td>
                                </tr>
                                <tr class="severity-critical">
                                    <td>🔴 CRITICAL</td>
                                    <td>8.0 - 10.0</td>
                                    <td>❌ FAIL</td>
                                    <td>Severe security vulnerabilities</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="severity-examples">
                        <h4>Common Patterns by Severity:</h4>
                        <div class="example-grid">
                            <div class="example-card critical">
                                <h5>🔴 CRITICAL Examples</h5>
                                <ul>
                                    <li><code>"Action": "*"</code> - Full admin access</li>
                                    <li><code>"iam:*"</code> - IAM full control</li>
                                    <li><code>"s3:*"</code> - S3 full control</li>
                                </ul>
                            </div>
                            <div class="example-card high">
                                <h5>🟠 HIGH Examples</h5>
                                <ul>
                                    <li><code>"Resource": "*"</code> - Wildcard resources</li>
                                    <li><code>"dynamodb:*"</code> - DynamoDB full control</li>
                                    <li><code>"lambda:*"</code> - Lambda full control</li>
                                </ul>
                            </div>
                            <div class="example-card medium">
                                <h5>🟡 MEDIUM Examples</h5>
                                <ul>
                                    <li>Missing resource restrictions</li>
                                    <li>Cross-account access</li>
                                    <li>Data access without conditions</li>
                                </ul>
                            </div>
                            <div class="example-card low">
                                <h5>🟢 LOW Examples</h5>
                                <ul>
                                    <li>Minor configuration issues</li>
                                    <li>Best practice violations</li>
                                    <li>Informational findings</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                function getSeverityIcon(severity) {
                    const icons = {
                        'critical': '❌',
                        'high': '⚠️',
                        'medium': '🔶',
                        'low': 'ℹ️',
                        'info': '✅'
                    };
                    return icons[severity] || '•';
                }
                
                function getResultClass(passed, riskScore) {
                    if (passed) {
                        if (riskScore >= 3.0) return 'result-passed-medium';
                        return 'result-passed';
                    } else {
                        if (riskScore >= 8.0) return 'result-failed-critical';
                        return 'result-failed-high';
                    }
                }
                
                function formatFindings(findings) {
                    if (!findings || findings.length === 0) return '';
                    
                    let html = '<div class="findings-section"><h4>Security Findings:</h4>';
                    
                    findings.forEach(finding => {
                        const icon = getSeverityIcon(finding.severity);
                        html += `
                            <div class="finding-item finding-${finding.severity}">
                                <div class="finding-title">${icon} ${finding.title}</div>
                                <div class="finding-description">${finding.description}</div>
                                ${finding.action_pattern ? `<div><strong>Actions:</strong> ${finding.action_pattern}</div>` : ''}
                                ${finding.resource_pattern ? `<div><strong>Resources:</strong> ${finding.resource_pattern}</div>` : ''}
                                ${finding.recommendation ? `<div class="finding-recommendation"><strong>Recommendation:</strong> ${finding.recommendation}</div>` : ''}
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                    return html;
                }
                
                document.getElementById('analysisForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const policyContent = document.getElementById('policyContent').value;
                    const includeInfo = document.getElementById('includeInfo').checked;
                    
                    if (!policyContent.trim()) {
                        alert('Please enter a policy to analyze');
                        return;
                    }
                    
                    const resultDiv = document.getElementById('result');
                    const submitButton = document.querySelector('button[type="submit"]');
                    
                    // Disable button and show loading state
                    submitButton.disabled = true;
                    submitButton.innerHTML = '⏳ Analyzing...';
                    
                    resultDiv.innerHTML = `
                        <div class="loading">
                            <div class="loading-spinner"></div>
                            <div>🔍 Analyzing policy...</div>
                            <div style="font-size: 14px; margin-top: 10px; color: #999;">This usually takes a few seconds</div>
                        </div>
                    `;
                    
                    // Smooth scroll to results
                    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    
                    try {
                        const response = await fetch('/analyze', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                policy_content: policyContent,
                                include_info: includeInfo
                            })
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            const result = data.result;
                            const statusIcon = result.passed ? '✅' : '❌';
                            const statusText = result.passed ? 'PASSED' : 'FAILED';
                            const resultClass = getResultClass(result.passed, result.risk_score);
                            
                            // Add a small delay for smoother transition
                            setTimeout(() => {
                                resultDiv.className = `result ${resultClass}`;
                            resultDiv.innerHTML = `
                                <h3><span class="status-icon">${statusIcon}</span>Analysis Complete</h3>
                                
                                <div class="summary-grid">
                                    <div class="summary-card">
                                        <strong style="color: ${result.passed ? '#28a745' : '#dc3545'}">${statusText}</strong>
                                        <span>Status</span>
                                    </div>
                                    <div class="summary-card">
                                        <strong>${result.risk_score}/10.0</strong>
                                        <span>Risk Score</span>
                                    </div>
                                    <div class="summary-card">
                                        <strong>${result.total_findings}</strong>
                                        <span>Findings</span>
                                    </div>
                                    <div class="summary-card">
                                        <strong>${result.metadata.statement_count}</strong>
                                        <span>Statements</span>
                                    </div>
                                </div>
                                
                                ${result.summary && Object.keys(result.summary).length > 0 ? `
                                    <h4>Findings by Severity:</h4>
                                    <div style="margin: 10px 0;">
                                        ${Object.entries(result.summary).map(([severity, count]) => 
                                            `<span style="margin-right: 15px;">${getSeverityIcon(severity)} <strong>${severity.toUpperCase()}:</strong> ${count}</span>`
                                        ).join('')}
                                    </div>
                                ` : ''}
                                
                                ${formatFindings(result.findings)}
                                
                                <details style="margin-top: 20px;">
                                    <summary style="cursor: pointer; font-weight: bold;">Raw Analysis Data</summary>
                                    <pre>${JSON.stringify(result, null, 2)}</pre>
                                </details>
                            `;
                            }, 100); // Small delay for smoother transition
                        } else {
                            resultDiv.className = 'result error';
                            resultDiv.innerHTML = `<h3>❌ Analysis Failed</h3><p>${data.message}</p>`;
                        }
                        
                        // Reset button state
                        submitButton.disabled = false;
                        submitButton.innerHTML = '🔍 Analyze Policy';
                    } catch (error) {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
                        
                        // Reset button state
                        submitButton.disabled = false;
                        submitButton.innerHTML = '🔍 Analyze Policy';
                    }
                });
            </script>
        </body>
        </html>
        """
    
    @app.post("/analyze")
    async def analyze_policy(request: AnalysisRequest) -> AnalysisResponse:
        """Analyze an IAM policy."""
        try:
            # Convert severity string to enum
            severity_map = {
                'critical': Severity.CRITICAL,
                'high': Severity.HIGH,
                'medium': Severity.MEDIUM,
                'low': Severity.LOW,
            }
            
            # Create analysis configuration
            config = AnalysisConfig(
                fail_on_severity=severity_map.get(request.fail_on, Severity.CRITICAL),
                include_info=request.include_info,
                max_findings_per_category=request.max_findings,
            )
            
            # Initialize analyzer
            analyzer = PolicyAnalyzer(config)
            
            # Analyze the policy
            result = analyzer.analyze_string(request.policy_content)
            
            # Convert result to dict for JSON response
            result_dict = {
                "risk_score": result.risk_score,
                "passed": result.passed,
                "total_findings": result.total_findings,
                "summary": result.summary,
                "metadata": {
                    "filename": result.metadata.filename,
                    "policy_name": result.metadata.policy_name,
                    "statement_count": result.metadata.statement_count,
                    "action_count": result.metadata.action_count,
                    "resource_count": result.metadata.resource_count,
                },
                "findings": [
                    {
                        "id": f.id,
                        "title": f.title,
                        "description": f.description,
                        "severity": f.severity.value,
                        "category": f.category,
                        "statement_index": f.statement_index,
                        "action_pattern": f.action_pattern,
                        "resource_pattern": f.resource_pattern,
                        "recommendation": f.recommendation,
                        "examples": f.examples,
                        "references": f.references,
                    }
                    for f in result.findings
                ]
            }
            
            return AnalysisResponse(
                success=True,
                message="Analysis completed successfully",
                result=result_dict
            )
            
        except Exception as e:
            return AnalysisResponse(
                success=False,
                message=f"Analysis failed: {str(e)}"
            )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "tool": "iamx", "version": "0.1.0"}
    
    return app
