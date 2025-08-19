let selected = null;
let selectedInfo = null;
let previewSocket = null;
let canvas = null;
let ctx = null;
let isDrawing = false;
let isGesturing = false;
let gesturePath = [];
let gestureStartTs = 0;
let isStreaming = false;
let previewFixedWidth = null; // px
let previewFixedHeight = null; // px
let previewLockAspect = false;
let previewArW = null; // aspect ratio width part
let previewArH = null; // aspect ratio height part

// Agent state tracking
let agentSettings = {};
let agentStatus = { status: 'ready', message: 'Ready' };
let agentTodos = [];
let statusUpdateInterval = null;

// WebSocket for JSON message communication
let messageSocket = null;
let messageSocketReconnectInterval = null;
let isMessageSocketConnected = false;

function $id(id) { return document.getElementById(id); }

async function refresh(){
  const res = await fetch('/api/clients');
  const js = await res.json();
  const root = $id('clients');
  root.innerHTML = '';
  (js.clients || []).forEach(c => {
    const div = document.createElement('div');
    div.className = 'list-item';
    div.setAttribute('data-client-id', c.id);
    div.onclick = () => selectClient(c.id);
    const type = (c.brand && c.model) ? `${c.brand} ${c.model}` : (c.model || 'Unknown');
    const batt = (typeof c.battery === 'number') ? `${c.battery}%` : '-';
    const stateDot = c.is_running ? '<span class="dot green"></span>' : '<span class="dot red"></span>';
    div.innerHTML = `
      <div class='row space-between'>
        <div>${stateDot}<strong>${c.device_name || type || 'Unknown'}</strong></div>
        <div class='pill'>🔋 ${batt}</div>
      </div>
      <div class='muted small'>${type}</div>`;
    root.appendChild(div);
  });
}

async function selectClient(id){
  // Stop polling for previous client
  stopAgentStatusPolling();
  
  selected = id;
  const res = await fetch(`/api/clients/${id}`);
  const c = await res.json();
  selectedInfo = c;
  renderDetails();
  // Stop any existing stream when switching devices; do not auto-start
  teardownPreview();
  
  // Reset agent status for new client
  updateAgentStatus({ status: 'ready', message: 'Ready' });
  updateAgentTodos([]);
  
  // Start polling if agent is running
  if (c.is_running) {
    updateAgentStatus({ status: 'running', message: c.active_goal || 'Running...' });
    //startAgentStatusPolling();
  }
}

function renderDetails(){
  if(!selectedInfo) return;
  const c = selectedInfo;
  const type = (c.brand && c.model) ? `${c.brand} ${c.model}` : (c.model || 'Unknown');
  const batt = (typeof c.battery === 'number') ? `${c.battery}%` : '-';
  const stateDot = c.is_running ? '<span class="dot green"></span>' : '<span class="dot red"></span>';
  $id('detail-title').innerText = `Device · ${c.device_name || type || selected}`;
  const d = $id('details');
  d.innerHTML = `
    <div class='row space-between'>
      <div class='row'>${stateDot}<strong>${c.device_name || type}</strong></div>
      <div class='pill'>🔋 ${batt}</div>
    </div>
    <div class='muted'>${type}</div>
    <div class='row' style='gap:16px; margin-top:8px;'>
      <div><span class='muted small'>Serial</span> <span class='kbd'>${c.serial || ''}</span></div>
      <div><span class='muted small'>Screen</span> <span class='kbd'>${c.width || '?'}×${c.height || '?'}</span></div>
      <div><span class='muted small'>SDK</span> <span class='kbd'>${c.sdk || ''}</span></div>
      <div><span class='muted small'>Goal</span> <span class='kbd'>${c.active_goal || '-'}</span></div>
    </div>
  `;
}

function showFullInfoModal(){
  if(!selectedInfo) return;
  $id('full-info-pre').textContent = JSON.stringify(selectedInfo, null, 2);
  const modal = $id('full-info-modal');
  modal.setAttribute('aria-hidden', 'false');
}

function closeModal(){
  const modal = $id('full-info-modal');
  modal.setAttribute('aria-hidden', 'true');
}

function openScreenshot(){
  if(!selected) return;
  const modal = $id('screenshot-modal');
  const img = $id('screenshot-img');
  img.src = `/api/clients/${selected}/screenshot?ts=${Date.now()}`;
  modal.setAttribute('aria-hidden', 'false');
}

function closeScreenshot(){
  const modal = $id('screenshot-modal');
  modal.setAttribute('aria-hidden', 'true');
}

async function openApps(){
  if(!selected) return;
  const modal = $id('apps-modal');
  const loading = $id('apps-loading');
  const list = $id('apps-list');
  const error = $id('apps-error');
  
  // Show modal and loading state
  modal.setAttribute('aria-hidden', 'false');
  loading.style.display = 'block';
  list.style.display = 'none';
  error.style.display = 'none';
  
  try {
    const res = await fetch(`/api/clients/${selected}/apps`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const apps = await res.json();
    
    // Clear and populate apps list
    list.innerHTML = '';
    
    if (!apps || apps.length === 0) {
      list.innerHTML = '<div class="apps-loading">No apps found</div>';
    } else {
      apps.forEach(app => {
        const item = document.createElement('div');
        item.className = 'app-item';
        item.onclick = () => startApp(app.packageName);
        
        const iconSrc = app.icon 
          ? `data:image/png;base64,${app.icon}`
          : 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDgiIGhlaWdodD0iNDgiIHZpZXdCb3g9IjAgMCA0OCA0OCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiByeD0iOCIgZmlsbD0iIzM3NDE1MSIvPgo8cGF0aCBkPSJNMjQgMzJWMTZNMTYgMjRIMzIiIHN0cm9rZT0iIzljYTNhZiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KPC9zdmc+'; // Default app icon placeholder
        
        item.innerHTML = `
          <img class="app-icon" src="${iconSrc}" alt="${app.appName || app.packageName}" onerror="this.style.display='none'" />
          <div class="app-info">
            <div class="app-name">${app.appName || app.packageName}</div>
            <div class="app-package">${app.packageName}</div>
          </div>
        `;
        list.appendChild(item);
      });
    }
    
    loading.style.display = 'none';
    list.style.display = 'grid';
  } catch (e) {
    console.error('Failed to load apps:', e);
    loading.style.display = 'none';
    error.style.display = 'block';
    error.textContent = `Failed to load apps: ${e.message}`;
  }
}

function closeApps(){
  const modal = $id('apps-modal');
  modal.setAttribute('aria-hidden', 'true');
}

async function startApp(packageName){
  if(!selected || !packageName) return;
  try {
    await fetch(`/api/clients/${selected}/start_app`, {
      method: 'POST', 
      headers: {'Content-Type': 'application/json'}, 
      body: JSON.stringify({package: packageName})
    });
    // Close apps modal after starting an app
    closeApps();
  } catch (e) {
    console.error('Failed to start app:', e);
  }
}

async function tapXY(){
  if(!selected) return;
  const x = parseInt($id('tapx').value);
  const y = parseInt($id('tapy').value);
  await fetch(`/api/clients/${selected}/tap`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({x,y})});
}

