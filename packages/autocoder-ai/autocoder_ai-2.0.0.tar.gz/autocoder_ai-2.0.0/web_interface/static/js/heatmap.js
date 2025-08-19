/**
 * Task Progress Heatmap Visualization
 * Interactive heatmap showing task execution patterns and system activity
 */

class TaskHeatmap {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            hours: options.hours || 24,
            cellSize: options.cellSize || 20,
            refreshInterval: options.refreshInterval || 30000, // 30 seconds
            ...options
        };
        
        this.data = [];
        this.colorScale = {
            inactive: '#ebedf0',
            low: '#c6e48b', 
            medium: '#7bc96f',
            high: '#239a3b',
            peak: '#196127'
        };
        
        this.init();
    }
    
    async init() {
        this.createHeatmapStructure();
        await this.loadData();
        this.render();
        this.startAutoRefresh();
    }
    
    createHeatmapStructure() {
        this.container.innerHTML = `
            <div class="heatmap-header">
                <div class="heatmap-title">
                    <h4>Task Progress Heatmap</h4>
                    <div class="heatmap-controls">
                        <select class="form-select form-select-sm" id="heatmap-hours">
                            <option value="6">Last 6 hours</option>
                            <option value="12">Last 12 hours</option>
                            <option value="24" selected>Last 24 hours</option>
                            <option value="48">Last 48 hours</option>
                            <option value="168">Last week</option>
                        </select>
                        <button class="btn btn-sm btn-outline-primary" id="heatmap-refresh">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>
                </div>
                <div class="heatmap-legend">
                    <span class="legend-label">Less</span>
                    <div class="legend-colors">
                        <div class="legend-color" style="background-color: ${this.colorScale.inactive}"></div>
                        <div class="legend-color" style="background-color: ${this.colorScale.low}"></div>
                        <div class="legend-color" style="background-color: ${this.colorScale.medium}"></div>
                        <div class="legend-color" style="background-color: ${this.colorScale.high}"></div>
                        <div class="legend-color" style="background-color: ${this.colorScale.peak}"></div>
                    </div>
                    <span class="legend-label">More</span>
                </div>
            </div>
            <div class="heatmap-grid" id="heatmap-grid"></div>
            <div class="heatmap-stats" id="heatmap-stats"></div>
            <div class="heatmap-tooltip" id="heatmap-tooltip"></div>
        `;
        
        // Add event listeners
        document.getElementById('heatmap-hours').addEventListener('change', (e) => {
            this.options.hours = parseInt(e.target.value);
            this.loadData();
        });
        
        document.getElementById('heatmap-refresh').addEventListener('click', () => {
            this.loadData();
        });
    }
    
    async loadData() {
        try {
            const response = await fetch(`/api/heatmap/data?hours_back=${this.options.hours}`, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                this.data = result.heatmap_data;
                this.render();
                await this.loadStats();
            } else {
                console.error('Failed to load heatmap data:', response.statusText);
                this.showError('Failed to load heatmap data');
            }
        } catch (error) {
            console.error('Error loading heatmap data:', error);
            this.showError('Error connecting to heatmap service');
        }
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/heatmap/stats', {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const stats = await response.json();
                this.renderStats(stats);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    render() {
        const grid = document.getElementById('heatmap-grid');
        if (!grid || !this.data.length) return;
        
        // Group data by day and hour
        const timeSlots = this.organizeTimeSlots();
        
        grid.innerHTML = '';
        
        // Create time axis
        this.createTimeAxis(grid, timeSlots);
        
        // Create heatmap cells
        this.createHeatmapCells(grid, timeSlots);
    }
    
    organizeTimeSlots() {
        const slots = new Map();
        
        this.data.forEach(item => {
            const date = new Date(item.time_slot + ':00');
            const dayKey = date.toDateString();
            const hour = date.getHours();
            const minute = Math.floor(date.getMinutes() / 5) * 5;
            
            if (!slots.has(dayKey)) {
                slots.set(dayKey, new Map());
            }
            
            const timeKey = `${hour}:${minute.toString().padStart(2, '0')}`;
            slots.get(dayKey).set(timeKey, item);
        });
        
        return slots;
    }
    
    createTimeAxis(container, timeSlots) {
        const timeAxis = document.createElement('div');
        timeAxis.className = 'heatmap-time-axis';
        
        // Hour labels
        for (let hour = 0; hour < 24; hour += 3) {
            const label = document.createElement('div');
            label.className = 'time-label';
            label.textContent = `${hour}:00`;
            label.style.left = `${(hour / 24) * 100}%`;
            timeAxis.appendChild(label);
        }
        
        container.appendChild(timeAxis);
    }
    
    createHeatmapCells(container, timeSlots) {
        const heatmapRows = document.createElement('div');
        heatmapRows.className = 'heatmap-rows';
        
        Array.from(timeSlots.keys()).reverse().forEach(dayKey => {
            const row = document.createElement('div');
            row.className = 'heatmap-row';
            
            // Day label
            const dayLabel = document.createElement('div');
            dayLabel.className = 'day-label';
            dayLabel.textContent = new Date(dayKey).toLocaleDateString('en', { 
                weekday: 'short', 
                month: 'short', 
                day: 'numeric' 
            });
            row.appendChild(dayLabel);
            
            // Hour cells
            const cellsContainer = document.createElement('div');
            cellsContainer.className = 'heatmap-cells';
            
            for (let hour = 0; hour < 24; hour++) {
                for (let minute = 0; minute < 60; minute += 5) {
                    const timeKey = `${hour}:${minute.toString().padStart(2, '0')}`;
                    const cellData = timeSlots.get(dayKey)?.get(timeKey);
                    
                    const cell = document.createElement('div');
                    cell.className = 'heatmap-cell';
                    cell.style.backgroundColor = this.getCellColor(cellData);
                    
                    if (cellData) {
                        cell.setAttribute('data-activity', this.getCellActivity(cellData));
                        cell.setAttribute('data-time', `${dayKey} ${timeKey}`);
                        this.addCellTooltip(cell, cellData);
                    }
                    
                    cellsContainer.appendChild(cell);
                }
            }
            
            row.appendChild(cellsContainer);
            heatmapRows.appendChild(row);
        });
        
        container.appendChild(heatmapRows);
    }
    
    getCellColor(cellData) {
        if (!cellData) return this.colorScale.inactive;
        
        const totalActivity = cellData.active_tasks + cellData.completed_tasks;
        
        if (cellData.peak_activity || totalActivity >= 5) return this.colorScale.peak;
        if (totalActivity >= 3) return this.colorScale.high;
        if (totalActivity >= 2) return this.colorScale.medium;
        if (totalActivity >= 1) return this.colorScale.low;
        
        return this.colorScale.inactive;
    }
    
    getCellActivity(cellData) {
        return cellData.active_tasks + cellData.completed_tasks + cellData.failed_tasks;
    }
    
    addCellTooltip(cell, cellData) {
        cell.addEventListener('mouseenter', (e) => {
            const tooltip = document.getElementById('heatmap-tooltip');
            const rect = cell.getBoundingClientRect();
            
            tooltip.innerHTML = `
                <div class="tooltip-time">${cellData.time_slot}</div>
                <div class="tooltip-stats">
                    <div><span class="stat-label">Active:</span> <span class="stat-value">${cellData.active_tasks}</span></div>
                    <div><span class="stat-label">Completed:</span> <span class="stat-value">${cellData.completed_tasks}</span></div>
                    <div><span class="stat-label">Failed:</span> <span class="stat-value">${cellData.failed_tasks}</span></div>
                    <div><span class="stat-label">Avg Progress:</span> <span class="stat-value">${cellData.avg_progress}%</span></div>
                    ${cellData.peak_activity ? '<div class="peak-indicator">🔥 Peak Activity</div>' : ''}
                </div>
            `;
            
            tooltip.style.display = 'block';
            tooltip.style.left = `${rect.left + rect.width / 2}px`;
            tooltip.style.top = `${rect.top - 10}px`;
        });
        
        cell.addEventListener('mouseleave', () => {
            const tooltip = document.getElementById('heatmap-tooltip');
            tooltip.style.display = 'none';
        });
    }
    
    renderStats(statsData) {
        const statsContainer = document.getElementById('heatmap-stats');
        const { system_stats, agent_performance } = statsData;
        
        statsContainer.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-title">Total Jobs</div>
                    <div class="stat-value">${system_stats.total_jobs}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Success Rate</div>
                    <div class="stat-value">${system_stats.success_rate}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Peak Hour</div>
                    <div class="stat-value">${system_stats.peak_hour}:00</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Active Periods</div>
                    <div class="stat-value">${system_stats.active_time_slots}</div>
                </div>
            </div>
            <div class="agent-performance">
                <h5>Agent Performance</h5>
                <div class="agent-grid">
                    ${Object.entries(agent_performance).map(([agent, stats]) => `
                        <div class="agent-card">
                            <div class="agent-name">${agent}</div>
                            <div class="agent-stats">
                                <div>Tasks: ${stats.task_count}</div>
                                <div>Avg Progress: ${stats.avg_progress}%</div>
                                <div>Avg Time: ${stats.avg_time_per_task}s</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    showError(message) {
        this.container.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i>
                ${message}
            </div>
        `;
    }
    
    startAutoRefresh() {
        setInterval(() => {
            this.loadData();
        }, this.options.refreshInterval);
    }
    
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Initialize heatmap when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('task-heatmap')) {
        window.taskHeatmap = new TaskHeatmap('task-heatmap', {
            hours: 24,
            refreshInterval: 30000
        });
    }
});