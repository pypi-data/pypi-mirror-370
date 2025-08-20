// Task Monitor - Real-time monitoring for AI agent tasks

class TaskMonitor {
    constructor(sessionId, projectId) {
        this.sessionId = sessionId;
        this.projectId = projectId;
        this.socket = null;
        this.agents = {};
        this.interactions = [];
        this.messages = [];
        this.startTime = Date.now();
        this.humanInputPending = false;
        
        this.init();
    }
    
    init() {
        this.initWebSocket();
        this.bindEvents();
        this.loadSessionData();
        this.initAgentPositions();
        this.startMonitoring();
    }
    
    initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/task/${this.sessionId}`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('Connected to task monitor');
            this.updateChatStatus('connected');
            this.enableChat();
            
            // Join session room
            this.sendMessage({
                type: 'join_session',
                session_id: this.sessionId
            });
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.socket.onclose = () => {
            console.log('Disconnected from task monitor');
            this.updateChatStatus('disconnected');
            this.disableChat();
            
            // Try to reconnect after 3 seconds
            setTimeout(() => this.initWebSocket(), 3000);
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateChatStatus('error');
        };
    }
    
    handleWebSocketMessage(data) {
        const { type, payload } = data;
        
        switch (type) {
            case 'agent_started':
                this.handleAgentStarted(payload);
                break;
            case 'agent_progress':
                this.handleAgentProgress(payload);
                break;
            case 'agent_completed':
                this.handleAgentCompleted(payload);
                break;
            case 'agent_failed':
                this.handleAgentFailed(payload);
                break;
            case 'agent_interaction':
                this.handleAgentInteraction(payload);
                break;
            case 'agent_thinking':
                this.handleAgentThinking(payload);
                break;
            case 'human_input_required':
                this.handleHumanInputRequired(payload);
                break;
            case 'chat_message':
                this.handleChatMessage(payload);
                break;
            case 'console_output':
                this.handleConsoleOutput(payload);
                break;
            case 'file_created':
                this.handleFileCreated(payload);
                break;
            case 'error':
                this.handleError(payload);
                break;
            case 'task_completed':
                this.handleTaskCompleted(payload);
                break;
            case 'task_failed':
                this.handleTaskFailed(payload);
                break;
            case 'metrics_update':
                this.handleMetricsUpdate(payload);
                break;
        }
    }
    
    sendMessage(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        }
    }
    
    bindEvents() {
        // Cancel task button
        document.getElementById('cancelTask')?.addEventListener('click', () => {
            if (confirm('Are you sure you want to cancel this task?')) {
                this.cancelTask();
            }
        });
        
        // Chat input
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendMessage');
        
        if (chatInput && sendButton) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendChatMessage();
                }
            });
            
            sendButton.addEventListener('click', () => {
                this.sendChatMessage();
            });
        }
    }
    
    loadSessionData() {
        fetch(`/api/sessions/${this.sessionId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.updateTaskInfo(data.session);
                    if (data.session.status === 'completed') {
                        this.handleTaskCompleted(data.session);
                    }
                }
            })
            .catch(error => console.error('Error loading session data:', error));
    }
    
    updateTaskInfo(session) {
        const statusIndicator = document.getElementById('taskStatus');
        const taskDescription = document.getElementById('taskDescription');
        const startTime = document.getElementById('startTime');
        
        if (statusIndicator) {
            statusIndicator.className = `status-indicator ${session.status}`;
        }
        
        if (taskDescription && session.task_description) {
            taskDescription.textContent = session.task_description;
        }
        
        if (startTime && session.created_at) {
            startTime.textContent = new Date(session.created_at).toLocaleString();
        }
    }
    
    initAgentPositions() {
        // Initialize agent positions for interaction visualization
        const agents = ['planner', 'developer', 'tester', 'ui_ux_expert', 'db_expert', 'devops_expert'];
        const container = document.getElementById('interactionFlow');
        
        if (!container) return;
        
        const width = container.offsetWidth;
        const height = container.offsetHeight;
        
        // Position agents in a circle
        agents.forEach((agent, index) => {
            const angle = (index * 2 * Math.PI) / agents.length;
            const x = width / 2 + Math.cos(angle) * (Math.min(width, height) / 3);
            const y = height / 2 + Math.sin(angle) * (Math.min(width, height) / 3);
            
            this.agents[agent] = {
                x: x,
                y: y,
                status: 'idle',
                startTime: null,
                metrics: {}
            };
            
            // Create agent node in visualization
            this.createAgentNode(agent, x, y);
        });
    }
    
    createAgentNode(agent, x, y) {
        const container = document.getElementById('interactionFlow');
        if (!container) return;
        
        const node = document.createElement('div');
        node.className = 'agent-node';
        node.id = `node-${agent}`;
        node.style.position = 'absolute';
        node.style.left = `${x - 30}px`;
        node.style.top = `${y - 30}px`;
        node.style.width = '60px';
        node.style.height = '60px';
        node.style.borderRadius = '50%';
        node.style.background = '#fff';
        node.style.border = '3px solid #dee2e6';
        node.style.display = 'flex';
        node.style.alignItems = 'center';
        node.style.justifyContent = 'center';
        node.style.fontSize = '24px';
        node.style.zIndex = '10';
        node.style.transition = 'all 0.3s ease';
        
        // Add icon based on agent type
        const icons = {
            planner: '🧠',
            developer: '💻',
            tester: '🧪',
            ui_ux_expert: '🎨',
            db_expert: '🗄️',
            devops_expert: '⚙️'
        };
        
        node.innerHTML = icons[agent] || '🤖';
        node.title = agent.replace(/_/g, ' ').toUpperCase();
        
        container.appendChild(node);
    }
    
    handleAgentStarted(data) {
        const { agent, task, timestamp } = data;
        
        // Update agent card
        const agentCard = document.querySelector(`[data-agent="${agent}"]`);
        if (agentCard) {
            agentCard.classList.add('active');
            const status = agentCard.querySelector('.agent-status');
            if (status) {
                status.textContent = 'Running';
                status.className = 'badge bg-primary agent-status';
            }
            
            const activity = agentCard.querySelector('.agent-activity');
            if (activity) {
                activity.innerHTML = `<small class="text-primary">▶ ${task}</small>`;
            }
            
            const progressBar = agentCard.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = '25%';
            }
        }
        
        // Update visualization node
        const node = document.getElementById(`node-${agent}`);
        if (node) {
            node.style.border = '3px solid #0d6efd';
            node.style.background = 'rgba(13, 110, 253, 0.1)';
            node.style.transform = 'scale(1.2)';
        }
        
        // Add to timeline
        this.addTimelineEvent({
            agent: agent,
            event: 'started',
            task: task,
            timestamp: timestamp
        });
        
        // Store agent state
        if (this.agents[agent]) {
            this.agents[agent].status = 'running';
            this.agents[agent].startTime = Date.now();
        }
    }
    
    handleAgentProgress(data) {
        const { agent, message, progress, details } = data;
        
        // Update agent card
        const agentCard = document.querySelector(`[data-agent="${agent}"]`);
        if (agentCard) {
            const activity = agentCard.querySelector('.agent-activity');
            if (activity) {
                const newActivity = document.createElement('div');
                newActivity.innerHTML = `<small>• ${message}</small>`;
                activity.appendChild(newActivity);
                activity.scrollTop = activity.scrollHeight;
            }
            
            const progressBar = agentCard.querySelector('.progress-bar');
            if (progressBar && progress) {
                progressBar.style.width = `${progress}%`;
            }
        }
        
        // Update metrics if provided
        if (details && details.metrics) {
            this.updateAgentMetrics(agent, details.metrics);
        }
    }
    
    handleAgentThinking(data) {
        const { agent, thinking_about, reasoning_tokens } = data;
        
        // Show thinking indicator
        const agentCard = document.querySelector(`[data-agent="${agent}"]`);
        if (agentCard) {
            const activity = agentCard.querySelector('.agent-activity');
            if (activity) {
                const thinkingDiv = document.createElement('div');
                thinkingDiv.className = 'thinking-indicator';
                thinkingDiv.innerHTML = `
                    <small class="text-info">
                        <i class="fas fa-brain fa-pulse me-1"></i>
                        Thinking: ${thinking_about}
                        ${reasoning_tokens ? `(${reasoning_tokens} tokens)` : ''}
                    </small>
                `;
                activity.appendChild(thinkingDiv);
                activity.scrollTop = activity.scrollHeight;
            }
        }
    }
    
    handleAgentCompleted(data) {
        const { agent, result, timestamp } = data;
        
        // Update agent card
        const agentCard = document.querySelector(`[data-agent="${agent}"]`);
        if (agentCard) {
            agentCard.classList.remove('active');
            agentCard.classList.add('completed');
            
            const status = agentCard.querySelector('.agent-status');
            if (status) {
                status.textContent = 'Completed';
                status.className = 'badge bg-success agent-status';
            }
            
            const progressBar = agentCard.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = '100%';
            }
            
            // Update time metric
            if (this.agents[agent] && this.agents[agent].startTime) {
                const duration = Math.round((Date.now() - this.agents[agent].startTime) / 1000);
                const timeMetric = agentCard.querySelector('.metric-value');
                if (timeMetric && timeMetric.nextElementSibling?.textContent === 'Time') {
                    timeMetric.textContent = `${duration}s`;
                }
            }
        }
        
        // Update visualization node
        const node = document.getElementById(`node-${agent}`);
        if (node) {
            node.style.border = '3px solid #198754';
            node.style.background = 'rgba(25, 135, 84, 0.1)';
            node.style.transform = 'scale(1)';
        }
        
        // Add to timeline
        this.addTimelineEvent({
            agent: agent,
            event: 'completed',
            result: result,
            timestamp: timestamp
        });
    }
    
    handleAgentFailed(data) {
        const { agent, error, timestamp } = data;
        
        // Update agent card
        const agentCard = document.querySelector(`[data-agent="${agent}"]`);
        if (agentCard) {
            agentCard.classList.remove('active');
            agentCard.classList.add('failed');
            
            const status = agentCard.querySelector('.agent-status');
            if (status) {
                status.textContent = 'Failed';
                status.className = 'badge bg-danger agent-status';
            }
            
            const activity = agentCard.querySelector('.agent-activity');
            if (activity) {
                activity.innerHTML = `<small class="text-danger">❌ ${error}</small>`;
            }
        }
        
        // Update visualization node
        const node = document.getElementById(`node-${agent}`);
        if (node) {
            node.style.border = '3px solid #dc3545';
            node.style.background = 'rgba(220, 53, 69, 0.1)';
            node.style.transform = 'scale(1)';
        }
        
        // Add to timeline
        this.addTimelineEvent({
            agent: agent,
            event: 'failed',
            error: error,
            timestamp: timestamp
        });
        
        // Add to errors tab
        this.addError(agent, error);
    }
    
    handleAgentInteraction(data) {
        const { from_agent, to_agent, interaction_type, message } = data;
        
        // Draw interaction line
        this.drawInteraction(from_agent, to_agent, interaction_type);
        
        // Add to timeline
        this.addTimelineEvent({
            agent: from_agent,
            event: 'interaction',
            target: to_agent,
            type: interaction_type,
            message: message,
            timestamp: Date.now()
        });
        
        // Store interaction for visualization
        this.interactions.push({
            from: from_agent,
            to: to_agent,
            type: interaction_type,
            timestamp: Date.now()
        });
    }
    
    drawInteraction(fromAgent, toAgent, type) {
        const svg = document.getElementById('interactionSvg');
        if (!svg) return;
        
        const from = this.agents[fromAgent];
        const to = this.agents[toAgent];
        
        if (!from || !to) return;
        
        // Create animated line
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', from.x);
        line.setAttribute('y1', from.y);
        line.setAttribute('x2', to.x);
        line.setAttribute('y2', to.y);
        line.setAttribute('class', 'agent-interaction-line');
        
        // Color based on interaction type
        const colors = {
            'call': '#0d6efd',
            'response': '#198754',
            'error': '#dc3545',
            'data': '#ffc107'
        };
        line.style.stroke = colors[type] || '#6c757d';
        
        svg.appendChild(line);
        
        // Animate and remove after 3 seconds
        setTimeout(() => {
            line.style.opacity = '0';
            setTimeout(() => line.remove(), 500);
        }, 3000);
        
        // Create arrow marker
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.setAttribute('id', `arrow-${Date.now()}`);
        marker.setAttribute('markerWidth', '10');
        marker.setAttribute('markerHeight', '10');
        marker.setAttribute('refX', '9');
        marker.setAttribute('refY', '3');
        marker.setAttribute('orient', 'auto');
        marker.setAttribute('markerUnits', 'strokeWidth');
        
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', 'M0,0 L0,6 L9,3 z');
        path.setAttribute('fill', line.style.stroke);
        
        marker.appendChild(path);
        svg.appendChild(marker);
        
        line.setAttribute('marker-end', `url(#${marker.id})`);
    }
    
    handleHumanInputRequired(data) {
        const { agent, question, context, options } = data;
        
        this.humanInputPending = true;
        
        // Show notification
        this.showNotification('Human input required!', 'warning');
        
        // Add to chat as agent message
        this.addChatMessage({
            type: 'agent',
            agent: agent,
            message: question,
            requiresResponse: true,
            options: options
        });
        
        // Enable special input mode
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.disabled = false;
            chatInput.placeholder = 'Your response is required...';
            chatInput.focus();
            chatInput.classList.add('border-warning');
        }
        
        // Add to timeline
        this.addTimelineEvent({
            agent: agent,
            event: 'human_input_required',
            question: question,
            timestamp: Date.now()
        });
    }
    
    handleChatMessage(data) {
        this.addChatMessage(data);
    }
    
    addChatMessage(data) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;
        
        // Clear placeholder if exists
        const placeholder = chatMessages.querySelector('.text-center');
        if (placeholder) {
            placeholder.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${data.type}`;
        
        if (data.type === 'agent') {
            const agentIcons = {
                planner: '🧠',
                developer: '💻',
                tester: '🧪',
                ui_ux_expert: '🎨',
                db_expert: '🗄️',
                devops_expert: '⚙️'
            };
            
            messageDiv.innerHTML = `
                <div class="agent-avatar bg-primary text-white">
                    ${agentIcons[data.agent] || '🤖'}
                </div>
                <div class="message-bubble">
                    <small class="d-block mb-1 fw-bold">${data.agent?.replace(/_/g, ' ').toUpperCase() || 'AGENT'}</small>
                    ${data.message}
                    ${data.requiresResponse ? '<br><small class="text-warning mt-2 d-block">⚠️ Response required</small>' : ''}
                </div>
            `;
        } else if (data.type === 'human') {
            messageDiv.innerHTML = `
                <div class="message-bubble">
                    ${data.message}
                </div>
                <div class="agent-avatar bg-secondary text-white">
                    👤
                </div>
            `;
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Store message
        this.messages.push(data);
    }
    
    sendChatMessage() {
        const chatInput = document.getElementById('chatInput');
        if (!chatInput || !chatInput.value.trim()) return;
        
        const message = chatInput.value.trim();
        
        // Add to chat UI
        this.addChatMessage({
            type: 'human',
            message: message,
            timestamp: Date.now()
        });
        
        // Send to backend
        this.sendMessage({
            type: this.humanInputPending ? 'human_response' : 'chat_message',
            session_id: this.sessionId,
            message: message
        });
        
        // Clear input
        chatInput.value = '';
        
        // Reset human input mode if was pending
        if (this.humanInputPending) {
            this.humanInputPending = false;
            chatInput.classList.remove('border-warning');
            chatInput.placeholder = 'Type your message...';
        }
    }
    
    handleConsoleOutput(data) {
        const consoleOutput = document.getElementById('consoleOutput');
        if (!consoleOutput) return;
        
        const code = consoleOutput.querySelector('code');
        if (code) {
            // Append new output
            const timestamp = new Date().toLocaleTimeString();
            code.innerHTML += `\n[${timestamp}] ${data.output}`;
            
            // Auto-scroll to bottom
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }
    }
    
    handleFileCreated(data) {
        const { filename, path, size, agent } = data;
        
        const filesList = document.getElementById('filesList');
        if (!filesList) return;
        
        // Clear placeholder if exists
        const placeholder = filesList.querySelector('.text-muted');
        if (placeholder) {
            placeholder.remove();
        }
        
        // Create file entry
        const fileEntry = document.createElement('div');
        fileEntry.className = 'file-entry mb-2 p-2 border rounded';
        fileEntry.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <i class="fas fa-file-code me-2 text-primary"></i>
                    <strong>${filename}</strong>
                    <small class="text-muted ms-2">(${this.formatFileSize(size)})</small>
                    <br>
                    <small class="text-muted">Created by ${agent} • ${path}</small>
                </div>
                <button class="btn btn-sm btn-outline-primary" onclick="window.open('/api/sessions/${this.sessionId}/files/${filename}', '_blank')">
                    <i class="fas fa-eye"></i>
                </button>
            </div>
        `;
        
        filesList.appendChild(fileEntry);
        
        // Update file count in agent metrics
        this.updateAgentFileCount(agent);
    }
    
    handleError(data) {
        const { agent, error, severity } = data;
        
        this.addError(agent, error, severity);
        
        // Show notification for critical errors
        if (severity === 'critical') {
            this.showNotification(`Critical error in ${agent}: ${error}`, 'danger');
        }
    }
    
    addError(agent, error, severity = 'error') {
        const errorsList = document.getElementById('errorsList');
        if (!errorsList) return;
        
        // Clear placeholder if exists
        const placeholder = errorsList.querySelector('.text-muted');
        if (placeholder) {
            placeholder.remove();
        }
        
        const errorEntry = document.createElement('div');
        errorEntry.className = `alert alert-${severity === 'critical' ? 'danger' : 'warning'} mb-2`;
        errorEntry.innerHTML = `
            <div class="d-flex align-items-start">
                <i class="fas fa-exclamation-triangle me-2 mt-1"></i>
                <div>
                    <strong>${agent.replace(/_/g, ' ').toUpperCase()}</strong><br>
                    ${error}
                    <br>
                    <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                </div>
            </div>
        `;
        
        errorsList.appendChild(errorEntry);
    }
    
    handleTaskCompleted(data) {
        const statusIndicator = document.getElementById('taskStatus');
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator completed';
        }
        
        // Show download button
        const downloadBtn = document.getElementById('downloadResults');
        if (downloadBtn) {
            downloadBtn.style.display = 'inline-block';
            downloadBtn.onclick = () => {
                window.location.href = `/api/sessions/${this.sessionId}/download`;
            };
        }
        
        // Disable cancel button
        const cancelBtn = document.getElementById('cancelTask');
        if (cancelBtn) {
            cancelBtn.disabled = true;
        }
        
        // Show notification
        this.showNotification('Task completed successfully!', 'success');
        
        // Add final timeline event
        this.addTimelineEvent({
            event: 'task_completed',
            timestamp: Date.now()
        });
    }
    
    handleTaskFailed(data) {
        const statusIndicator = document.getElementById('taskStatus');
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator failed';
        }
        
        // Disable cancel button
        const cancelBtn = document.getElementById('cancelTask');
        if (cancelBtn) {
            cancelBtn.disabled = true;
        }
        
        // Show notification
        this.showNotification(`Task failed: ${data.error}`, 'danger');
        
        // Add to errors
        this.addError('System', data.error, 'critical');
        
        // Add final timeline event
        this.addTimelineEvent({
            event: 'task_failed',
            error: data.error,
            timestamp: Date.now()
        });
    }
    
    handleMetricsUpdate(data) {
        const { agent, metrics } = data;
        this.updateAgentMetrics(agent, metrics);
    }
    
    updateAgentMetrics(agent, metrics) {
        const agentCard = document.querySelector(`[data-agent="${agent}"]`);
        if (!agentCard) return;
        
        Object.entries(metrics).forEach(([key, value]) => {
            const metricElements = agentCard.querySelectorAll('.metric-item');
            metricElements.forEach(element => {
                const label = element.querySelector('.metric-label');
                const valueElement = element.querySelector('.metric-value');
                
                if (label && valueElement) {
                    const labelText = label.textContent.toLowerCase();
                    if (labelText === key.toLowerCase()) {
                        valueElement.textContent = value;
                    }
                }
            });
        });
    }
    
    updateAgentFileCount(agent) {
        const agentCard = document.querySelector(`[data-agent="${agent}"]`);
        if (!agentCard) return;
        
        const filesMetric = agentCard.querySelector('.metric-value');
        if (filesMetric && filesMetric.nextElementSibling?.textContent === 'Files') {
            const currentCount = parseInt(filesMetric.textContent) || 0;
            filesMetric.textContent = currentCount + 1;
        }
    }
    
    addTimelineEvent(event) {
        const timeline = document.getElementById('activityTimeline');
        if (!timeline) return;
        
        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item';
        
        const iconClass = {
            'started': 'fas fa-play text-primary',
            'completed': 'fas fa-check text-success',
            'failed': 'fas fa-times text-danger',
            'interaction': 'fas fa-exchange-alt text-info',
            'human_input_required': 'fas fa-user text-warning',
            'task_completed': 'fas fa-flag-checkered text-success',
            'task_failed': 'fas fa-exclamation-triangle text-danger'
        };
        
        const icon = iconClass[event.event] || 'fas fa-info-circle';
        
        let content = '';
        switch (event.event) {
            case 'started':
                content = `<strong>${event.agent}</strong> started: ${event.task}`;
                break;
            case 'completed':
                content = `<strong>${event.agent}</strong> completed`;
                break;
            case 'failed':
                content = `<strong>${event.agent}</strong> failed: ${event.error}`;
                break;
            case 'interaction':
                content = `<strong>${event.agent}</strong> → <strong>${event.target}</strong>: ${event.type}`;
                break;
            case 'human_input_required':
                content = `<strong>${event.agent}</strong> needs human input`;
                break;
            case 'task_completed':
                content = `<strong>Task completed successfully</strong>`;
                break;
            case 'task_failed':
                content = `<strong>Task failed:</strong> ${event.error}`;
                break;
        }
        
        timelineItem.innerHTML = `
            <div class="timeline-icon">
                <i class="${icon}"></i>
            </div>
            <div class="timeline-content">
                <div>${content}</div>
                <small class="text-muted">${new Date(event.timestamp || Date.now()).toLocaleTimeString()}</small>
            </div>
        `;
        
        timeline.insertBefore(timelineItem, timeline.firstChild);
        
        // Keep only last 50 events
        while (timeline.children.length > 50) {
            timeline.removeChild(timeline.lastChild);
        }
    }
    
    cancelTask() {
        this.sendMessage({
            type: 'cancel_task',
            session_id: this.sessionId
        });
        
        // Update UI
        const cancelBtn = document.getElementById('cancelTask');
        if (cancelBtn) {
            cancelBtn.disabled = true;
            cancelBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Cancelling...';
        }
    }
    
    enableChat() {
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendMessage');
        
        if (chatInput) chatInput.disabled = false;
        if (sendButton) sendButton.disabled = false;
    }
    
    disableChat() {
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendMessage');
        
        if (chatInput) chatInput.disabled = true;
        if (sendButton) sendButton.disabled = true;
    }
    
    updateChatStatus(status) {
        const chatStatus = document.getElementById('chatStatus');
        if (!chatStatus) return;
        
        const statusConfig = {
            'connected': { text: 'Connected', class: 'bg-success' },
            'disconnected': { text: 'Disconnected', class: 'bg-danger' },
            'error': { text: 'Error', class: 'bg-warning' }
        };
        
        const config = statusConfig[status] || statusConfig['disconnected'];
        chatStatus.textContent = config.text;
        chatStatus.className = `badge ${config.class}`;
    }
    
    showNotification(message, type = 'info') {
        // Create toast notification
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        const toastElement = document.createElement('div');
        toastElement.innerHTML = toastHtml;
        
        // Add to container
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
        }
        
        container.appendChild(toastElement.firstElementChild);
        
        // Show toast
        const toast = new bootstrap.Toast(toastElement.firstElementChild);
        toast.show();
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    startMonitoring() {
        // Poll for updates every 5 seconds as backup
        this.monitoringInterval = setInterval(() => {
            this.loadSessionData();
        }, 5000);
    }
    
    stopMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }
    }
    
    destroy() {
        this.stopMonitoring();
        if (this.socket) {
            this.socket.close();
        }
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TaskMonitor;
}