// Screenshot click disabled; use video canvas
// function onImageTap(e){ ... }

async function sendGoal(){
  if(!selected) return;
  const goal = $id('goal').value.trim();
  if (!goal) return;
  
  // Prepare payload with agent settings
  const payload = { goal, ...agentSettings };
  
  try {
    await fetch(`/api/clients/${selected}/goal`, {
      method: 'POST', 
      headers: {'Content-Type': 'application/json'}, 
      body: JSON.stringify(payload)
    });
    
    // Start polling for agent status updates
    //startAgentStatusPolling();
    
    // Update UI to show agent is starting
    updateAgentStatus({ status: 'running', message: 'Starting agent...' });
  } catch (e) {
    console.error('Failed to send goal:', e);
    updateAgentStatus({ status: 'failed', message: 'Failed to start agent' });
  }
}

async function inputText(){
  if(!selected) return;
  const text = $id('text').value;
  await fetch(`/api/clients/${selected}/input`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({text})});
}

async function swipe(){
  if(!selected) return;
  const sx = parseInt($id('sx').value);
  const sy = parseInt($id('sy').value);
  const ex = parseInt($id('ex').value);
  const ey = parseInt($id('ey').value);
  const duration_ms = parseInt($id('dur').value || '300');
  await fetch(`/api/clients/${selected}/swipe`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({start_x:sx,start_y:sy,end_x:ex,end_y:ey,duration_ms})});
}

// Wire events
// Streaming helpers -------------------------------------------------------
function setupVideoPlayback(){ /* no-op */ }

function teardownPreview(){
  try { if (previewSocket) previewSocket.close(); } catch(_) {}
  previewSocket = null;
  isStreaming = false;
  updateStreamUI();
}

function setupPreview(){
  if (!selected) return;
  if (!canvas) canvas = $id('videoCanvas');
  if (!ctx) ctx = canvas.getContext('2d');
  const proto = (location.protocol === 'https:') ? 'wss' : 'ws';
  previewSocket = new WebSocket(`${proto}://${location.host}/ws/preview/${selected}`);
  previewSocket.binaryType = 'arraybuffer';
  previewSocket.onopen = () => { isStreaming = true; updateStreamUI(); };
  previewSocket.onclose = () => { isStreaming = false; updateStreamUI(); };
  previewSocket.onmessage = (ev) => {
    if (typeof ev.data === 'string') {
      try {
        const js = JSON.parse(ev.data);
        if (js.type === 'preview_info') {
          // could display serial/params
        }
      } catch(_) {}
      return;
    }
    // Binary JPEG from server; draw using createImageBitmap
    if (isDrawing) return; // drop frames while busy to avoid backlog
    isDrawing = true;
    const blob = new Blob([ev.data], { type: 'image/jpeg' });
    const doCanvas = (imgWidth, imgHeight, draw) => {
      try {
        // Determine target canvas attribute size based on fixed settings/aspect lock
        const { w: targetW, h: targetH } = computePreviewTargetSize(imgWidth, imgHeight);
        if (canvas.width !== targetW || canvas.height !== targetH) {
          canvas.setAttribute('width', String(targetW));
          canvas.setAttribute('height', String(targetH));
        }
        if (!ctx) ctx = canvas.getContext('2d', { alpha: false, desynchronized: true });
        ctx.imageSmoothingEnabled = false;
        draw();
      } finally {
        isDrawing = false;
      }
    };
    if ('createImageBitmap' in window) {
      createImageBitmap(blob).then(bitmap => {
        doCanvas(bitmap.width, bitmap.height, () => {
          ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
          try { bitmap.close(); } catch(_) {}
        });
      }).catch(() => {
        // Fallback to Image decode
        const url = URL.createObjectURL(blob);
        const img = new Image();
        img.onload = () => { doCanvas(img.width, img.height, () => { ctx.drawImage(img, 0, 0, canvas.width, canvas.height); URL.revokeObjectURL(url); }); };
        img.onerror = () => { try { URL.revokeObjectURL(url); } catch(_) {}; isDrawing = false; };
        img.src = url;
      });
    } else {
      // No createImageBitmap support: use Image()
      const url = URL.createObjectURL(blob);
      const img = new Image();
      img.onload = () => { doCanvas(img.width, img.height, () => { ctx.drawImage(img, 0, 0, canvas.width, canvas.height); URL.revokeObjectURL(url); }); };
      img.onerror = () => { try { URL.revokeObjectURL(url); } catch(_) {}; isDrawing = false; };
      img.src = url;
    }
  };
}

