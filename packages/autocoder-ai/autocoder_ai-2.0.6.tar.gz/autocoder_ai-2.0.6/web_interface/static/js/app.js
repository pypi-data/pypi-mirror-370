// Main JavaScript for AI Coding Agent System Web Interface

class AgentSystemApp {
    constructor() {
        this.socket = null;
        this.currentSession = null;
        this.init();
    }
    
    init() {
        this.initSocketIO();
        this.bindEvents();
    }
    
    initSocketIO() {
        // Use native WebSocket for FastAPI compatibility
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/socket.io/`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('Connected to AI Coding Agent System');
            this.showNotification('Connected to system', 'success');
        };
        
        this.socket.onclose = () => {
            console.log('Disconnected from system');
            this.showNotification('Disconnected from system', 'warning');
        };
        
        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showNotification('Connection error', 'danger');
        };
    }
    
    handleWebSocketMessage(data) {
        const { type } = data;
        
        switch (type) {
            case 'task_started':
                this.handleTaskStarted(data);
                break;
            case 'agent_progress':
                this.handleAgentProgress(data);
                break;
            case 'task_completed':
                this.handleTaskCompleted(data);
                break;
            case 'task_failed':
                this.handleTaskFailed(data);
                break;
            case 'error':
                this.showNotification(data.message, 'danger');
                break;
            case 'status':
                console.log('Status:', data.message);
                break;
            default:
                console.log('Unknown message type:', type, data);
        }
    }
    
    sendWebSocketMessage(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        } else {
            console.error('WebSocket not connected');
        }
    }
    
    bindEvents() {
        console.log('Binding events for AgentSystemApp');
        
        // Form submissions - use event delegation for dynamically created forms
        // Removed ajax-form handler to prevent modal refresh issues
        
        // Button clicks - check both target and parent elements for data-action
        document.addEventListener('click', (e) => {
            console.log('Click detected on:', e.target);
            
            let actionElement = e.target;
            
            // Check if clicked element has data-action
            if (actionElement.dataset.action) {
                console.log('Found action on target:', actionElement.dataset.action);
                this.handleButtonClick(actionElement);
                return;
            }
            
            // Check parent elements for data-action (in case icon was clicked)
            while (actionElement && actionElement !== document) {
                if (actionElement.dataset && actionElement.dataset.action) {
                    console.log('Found action on parent:', actionElement.dataset.action);
                    this.handleButtonClick(actionElement);
                    return;
                }
                actionElement = actionElement.parentElement;
            }
        });
        
        // Load projects on page load
        this.loadProjects();
        this.loadSystemStats();
    }
    
    handleTaskStarted(data) {
        const sessionId = data.session_id;
        this.currentSession = sessionId;
        
        // Join the session room for real-time updates
        this.socket.emit('join_session', { session_id: sessionId });
        
        // Show progress modal or update UI
        this.showTaskProgress(sessionId);
    }
    
    handleAgentProgress(data) {
        console.log(`Agent ${data.agent}: ${data.status} - ${data.message}`);
        this.updateAgentStatus(data.agent, data.status, data.message);
    }
    
    handleTaskCompleted(data) {
        console.log('Task completed:', data);
        this.showTaskResults(data);
        this.hideTaskProgress();
    }
    
    handleTaskFailed(data) {
        console.log('Task failed:', data.error);
        this.showNotification(`Task failed: ${data.error}`, 'danger');
        this.hideTaskProgress();
    }
    
    handleFormSubmit(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        const action = form.dataset.action;
        
        switch(action) {
            case 'create-project':
                this.createProject(data);
                break;
            case 'create-session':
                this.createSession(data);
                break;
            case 'execute-task':
                this.executeTask(data);
                break;
            case 'run-task':
                this.handleRunTask(data);
                break;
        }
    }
    
    handleButtonClick(button) {
        const action = button.dataset.action;
        const data = { ...button.dataset };
        
        console.log('Button clicked with action:', action);
        
        switch(action) {
            case 'create-project':
                console.log('Opening create project modal');
                this.showCreateProjectModal();
                break;
            case 'run-task':
                console.log('Opening run task modal');
                // Get project ID if available
                const projectId = button.dataset.projectId || null;
                this.showRunTaskModal(projectId);
                break;
            case 'view-logs':
                console.log('Opening logs modal');
                this.showLogsModal();
                break;
            case 'settings':
                console.log('Opening settings modal');
                this.showSettingsModal();
                break;
            case 'execute-task':
                this.executeTask(data);
                break;
            case 'cancel-task':
                this.cancelTask(data);
                break;
            case 'view-files':
                this.viewFiles(data);
                break;
            case 'save-settings':
                this.saveSettings();
                break;
            case 'reset-defaults':
                this.resetToDefaults();
                break;
            default:
                console.log('Unknown action:', action);
        }
    }
    
    createProject(data) {
        return fetch('/api/projects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                this.showNotification('Project created successfully', 'success');
                // Close modal and refresh projects
                const modal = document.querySelector('.modal.show');
                if (modal) {
                    const bootstrapModal = bootstrap.Modal.getInstance(modal);
                    bootstrapModal.hide();
                }
                this.loadProjects();
                return result;
            } else {
                this.showNotification(result.error, 'danger');
                throw new Error(result.error);
            }
        })
        .catch(error => {
            this.showNotification('Error creating project', 'danger');
            console.error(error);
            throw error;
        });
    }
    
    createSession(data) {
        const projectId = data.project_id;
        
        fetch(`/api/projects/${projectId}/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                this.showNotification('Session created successfully', 'success');
                
                // Refresh the tasks list if we're on a project page
                if (typeof loadProjectTasks === 'function') {
                    loadProjectTasks();
                }
                
                // Refresh projects list
                this.loadProjects();
                
                return result.session.id;
            } else {
                throw new Error(result.error);
            }
        })
        .then(sessionId => {
            // Automatically execute the task
            this.sendWebSocketMessage({
                type: 'execute_task',
                data: {
                    session_id: sessionId,
                    task_description: data.task_description
                }
            });
        })
        .catch(error => {
            this.showNotification('Error creating session', 'danger');
            console.error(error);
        });
    }
    
    executeTask(data) {
        const sessionId = data.session_id;
        const taskDescription = data.task_description;
        
        this.sendWebSocketMessage({
            type: 'execute_task',
            data: {
                session_id: sessionId,
                task_description: taskDescription
            }
        });
    }
    
    cancelTask(data) {
        const sessionId = data.session_id;
        this.sendWebSocketMessage({
            type: 'cancel_task',
            data: { session_id: sessionId }
        });
    }
    
    showTaskProgress(sessionId) {
        // Create or show progress modal
        let modal = document.getElementById('progressModal');
        if (!modal) {
            modal = this.createProgressModal();
            document.body.appendChild(modal);
        }
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Reset progress bars
        this.resetProgressBars();
    }
    
    hideTaskProgress() {
        const modal = document.getElementById('progressModal');
        if (modal) {
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
        }
    }
    
    createProgressModal() {
        const modal = document.createElement('div');
        modal.id = 'progressModal';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-cogs me-2"></i>
                            AI Agents Working...
                        </h5>
                    </div>
                    <div class="modal-body">
                        <div class="agent-progress mb-3" data-agent="planner">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="fw-bold">
                                    <i class="fas fa-brain me-2 text-danger"></i>
                                    Planner Agent
                                </span>
                                <span class="badge bg-secondary">Waiting</span>
                            </div>
                            <div class="progress">
                                <div class="progress-bar" style="width: 0%"></div>
                            </div>
                        </div>
                        
                        <div class="agent-progress mb-3" data-agent="developer">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="fw-bold">
                                    <i class="fas fa-code me-2 text-success"></i>
                                    Developer Agent
                                </span>
                                <span class="badge bg-secondary">Waiting</span>
                            </div>
                            <div class="progress">
                                <div class="progress-bar" style="width: 0%"></div>
                            </div>
                        </div>
                        
                        <div class="agent-progress mb-3" data-agent="ui_ux_expert">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="fw-bold">
                                    <i class="fas fa-palette me-2 text-warning"></i>
                                    UI/UX Expert
                                </span>
                                <span class="badge bg-secondary">Waiting</span>
                            </div>
                            <div class="progress">
                                <div class="progress-bar" style="width: 0%"></div>
                            </div>
                        </div>
                        
                        <div class="agent-progress mb-3" data-agent="db_expert">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="fw-bold">
                                    <i class="fas fa-database me-2 text-primary"></i>
                                    Database Expert
                                </span>
                                <span class="badge bg-secondary">Waiting</span>
                            </div>
                            <div class="progress">
                                <div class="progress-bar" style="width: 0%"></div>
                            </div>
                        </div>
                        
                        <div class="agent-progress mb-3" data-agent="tester">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="fw-bold">
                                    <i class="fas fa-vial me-2 text-info"></i>
                                    Tester Agent
                                </span>
                                <span class="badge bg-secondary">Waiting</span>
                            </div>
                            <div class="progress">
                                <div class="progress-bar" style="width: 0%"></div>
                            </div>
                        </div>
                        
                        <div class="agent-progress mb-3" data-agent="devops_expert">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="fw-bold">
                                    <i class="fas fa-server me-2 text-secondary"></i>
                                    DevOps Expert
                                </span>
                                <span class="badge bg-secondary">Waiting</span>
                            </div>
                            <div class="progress">
                                <div class="progress-bar" style="width: 0%"></div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-danger" data-action="cancel-task">
                            <i class="fas fa-stop me-2"></i>
                            Cancel Task
                        </button>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }
    
    resetProgressBars() {
        document.querySelectorAll('.agent-progress').forEach(element => {
            const badge = element.querySelector('.badge');
            const progressBar = element.querySelector('.progress-bar');
            
            badge.textContent = 'Waiting';
            badge.className = 'badge bg-secondary';
            progressBar.style.width = '0%';
        });
    }
    
    updateAgentStatus(agentName, status, message) {
        const agentElement = document.querySelector(`[data-agent="${agentName}"]`);
        if (!agentElement) return;
        
        const badge = agentElement.querySelector('.badge');
        const progressBar = agentElement.querySelector('.progress-bar');
        
        switch(status) {
            case 'started':
                badge.textContent = 'Running';
                badge.className = 'badge bg-primary';
                progressBar.style.width = '25%';
                break;
            case 'progress':
                badge.textContent = 'Working';
                badge.className = 'badge bg-info';
                progressBar.style.width = '50%';
                break;
            case 'completed':
                badge.textContent = 'Completed';
                badge.className = 'badge bg-success';
                progressBar.style.width = '100%';
                break;
            case 'failed':
                badge.textContent = 'Failed';
                badge.className = 'badge bg-danger';
                progressBar.style.width = '100%';
                break;
        }
        
        if (message) {
            // You could add a message display area here
            console.log(`${agentName}: ${message}`);
        }
    }
    
    showTaskResults(data) {
        this.showNotification('Task completed successfully!', 'success');
        
        // Display results in a modal or redirect to results page
        if (data.files_created && data.files_created.length > 0) {
            this.showFilesCreated(data.files_created);
        }
    }
    
    showFilesCreated(files) {
        const filesList = files.map(file => `<li class="list-group-item">${file}</li>`).join('');
        
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-file-code me-2"></i>
                            Files Generated
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>The following files were generated:</p>
                        <ul class="list-group">
                            ${filesList}
                        </ul>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="window.location.reload()">
                            Refresh Page
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Remove modal from DOM when hidden
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
    
    showNotification(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // Add to toast container or create one
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        const bootstrapToast = new bootstrap.Toast(toast);
        bootstrapToast.show();
        
        // Remove toast from DOM when hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    viewFiles(data) {
        const sessionId = data.session_id;
        // Implementation for viewing generated files
        window.open(`/api/sessions/${sessionId}/files`, '_blank');
    }
    
    handleRunTask(data) {
        // If we have a project_id, create a session under that project
        // Otherwise, create a new project
        if (data.project_id) {
            // Create session under existing project
            this.createSession({
                project_id: data.project_id,
                task_description: data.task_description,
                context: {
                    enable_git: data.enable_git === 'on',
                    test_code: data.test_code === 'on'
                }
            });
        } else {
            // Create a new project first, then run the task
            const projectName = `Task: ${data.task_description.substring(0, 50)}...`;
            
            this.createProject({
                name: projectName,
                description: data.task_description
            }).then((result) => {
                // Create session under the new project
                if (result && result.project) {
                    this.createSession({
                        project_id: result.project.id,
                        task_description: data.task_description,
                        context: {
                            enable_git: data.enable_git === 'on',
                            test_code: data.test_code === 'on'
                        }
                    });
                }
            });
        }
    }
    
    loadProjects() {
        fetch('/api/projects')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.displayProjects(data.projects);
                    this.updateStats(data.projects);
                } else {
                    console.error('Failed to load projects:', data.error);
                }
            })
            .catch(error => {
                console.error('Error loading projects:', error);
                const container = document.getElementById('recentProjects');
                if (container) {
                    container.innerHTML = `
                        <div class="text-center py-4">
                            <i class="fas fa-exclamation-triangle text-warning fa-2x mb-2"></i>
                            <p class="text-muted">Failed to load projects</p>
                        </div>
                    `;
                }
            });
    }
    
    displayProjects(projects) {
        const container = document.getElementById('recentProjects');
        if (!container) return;
        
        if (projects.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-folder-open text-muted fa-2x mb-2"></i>
                    <p class="text-muted">No projects yet</p>
                    <button class="btn btn-primary btn-sm" data-action="create-project">
                        <i class="fas fa-plus me-1"></i>
                        Create Your First Project
                    </button>
                </div>
            `;
            return;
        }
        
        const projectsHtml = projects.slice(0, 5).map(project => `
            <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                <div>
                    <h6 class="mb-1">${project.name}</h6>
                    <small class="text-muted">${project.description || 'No description'}</small>
                </div>
                <div>
                    <span class="badge bg-${project.status === 'active' ? 'success' : 'secondary'}">${project.status}</span>
                    <button class="btn btn-sm btn-outline-primary ms-2" onclick="window.location.href='/project/${project.id}'">
                        View
                    </button>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = projectsHtml;
    }
    
    updateStats(projects) {
        const totalProjects = document.getElementById('totalProjects');
        if (totalProjects) totalProjects.textContent = projects.length;
        
        const activeSessions = projects.reduce((total, project) => {
            return total + (project.sessions ? project.sessions.filter(s => s.status === 'running').length : 0);
        }, 0);
        const activeSessionsEl = document.getElementById('activeSessions');
        if (activeSessionsEl) activeSessionsEl.textContent = activeSessions;
        
        const completedTasks = projects.reduce((total, project) => {
            return total + (project.sessions ? project.sessions.filter(s => s.status === 'completed').length : 0);
        }, 0);
        const completedTasksEl = document.getElementById('completedTasks');
        if (completedTasksEl) completedTasksEl.textContent = completedTasks;
        
        const filesGeneratedEl = document.getElementById('filesGenerated');
        if (filesGeneratedEl) filesGeneratedEl.textContent = completedTasks * 3; // Rough estimate
    }
    
    loadSystemStats() {
        fetch('/api/config')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const agentCount = data.config.agents.length;
                    const agentStatusEl = document.getElementById('agentStatus');
                    if (agentStatusEl) agentStatusEl.textContent = `${agentCount} Active`;
                }
            })
            .catch(error => {
                console.error('Error loading config:', error);
            });
    }
    
    showCreateProjectModal() {
        // Remove any existing modal
        const existingModal = document.getElementById('createProjectModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        const modal = document.createElement('div');
        modal.id = 'createProjectModal';
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-plus me-2"></i>
                            Create New Project
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form data-action="create-project" id="createProjectForm">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label for="projectName" class="form-label">Project Name</label>
                                <input type="text" class="form-control" id="projectName" name="name" required autocomplete="off">
                            </div>
                            <div class="mb-3">
                                <label for="projectDescription" class="form-label">Description</label>
                                <textarea class="form-control" id="projectDescription" name="description" rows="3" autocomplete="off"></textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-primary">Create Project</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal, {
            backdrop: 'static',
            keyboard: false
        });
        
        // Handle form submission
        const form = modal.querySelector('#createProjectForm');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.handleFormSubmit(form);
            return false;
        });
        
        bootstrapModal.show();
        
        // Focus on the first input field
        modal.addEventListener('shown.bs.modal', () => {
            const firstInput = modal.querySelector('#projectName');
            if (firstInput) {
                firstInput.focus();
            }
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
    
    showRunTaskModal(projectId = null) {
        // Remove any existing modal
        const existingModal = document.getElementById('runTaskModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        const modal = document.createElement('div');
        modal.id = 'runTaskModal';
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-play me-2"></i>
                            Run New Task
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form id="runTaskForm">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label for="taskDescription" class="form-label">Task Description</label>
                                <textarea class="form-control" id="taskDescription" name="task_description" rows="4" 
                                          placeholder="Describe what you want the AI agents to build..." required autocomplete="off"></textarea>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="enableGit" name="enable_git" checked>
                                        <label class="form-check-label" for="enableGit">
                                            <i class="fab fa-git-alt me-1"></i>
                                            Enable Git Integration
                                        </label>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="testCode" name="test_code" checked>
                                        <label class="form-check-label" for="testCode">
                                            <i class="fas fa-vial me-1"></i>
                                            Test Generated Code
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-rocket me-2"></i>
                                Start Task
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal, {
            backdrop: 'static',
            keyboard: false
        });
        
        // Handle form submission
        const form = modal.querySelector('#runTaskForm');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            // Get form data
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // Add project ID if provided
            if (projectId) {
                data.project_id = projectId;
            }
            
            // Call the handler
            await this.handleRunTask(data);
            
            // Close the modal
            bootstrapModal.hide();
            return false;
        });
        
        bootstrapModal.show();
        
        // Focus on the textarea
        modal.addEventListener('shown.bs.modal', () => {
            const textarea = modal.querySelector('#taskDescription');
            if (textarea) {
                textarea.focus();
            }
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
    
    showLogsModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-list me-2"></i>
                            System Logs
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="bg-dark text-light p-3 rounded" style="height: 400px; overflow-y: auto; font-family: monospace;">
                            <div id="logContent">Loading logs...</div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="this.closest('.modal-body').querySelector('#logContent').innerHTML='Logs refreshed at ' + new Date().toLocaleTimeString()">
                            Refresh
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Simulate log content
        setTimeout(() => {
            const logEl = document.getElementById('logContent');
            if (logEl) {
                logEl.innerHTML = `
                    <div>[${new Date().toISOString()}] INFO: SQLite memory persistence tables initialized</div>
                    <div>[${new Date().toISOString()}] INFO: Web interface started on port 5000</div>
                    <div>[${new Date().toISOString()}] INFO: 6 AI agents loaded and ready</div>
                    <div>[${new Date().toISOString()}] INFO: Code execution sandbox initialized</div>
                    <div>[${new Date().toISOString()}] INFO: Git integration ready</div>
                    <div class="text-success">[${new Date().toISOString()}] INFO: System fully operational</div>
                `;
            }
        }, 1000);
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
    
    showSettingsModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-cog me-2"></i>
                            Agent System Settings
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Navigation Tabs -->
                        <ul class="nav nav-pills mb-4" id="settingsTabs" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button class="nav-link active" id="general-tab" data-bs-toggle="pill" data-bs-target="#general" type="button" role="tab">
                                    <i class="fas fa-cog me-1"></i>General
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="providers-tab" data-bs-toggle="pill" data-bs-target="#providers" type="button" role="tab">
                                    <i class="fas fa-server me-1"></i>Providers
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="agents-tab" data-bs-toggle="pill" data-bs-target="#agents" type="button" role="tab">
                                    <i class="fas fa-users me-1"></i>Agents
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="templates-tab" data-bs-toggle="pill" data-bs-target="#templates" type="button" role="tab">
                                    <i class="fas fa-magic me-1"></i>Templates
                                </button>
                            </li>
                        </ul>
                        
                        <!-- Tab Content -->
                        <div class="tab-content" id="settingsTabContent">
                            <!-- General Settings Tab -->
                            <div class="tab-pane fade show active" id="general" role="tabpanel">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-globe me-2"></i>Project Settings</h6>
                                        <hr>
                                        
                                        <div class="mb-3">
                                            <label for="outputDir" class="form-label">Output Directory</label>
                                            <input type="text" class="form-control" id="outputDir" value="output">
                                        </div>
                                        
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="enableLogging" checked>
                                                <label class="form-check-label" for="enableLogging">
                                                    <i class="fas fa-file-alt me-1"></i>
                                                    Verbose Logging
                                                </label>
                                            </div>
                                        </div>
                                        
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="autoGit" checked>
                                                <label class="form-check-label" for="autoGit">
                                                    <i class="fab fa-git-alt me-1"></i>
                                                    Auto-enable Git
                                                </label>
                                            </div>
                                        </div>
                                        
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="enableCodeTesting" checked>
                                                <label class="form-check-label" for="enableCodeTesting">
                                                    <i class="fas fa-vial me-1"></i>
                                                    Auto-test Generated Code
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-brain me-2"></i>Global AI Settings</h6>
                                        <hr>
                                        
                                        <div class="mb-3">
                                            <label for="globalTemperature" class="form-label">Default Temperature</label>
                                            <input type="range" class="form-range" id="globalTemperature" 
                                                   min="0" max="2" step="0.1" value="0" 
                                                   oninput="this.nextElementSibling.textContent = this.value">
                                            <small class="text-muted">0</small>
                                        </div>
                                        
                                        <div class="mb-3">
                                            <label for="globalMaxTokens" class="form-label">Default Max Tokens</label>
                                            <input type="number" class="form-control" id="globalMaxTokens" value="2048" min="128" max="8192" step="128">
                                        </div>
                                        
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="enableGlobalReasoning" checked>
                                                <label class="form-check-label" for="enableGlobalReasoning">
                                                    <i class="fas fa-lightbulb me-1"></i>
                                                    Enable Global AI Reasoning
                                                </label>
                                            </div>
                                            <small class="text-muted">Enable thinking blocks for supported models</small>
                                        </div>
                                        
                                        <div class="mb-3">
                                            <label for="globalThinkingBudget" class="form-label">Global Thinking Token Budget</label>
                                            <input type="number" class="form-control" id="globalThinkingBudget" value="2048" min="512" max="8192" step="256">
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Providers Tab -->
                            <div class="tab-pane fade" id="providers" role="tabpanel">
                                <div class="row">
                                    <div class="col-12">
                                        <h6><i class="fas fa-server me-2"></i>LLM Providers Configuration</h6>
                                        <hr>
                                        <div id="providersContainer">
                                            <!-- Provider configs will be loaded here -->
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Agents Tab -->
                            <div class="tab-pane fade" id="agents" role="tabpanel">
                                <div class="row">
                                    <div class="col-12">
                                        <h6><i class="fas fa-users-cog me-2"></i>Per-Agent Model Configuration</h6>
                                        <hr>
                                    </div>
                                </div>
                                <div class="row" id="agentConfigs">
                                    <!-- Agent configs will be dynamically loaded here -->
                                </div>
                            </div>
                            
                            <!-- Templates Tab -->
                            <div class="tab-pane fade" id="templates" role="tabpanel">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-magic me-2"></i>Configuration Templates</h6>
                                        <hr>
                                        
                                        <div class="mb-3">
                                            <button class="btn btn-outline-primary w-100" data-template="speed" onclick="window.agentApp.applyConfigTemplate('speed')">
                                                <i class="fas fa-rocket me-2"></i>
                                                Speed Optimized
                                                <small class="d-block text-muted">Fast models, low reasoning</small>
                                            </button>
                                        </div>
                                        <div class="mb-3">
                                            <button class="btn btn-outline-success w-100" data-template="quality" onclick="window.agentApp.applyConfigTemplate('quality')">
                                                <i class="fas fa-star me-2"></i>
                                                Quality Focused
                                                <small class="d-block text-muted">Premium models, high reasoning</small>
                                            </button>
                                        </div>
                                        <div class="mb-3">
                                            <button class="btn btn-outline-info w-100" data-template="reasoning" onclick="window.agentApp.applyConfigTemplate('reasoning')">
                                                <i class="fas fa-brain me-2"></i>
                                                Reasoning Enhanced
                                                <small class="d-block text-muted">Reasoning-capable models only</small>
                                            </button>
                                        </div>
                                        <div class="mb-3">
                                            <button class="btn btn-outline-warning w-100" data-template="balanced" onclick="window.agentApp.applyConfigTemplate('balanced')">
                                                <i class="fas fa-balance-scale me-2"></i>
                                                Balanced
                                                <small class="d-block text-muted">Mix of speed and quality</small>
                                            </button>
                                        </div>
                                    </div>
                                    
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-info-circle me-2"></i>Template Details</h6>
                                        <hr>
                                        <div class="alert alert-info">
                                            <h6>How Templates Work:</h6>
                                            <ul class="mb-0">
                                                <li><strong>Speed:</strong> Uses GPT-3.5 Turbo for all agents, minimal reasoning</li>
                                                <li><strong>Quality:</strong> Uses premium models (GPT-4, Claude) with high reasoning</li>
                                                <li><strong>Reasoning:</strong> Only reasoning-capable models with maximum thinking</li>
                                                <li><strong>Balanced:</strong> Mix of models optimized for each agent's role</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Per-Agent Configuration -->
                        <div class="row mt-4">
                            <div class="col-12">
                                <h6><i class="fas fa-users-cog me-2"></i>Per-Agent Model Configuration</h6>
                                <hr>
                            </div>
                        </div>
                        
                        <div class="row" id="agentConfigs">
                            <!-- Agent configs will be dynamically loaded here -->
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-warning" data-action="reset-defaults">
                            <i class="fas fa-undo me-1"></i>
                            Reset to Defaults
                        </button>
                        <button type="button" class="btn btn-primary" data-action="save-settings">
                            <i class="fas fa-save me-1"></i>
                            Save Settings
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal);
        
        // Load current settings and agent configurations after DOM is ready
        setTimeout(() => {
            this.loadSettingsData(modal);
        }, 50);
        
        // Bind reasoning enable/disable toggle
        const reasoningCheckbox = modal.querySelector('#enableReasoning');
        const reasoningSettings = modal.querySelector('#reasoningSettings');
        if (reasoningCheckbox && reasoningSettings) {
            reasoningCheckbox.addEventListener('change', (e) => {
                reasoningSettings.style.display = e.target.checked ? 'block' : 'none';
            });
        }
        
        bootstrapModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
    
    async loadSettingsData(modal) {
        try {
            // First load current configuration from backend
            const response = await fetch('/api/config');
            const data = await response.json();
            
            if (data.success && data.config) {
                this.currentConfig = data.config.current_settings || {};
                console.log('Loaded current config:', this.currentConfig);
            }
            
            // Load provider configurations
            this.loadProviderConfigs(modal);
            
            // Load agent configurations
            this.loadAgentConfigs(modal);
            
            // Apply saved settings from backend
            this.applySavedSettings(modal);
        } catch (error) {
            console.error('Error loading settings data:', error);
        }
    }
    
    loadProviderConfigs(modal) {
        const providers = [
            { 
                name: 'OpenAI', 
                key: 'openai', 
                icon: 'fas fa-robot',
                models: ['gpt-5', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-chat', 'o1', 'o1-mini', 'o3-mini', 'o4-mini', 'gpt-4', 'gpt-4-turbo', 'gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'],
                apiKeyVar: 'OPENAI_API_KEY',
                description: 'Latest GPT-5 and o-series reasoning models with advanced capabilities',
                reasoning: true
            },
            { 
                name: 'Anthropic', 
                key: 'anthropic', 
                icon: 'fas fa-brain',
                models: ['claude-4-opus', 'claude-4-sonnet', 'claude-3-7-sonnet-20250219', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307', 'claude-3-opus-20240229'],
                apiKeyVar: 'ANTHROPIC_API_KEY',
                description: 'Advanced reasoning with latest Claude 4 and safety-focused models',
                reasoning: true
            },
            { 
                name: 'DeepSeek', 
                key: 'deepseek', 
                icon: 'fas fa-search',
                models: ['deepseek-r1', 'deepseek-chat', 'deepseek-coder'],
                apiKeyVar: 'DEEPSEEK_API_KEY',
                description: 'Open-source R1 reasoning model competing with o1, coding-focused',
                reasoning: true
            },
            { 
                name: 'Google', 
                key: 'google', 
                icon: 'fab fa-google',
                models: ['gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-2.5-deep-think', 'gemini-2.0-flash', 'gemini-2.0-flash-thinking', 'gemini-2.0-pro-experimental', 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro'],
                apiKeyVar: 'GOOGLE_API_KEY',
                description: 'Latest Gemini 2.5 with thinking capabilities and multimodal reasoning',
                reasoning: true
            },
            { 
                name: 'XAI', 
                key: 'xai', 
                icon: 'fas fa-times',
                models: ['grok-3', 'grok-beta', 'grok-vision-beta'],
                apiKeyVar: 'XAI_API_KEY',
                description: 'Latest Grok 3 with real-time reasoning and unfiltered responses',
                reasoning: true
            },
            { 
                name: 'Mistral', 
                key: 'mistral', 
                icon: 'fas fa-wind',
                models: ['mistral-small-3.1', 'mistral-medium-3', 'mistral-large', 'mistral-medium', 'mistral-small', 'mistral-7b-instruct', 'mistral-8x7b-instruct'],
                apiKeyVar: 'MISTRAL_API_KEY',
                description: 'European AI models with latest 2025 releases, efficient and lightweight'
            }
        ];
        
        const container = modal.querySelector('#providersContainer');
        container.innerHTML = providers.map(provider => `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-6">
                            <h6 class="card-title mb-1">
                                <i class="${provider.icon} me-2 text-primary"></i>
                                ${provider.name}
                                ${provider.reasoning ? '<span class="badge bg-info ms-2">Reasoning</span>' : ''}
                            </h6>
                            <p class="card-text small text-muted mb-3">${provider.description}</p>
                            
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="provider_${provider.key}" data-provider="${provider.key}">
                                <label class="form-check-label" for="provider_${provider.key}">
                                    Enable ${provider.name}
                                </label>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="provider-config" id="config_${provider.key}" style="display: none;">
                                <div class="mb-2">
                                    <label for="apikey_${provider.key}" class="form-label small">API Key</label>
                                    <div class="input-group">
                                        <input type="password" class="form-control form-control-sm" 
                                               id="apikey_${provider.key}" placeholder="Enter ${provider.apiKeyVar}">
                                        <button class="btn btn-outline-secondary btn-sm" type="button" 
                                                onclick="this.previousElementSibling.type = this.previousElementSibling.type === 'password' ? 'text' : 'password'">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                        <button class="btn btn-outline-primary btn-sm update-models-btn" type="button" 
                                                data-provider="${provider.key}" onclick="app.updateProviderModels('${provider.key}')">
                                            <i class="fas fa-sync-alt"></i>
                                        </button>
                                    </div>
                                    <small class="text-muted">Environment variable: ${provider.apiKeyVar}</small>
                                </div>
                                
                                <div class="mb-2">
                                    <label class="form-label small">Available Models</label>
                                    <div class="d-flex justify-content-between align-items-center mb-2">
                                        <button class="btn btn-outline-secondary btn-sm" type="button" 
                                                onclick="app.selectAllModels('${provider.key}', true)">
                                            <i class="fas fa-check-square me-1"></i>Select All
                                        </button>
                                        <button class="btn btn-outline-secondary btn-sm" type="button" 
                                                onclick="app.selectAllModels('${provider.key}', false)">
                                            <i class="fas fa-square me-1"></i>Unselect All
                                        </button>
                                    </div>
                                    <div class="models-loading" id="loading_${provider.key}" style="display: none;">
                                        <div class="text-center p-2">
                                            <i class="fas fa-spinner fa-spin me-2"></i>
                                            <small class="text-muted">Fetching models...</small>
                                        </div>
                                    </div>
                                    <div class="models-list" id="models_${provider.key}" style="max-height: 200px; overflow-y: auto;">
                                        ${provider.models.map(model => `
                                            <div class="form-check form-check-sm">
                                                <input class="form-check-input" type="checkbox" 
                                                       id="model_${provider.key}_${model}" 
                                                       data-provider="${provider.key}" 
                                                       data-model="${model}" checked>
                                                <label class="form-check-label small" for="model_${provider.key}_${model}">
                                                    ${model}
                                                </label>
                                            </div>
                                        `).join('')}
                                    </div>
                                    <div class="models-updated" id="updated_${provider.key}" style="display: none;">
                                        <small class="text-success">
                                            <i class="fas fa-check-circle me-1"></i>
                                            Models updated from API
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Add event listeners for provider toggles with delay
        setTimeout(() => {
            providers.forEach(provider => {
                const checkbox = modal.querySelector(`#provider_${provider.key}`);
                const config = modal.querySelector(`#config_${provider.key}`);
                
                if (checkbox && config) {
                    checkbox.addEventListener('change', (e) => {
                        config.style.display = e.target.checked ? 'block' : 'none';
                        this.updateAvailableModels(modal);
                    });
                }
            });
        }, 100);
    }
    
    loadAgentConfigs(modal) {
        const agentConfigs = [
            { name: 'Planner', key: 'planner', icon: 'fas fa-sitemap', description: 'Strategic planning and task breakdown' },
            { name: 'Developer', key: 'developer', icon: 'fas fa-code', description: 'Core code implementation' },
            { name: 'Tester', key: 'tester', icon: 'fas fa-bug', description: 'Testing strategy and QA' },
            { name: 'UI/UX Expert', key: 'ui_ux_expert', icon: 'fas fa-paint-brush', description: 'User interface and experience' },
            { name: 'DB Expert', key: 'db_expert', icon: 'fas fa-database', description: 'Database design and optimization' },
            { name: 'DevOps Expert', key: 'devops_expert', icon: 'fas fa-server', description: 'Deployment and infrastructure' }
        ];
        
        const container = modal.querySelector('#agentConfigs');
        container.innerHTML = agentConfigs.map((agent, index) => `
            <div class="col-md-6 mb-4">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="${agent.icon} me-2 text-primary"></i>
                            ${agent.name}
                        </h6>
                        <p class="card-text small text-muted">${agent.description}</p>
                        
                        <div class="mb-2">
                            <label for="model_${agent.key}" class="form-label small">Model</label>
                            <select class="form-select form-select-sm" id="model_${agent.key}" data-agent="${agent.key}">
                                <option value="">Select a model...</option>
                            </select>
                        </div>
                        
                        <div class="mb-2">
                            <label for="temp_${agent.key}" class="form-label small">Temperature</label>
                            <input type="range" class="form-range" id="temp_${agent.key}" 
                                   min="0" max="2" step="0.1" value="0" 
                                   oninput="this.nextElementSibling.textContent = this.value">
                            <small class="text-muted">0</small>
                        </div>
                        
                        <div class="mb-2">
                            <label for="max_tokens_${agent.key}" class="form-label small">Max Tokens</label>
                            <input type="number" class="form-control form-control-sm" 
                                   id="max_tokens_${agent.key}" value="2048" min="128" max="8192" step="128">
                        </div>
                        
                        <div class="mb-2">
                            <div class="form-check form-check-sm">
                                <input class="form-check-input" type="checkbox" id="reasoning_${agent.key}">
                                <label class="form-check-label small" for="reasoning_${agent.key}">
                                    Enable reasoning for this agent
                                </label>
                            </div>
                        </div>
                        
                        <div class="reasoning-config" id="reasoning_config_${agent.key}" style="display: none;">
                            <div class="mb-2">
                                <label for="reasoning_effort_${agent.key}" class="form-label small">Reasoning Effort</label>
                                <select class="form-select form-select-sm" id="reasoning_effort_${agent.key}">
                                    <option value="low">Low - Fast reasoning</option>
                                    <option value="medium" selected>Medium - Balanced</option>
                                    <option value="high">High - Deep reasoning</option>
                                </select>
                            </div>
                            
                            <div class="mb-2">
                                <label for="thinking_budget_${agent.key}" class="form-label small">Thinking Budget</label>
                                <input type="number" class="form-control form-control-sm" 
                                       id="thinking_budget_${agent.key}" value="2048" min="512" max="8192" step="256">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Add event listeners for reasoning toggles with delay
        setTimeout(() => {
            agentConfigs.forEach(agent => {
                const reasoningCheckbox = modal.querySelector(`#reasoning_${agent.key}`);
                const reasoningConfig = modal.querySelector(`#reasoning_config_${agent.key}`);
                
                if (reasoningCheckbox && reasoningConfig) {
                    reasoningCheckbox.addEventListener('change', (e) => {
                        reasoningConfig.style.display = e.target.checked ? 'block' : 'none';
                    });
                }
            });
        }, 100);
        
        // Initial load of available models with delay
        setTimeout(() => {
            this.updateAvailableModels(modal);
        }, 150);
    }
    
    updateAvailableModels(modal) {
        if (!modal) return;
        
        const agentKeys = ['planner', 'developer', 'tester', 'ui_ux_expert', 'db_expert', 'devops_expert'];
        const enabledProviders = [];
        
        // Get enabled providers and their models
        ['openai', 'anthropic', 'deepseek', 'google', 'xai', 'mistral'].forEach(provider => {
            const checkbox = modal.querySelector(`#provider_${provider}`);
            if (checkbox && checkbox.checked) {
                const models = [];
                modal.querySelectorAll(`input[data-provider="${provider}"][data-model]`).forEach(modelCheckbox => {
                    if (modelCheckbox.checked) {
                        models.push({
                            value: `${provider}/${modelCheckbox.dataset.model}`,
                            text: `${provider.charAt(0).toUpperCase() + provider.slice(1)} ${modelCheckbox.dataset.model}`
                        });
                    }
                });
                enabledProviders.push(...models);
            }
        });
        
        // Update agent model dropdowns
        agentKeys.forEach(agentKey => {
            const select = modal.querySelector(`#model_${agentKey}`);
            if (select) {
                const currentValue = select.value;
                select.innerHTML = '<option value="">Select a model...</option>';
                
                enabledProviders.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.value;
                    option.textContent = model.text;
                    if (model.value === currentValue) {
                        option.selected = true;
                    }
                    select.appendChild(option);
                });
            }
        });
    }
    
    applyConfigTemplate(template) {
        const modal = document.querySelector('.modal.show');
        if (!modal) return;
        
        const templates = {
            speed: {
                global_reasoning: false,
                global_temperature: 0.3,
                providers: ['openai'],
                models: { 
                    planner: 'openai/gpt-3.5-turbo', 
                    developer: 'openai/gpt-3.5-turbo',
                    tester: 'openai/gpt-3.5-turbo',
                    ui_ux_expert: 'openai/gpt-3.5-turbo',
                    db_expert: 'openai/gpt-3.5-turbo',
                    devops_expert: 'openai/gpt-3.5-turbo'
                },
                reasoning: {}
            },
            quality: {
                global_reasoning: true,
                global_temperature: 0,
                providers: ['openai', 'anthropic'],
                models: { 
                    planner: 'anthropic/claude-3-7-sonnet-20250219', 
                    developer: 'anthropic/claude-3-7-sonnet-20250219',
                    tester: 'openai/gpt-4',
                    ui_ux_expert: 'anthropic/claude-3-sonnet-20240229',
                    db_expert: 'openai/gpt-4',
                    devops_expert: 'openai/gpt-4'
                },
                reasoning: {
                    planner: { enabled: true, effort: 'high', budget: 4096 },
                    developer: { enabled: true, effort: 'high', budget: 4096 },
                    tester: { enabled: false, effort: 'medium', budget: 2048 },
                    ui_ux_expert: { enabled: true, effort: 'medium', budget: 2048 },
                    db_expert: { enabled: false, effort: 'medium', budget: 2048 },
                    devops_expert: { enabled: false, effort: 'low', budget: 1024 }
                }
            },
            reasoning: {
                global_reasoning: true,
                global_temperature: 0,
                providers: ['anthropic', 'deepseek', 'xai'],
                models: { 
                    planner: 'anthropic/claude-3-7-sonnet-20250219', 
                    developer: 'deepseek/deepseek-chat',
                    tester: 'anthropic/claude-3-7-sonnet-20250219',
                    ui_ux_expert: 'anthropic/claude-3-7-sonnet-20250219',
                    db_expert: 'deepseek/deepseek-chat',
                    devops_expert: 'xai/grok-beta'
                },
                reasoning: {
                    planner: { enabled: true, effort: 'high', budget: 8192 },
                    developer: { enabled: true, effort: 'high', budget: 8192 },
                    tester: { enabled: true, effort: 'medium', budget: 4096 },
                    ui_ux_expert: { enabled: true, effort: 'high', budget: 4096 },
                    db_expert: { enabled: true, effort: 'high', budget: 8192 },
                    devops_expert: { enabled: true, effort: 'medium', budget: 2048 }
                }
            },
            balanced: {
                global_reasoning: true,
                global_temperature: 0,
                providers: ['openai', 'anthropic'],
                models: { 
                    planner: 'openai/gpt-4', 
                    developer: 'anthropic/claude-3-7-sonnet-20250219',
                    tester: 'openai/gpt-4-turbo',
                    ui_ux_expert: 'anthropic/claude-3-sonnet-20240229',
                    db_expert: 'openai/gpt-4',
                    devops_expert: 'openai/gpt-4-turbo'
                },
                reasoning: {
                    planner: { enabled: true, effort: 'medium', budget: 2048 },
                    developer: { enabled: true, effort: 'high', budget: 4096 },
                    tester: { enabled: false, effort: 'low', budget: 1024 },
                    ui_ux_expert: { enabled: true, effort: 'medium', budget: 2048 },
                    db_expert: { enabled: false, effort: 'medium', budget: 2048 },
                    devops_expert: { enabled: false, effort: 'low', budget: 1024 }
                }
            }
        };
        
        const config = templates[template];
        if (!config) return;
        
        // Apply global settings
        const globalReasoningCheckbox = modal.querySelector('#enableGlobalReasoning');
        const globalTempSlider = modal.querySelector('#globalTemperature');
        
        if (globalReasoningCheckbox) globalReasoningCheckbox.checked = config.global_reasoning;
        if (globalTempSlider) {
            globalTempSlider.value = config.global_temperature;
            globalTempSlider.nextElementSibling.textContent = config.global_temperature;
        }
        
        // Enable required providers
        config.providers.forEach(provider => {
            const checkbox = modal.querySelector(`#provider_${provider}`);
            const configDiv = modal.querySelector(`#config_${provider}`);
            if (checkbox) {
                checkbox.checked = true;
                if (configDiv) {
                    configDiv.style.display = 'block';
                }
            }
        });
        
        // Update models after enabling providers
        this.updateAvailableModels(modal);
        
        // Wait for models to update, then apply settings
        setTimeout(() => {
            // Apply per-agent settings
            Object.entries(config.models).forEach(([agent, model]) => {
                const modelSelect = modal.querySelector(`#model_${agent}`);
                const tempSlider = modal.querySelector(`#temp_${agent}`);
                const reasoningCheck = modal.querySelector(`#reasoning_${agent}`);
                
                if (modelSelect) modelSelect.value = model;
                if (tempSlider) {
                    tempSlider.value = config.global_temperature;
                    tempSlider.nextElementSibling.textContent = config.global_temperature;
                }
                
                const agentReasoning = config.reasoning[agent];
                if (reasoningCheck && agentReasoning) {
                    reasoningCheck.checked = agentReasoning.enabled;
                    
                    // Trigger reasoning config visibility
                    const reasoningConfig = modal.querySelector(`#reasoning_config_${agent}`);
                    if (reasoningConfig) {
                        reasoningConfig.style.display = agentReasoning.enabled ? 'block' : 'none';
                        
                        const effortSelect = modal.querySelector(`#reasoning_effort_${agent}`);
                        const budgetInput = modal.querySelector(`#thinking_budget_${agent}`);
                        
                        if (effortSelect) effortSelect.value = agentReasoning.effort;
                        if (budgetInput) budgetInput.value = agentReasoning.budget;
                    }
                }
            });
            
            this.showNotification(`Applied ${template} configuration template`, 'success');
        }, 100);
    }
    
    saveSettings() {
        const modal = document.querySelector('.modal.show');
        if (!modal) return;
        
        // Collect all settings
        const settings = {
            global: {
                output_dir: modal.querySelector('#outputDir').value,
                verbose_logging: modal.querySelector('#enableLogging').checked,
                auto_git: modal.querySelector('#autoGit').checked,
                auto_test_code: modal.querySelector('#enableCodeTesting').checked,
                default_temperature: parseFloat(modal.querySelector('#globalTemperature').value),
                default_max_tokens: parseInt(modal.querySelector('#globalMaxTokens').value),
                global_reasoning: modal.querySelector('#enableGlobalReasoning').checked,
                global_thinking_budget: parseInt(modal.querySelector('#globalThinkingBudget').value)
            },
            providers: {},
            agents: {}
        };
        
        // Collect provider settings
        ['openai', 'anthropic', 'deepseek', 'google', 'xai', 'mistral'].forEach(provider => {
            const checkbox = modal.querySelector(`#provider_${provider}`);
            if (checkbox && checkbox.checked) {
                const apiKey = modal.querySelector(`#apikey_${provider}`).value;
                const enabledModels = [];
                
                modal.querySelectorAll(`input[data-provider="${provider}"][data-model]`).forEach(modelCheckbox => {
                    if (modelCheckbox.checked) {
                        enabledModels.push(modelCheckbox.dataset.model);
                    }
                });
                
                settings.providers[provider] = {
                    enabled: true,
                    api_key: apiKey,
                    models: enabledModels
                };
            }
        });
        
        // Collect per-agent settings
        const agents = ['planner', 'developer', 'tester', 'ui_ux_expert', 'db_expert', 'devops_expert'];
        agents.forEach(agent => {
            const modelSelect = modal.querySelector(`#model_${agent}`);
            const tempSlider = modal.querySelector(`#temp_${agent}`);
            const maxTokensInput = modal.querySelector(`#max_tokens_${agent}`);
            const reasoningCheck = modal.querySelector(`#reasoning_${agent}`);
            
            settings.agents[agent] = {
                model: modelSelect ? modelSelect.value : '',
                temperature: tempSlider ? parseFloat(tempSlider.value) : 0,
                max_tokens: maxTokensInput ? parseInt(maxTokensInput.value) : 2048,
                reasoning_enabled: reasoningCheck ? reasoningCheck.checked : false
            };
            
            // Add reasoning-specific settings if enabled
            if (reasoningCheck && reasoningCheck.checked) {
                const effortSelect = modal.querySelector(`#reasoning_effort_${agent}`);
                const budgetInput = modal.querySelector(`#thinking_budget_${agent}`);
                
                settings.agents[agent].reasoning = {
                    effort: effortSelect ? effortSelect.value : 'medium',
                    thinking_budget: budgetInput ? parseInt(budgetInput.value) : 2048
                };
            }
        });
        
        console.log('Saving settings:', settings);
        
        // Save to backend
        fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                this.showNotification('Settings saved successfully!', 'success');
                bootstrap.Modal.getInstance(modal).hide();
            } else {
                this.showNotification('Error saving settings: ' + result.error, 'danger');
            }
        })
        .catch(error => {
            console.error('Error saving settings:', error);
            this.showNotification('Error saving settings', 'danger');
        });
    }
    
    resetToDefaults() {
        if (confirm('Reset all settings to defaults? This cannot be undone.')) {
            const modal = document.querySelector('.modal.show');
            if (!modal) return;
            
            // Reset global settings
            modal.querySelector('#outputDir').value = 'output';
            modal.querySelector('#enableLogging').checked = true;
            modal.querySelector('#autoGit').checked = true;
            modal.querySelector('#enableCodeTesting').checked = true;
            modal.querySelector('#globalTemperature').value = 0;
            modal.querySelector('#globalTemperature').nextElementSibling.textContent = '0';
            modal.querySelector('#globalMaxTokens').value = 2048;
            modal.querySelector('#enableGlobalReasoning').checked = false;
            modal.querySelector('#globalThinkingBudget').value = 2048;
            
            // Reset provider settings
            ['openai', 'anthropic', 'deepseek', 'google', 'xai', 'mistral'].forEach(provider => {
                const checkbox = modal.querySelector(`#provider_${provider}`);
                const config = modal.querySelector(`#config_${provider}`);
                const apiKeyInput = modal.querySelector(`#apikey_${provider}`);
                if (checkbox) {
                    checkbox.checked = provider === 'openai'; // Only enable OpenAI by default
                    if (config) {
                        config.style.display = provider === 'openai' ? 'block' : 'none';
                    }
                    if (apiKeyInput) {
                        apiKeyInput.value = ''; // Clear API key
                    }
                }
            });
            
            // Update available models
            this.updateAvailableModels(modal);
            
            // Reset agent settings
            const agents = ['planner', 'developer', 'tester', 'ui_ux_expert', 'db_expert', 'devops_expert'];
            agents.forEach(agent => {
                const tempSlider = modal.querySelector(`#temp_${agent}`);
                const maxTokensInput = modal.querySelector(`#max_tokens_${agent}`);
                const reasoningCheck = modal.querySelector(`#reasoning_${agent}`);
                const reasoningConfig = modal.querySelector(`#reasoning_config_${agent}`);
                
                if (tempSlider) {
                    tempSlider.value = 0;
                    tempSlider.nextElementSibling.textContent = '0';
                }
                if (maxTokensInput) maxTokensInput.value = 2048;
                if (reasoningCheck) reasoningCheck.checked = false;
                if (reasoningConfig) reasoningConfig.style.display = 'none';
            });
            
            this.showNotification('Settings reset to defaults', 'info');
        }
    }
    
    // Add new method to handle select/unselect all models
    selectAllModels(providerKey, selectAll) {
        const modelsList = document.getElementById(`models_${providerKey}`);
        if (!modelsList) return;
        
        const checkboxes = modelsList.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectAll;
        });
        
        // Update available models for agent dropdowns
        const modal = modelsList.closest('.modal-content');
        if (modal) {
            this.updateAvailableModels(modal);
        }
    }
    
    // Add new method to apply saved settings from backend
    applySavedSettings(modal) {
        if (!this.currentConfig) return;
        
        // Apply global settings
        const globalSettings = this.currentConfig.global_settings || {};
        if (modal.querySelector('#outputDir')) {
            modal.querySelector('#outputDir').value = globalSettings.output_dir || 'output';
        }
        if (modal.querySelector('#enableLogging')) {
            modal.querySelector('#enableLogging').checked = globalSettings.verbose_logging !== false;
        }
        if (modal.querySelector('#autoGit')) {
            modal.querySelector('#autoGit').checked = globalSettings.auto_git !== false;
        }
        if (modal.querySelector('#enableCodeTesting')) {
            modal.querySelector('#enableCodeTesting').checked = globalSettings.auto_test_code !== false;
        }
        if (modal.querySelector('#globalTemperature')) {
            const temp = globalSettings.default_temperature || 0;
            modal.querySelector('#globalTemperature').value = temp;
            modal.querySelector('#globalTemperature').nextElementSibling.textContent = temp;
        }
        if (modal.querySelector('#globalMaxTokens')) {
            modal.querySelector('#globalMaxTokens').value = globalSettings.default_max_tokens || 2048;
        }
        
        // Apply provider settings
        const providers = this.currentConfig.providers || {};
        Object.entries(providers).forEach(([providerKey, providerConfig]) => {
            const checkbox = modal.querySelector(`#provider_${providerKey}`);
            const configDiv = modal.querySelector(`#config_${providerKey}`);
            const apiKeyInput = modal.querySelector(`#apikey_${providerKey}`);
            
            if (checkbox && providerConfig.enabled) {
                checkbox.checked = true;
                if (configDiv) {
                    configDiv.style.display = 'block';
                }
                if (apiKeyInput && providerConfig.api_key) {
                    apiKeyInput.value = providerConfig.api_key;
                }
                
                // Apply model selections
                if (providerConfig.models && Array.isArray(providerConfig.models)) {
                    // First uncheck all models for this provider
                    modal.querySelectorAll(`input[data-provider="${providerKey}"][data-model]`).forEach(modelCheckbox => {
                        modelCheckbox.checked = false;
                    });
                    
                    // Then check only the saved models
                    providerConfig.models.forEach(modelId => {
                        const modelCheckbox = modal.querySelector(`#model_${providerKey}_${modelId}`);
                        if (modelCheckbox) {
                            modelCheckbox.checked = true;
                        }
                    });
                }
            }
        });
        
        // Apply agent settings
        const agents = this.currentConfig.agents || {};
        Object.entries(agents).forEach(([agentKey, agentConfig]) => {
            const modelConfig = agentConfig.model || {};
            const reasoningConfig = agentConfig.reasoning || {};
            
            // Set temperature
            const tempSlider = modal.querySelector(`#temp_${agentKey}`);
            if (tempSlider && modelConfig.temperature !== undefined) {
                tempSlider.value = modelConfig.temperature;
                tempSlider.nextElementSibling.textContent = modelConfig.temperature;
            }
            
            // Set max tokens
            const maxTokensInput = modal.querySelector(`#max_tokens_${agentKey}`);
            if (maxTokensInput && modelConfig.max_tokens) {
                maxTokensInput.value = modelConfig.max_tokens;
            }
            
            // Set reasoning
            const reasoningCheck = modal.querySelector(`#reasoning_${agentKey}`);
            const reasoningConfigDiv = modal.querySelector(`#reasoning_config_${agentKey}`);
            if (reasoningCheck && reasoningConfig.enabled !== undefined) {
                reasoningCheck.checked = reasoningConfig.enabled;
                if (reasoningConfigDiv) {
                    reasoningConfigDiv.style.display = reasoningConfig.enabled ? 'block' : 'none';
                }
            }
        });
        
        // Update available models after applying settings
        setTimeout(() => {
            this.updateAvailableModels(modal);
            
            // Set agent model selections
            Object.entries(agents).forEach(([agentKey, agentConfig]) => {
                const modelConfig = agentConfig.model || {};
                const modelSelect = modal.querySelector(`#model_${agentKey}`);
                if (modelSelect && modelConfig.provider && modelConfig.model) {
                    const modelValue = `${modelConfig.provider}/${modelConfig.model}`;
                    modelSelect.value = modelValue;
                }
            });
        }, 100);
    }
    
    async updateProviderModels(providerKey) {
        console.log('Updating models for provider:', providerKey);
        
        const apiKeyInput = document.getElementById(`apikey_${providerKey}`);
        const loadingDiv = document.getElementById(`loading_${providerKey}`);
        const modelsList = document.getElementById(`models_${providerKey}`);
        const updatedDiv = document.getElementById(`updated_${providerKey}`);
        const updateBtn = document.querySelector(`[data-provider="${providerKey}"].update-models-btn`);
        
        if (!apiKeyInput || !apiKeyInput.value.trim()) {
            this.showNotification('Please enter an API key first', 'warning');
            return;
        }
        
        // Show loading state
        if (loadingDiv) loadingDiv.style.display = 'block';
        if (modelsList) modelsList.style.display = 'none';
        if (updatedDiv) updatedDiv.style.display = 'none';
        if (updateBtn) {
            updateBtn.disabled = true;
            const icon = updateBtn.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-spinner fa-spin';
            }
        }
        
        try {
            // Prepare request data
            const requestData = {
                api_key: apiKeyInput.value.trim()
            };
            
            // Add base_url for providers that need it
            if (providerKey === 'ollama') {
                requestData.base_url = 'http://localhost:11434';
            }
            // For openai_compatible, we would need a base_url input - for now skip this provider type
            if (providerKey === 'openai_compatible') {
                this.showNotification('OpenAI Compatible provider needs base_url configuration', 'info');
                return;
            }
            
            const response = await fetch(`/api/providers/${providerKey}/test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            
            if (data.success && data.models) {
                this.displayFetchedModels(providerKey, data.models);
                this.showNotification(`Successfully fetched ${data.models.length} models`, 'success');
                if (updatedDiv) updatedDiv.style.display = 'block';
            } else {
                throw new Error(data.error || 'Failed to fetch models');
            }
            
        } catch (error) {
            console.error('Error updating models:', error);
            this.showNotification(`Failed to update models: ${error.message}`, 'danger');
            
            // Restore original models list
            if (modelsList) modelsList.style.display = 'block';
            
        } finally {
            // Hide loading state
            if (loadingDiv) loadingDiv.style.display = 'none';
            if (updateBtn) {
                updateBtn.disabled = false;
                const icon = updateBtn.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-sync-alt';
                }
            }
        }
    }
    
    displayFetchedModels(providerKey, models) {
        const modelsList = document.getElementById(`models_${providerKey}`);
        if (!modelsList || !models || models.length === 0) return;
        
        // Clear existing models
        modelsList.innerHTML = '';
        
        // Add fetched models
        models.forEach(model => {
            const modelDiv = document.createElement('div');
            modelDiv.className = 'form-check form-check-sm';
            
            const reasoningIcon = model.supports_reasoning ? 
                '<i class="fas fa-brain text-info ms-1" title="Supports reasoning/thinking"></i>' : '';
            const visionIcon = model.supports_vision ? 
                '<i class="fas fa-image text-success ms-1" title="Supports images/vision"></i>' : '';
            
            modelDiv.innerHTML = `
                <input class="form-check-input" type="checkbox" 
                       id="model_${providerKey}_${model.id}" 
                       data-provider="${providerKey}" 
                       data-model="${model.id}" 
                       data-reasoning="${model.supports_reasoning}" 
                       data-vision="${model.supports_vision || false}"
                       checked>
                <label class="form-check-label small d-flex align-items-center" for="model_${providerKey}_${model.id}">
                    ${model.name || model.id}
                    ${reasoningIcon}
                    ${visionIcon}
                </label>
            `;
            
            modelsList.appendChild(modelDiv);
        });
        
        // Show the updated models list
        modelsList.style.display = 'block';
        
        // Update available models for agent dropdowns
        const modal = modelsList.closest('.modal-content');
        if (modal) {
            this.updateAvailableModels(modal);
        }
    }
    
    // Image Upload functionality
    initImageUpload() {
        const imageUploadArea = document.getElementById('imageUploadArea');
        const imageInput = document.getElementById('imageInput');
        const uploadedImages = document.getElementById('uploadedImages');
        const imagePreview = document.getElementById('imagePreview');
        
        if (!imageUploadArea || !imageInput) return;
        
        // Drag and drop handling
        imageUploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            imageUploadArea.classList.add('dragover');
        });
        
        imageUploadArea.addEventListener('dragleave', () => {
            imageUploadArea.classList.remove('dragover');
        });
        
        imageUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            imageUploadArea.classList.remove('dragover');
            const files = Array.from(e.dataTransfer.files);
            this.handleImageFiles(files);
        });
        
        // File input change
        imageInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.handleImageFiles(files);
        });
        
        // Click to upload
        imageUploadArea.addEventListener('click', () => {
            imageInput.click();
        });
    }
    
    async handleImageFiles(files) {
        for (const file of files) {
            if (!file.type.startsWith('image/')) {
                this.showNotification('Please select only image files', 'warning');
                continue;
            }
            
            if (file.size > 10 * 1024 * 1024) { // 10MB limit
                this.showNotification('Image size must be less than 10MB', 'warning');
                continue;
            }
            
            await this.uploadImage(file);
        }
    }
    
    async uploadImage(file) {
        try {
            // Show upload progress
            const uploadId = Date.now().toString();
            this.showImageUploadProgress(uploadId, file.name);
            
            // Get presigned upload URL
            const response = await fetch('/api/images/upload-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: file.name
                })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to get upload URL');
            }
            
            // Check if this is a local upload URL or cloud presigned URL
            if (data.upload_url.startsWith('/local-upload/')) {
                // Local upload - use multipart form
                const formData = new FormData();
                formData.append('file', file);
                
                const uploadResponse = await fetch(data.upload_url, {
                    method: 'POST',
                    body: formData
                });
                
                if (!uploadResponse.ok) {
                    throw new Error('Failed to upload image locally');
                }
            } else {
                // Cloud upload - use presigned URL
                const uploadResponse = await fetch(data.upload_url, {
                    method: 'PUT',
                    body: file,
                    headers: {
                        'Content-Type': file.type
                    }
                });
                
                if (!uploadResponse.ok) {
                    throw new Error('Failed to upload image to cloud');
                }
            }
            
            // Store image metadata
            const metadataResponse = await fetch('/api/images/metadata', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: file.name,
                    upload_url: data.upload_url,
                    content_type: file.type,
                    session_id: this.currentSessionId || null
                })
            });
            
            if (metadataResponse.ok) {
                this.addImageToPreview(file, data.upload_url);
                this.showNotification(`Image "${file.name}" uploaded successfully`, 'success');
            }
            
            this.removeImageUploadProgress(uploadId);
            
        } catch (error) {
            console.error('Image upload error:', error);
            this.showNotification(`Failed to upload "${file.name}": ${error.message}`, 'danger');
            this.removeImageUploadProgress(uploadId);
        }
    }
    
    showImageUploadProgress(uploadId, filename) {
        const progressDiv = document.createElement('div');
        progressDiv.id = `upload-progress-${uploadId}`;
        progressDiv.className = 'upload-progress mb-2';
        progressDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                <small>Uploading "${filename}"...</small>
            </div>
        `;
        
        const uploadedImages = document.getElementById('uploadedImages');
        if (uploadedImages) {
            uploadedImages.appendChild(progressDiv);
        }
    }
    
    removeImageUploadProgress(uploadId) {
        const progressDiv = document.getElementById(`upload-progress-${uploadId}`);
        if (progressDiv) {
            progressDiv.remove();
        }
    }
    
    addImageToPreview(file, uploadUrl) {
        const uploadedImages = document.getElementById('uploadedImages');
        if (!uploadedImages) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const imageDiv = document.createElement('div');
            imageDiv.className = 'uploaded-image mb-2 p-2 border rounded';
            imageDiv.innerHTML = `
                <div class="d-flex align-items-center">
                    <img src="${e.target.result}" alt="${file.name}" class="img-thumbnail me-2" style="width: 50px; height: 50px; object-fit: cover;">
                    <div class="flex-grow-1">
                        <div class="fw-bold">${file.name}</div>
                        <small class="text-muted">${(file.size / 1024 / 1024).toFixed(2)} MB</small>
                    </div>
                    <button type="button" class="btn btn-outline-danger btn-sm" onclick="this.parentElement.parentElement.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            
            uploadedImages.appendChild(imageDiv);
        };
        reader.readAsDataURL(file);
        
        // Store image info for task execution
        if (!this.uploadedImages) {
            this.uploadedImages = [];
        }
        this.uploadedImages.push({
            filename: file.name,
            size: file.size,
            type: file.type,
            upload_url: uploadUrl
        });
        
        // Show the uploaded images section
        const uploadedImagesDiv = document.getElementById('uploadedImages');
        if (uploadedImagesDiv) {
            uploadedImagesDiv.style.display = 'block';
        }
    }
    
    getUploadedImages() {
        return this.uploadedImages || [];
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AgentSystemApp();
    window.app.initImageUpload();
});