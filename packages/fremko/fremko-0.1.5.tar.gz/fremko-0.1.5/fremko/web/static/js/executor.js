// Code Executor JavaScript

let isExecuting = false;
let executionStartTime = 0;
let selectedDevice = null;
let devices = [];
let devicePanelCollapsed = false;

function $id(id) { return document.getElementById(id); }

// Example code snippets using ONLY DEFAULT persona allowed tools
const EXAMPLES = {
  basic: `# Basic example using DEFAULT persona tools
print("Starting device automation...")

# Perform some actions (DEFAULT tools only)
await tap_by_index(1)
await remember("Tapped element at index 1")

# Complete the task
await complete(True, "Basic automation completed successfully")`,

  
  app_launch: `# App management example
print("Managing applications...")

# List installed packages
packages = await list_packages(False)
print(f"Found {len(packages)} user apps")

# Start a specific app
await start_app("com.android.settings")
print("Launched Settings app")

# Navigate and interact
await tap_by_index(2)
await swipe(100, 300, 100, 100, 500)

await complete(True, "App launched and navigated successfully")`,

  
  text_input: `# Text input and form interaction
print("Demonstrating text input...")

# Tap on a text field (usually at index 0 in forms)
await tap_by_index(0)

# Input some text
await input_text(0, "Hello from web executor!")

# Use device keys
await press_key(66)  # ENTER key
await press_key(4)   # BACK key

# Remember what we did
await remember("Filled out a form with sample text")

await complete(True, "Text input demonstration completed")`,

  
  navigation: `# Navigation example using only DEFAULT persona tools
print("Performing navigation...")

# Navigate through multiple screens
await tap_by_index(3)  # Main menu item
await tap_by_index(1)  # Sub-menu item

# Perform gestures
await swipe(200, 400, 200, 200, 300)  # Scroll up
await swipe(300, 200, 100, 200, 400)  # Swipe left

# Use press_key for back navigation (DEFAULT persona way)
await press_key(4)  # BACK key

await complete(True, "Navigation completed successfully")`
};

// Update line/column display
function updateLineCol() {
  const editor = $id('code-editor');
  const linecol = $id('line-col');
  if (!editor || !linecol) return;
  
  const pos = editor.selectionStart;
  const text = editor.value.substring(0, pos);
  const lines = text.split('\n');
  const line = lines.length;
  const col = lines[lines.length - 1].length + 1;
  
  linecol.textContent = `Line ${line}, Col ${col}`;
}

// Update editor status
function updateEditorStatus(status, className = '') {
  const statusEl = $id('editor-status');
  if (statusEl) {
    statusEl.textContent = status;
    statusEl.className = `status-text ${className}`;
  }
}

// Clear all results
function clearResults() {
  const consoleOutput = $id('console-output');
  const toolActions = $id('tool-actions');
  const execStatus = $id('exec-status');
  const execTime = $id('exec-time');
  const memoryCount = $id('memory-count');
  
  if (consoleOutput) consoleOutput.textContent = 'Ready to execute code...';
  if (toolActions) toolActions.innerHTML = '<div class="no-actions">No tool actions yet</div>';
  if (execStatus) execStatus.textContent = 'Ready';
  if (execTime) execTime.textContent = '-';
  if (memoryCount) memoryCount.textContent = '0 items';
}

// Display execution results
function displayResults(result) {
  const consoleOutput = $id('console-output');
  const toolActions = $id('tool-actions');
  const execStatus = $id('exec-status');
  const execTime = $id('exec-time');
  const memoryCount = $id('memory-count');
  
  // Console output
  if (consoleOutput) {
    if (result.success) {
      consoleOutput.textContent = result.output || 'Code executed successfully (no output)';
    } else {
      consoleOutput.textContent = `Error: ${result.error}\n\n${result.output || ''}`;
    }
  }
  
  // Tool actions - note: real WsTools doesn't provide tool_actions in response
  if (toolActions) {
    toolActions.innerHTML = '<div class="no-actions">Tool actions executed on device (check device for results)</div>';
  }
  
  // Execution info
  const executionTime = Date.now() - executionStartTime;
  if (execStatus) {
    if (result.success) {
      if (result.finished) {
        execStatus.textContent = result.task_success ? 'Task Completed ✓' : 'Task Failed ✗';
      } else {
        execStatus.textContent = 'Executed ✓';
      }
    } else {
      execStatus.textContent = 'Error ✗';
    }
  }
  
  if (execTime) {
    execTime.textContent = `${executionTime}ms`;
  }
  
  // Memory count - simplified since we don't have tool action logs
  if (memoryCount) {
    memoryCount.textContent = 'See device memory';
  }
}

// Device Management Functions
async function loadDevices() {
  try {
    const response = await fetch('/api/clients');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    devices = data.clients || [];
    displayDevices();
    
  } catch (error) {
    console.error('Failed to load devices:', error);
    const deviceList = $id('device-list');
    if (deviceList) {
      deviceList.innerHTML = '<div class="no-devices">Failed to load devices</div>';
    }
  }
}