function updateStreamUI(){
  const wrap = $id('videoCanvasWrap');
  const startBtn = $id('stream-start-btn');
  const updBtn = $id('stream-update-btn');
  const stopBtn = $id('stream-stop-btn');
  const fmtSel = $id('stream-format');
  const qWrap = $id('quality-wrap');
  const brWrap = $id('bitrate-wrap');
  if (wrap) wrap.style.display = isStreaming ? '' : 'none';
  if (startBtn) startBtn.hidden = isStreaming;
  if (updBtn) updBtn.hidden = !isStreaming;
  if (stopBtn) stopBtn.hidden = !isStreaming;
  const fmt = fmtSel ? fmtSel.value : 'h264';
  const isJpeg = (fmt === 'jpeg');
  if (qWrap) qWrap.style.display = isJpeg ? '' : 'none';
  if (brWrap) brWrap.style.display = (fmt === 'h264') ? '' : 'none';
  applyPreviewResizeStyles();
}

async function controlStream(kind){
  if(!selected) return;
  if (kind === 'start') {
    const fps = parseInt($id('stream-fps').value || '12');
    const quality = parseInt($id('stream-quality').value || '75');
    const fmtSel = $id('stream-format');
    const format = fmtSel ? (fmtSel.value || 'h264') : 'h264';
    const payload = { fps, quality, format };
    if (format === 'h264') {
      const br = parseInt(($id('stream-bitrate')?.value || '1500'));
      if (br) payload.bitrate_kbps = br;
    }
    await fetch(`/api/clients/${selected}/stream/start`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    setupPreview();
    isStreaming = true;
    updateStreamUI();
  } else if (kind === 'update') {
    const fpsVal = $id('stream-fps').value.trim();
    const qVal = $id('stream-quality').value.trim();
    const payload = {};
    if (fpsVal) payload.fps = parseInt(fpsVal);
    if (qVal) payload.quality = parseInt(qVal);
    const fmtSel = $id('stream-format');
    if (fmtSel && fmtSel.value) payload.format = fmtSel.value;
    if (payload.format === 'h264') {
      const br = parseInt(($id('stream-bitrate')?.value || '').trim() || '0');
      if (br > 0) payload.bitrate_kbps = br;
    }
    await fetch(`/api/clients/${selected}/stream/update`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
  } else if (kind === 'stop') {
    await fetch(`/api/clients/${selected}/stream/stop`, { method:'POST' });
    teardownPreview();
  }
}

function _canvasToDeviceXY(clientX, clientY){
  if (!canvas) canvas = $id('videoCanvas');
  const rect = canvas.getBoundingClientRect();
  const nx = Math.min(Math.max(0, (clientX - rect.left) / Math.max(1, rect.width)), 1);
  const ny = Math.min(Math.max(0, (clientY - rect.top) / Math.max(1, rect.height)), 1);
  const targetW = (selectedInfo && typeof selectedInfo.width === 'number') ? selectedInfo.width : (canvas.width || 1);
  const targetH = (selectedInfo && typeof selectedInfo.height === 'number') ? selectedInfo.height : (canvas.height || 1);
  let dx = Math.round(nx * targetW);
  let dy = Math.round(ny * targetH);
  dx = Math.min(Math.max(0, dx), Math.max(1, targetW) - 1);
  dy = Math.min(Math.max(0, dy), Math.max(1, targetH) - 1);
  return { x: dx, y: dy };
}

function onCanvasPointerDown(e){
  if(!selected || !isStreaming) return;
  try { canvas.setPointerCapture(e.pointerId); } catch(_) {}
  isGesturing = true;
  gesturePath = [];
  gestureStartTs = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
  const { x, y } = _canvasToDeviceXY(e.clientX, e.clientY);
  gesturePath.push({ x, y, t: 0 });
}

function onCanvasPointerMove(e){
  if(!isGesturing || !isStreaming) return;
  const now = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
  const { x, y } = _canvasToDeviceXY(e.clientX, e.clientY);
  gesturePath.push({ x, y, t: Math.max(0, Math.round(now - gestureStartTs)) });
}

function onCanvasPointerUp(e){
  if(!isGesturing || !isStreaming) return;
  isGesturing = false;
  try { canvas.releasePointerCapture(e.pointerId); } catch(_) {}
  if (!selected || !gesturePath || gesturePath.length === 0) {
    gesturePath = [];
    return;
  }

  // Decide: tap vs gesture
  const first = gesturePath[0];
  const last = gesturePath[gesturePath.length - 1];
  const dx = (last.x ?? first.x) - first.x;
  const dy = (last.y ?? first.y) - first.y;
  const dist2 = (dx*dx) + (dy*dy);
  const duration = (typeof last.t === 'number' && typeof first.t === 'number') ? (last.t - first.t) : 0;
  const isClickLike = (gesturePath.length < 2) || (dist2 <= 25 && duration <= 300);

  if (isClickLike) {
    // Single tap at last coordinate
    const tapX = last.x ?? first.x;
    const tapY = last.y ?? first.y;
    fetch(`/api/clients/${selected}/tap`, {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ x: tapX, y: tapY })
    }).catch(()=>{});
  } else {
    const payload = { points: gesturePath };
    fetch(`/api/clients/${selected}/gesture_path`, {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    }).catch(()=>{});
  }
  gesturePath = [];
}

