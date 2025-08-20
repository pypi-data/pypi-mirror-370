/**
 * MCP Configuration Management UI
 */

class MCPConfigManager {
    constructor() {
        this.apiUrl = '';
        this.currentServers = {};
        this.availableTools = {};
        this.init();
    }

    init() {
        this.loadMCPStatus();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Add server form
        document.getElementById('add-server-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.addServer();
        });

        // Refresh tools button
        document.getElementById('refresh-tools')?.addEventListener('click', () => {
            this.refreshTools();
        });

        // Server connect/disconnect buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('connect-server')) {
                this.connectServer(e.target.dataset.server);
            } else if (e.target.classList.contains('disconnect-server')) {
                this.disconnectServer(e.target.dataset.server);
            }
        });
    }

    async loadMCPStatus() {
        try {
            const response = await fetch('/api/mcp/status');
            const data = await response.json();
            
            if (data.success) {
                this.updateStatusDisplay(data.status);
                await this.loadServers();
                await this.loadTools();
            } else {
                this.showError('MCP support not available');
            }
        } catch (error) {
            console.error('Error loading MCP status:', error);
            this.showError('Failed to load MCP status');
        }
    }

    async loadServers() {
        try {
            const response = await fetch('/api/mcp/servers');
            const data = await response.json();
            
            if (data.success) {
                this.currentServers = data.servers;
                this.updateServersDisplay(data.servers);
                this.updateStatusDisplay(data.status);
            }
        } catch (error) {
            console.error('Error loading servers:', error);
            this.showError('Failed to load MCP servers');
        }
    }

    async loadTools() {
        try {
            const response = await fetch('/api/mcp/tools');
            const data = await response.json();
            
            if (data.success) {
                this.availableTools = data.tools_by_server;
                this.updateToolsDisplay(data.tools_by_server);
            }
        } catch (error) {
            console.error('Error loading tools:', error);
            // Don't show error for tools as servers might not be connected yet
        }
    }

    updateStatusDisplay(status) {
        const statusContainer = document.getElementById('mcp-status');
        if (!statusContainer) return;

        statusContainer.innerHTML = `
            <div class="row">
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">${status.total_servers || 0}</h5>
                            <p class="card-text">Total Servers</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title text-success">${status.enabled_servers || 0}</h5>
                            <p class="card-text">Enabled</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title text-info">${status.connected_servers || 0}</h5>
                            <p class="card-text">Connected</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title text-warning">${status.total_tools || 0}</h5>
                            <p class="card-text">Available Tools</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    updateServersDisplay(servers) {
        const serversContainer = document.getElementById('mcp-servers');
        if (!serversContainer) return;

        if (Object.keys(servers).length === 0) {
            serversContainer.innerHTML = '<p class="text-muted">No MCP servers configured.</p>';
            return;
        }

        const serversHtml = Object.entries(servers).map(([name, config]) => {
            const statusBadge = config.enabled ? 
                (config.connected ? '<span class="badge bg-success">Connected</span>' : '<span class="badge bg-warning">Disconnected</span>') :
                '<span class="badge bg-secondary">Disabled</span>';

            return `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-8">
                                <h5 class="card-title">
                                    ${name} ${statusBadge}
                                </h5>
                                <p class="card-text">${config.description || 'No description'}</p>
                                <small class="text-muted">Command: <code>${config.command}</code></small>
                            </div>
                            <div class="col-md-4 text-end">
                                ${config.enabled && !config.connected ? 
                                    `<button class="btn btn-outline-success btn-sm connect-server me-2" data-server="${name}">Connect</button>` :
                                    config.connected ? 
                                        `<button class="btn btn-outline-danger btn-sm disconnect-server me-2" data-server="${name}">Disconnect</button>` : ''
                                }
                                <button class="btn btn-outline-secondary btn-sm" onclick="mcpConfig.editServer('${name}')">Edit</button>
                            </div>
                        </div>
                        ${config.tools_count > 0 ? `<div class="mt-2"><small class="text-info">${config.tools_count} tools available</small></div>` : ''}
                    </div>
                </div>
            `;
        }).join('');

        serversContainer.innerHTML = serversHtml;
    }

    updateToolsDisplay(toolsByServer) {
        const toolsContainer = document.getElementById('available-tools');
        if (!toolsContainer) return;

        if (Object.keys(toolsByServer).length === 0) {
            toolsContainer.innerHTML = '<p class="text-muted">No tools available. Connect to MCP servers to see tools.</p>';
            return;
        }

        const toolsHtml = Object.entries(toolsByServer).map(([serverName, tools]) => {
            const toolsList = tools.map(tool => `
                <div class="col-md-6">
                    <div class="card mb-2">
                        <div class="card-body py-2">
                            <h6 class="card-title mb-1">${tool.name}</h6>
                            <p class="card-text small text-muted mb-0">${tool.description || 'No description'}</p>
                        </div>
                    </div>
                </div>
            `).join('');

            return `
                <div class="mb-4">
                    <h5>${serverName} (${tools.length} tools)</h5>
                    <div class="row">
                        ${toolsList}
                    </div>
                </div>
            `;
        }).join('');

        toolsContainer.innerHTML = toolsHtml;
    }

    async addServer() {
        const form = document.getElementById('add-server-form');
        const formData = new FormData(form);
        
        const serverConfig = {
            name: formData.get('name'),
            command: formData.get('command'),
            args: formData.get('args') ? formData.get('args').split(' ').filter(Boolean) : [],
            description: formData.get('description') || '',
            timeout: parseInt(formData.get('timeout')) || 30,
            enabled: formData.get('enabled') === 'on',
            env: {}
        };

        // Parse environment variables if any
        const envVars = formData.get('env');
        if (envVars) {
            envVars.split('\n').forEach(line => {
                const [key, value] = line.split('=');
                if (key && value) {
                    serverConfig.env[key.trim()] = value.trim();
                }
            });
        }

        try {
            const response = await fetch('/api/mcp/servers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(serverConfig)
            });

            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(data.message);
                form.reset();
                await this.loadServers();
            } else {
                this.showError(data.error || 'Failed to add server');
            }
        } catch (error) {
            console.error('Error adding server:', error);
            this.showError('Failed to add server');
        }
    }

    async connectServer(serverName) {
        try {
            const response = await fetch(`/api/mcp/servers/${serverName}/connect`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(data.message);
                await this.loadServers();
                await this.loadTools();
            } else {
                this.showError(data.message || 'Failed to connect to server');
            }
        } catch (error) {
            console.error('Error connecting server:', error);
            this.showError('Failed to connect to server');
        }
    }

    async disconnectServer(serverName) {
        try {
            const response = await fetch(`/api/mcp/servers/${serverName}/disconnect`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(data.message);
                await this.loadServers();
                await this.loadTools();
            } else {
                this.showError(data.message || 'Failed to disconnect from server');
            }
        } catch (error) {
            console.error('Error disconnecting server:', error);
            this.showError('Failed to disconnect from server');
        }
    }

    async refreshTools() {
        try {
            const response = await fetch('/api/mcp/refresh', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(data.message);
                await this.loadTools();
            } else {
                this.showError('Failed to refresh tools');
            }
        } catch (error) {
            console.error('Error refreshing tools:', error);
            this.showError('Failed to refresh tools');
        }
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showAlert(message, type) {
        const alertsContainer = document.getElementById('mcp-alerts') || document.body;
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        alertsContainer.appendChild(alert);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize MCP configuration manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.mcpConfig = new MCPConfigManager();
});