function displayDevices() {
  const deviceList = $id('device-list');
  if (!deviceList) return;
  
  if (devices.length === 0) {
    deviceList.innerHTML = '<div class="no-devices">No devices connected</div>';
    return;
  }
  
  deviceList.innerHTML = devices.map(device => {
    const isSelected = selectedDevice && selectedDevice.id === device.id;
    const isConnected = device.connected;
    const deviceName = device.device_name || `${device.brand || ''} ${device.model || ''}`.trim() || 'Unknown Device';
    const battery = device.battery !== undefined ? `${device.battery}%` : 'N/A';
    
    return `
      <div class="device-item ${isSelected ? 'selected' : ''} ${!isConnected ? 'disconnected' : ''}" 
           data-device-id="${device.id}" 
           onclick="${isConnected ? `selectDevice('${device.id}')` : ''}">
        <div class="device-name">${deviceName}</div>
        <div class="device-info">
          <div class="device-status">
            <span class="status-dot ${isConnected ? 'connected' : ''}"></span>
            ${isConnected ? 'Connected' : 'Disconnected'}
          </div>
          <span>🔋 ${battery}</span>
          <span>${device.width || '?'}×${device.height || '?'}</span>
        </div>
      </div>
    `;
  }).join('');
}

function selectDevice(deviceId) {
  const device = devices.find(d => d.id === deviceId);
  if (!device || !device.connected) return;
  
  selectedDevice = device;
  displayDevices(); // Update selection UI
  displaySelectedDevice();
  updateEditorStatus('Device selected', 'success');
}

function displaySelectedDevice() {
  const selectedInfo = $id('selected-device-info');
  const deviceDetails = $id('device-details');
  
  if (!selectedDevice) {
    if (selectedInfo) selectedInfo.style.display = 'none';
    return;
  }
  
  if (selectedInfo) selectedInfo.style.display = 'block';
  
  if (deviceDetails) {
    const deviceName = selectedDevice.device_name || `${selectedDevice.brand || ''} ${selectedDevice.model || ''}`.trim() || 'Unknown Device';
    deviceDetails.innerHTML = `
      <div class="detail-item">
        <span class="detail-label">Name:</span> ${deviceName}
      </div>
      <div class="detail-item">
        <span class="detail-label">Serial:</span> ${selectedDevice.serial || 'N/A'}
      </div>
      <div class="detail-item">
        <span class="detail-label">Resolution:</span> ${selectedDevice.width || '?'}×${selectedDevice.height || '?'}
      </div>
      <div class="detail-item">
        <span class="detail-label">SDK:</span> ${selectedDevice.sdk || 'N/A'}
      </div>
      <div class="detail-item">
        <span class="detail-label">Battery:</span> ${selectedDevice.battery !== undefined ? selectedDevice.battery + '%' : 'N/A'}
      </div>
    `;
  }
}

// Toggle device panel visibility
function toggleDevicePanel() {
  const devicePanel = $id('device-panel');
  const executorLayout = devicePanel?.parentElement;
  const toggleBtn = $id('toggle-device-panel-btn');
  const showBtn = $id('show-device-panel-btn');
  
  if (!devicePanel || !executorLayout) return;
  
  devicePanelCollapsed = !devicePanelCollapsed;
  
  if (devicePanelCollapsed) {
    // Hide panel completely and free all grid space
    devicePanel.classList.remove('collapsed');
    executorLayout.classList.remove('device-panel-collapsed');
    devicePanel.classList.add('hidden');
    executorLayout.classList.add('device-panel-hidden');
    if (toggleBtn) toggleBtn.innerHTML = '→';
    if (toggleBtn) toggleBtn.title = 'Show device selection';
    if (showBtn) showBtn.style.display = 'flex';
  } else {
    // Show panel and restore layout
    devicePanel.classList.remove('hidden');
    executorLayout.classList.remove('device-panel-hidden');
    if (toggleBtn) toggleBtn.innerHTML = '←';
    if (toggleBtn) toggleBtn.title = 'Hide device selection';
    if (showBtn) showBtn.style.display = 'none';
  }
}

// Execute code
async function executeCode() {
  if (isExecuting) return;
  
  const codeEditor = $id('code-editor');
  const runBtn = $id('run-code-btn');
  const loadingModal = $id('loading-modal');
  
  const code = codeEditor.value.trim();
  if (!code) {
    updateEditorStatus('No code to execute', 'error');
    return;
  }
  
  if (!selectedDevice) {
    updateEditorStatus('No device selected', 'error');
    return;
  }
  
  try {
    isExecuting = true;
    executionStartTime = Date.now();
    
    // Update UI
    if (runBtn) runBtn.disabled = true;
    if (loadingModal) loadingModal.setAttribute('aria-hidden', 'false');
    updateEditorStatus('Executing on device...', 'running');
    
    // Send code to backend with device ID
    const response = await fetch('/api/executor/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        code: code,
        client_id: selectedDevice.id 
      }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    // Display results
    displayResults(result);
    
    // Update status
    if (result.success) {
      updateEditorStatus('Execution completed', 'success');
    } else {
      updateEditorStatus('Execution failed', 'error');
    }
    
  } catch (error) {
    console.error('Execution error:', error);
    updateEditorStatus('Connection error', 'error');
    
    const consoleOutput = $id('console-output');
    if (consoleOutput) {
      consoleOutput.textContent = `Connection Error: ${error.message}\n\nPlease check that the server is running and try again.`;
    }
    
  } finally {
    isExecuting = false;
    if (runBtn) runBtn.disabled = false;
    if (loadingModal) loadingModal.setAttribute('aria-hidden', 'true');
  }
}