// WebSocket Message Communication Functions -------------------------------
function connectMessageSocket(){
  if (messageSocket && (messageSocket.readyState === WebSocket.CONNECTING || messageSocket.readyState === WebSocket.OPEN)) {
    return; // Already connected or connecting
  }
  
  const proto = (location.protocol === 'https:') ? 'wss' : 'ws';
  messageSocket = new WebSocket(`${proto}://${location.host}/ws/messages`);
  
  messageSocket.onopen = () => {
    console.log('Message WebSocket connected');
    isMessageSocketConnected = true;
    updateWebSocketStatus();
    
    // Clear reconnection interval if it was running
    if (messageSocketReconnectInterval) {
      clearInterval(messageSocketReconnectInterval);
      messageSocketReconnectInterval = null;
    }
  };
  
  messageSocket.onclose = () => {
    console.log('Message WebSocket disconnected');
    isMessageSocketConnected = false;
    updateWebSocketStatus();
    
    // Attempt to reconnect every 5 seconds
    if (!messageSocketReconnectInterval) {
      messageSocketReconnectInterval = setInterval(() => {
        console.log('Attempting to reconnect message WebSocket...');
        connectMessageSocket();
      }, 5000);
    }
  };
  
  messageSocket.onerror = (error) => {
    console.error('Message WebSocket error:', error);
    isMessageSocketConnected = false;
    updateWebSocketStatus();
  };
  
  messageSocket.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);
      handleWebSocketMessage(message);
    } catch (e) {
      console.error('Failed to parse WebSocket message:', e);
    }
  };
}

function disconnectMessageSocket(){
  if (messageSocketReconnectInterval) {
    clearInterval(messageSocketReconnectInterval);
    messageSocketReconnectInterval = null;
  }
  
  if (messageSocket) {
    messageSocket.close();
    messageSocket = null;
  }
  
  isMessageSocketConnected = false;
  updateWebSocketStatus();
}

function sendWebSocketMessage(message){
  if (!messageSocket || messageSocket.readyState !== WebSocket.OPEN) {
    console.warn('WebSocket not connected, cannot send message');
    return false;
  }
  
  try {
    messageSocket.send(JSON.stringify(message));
    return true;
  } catch (e) {
    console.error('Failed to send WebSocket message:', e);
    return false;
  }
}

function handleWebSocketMessage(message){
  console.log('Received WebSocket message:', message);
  
  const messageType = message.type;
  
  switch (messageType) {
    case 'connection':
      console.log('WebSocket connection established:', message.message);
      break;
      
    case 'pong':
      console.log('Received pong:', message);
      break;
      
    case 'broadcast':
      console.log('Received broadcast:', message.content);
      // You can show notifications or update UI based on broadcast messages
      break;
      
    case 'broadcast_sent':
      console.log('Broadcast confirmation:', message.message);
      break;
      
    case 'client_status_response':
      console.log('Client status update:', message.data);
      // Update UI with new client status if needed
      break;
      
    case 'agent_status_response':
      if (message.client_id === selected) {
        updateAgentStatus(message.data.status);
        updateAgentTodos(message.data.todos);
      }
      break;
      
    case 'device_event':
      console.log('Device event received:', message);
      handleDeviceEvent(message);
      break;
      
    case 'task_update':
      console.log('Task update received:', message);
      handleTaskUpdate(message);
      break;
      
    case 'error':
      console.error('WebSocket error:', message.message);
      break;
      
    default:
      console.log('Unknown message type:', messageType, message);
  }
}

function updateWebSocketStatus(){
  // You can add UI elements to show WebSocket connection status
  const statusElement = document.getElementById('websocket-status');
  if (statusElement) {
    statusElement.textContent = isMessageSocketConnected ? 'Connected' : 'Disconnected';
    statusElement.className = `status ${isMessageSocketConnected ? 'connected' : 'disconnected'}`;
  }
}

// WebSocket utility functions
function pingWebSocket(){
  return sendWebSocketMessage({
    type: 'ping',
    timestamp: Date.now()
  });
}

function broadcastMessage(content){
  return sendWebSocketMessage({
    type: 'broadcast',
    content: content,
    timestamp: Date.now()
  });
}

function requestClientStatus(){
  return sendWebSocketMessage({
    type: 'client_status',
    timestamp: Date.now()
  });
}

function requestAgentStatus(clientId){
  return sendWebSocketMessage({
    type: 'agent_command',
    client_id: clientId,
    command: 'get_status',
    timestamp: Date.now()
  });
}

function handleDeviceEvent(message){
  const clientId = message.client_id;
  const deviceInfo = message.device_info;
  const agentData = message.agent_data;
  
  console.log('Handling device event for client:', clientId, agentData);
  
  // Update agent status if this is for the currently selected client
  if (clientId === selected && agentData) {
    // Determine status based on agent data
    let status = { status: 'ready', message: 'Ready' };
    
    if (agentData.is_running) {
      status = { 
        status: 'running', 
        message: agentData.current_step || agentData.active_goal || 'Running...' 
      };
    } else if (agentData.is_complete) {
      if (agentData.is_success) {
        status = { 
          status: 'completed', 
          message: `Completed: ${agentData.goal || 'Goal completed'}` 
        };
      } else {
        status = { 
          status: 'failed', 
          message: `Failed: ${agentData.goal || 'Goal failed'}` 
        };
      }
    }
    
    // Update the UI with the new agent status
    updateAgentStatus(status);
    
    // Update step indicator if available
    if (agentData.current_step) {
      const stepEl = document.getElementById('current-step');
      if (stepEl) {
        stepEl.textContent = agentData.current_step;
      }
    }
  }
  
  // Update the client list to reflect any changes
  if (deviceInfo) {
    const clientEl = document.querySelector(`[data-client-id="${clientId}"]`);
    if (clientEl) {
      // Update the visual indicator in the client list
      const dot = clientEl.querySelector('.dot');
      if (dot && agentData) {
        if (agentData.is_running) {
          dot.className = 'dot green';
        } else {
          dot.className = 'dot red';
        }
      }
    }
  }
  
  // Show notification for significant events
  if (agentData && agentData.is_complete && clientId === selected) {
    const message = agentData.is_success ? 'Goal completed successfully!' : 'Goal failed.';
    showNotification(message, agentData.is_success ? 'success' : 'error');
  }
}

