/**
 * MSA Reasoning Engine - Onboarding Wizard JavaScript
 * Interactive setup wizard for new users
 */

class OnboardingWizard {
    // Utility function to escape HTML special characters
    static escapeHTML(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/`/g, '&#96;');
    }

    constructor() {
        this.currentStep = 1;
        this.totalSteps = 6;
        this.systemStatus = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateUI();
    }

    bindEvents() {
        document.getElementById('nextBtn').addEventListener('click', () => this.nextStep());
        document.getElementById('prevBtn').addEventListener('click', () => this.prevStep());
        document.getElementById('runTest').addEventListener('click', () => this.runSystemTest());
    }

    nextStep() {
        if (this.currentStep < this.totalSteps) {
            // Handle step-specific logic before advancing
            this.handleStepExit(this.currentStep);
            
            this.currentStep++;
            this.updateUI();
            
            // Handle step-specific logic after entering
            this.handleStepEnter(this.currentStep);
        }
    }

    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateUI();
        }
    }

    handleStepEnter(step) {
        switch (step) {
            case 2:
                this.checkSystemStatus();
                break;
            case 4:
                this.checkDaytonaStatus();
                break;
        }
    }

    handleStepExit(step) {
        // Any cleanup needed when leaving a step
    }

    updateUI() {
        // Update step indicators
        document.querySelectorAll('.step-indicator').forEach((indicator, index) => {
            const stepNum = index + 1;
            indicator.classList.remove('active', 'completed');
            
            if (stepNum < this.currentStep) {
                indicator.classList.add('completed');
            } else if (stepNum === this.currentStep) {
                indicator.classList.add('active');
            }
        });

        // Update progress bar
        const progress = (this.currentStep / this.totalSteps) * 100;
        document.getElementById('progressBar').style.width = `${progress}%`;
        document.getElementById('progressText').textContent = `Step ${this.currentStep} of ${this.totalSteps}`;

        // Show/hide step content
        document.querySelectorAll('.step-content').forEach((content, index) => {
            const stepNum = index + 1;
            if (stepNum === this.currentStep) {
                content.classList.remove('hidden');
                content.classList.add('fade-in');
            } else {
                content.classList.add('hidden');
                content.classList.remove('fade-in');
            }
        });

        // Update navigation buttons
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        
        prevBtn.disabled = this.currentStep === 1;
        
        if (this.currentStep === this.totalSteps) {
            nextBtn.style.display = 'none';
        } else {
            nextBtn.style.display = 'block';
            nextBtn.textContent = this.currentStep === this.totalSteps - 1 ? 'Complete Setup' : 'Next';
        }
    }

    async checkSystemStatus() {
        const checks = [
            { id: 'redis', name: 'Redis Cloud Connection', endpoint: '/api/v1/health' },
            { id: 'database', name: 'PostgreSQL Database', endpoint: '/api/v1/health' },
            { id: 'kernel', name: 'Semantic Kernel', endpoint: '/api/v1/health' },
            { id: 'reasoning', name: 'v2 Reasoning Kernel', endpoint: '/api/v2/health' },
            { id: 'daytona', name: 'Daytona Sandbox', endpoint: '/api/v2/daytona/status' }
        ];

        for (const check of checks) {
            await this.performStatusCheck(check);
        }

        this.showStatusSummary();
    }

    async performStatusCheck(check) {
        const statusItem = document.querySelector(`[data-check="${check.id}"]`);
        const statusIcon = statusItem.querySelector('.status-icon');
        
        try {
            const response = await fetch(check.endpoint);
            const data = await response.json();
            
            const isHealthy = this.evaluateHealth(check.id, data, response.status);
            this.systemStatus[check.id] = isHealthy;
            
            statusIcon.innerHTML = isHealthy 
                ? '<svg class="w-6 h-6 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                : '<svg class="w-6 h-6 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
                
            statusItem.classList.remove('bg-slate-50');
            statusItem.classList.add(isHealthy ? 'bg-green-50' : 'bg-red-50');
            
        } catch (error) {
            console.error(`Status check failed for ${check.name}:`, error);
            this.systemStatus[check.id] = false;
            statusIcon.innerHTML = '<svg class="w-6 h-6 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
            statusItem.classList.remove('bg-slate-50');
            statusItem.classList.add('bg-red-50');
        }
    }

    evaluateHealth(checkId, data, status) {
        if (status !== 200) return false;
        
        switch (checkId) {
            case 'daytona':
                return data.service_status !== 'unavailable';
            case 'reasoning':
                return data.status === 'healthy' || data.message?.includes('v2');
            default:
                return data.status === 'healthy' || data.status === 'operational';
        }
    }

    showStatusSummary() {
        const summary = document.getElementById('statusSummary');
        const summaryText = document.getElementById('statusSummaryText');
        
        const healthyCount = Object.values(this.systemStatus).filter(Boolean).length;
        const totalCount = Object.keys(this.systemStatus).length;
        
        if (healthyCount === totalCount) {
            summary.className = 'mt-6 p-4 rounded-lg bg-green-50 border border-green-200';
            summaryText.textContent = 'All systems operational! Ready to proceed.';
        } else if (healthyCount > totalCount / 2) {
            summary.className = 'mt-6 p-4 rounded-lg bg-yellow-50 border border-yellow-200';
            summaryText.textContent = `${healthyCount}/${totalCount} systems operational. Some features may be limited.`;
        } else {
            summary.className = 'mt-6 p-4 rounded-lg bg-red-50 border border-red-200';
            summaryText.textContent = `Only ${healthyCount}/${totalCount} systems operational. Please check configuration.`;
        }
        
        summary.classList.remove('hidden');
    }

    async checkDaytonaStatus() {
        try {
            const response = await fetch('/api/v2/daytona/status');
            const data = await response.json();
            
            // Update Daytona status
            const daytonaStatus = document.getElementById('daytonaStatus');
            const daytonaStatusText = document.getElementById('daytonaStatusText');
            const apiKeyStatus = document.getElementById('apiKeyStatus');
            const apiKeyStatusText = document.getElementById('apiKeyStatusText');
            
            if (data.daytona_available) {
                daytonaStatus.className = 'w-3 h-3 rounded-full mr-3 bg-success';
                daytonaStatusText.textContent = 'Daytona Cloud connected';
            } else {
                daytonaStatus.className = 'w-3 h-3 rounded-full mr-3 bg-warning';
                daytonaStatusText.textContent = 'Using secure local fallback';
            }
            
            if (data.api_key_configured) {
                apiKeyStatus.className = 'w-3 h-3 rounded-full mr-3 bg-success';
                apiKeyStatusText.textContent = 'API key configured';
            } else {
                apiKeyStatus.className = 'w-3 h-3 rounded-full mr-3 bg-error';
                apiKeyStatusText.textContent = 'API key required for cloud features';
            }
            
            // Show configuration
            document.getElementById('daytonaConfig').classList.remove('hidden');
            
            // Show instructions if needed
            if (!data.api_key_configured) {
                document.getElementById('daytonaInstructions').classList.remove('hidden');
            }
            
        } catch (error) {
            console.error('Failed to check Daytona status:', error);
        }
    }

    async runSystemTest() {
        const testQuery = document.getElementById('testQuery').value;
        const runButton = document.getElementById('runTest');
        const progress = document.getElementById('testProgress');
        const results = document.getElementById('testResults');
        const output = document.getElementById('testOutput');
        
        // Show progress
        runButton.disabled = true;
        progress.classList.remove('hidden');
        results.classList.add('hidden');
        
        try {
            const response = await fetch('/api/v2/reasoning/reason', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: testQuery,
                    confidence_threshold: 0.7
                })
            });
            
            const data = await response.json();
            
            // Display results
            if (response.ok) {
                output.innerHTML = `
                    <div class="space-y-3">
                        <div><strong>Query:</strong> ${OnboardingWizard.escapeHTML(testQuery)}</div>
                        <div><strong>Overall Confidence:</strong> ${(data.overall_confidence * 100).toFixed(1)}%</div>
                        <div><strong>Processing Time:</strong> ${data.processing_time?.toFixed(2)}s</div>
                        <div><strong>Status:</strong> <span class="text-success">✓ Success</span></div>
                        <div class="mt-4">
                            <strong>Stage Results:</strong>
                            <ul class="list-disc list-inside mt-2 space-y-1 text-xs">
                                ${data.stage_results ? Object.entries(data.stage_results).map(([stage, result]) => 
                                    `<li><strong>${stage}:</strong> ${result.status} (${(result.confidence * 100).toFixed(1)}%)</li>`
                                ).join('') : '<li>Stage details not available</li>'}
                            </ul>
                        </div>
                    </div>
                `;
            } else {
                output.innerHTML = `
                    <div class="text-error">
                        <strong>Test Failed:</strong> ${data.message || 'Unknown error occurred'}
                    </div>
                `;
            }
            
        } catch (error) {
            console.error('Test failed:', error);
            output.innerHTML = `
                <div class="text-error">
                    <strong>Test Error:</strong> ${error.message}
                </div>
            `;
        } finally {
            // Hide progress, show results
            progress.classList.add('hidden');
            results.classList.remove('hidden');
            runButton.disabled = false;
        }
    }
}

// Initialize wizard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new OnboardingWizard();
});