// Load example code
function loadExample() {
  const examples = Object.keys(EXAMPLES);
  const randomExample = examples[Math.floor(Math.random() * examples.length)];
  
  const codeEditor = $id('code-editor');
  if (codeEditor) {
    codeEditor.value = EXAMPLES[randomExample];
    updateLineCol();
    updateEditorStatus('Example loaded', 'success');
  }
}

// Clear code editor
function clearCode() {
  const codeEditor = $id('code-editor');
  if (codeEditor) {
    codeEditor.value = '';
    updateLineCol();
    updateEditorStatus('Editor cleared', '');
  }
}

// Copy output to clipboard
async function copyOutput() {
  const consoleOutput = $id('console-output');
  if (!consoleOutput) return;
  
  try {
    await navigator.clipboard.writeText(consoleOutput.textContent);
    updateEditorStatus('Output copied to clipboard', 'success');
    setTimeout(() => updateEditorStatus('Ready', ''), 2000);
  } catch (error) {
    console.error('Failed to copy:', error);
    updateEditorStatus('Failed to copy output', 'error');
  }
}

// Toggle tools panel
function toggleToolsPanel() {
  const toolsContent = $id('tools-content');
  const toggleBtn = $id('toggle-tools-btn');
  
  if (toolsContent && toggleBtn) {
    const isCollapsed = toolsContent.classList.contains('collapsed');
    
    if (isCollapsed) {
      toolsContent.classList.remove('collapsed');
      toggleBtn.textContent = '−';
    } else {
      toolsContent.classList.add('collapsed');
      toggleBtn.textContent = '+';
    }
  }
}

// Handle keyboard shortcuts
function handleKeyDown(event) {
  // Ctrl/Cmd + Enter to execute
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault();
    executeCode();
  }
  
  // Ctrl/Cmd + Shift + C to clear
  if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'C') {
    event.preventDefault();
    clearCode();
  }
  
  // Tab support in textarea
  if (event.key === 'Tab') {
    event.preventDefault();
    const target = event.target;
    const start = target.selectionStart;
    const end = target.selectionEnd;
    
    target.value = target.value.substring(0, start) + '    ' + target.value.substring(end);
    target.selectionStart = target.selectionEnd = start + 4;
    updateLineCol();
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Wire up event listeners
  const runBtn = $id('run-code-btn');
  const clearBtn = $id('clear-code-btn');
  const exampleBtn = $id('load-example-btn');
  const clearResultsBtn = $id('clear-results-btn');
  const copyBtn = $id('copy-output-btn');
  const toggleBtn = $id('toggle-tools-btn');
  const refreshDevicesBtn = $id('refresh-devices-btn');
  const toggleDevicePanelBtn = $id('toggle-device-panel-btn');
  const showDevicePanelBtn = $id('show-device-panel-btn');
  const codeEditor = $id('code-editor');
  
  if (runBtn) runBtn.addEventListener('click', executeCode);
  if (clearBtn) clearBtn.addEventListener('click', clearCode);
  if (exampleBtn) exampleBtn.addEventListener('click', loadExample);
  if (clearResultsBtn) clearResultsBtn.addEventListener('click', clearResults);
  if (copyBtn) copyBtn.addEventListener('click', copyOutput);
  if (toggleBtn) toggleBtn.addEventListener('click', toggleToolsPanel);
  if (refreshDevicesBtn) refreshDevicesBtn.addEventListener('click', loadDevices);
  if (toggleDevicePanelBtn) toggleDevicePanelBtn.addEventListener('click', toggleDevicePanel);
  if (showDevicePanelBtn) showDevicePanelBtn.addEventListener('click', toggleDevicePanel);
  
  if (codeEditor) {
    codeEditor.addEventListener('input', updateLineCol);
    codeEditor.addEventListener('click', updateLineCol);
    codeEditor.addEventListener('keyup', updateLineCol);
    codeEditor.addEventListener('keydown', handleKeyDown);
  }
  
  // Close loading modal if clicked outside
  const loadingModal = $id('loading-modal');
  if (loadingModal) {
    loadingModal.addEventListener('click', function(event) {
      if (event.target === loadingModal) {
        loadingModal.setAttribute('aria-hidden', 'true');
      }
    });
  }
  
  // Initial setup
  updateLineCol();
  updateEditorStatus('Select a device to begin', '');
  
  // Load devices on page load
  loadDevices();
  
  console.log('Executor initialized');
});