function showNotification(message, type = 'info'){
  // Simple notification system - you can enhance this with better UI
  console.log(`[${type.toUpperCase()}] ${message}`);
  
  // You can implement a toast notification system here
  // For now, just update the agent status message
  const statusEl = document.getElementById('agent-status');
  if (statusEl && type !== 'info') {
    const indicator = statusEl.querySelector('.status-indicator') || statusEl;
    const originalText = indicator.textContent;
    
    indicator.textContent = `${type === 'success' ? '✓' : '✗'} ${message}`;
    
    // Restore original text after 3 seconds
    setTimeout(() => {
      if (indicator.textContent === `${type === 'success' ? '✓' : '✗'} ${message}`) {
        indicator.textContent = originalText;
      }
    }, 3000);
  }
}

function handleTaskUpdate(message){
  const clientId = message.client_id;
  const eventType = message.event_type;
  const taskData = message.task_data;
  const triggeredBy = message.triggered_by;
  
  console.log('Handling task update for client:', clientId, 'event:', eventType, 'data:', taskData);
  
  // Update tasks if this is for the currently selected client
  if (clientId === selected && taskData) {
    // Update the todos with the new task data
    updateAgentTodos(taskData.tasks || []);
    
    // Update task counter
    const counterEl = document.getElementById('task-counter');
    if (counterEl && taskData.tasks) {
      counterEl.textContent = `${taskData.completed_tasks || 0}/${taskData.total_tasks || 0}`;
    }
    
    // Show notification for task events
    if (triggeredBy && triggeredBy.description) {
      let notificationMessage = '';
      let notificationType = 'info';
      
      switch (eventType) {
        case 'complete_task':
          notificationMessage = `Task completed: ${triggeredBy.description}`;
          notificationType = 'success';
          break;
        case 'fail_task':
          notificationMessage = `Task failed: ${triggeredBy.description}`;
          notificationType = 'error';
          break;
        case 'set_tasks_with_agents':
          notificationMessage = `New task added: ${triggeredBy.description}`;
          notificationType = 'info';
          break;
        default:
          notificationMessage = `Task ${eventType}: ${triggeredBy.description}`;
          notificationType = 'info';
      }
      
      // Show notification for task events (but not too frequently)
      if (eventType !== 'set_tasks_with_agents' || taskData.total_tasks <= 5) {
        showNotification(notificationMessage, notificationType);
      }
    }
    
    // Update progress indicator if available
    const progressEl = document.getElementById('task-progress');
    if (progressEl && taskData.total_tasks > 0) {
      const percentage = Math.round((taskData.completed_tasks / taskData.total_tasks) * 100);
      progressEl.style.width = `${percentage}%`;
      progressEl.setAttribute('aria-valuenow', percentage);
    }
    
    // Update goal completion status
    if (taskData.goal_completed) {
      const goalMessage = taskData.goal_message || 'Goal completed';
      updateAgentStatus({ 
        status: 'completed', 
        message: goalMessage 
      });
      showNotification(goalMessage, 'success');
    }
  }
  
  // Update task statistics in a summary view if available
  updateTaskSummary(clientId, taskData);
}

function updateTaskSummary(clientId, taskData){
  // Update any task summary displays
  const summaryEl = document.getElementById('task-summary');
  if (summaryEl && clientId === selected && taskData) {
    summaryEl.innerHTML = `
      <div class="task-stats">
        <span class="stat completed">✓ ${taskData.completed_tasks || 0}</span>
        <span class="stat failed">✗ ${taskData.failed_tasks || 0}</span>
        <span class="stat pending">○ ${taskData.pending_tasks || 0}</span>
        <span class="stat total">Total: ${taskData.total_tasks || 0}</span>
      </div>
    `;
  }
}

// Agent Settings Functions ------------------------------------------------
function openAgentSettings(){
  const modal = $id('agent-settings-modal');
  if (!modal) return;
  
  // Load current settings into form
  $id('agent-provider').value = agentSettings.provider || 'GoogleGenAI';
  $id('agent-model').value = agentSettings.model || 'gemini-2.5-flash';
  $id('agent-base-url').value = agentSettings.base_url || '';
  $id('agent-steps').value = agentSettings.steps || 20;
  $id('agent-timeout').value = agentSettings.timeout || 700;
  $id('agent-vision').checked = agentSettings.vision !== false; // Default to true
  $id('agent-reasoning').checked = !!agentSettings.reasoning;
  $id('agent-reflection').checked = !!agentSettings.reflection;
  $id('agent-tracing').checked = !!agentSettings.tracing;
  $id('agent-debug').checked = !!agentSettings.debug;
  
  // Update reflection state based on vision and reasoning
  updateReflectionState();
  
  modal.setAttribute('aria-hidden', 'false');
}

function closeAgentSettings(){
  const modal = $id('agent-settings-modal');
  if (!modal) return;
  modal.setAttribute('aria-hidden', 'true');
}

function saveAgentSettings(){
  agentSettings = {
    provider: $id('agent-provider').value.trim() || 'GoogleGenAI',
    model: $id('agent-model').value.trim() || 'gemini-2.5-flash',
    base_url: $id('agent-base-url').value.trim(),
    steps: parseInt($id('agent-steps').value) || 150,
    timeout: parseInt($id('agent-timeout').value) || 700,
    vision: $id('agent-vision').checked,
    reasoning: $id('agent-reasoning').checked,
    reflection: $id('agent-reflection').checked,
    tracing: $id('agent-tracing').checked,
    debug: $id('agent-debug').checked,
  };
  
  // Remove empty fields
  Object.keys(agentSettings).forEach(key => {
    if (agentSettings[key] === '' || agentSettings[key] === null || agentSettings[key] === undefined) {
      delete agentSettings[key];
    }
  });
  
  // Save to localStorage
  try {
    localStorage.setItem('agent_settings', JSON.stringify(agentSettings));
  } catch(_) {}
  
  closeAgentSettings();
}

function updateReflectionState(){
  const visionChecked = $id('agent-vision').checked;
  const reasoningChecked = $id('agent-reasoning').checked;
  const reflectionCheckbox = $id('agent-reflection');
  const reflectionLabel = reflectionCheckbox.closest('.checkbox-label');
  
  const canUseReflection = visionChecked && reasoningChecked;
  
  if (!canUseReflection) {
    reflectionCheckbox.disabled = true;
    reflectionCheckbox.checked = false;
    if (reflectionLabel) {
      reflectionLabel.style.opacity = '0.5';
      reflectionLabel.style.cursor = 'not-allowed';
    }
  } else {
    reflectionCheckbox.disabled = false;
    if (reflectionLabel) {
      reflectionLabel.style.opacity = '1';
      reflectionLabel.style.cursor = 'pointer';
    }
  }
}

function resetAgentSettings(){
  agentSettings = {};
  try {
    localStorage.removeItem('agent_settings');
  } catch(_) {}
  
  // Reset form
  $id('agent-provider').value = 'GoogleGenAI';
  $id('agent-model').value = 'gemini-2.5-flash';
  $id('agent-base-url').value = '';
  $id('agent-steps').value = 150;
  $id('agent-timeout').value = 700;
  $id('agent-vision').checked = true; // Default to true
  $id('agent-reasoning').checked = false;
  $id('agent-reflection').checked = false;
  $id('agent-tracing').checked = false;
  $id('agent-debug').checked = false;
  
  // Update reflection state
  updateReflectionState();
}

function loadAgentSettings(){
  try {
    const saved = localStorage.getItem('agent_settings');
    if (saved) {
      agentSettings = JSON.parse(saved);
    }
  } catch(_) {
    agentSettings = {};
  }
}

// Agent Status Functions --------------------------------------------------
function updateAgentStatus(status){
  agentStatus = status;
  const statusEl = $id('agent-status');
  if (!statusEl) return;
  
  const indicator = statusEl.querySelector('.status-indicator') || statusEl;
  indicator.className = `status-indicator ${status.status}`;
  
  let icon = '⚡';
  if (status.status === 'running') icon = '🔄';
  else if (status.status === 'completed') icon = '✓';
  else if (status.status === 'failed') icon = '✗';
  
  indicator.textContent = `${icon} ${status.message}`;
}

function updateAgentTodos(todos){
  agentTodos = todos || [];
  const todosEl = $id('agent-todos');
  const counterEl = $id('task-counter');
  
  if (!todosEl) return;
  
  if (agentTodos.length === 0) {
    todosEl.innerHTML = '<div class="no-tasks muted small">No active tasks</div>';
    if (counterEl) counterEl.textContent = '0/0';
    return;
  }
  
  const completed = agentTodos.filter(t => t.status === 'completed').length;
  if (counterEl) counterEl.textContent = `${completed}/${agentTodos.length}`;
  
  todosEl.innerHTML = agentTodos.map(todo => {
    let icon = '○';
    let statusClass = 'pending';
    if (todo.status === 'completed') {
      icon = '✓';
      statusClass = 'completed';
    } else if (todo.status === 'failed') {
      icon = '✗';
      statusClass = 'failed';
    }
    
    const contentClass = todo.status === 'completed' ? 'todo-content completed' : 'todo-content';
    
    return `
      <div class="todo-item">
        <div class="todo-status ${statusClass}">${icon}</div>
        <div class="${contentClass}">${todo.description}</div>
      </div>
    `;
  }).join('');
}

async function refreshAgentStatus(){
  if (!selected) return;
  
  // Try WebSocket first, fallback to HTTP
  if (isMessageSocketConnected && requestAgentStatus(selected)) {
    return; // WebSocket request sent successfully
  }
  
  // Fallback to HTTP request
  try {
    const res = await fetch(`/api/clients/${selected}/status`);
    if (res.ok) {
      const data = await res.json();
      updateAgentStatus(data.status || { status: 'ready', message: 'Ready' });
      updateAgentTodos(data.todos || []);
    }
  } catch (e) {
    console.error('Failed to refresh agent status:', e);
  }
}

function startAgentStatusPolling(){
  if (statusUpdateInterval) {
    clearInterval(statusUpdateInterval);
  }
  
  statusUpdateInterval = setInterval(refreshAgentStatus, 2000);
}

function stopAgentStatusPolling(){
  if (statusUpdateInterval) {
    clearInterval(statusUpdateInterval);
    statusUpdateInterval = null;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  $id('refresh-btn').addEventListener('click', refresh);
  $id('screenshot-btn').addEventListener('click', openScreenshot);
  $id('apps-btn').addEventListener('click', openApps);
  $id('full-info-btn').addEventListener('click', showFullInfoModal);
  $id('modal-backdrop').addEventListener('click', closeModal);
  $id('modal-close').addEventListener('click', closeModal);
  $id('modal-close-footer').addEventListener('click', closeModal);
  $id('screenshot-backdrop').addEventListener('click', closeScreenshot);
  $id('screenshot-close').addEventListener('click', closeScreenshot);
  $id('screenshot-close-footer').addEventListener('click', closeScreenshot);
  $id('apps-backdrop').addEventListener('click', closeApps);
  $id('apps-close').addEventListener('click', closeApps);
  $id('apps-close-footer').addEventListener('click', closeApps);
  $id('send-goal-btn').addEventListener('click', sendGoal);
  $id('tapxy-btn').addEventListener('click', tapXY);
  $id('input-text-btn').addEventListener('click', inputText);
  $id('swipe-btn').addEventListener('click', swipe);
  
  // Agent settings modal wiring
  $id('agent-settings-btn').addEventListener('click', openAgentSettings);
  $id('agent-settings-backdrop').addEventListener('click', closeAgentSettings);
  $id('agent-settings-close').addEventListener('click', closeAgentSettings);
  $id('agent-settings-save').addEventListener('click', saveAgentSettings);
  $id('agent-settings-reset').addEventListener('click', resetAgentSettings);
  $id('refresh-agent-btn').addEventListener('click', refreshAgentStatus);
  $id('agent-vision').addEventListener('change', updateReflectionState);
  $id('agent-reasoning').addEventListener('change', updateReflectionState);

  canvas = $id('videoCanvas');
  ctx = canvas.getContext('2d');
  setupVideoPlayback();
  // Preview settings wiring
  const psb = $id('preview-settings-btn');
  if (psb) psb.addEventListener('click', openPreviewSettings);
  const psbBackdrop = $id('preview-settings-backdrop');
  if (psbBackdrop) psbBackdrop.addEventListener('click', closePreviewSettings);
  const psbClose = $id('preview-settings-close');
  if (psbClose) psbClose.addEventListener('click', closePreviewSettings);
  const psSave = $id('preview-settings-save');
  if (psSave) psSave.addEventListener('click', savePreviewSettings);
  const psReset = $id('preview-settings-reset');
  if (psReset) psReset.addEventListener('click', resetPreviewSettings);
  // Load saved values -> inputs and apply styles
  loadPreviewSettings();
  applyPreviewResizeStyles();
  wirePreviewSettingsLiveUpdates();
  
  // Load agent settings
  loadAgentSettings();
  
  // Initialize WebSocket connection
  connectMessageSocket();
  
  $id('stream-start-btn').addEventListener('click', () => controlStream('start'));
  $id('stream-update-btn').addEventListener('click', () => controlStream('update'));
  $id('stream-stop-btn').addEventListener('click', () => controlStream('stop'));
  const fmtSel = $id('stream-format');
  if (fmtSel) {
    fmtSel.addEventListener('change', () => {
      updateStreamUI();
      if (isStreaming) controlStream('update');
    });
  }
  canvas.addEventListener('pointerdown', onCanvasPointerDown);
  canvas.addEventListener('pointermove', onCanvasPointerMove);
  canvas.addEventListener('pointerup', onCanvasPointerUp);
  canvas.addEventListener('pointercancel', onCanvasPointerUp);

  refresh();
  updateStreamUI();
});

// Preview resize settings ----------------------------------------------------
function openPreviewSettings(){
  const modal = $id('preview-settings-modal');
  if (!modal) return;
  // populate inputs
  const wInp = $id('preview-width');
  const hInp = $id('preview-height');
  const arW = $id('preview-ar-w');
  const arH = $id('preview-ar-h');
  const arLock = $id('preview-lock-aspect');
  if (wInp) wInp.value = previewFixedWidth ? String(previewFixedWidth) : '';
  if (hInp) hInp.value = previewFixedHeight ? String(previewFixedHeight) : '';
  if (arW) arW.value = previewArW ? String(previewArW) : '';
  if (arH) arH.value = previewArH ? String(previewArH) : '';
  if (arLock) arLock.checked = !!previewLockAspect;
  modal.setAttribute('aria-hidden', 'false');
}

function closePreviewSettings(){
  const modal = $id('preview-settings-modal');
  if (!modal) return;
  modal.setAttribute('aria-hidden', 'true');
}

function applyPreviewResizeStyles(){
  if (!canvas) canvas = $id('videoCanvas');
  if (!canvas) return;
  // Prefer modifying HTML attributes rather than CSS styles so inline styles do not override
  const { w, h } = computePreviewTargetSize(canvas.width || 0, canvas.height || 0);
  if (w > 0) canvas.setAttribute('width', String(w)); else canvas.removeAttribute('width');
  if (h > 0) canvas.setAttribute('height', String(h)); else canvas.removeAttribute('height');
  // Clear any inline CSS width/height to ensure attributes govern display size
  try {
    canvas.style.removeProperty('width');
    canvas.style.removeProperty('height');
  } catch(_) {}
}

function savePreviewSettings(){
  const wInp = $id('preview-width');
  const hInp = $id('preview-height');
  const arW = $id('preview-ar-w');
  const arH = $id('preview-ar-h');
  const arLock = $id('preview-lock-aspect');
  const w = (wInp && wInp.value.trim()) ? parseInt(wInp.value.trim(), 10) : null;
  const h = (hInp && hInp.value.trim()) ? parseInt(hInp.value.trim(), 10) : null;
  previewFixedWidth = (typeof w === 'number' && !Number.isNaN(w) && w > 0) ? w : null;
  previewFixedHeight = (typeof h === 'number' && !Number.isNaN(h) && h > 0) ? h : null;
  const aw = (arW && arW.value.trim()) ? parseInt(arW.value.trim(), 10) : null;
  const ah = (arH && arH.value.trim()) ? parseInt(arH.value.trim(), 10) : null;
  previewArW = (typeof aw === 'number' && !Number.isNaN(aw) && aw > 0) ? aw : null;
  previewArH = (typeof ah === 'number' && !Number.isNaN(ah) && ah > 0) ? ah : null;
  previewLockAspect = !!(arLock && arLock.checked);
  // persist
  try {
    if (previewFixedWidth) localStorage.setItem('preview_w', String(previewFixedWidth)); else localStorage.removeItem('preview_w');
    if (previewFixedHeight) localStorage.setItem('preview_h', String(previewFixedHeight)); else localStorage.removeItem('preview_h');
    if (previewArW) localStorage.setItem('preview_ar_w', String(previewArW)); else localStorage.removeItem('preview_ar_w');
    if (previewArH) localStorage.setItem('preview_ar_h', String(previewArH)); else localStorage.removeItem('preview_ar_h');
    localStorage.setItem('preview_ar_lock', previewLockAspect ? '1' : '0');
  } catch(_) {}
  applyPreviewResizeStyles();
  closePreviewSettings();
}

function resetPreviewSettings(){
  previewFixedWidth = null;
  previewFixedHeight = null;
  previewArW = null;
  previewArH = null;
  previewLockAspect = false;
  try { localStorage.removeItem('preview_w'); localStorage.removeItem('preview_h'); } catch(_) {}
  try { localStorage.removeItem('preview_ar_w'); localStorage.removeItem('preview_ar_h'); localStorage.removeItem('preview_ar_lock'); } catch(_) {}
  const wInp = $id('preview-width');
  const hInp = $id('preview-height');
  const arW = $id('preview-ar-w');
  const arH = $id('preview-ar-h');
  const arLock = $id('preview-lock-aspect');
  if (wInp) wInp.value = '';
  if (hInp) hInp.value = '';
  if (arW) arW.value = '';
  if (arH) arH.value = '';
  if (arLock) arLock.checked = false;
  applyPreviewResizeStyles();
}

function loadPreviewSettings(){
  try {
    const w = parseInt(localStorage.getItem('preview_w') || '');
    const h = parseInt(localStorage.getItem('preview_h') || '');
    previewFixedWidth = Number.isFinite(w) && w > 0 ? w : null;
    previewFixedHeight = Number.isFinite(h) && h > 0 ? h : null;
    const aw = parseInt(localStorage.getItem('preview_ar_w') || '');
    const ah = parseInt(localStorage.getItem('preview_ar_h') || '');
    previewArW = Number.isFinite(aw) && aw > 0 ? aw : null;
    previewArH = Number.isFinite(ah) && ah > 0 ? ah : null;
    previewLockAspect = (localStorage.getItem('preview_ar_lock') || '0') === '1';
  } catch(_) {
    previewFixedWidth = null;
    previewFixedHeight = null;
    previewArW = null;
    previewArH = null;
    previewLockAspect = false;
  }
}

function computePreviewTargetSize(sourceW, sourceH){
  // start with explicit fixed sizes if provided; else source sizes
  let outW = (previewFixedWidth && previewFixedWidth > 0) ? previewFixedWidth : sourceW;
  let outH = (previewFixedHeight && previewFixedHeight > 0) ? previewFixedHeight : sourceH;
  if (previewLockAspect && previewArW && previewArH) {
    const ratio = previewArW / previewArH;
    // If both W and H explicitly provided, prefer W and adjust H to lock aspect
    if (previewFixedWidth && previewFixedWidth > 0 && (!previewFixedHeight || previewFixedHeight <= 0)) {
      outH = Math.round(outW / Math.max(1e-6, ratio));
    } else if ((!previewFixedWidth || previewFixedWidth <= 0) && previewFixedHeight && previewFixedHeight > 0) {
      outW = Math.round(outH * ratio);
    } else if (previewFixedWidth && previewFixedWidth > 0 && previewFixedHeight && previewFixedHeight > 0) {
      // Both provided: override height to maintain ratio based on width
      outH = Math.round(outW / Math.max(1e-6, ratio));
    } else {
      // None provided: lock aspect based on source width
      outH = Math.round(outW / Math.max(1e-6, ratio));
    }
  }
  outW = Math.max(1, Math.floor(outW));
  outH = Math.max(1, Math.floor(outH));
  return { w: outW, h: outH };
}

// Live-updating of settings fields when aspect is locked ---------------------
let _settingsGuard = false;
function _parsePosInt(str){
  const v = parseInt(String(str || '').trim(), 10);
  return Number.isFinite(v) && v > 0 ? v : null;
}
function wirePreviewSettingsLiveUpdates(){
  const wInp = $id('preview-width');
  const hInp = $id('preview-height');
  const arW = $id('preview-ar-w');
  const arH = $id('preview-ar-h');
  const arLock = $id('preview-lock-aspect');
  if (!wInp || !hInp || !arW || !arH || !arLock) return;

  const recalcFromWidth = () => {
    if (_settingsGuard) return; _settingsGuard = true;
    const lock = arLock.checked;
    const aw = _parsePosInt(arW.value);
    const ah = _parsePosInt(arH.value);
    const width = _parsePosInt(wInp.value);
    if (lock && aw && ah && width) {
      const ratio = aw / ah;
      const newH = Math.max(1, Math.round(width / Math.max(1e-6, ratio)));
      hInp.value = String(newH);
    }
    _settingsGuard = false;
  };
  const recalcFromHeight = () => {
    if (_settingsGuard) return; _settingsGuard = true;
    const lock = arLock.checked;
    const aw = _parsePosInt(arW.value);
    const ah = _parsePosInt(arH.value);
    const height = _parsePosInt(hInp.value);
    if (lock && aw && ah && height) {
      const ratio = aw / ah;
      const newW = Math.max(1, Math.round(height * ratio));
      wInp.value = String(newW);
    }
    _settingsGuard = false;
  };
  const recalcOnRatioChange = () => {
    if (_settingsGuard) return; _settingsGuard = true;
    const lock = arLock.checked;
    const aw = _parsePosInt(arW.value);
    const ah = _parsePosInt(arH.value);
    if (lock && aw && ah) {
      const width = _parsePosInt(wInp.value);
      const height = _parsePosInt(hInp.value);
      if (width) {
        const ratio = aw / ah;
        hInp.value = String(Math.max(1, Math.round(width / Math.max(1e-6, ratio))));
      } else if (height) {
        const ratio = aw / ah;
        wInp.value = String(Math.max(1, Math.round(height * ratio)));
      }
    }
    _settingsGuard = false;
  };

  wInp.addEventListener('input', recalcFromWidth);
  hInp.addEventListener('input', recalcFromHeight);
  arW.addEventListener('input', recalcOnRatioChange);
  arH.addEventListener('input', recalcOnRatioChange);
  arLock.addEventListener('change', () => {
    if (arLock.checked) recalcOnRatioChange();
  });
}


