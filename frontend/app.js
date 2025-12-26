// Chat Application with Form-to-Chat Transition
const API_BASE = '/api';

// Streaming configuration - disabled (reasoning models buffer output, so streaming doesn't help)
const USE_STREAMING = false;

// DOM Elements - Form Phase
const formPhase = document.getElementById('form-phase');
const emailForm = document.getElementById('email-form');
const purposeSelect = document.getElementById('purpose-select');
const toneSelect = document.getElementById('tone-select');
const detailsInput = document.getElementById('details-input');
const generateBtn = document.getElementById('generate-btn');
const modelSelect = document.getElementById('model-select');

// DOM Elements - Chat Phase
const chatPhase = document.getElementById('chat-phase');
const messagesContainer = document.getElementById('messages-container');
const messagesDiv = document.getElementById('messages');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const newChatBtn = document.getElementById('new-chat-btn');
const toast = document.getElementById('toast');
const toastText = document.getElementById('toast-text');
const chatHistoryList = document.getElementById('chat-history-list');
const sidebarHint = document.getElementById('sidebar-hint');

// State
let currentEmail = null;
let isLoading = false;
let currentPhase = 'form'; // 'form' or 'chat'
let conversationHistory = []; // Track conversation history for context
let initialInputs = null; // Store initial form inputs for summary panel
let availableModels = [];
let chatHistory = []; // Store all chats
let currentChatId = null; // Track current chat
let initialInputsCount = 0; // Track number of initial inputs/emails in current chat

// Purpose display names
const PURPOSE_LABELS = {
    'relationship_builder': 'Relationship Builder',
    'educational_content': 'Educational Content',
    'follow_up': 'Follow-up',
    'feedback_request': 'Feedback Request',
    'scheduling': 'Scheduling',
    'other': 'Other'
};

// Tone display names
const TONE_LABELS = {
    'professional': 'Professional',
    'formal': 'Formal',
    'friendly': 'Friendly',
    'casual': 'Casual'
};

// Length display names
const LENGTH_LABELS = {
    'short': 'Short',
    'medium': 'Medium',
    'long': 'Long'
};

// Cost display element
const costDisplayValue = document.getElementById('cost-display-value');

// Update cost display - now per-chat
function updateCostDisplay(additionalCost = 0) {
    if (!currentChatId) return;

    const chatIndex = chatHistory.findIndex(c => c.id === currentChatId);
    if (chatIndex !== -1) {
        chatHistory[chatIndex].cost = (chatHistory[chatIndex].cost || 0) + additionalCost;
        saveChatHistory();
        displayCurrentChatCost();
    }
}

// Display the cost for the current chat
function displayCurrentChatCost() {
    if (!costDisplayValue) return;

    if (!currentChatId) {
        costDisplayValue.textContent = '$0.000000';
        return;
    }

    const chat = chatHistory.find(c => c.id === currentChatId);
    const cost = chat ? (chat.cost || 0) : 0;
    costDisplayValue.textContent = `$${cost.toFixed(6)}`;
}

// Initialize
init();

async function init() {
    // Form event listeners
    emailForm.addEventListener('submit', handleFormSubmit);

    // Chat event listeners
    messageInput.addEventListener('input', handleInputChange);
    messageInput.addEventListener('keydown', handleKeyDown);
    sendBtn.addEventListener('click', sendMessage);
    newChatBtn.addEventListener('click', startNewChat);

    // Auto-resize textarea
    messageInput.addEventListener('input', autoResizeTextarea);
    detailsInput.addEventListener('input', autoResizeDetailsTextarea);

    // Load available models
    await loadModels();

    // Clear any persisted data on page load/refresh (fresh session each time)
    sessionStorage.removeItem('fmg-muse-chat-history');

    // Reset cost display for fresh session
    displayCurrentChatCost();
}

async function loadModels() {
    try {
        const response = await fetch(`${API_BASE}/models`);
        if (response.ok) {
            const data = await response.json();
            availableModels = data.models;
            const defaultModel = data.default;

            // Populate model select
            modelSelect.innerHTML = availableModels.map(model => {
                const isDefault = model.id === defaultModel;
                return `<option value="${model.id}" ${isDefault ? 'selected' : ''}>
                    ${model.name}
                </option>`;
            }).join('');
        }
    } catch (error) {
        console.error('Failed to load models:', error);
    }
}

function loadChatHistory() {
    const saved = sessionStorage.getItem('fmg-muse-chat-history');
    if (saved) {
        chatHistory = JSON.parse(saved);
        renderChatHistory();
    }
}

function saveChatHistory() {
    sessionStorage.setItem('fmg-muse-chat-history', JSON.stringify(chatHistory));
}

function renderChatHistory() {
    if (chatHistory.length === 0) {
        chatHistoryList.innerHTML = '';
        sidebarHint.style.display = 'block';
        return;
    }

    sidebarHint.style.display = 'none';
    chatHistoryList.innerHTML = chatHistory.map(chat => `
        <div class="chat-history-item ${chat.id === currentChatId ? 'active' : ''}" data-id="${chat.id}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
            <span class="chat-history-title" id="chat-title-${chat.id}">${escapeHtml(chat.title)}</span>
            <div class="chat-history-actions">
                <button class="chat-history-btn" onclick="event.stopPropagation(); renameChat('${chat.id}')" title="Rename">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                </button>
                <button class="chat-history-btn" onclick="event.stopPropagation(); deleteChat('${chat.id}')" title="Delete">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                </button>
            </div>
        </div>
    `).join('');

    // Add click handlers
    document.querySelectorAll('.chat-history-item').forEach(item => {
        item.addEventListener('click', () => loadChat(item.dataset.id));
    });
}

function createNewChat(title) {
    const chat = {
        id: Date.now().toString(),
        title: title || 'New Email',
        createdAt: new Date().toISOString(),
        initialInputs: null,
        conversationHistory: [],
        currentEmail: null,
        cost: 0, // Initialize cost for this chat
        emailCount: 0 // Track number of emails generated in this chat
    };
    chatHistory.unshift(chat);
    saveChatHistory();
    return chat;
}

function updateCurrentChat() {
    if (!currentChatId) return;

    const chatIndex = chatHistory.findIndex(c => c.id === currentChatId);
    if (chatIndex !== -1) {
        chatHistory[chatIndex].conversationHistory = conversationHistory;
        chatHistory[chatIndex].currentEmail = currentEmail;
        chatHistory[chatIndex].initialInputs = initialInputs;
        saveChatHistory();
    }
}

function loadChat(chatId) {
    const chat = chatHistory.find(c => c.id === chatId);
    if (!chat) return;

    currentChatId = chatId;
    conversationHistory = chat.conversationHistory || [];
    currentEmail = chat.currentEmail;
    initialInputs = chat.initialInputs;
    initialInputsCount = chat.emailCount || 0;

    // Display cost for this chat
    displayCurrentChatCost();

    // Rebuild the UI
    messagesDiv.innerHTML = '';

    // Remove existing inputs summary
    const existingSummary = document.getElementById('inputs-summary');
    if (existingSummary) existingSummary.remove();

    if (conversationHistory.length > 0) {
        // Show chat phase
        formPhase.hidden = true;
        chatPhase.hidden = false;
        currentPhase = 'chat';

        // Add inputs summary if exists
        if (initialInputs) addInputsSummary();

        // Rebuild messages with numbering
        let emailIndex = 0;
        conversationHistory.forEach(msg => {
            if (msg.role === 'user') {
                addMessage('user', msg.content);
            } else if (msg.email_subject && msg.email_body) {
                emailIndex++;
                addAssistantMessage({ subject: msg.email_subject, body: msg.email_body }, emailIndex, initialInputsCount);
            }
        });
    } else {
        // Show form phase
        formPhase.hidden = false;
        chatPhase.hidden = true;
        currentPhase = 'form';
    }

    renderChatHistory();
}

function renameChat(chatId) {
    const chat = chatHistory.find(c => c.id === chatId);
    if (!chat) return;

    const titleSpan = document.getElementById(`chat-title-${chatId}`);
    const currentTitle = chat.title;

    titleSpan.innerHTML = `<input type="text" value="${escapeHtml(currentTitle)}" onblur="saveRename('${chatId}', this)" onkeydown="handleRenameKey(event, '${chatId}', this)">`;
    titleSpan.querySelector('input').focus();
    titleSpan.querySelector('input').select();
}

function saveRename(chatId, input) {
    const newTitle = input.value.trim() || 'Untitled';
    const chatIndex = chatHistory.findIndex(c => c.id === chatId);
    if (chatIndex !== -1) {
        chatHistory[chatIndex].title = newTitle;
        saveChatHistory();
        renderChatHistory();
    }
}

function handleRenameKey(event, chatId, input) {
    if (event.key === 'Enter') {
        input.blur();
    } else if (event.key === 'Escape') {
        renderChatHistory();
    }
}

function deleteChat(chatId) {
    if (!confirm('Are you sure you want to delete this chat?')) return;

    chatHistory = chatHistory.filter(c => c.id !== chatId);
    saveChatHistory();

    if (currentChatId === chatId) {
        currentChatId = null;
        startNewChat();
    }

    renderChatHistory();
}

function autoResizeDetailsTextarea() {
    detailsInput.style.height = 'auto';
    detailsInput.style.height = Math.min(detailsInput.scrollHeight, 200) + 'px';
}

function handleInputChange() {
    const hasText = messageInput.value.trim().length > 0;
    sendBtn.disabled = !hasText || isLoading;
}

function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!sendBtn.disabled) {
            sendMessage();
        }
    }
}

function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 200) + 'px';
}

async function handleFormSubmit(e) {
    e.preventDefault();

    if (isLoading) return;

    const purpose = purposeSelect.value;
    const tone = toneSelect.value;
    const length = document.querySelector('input[name="length"]:checked').value;
    const details = detailsInput.value.trim();
    const model = modelSelect.value;

    if (!purpose || !details) {
        showToast('Please fill in all required fields', 'error');
        return;
    }

    // Store initial inputs for summary panel
    initialInputs = { purpose, tone, length, details };

    // Create new chat with first few words as title
    const chatTitle = details.substring(0, 40) + (details.length > 40 ? '...' : '');
    const chat = createNewChat(chatTitle);
    currentChatId = chat.id;

    // Show loading state on button
    isLoading = true;
    generateBtn.disabled = true;
    generateBtn.innerHTML = `
        <div class="typing-indicator" style="padding: 0;">
            <span></span>
            <span></span>
            <span></span>
        </div>
        Generating...
    `;

    const requestBody = {
        purpose,
        details,
        length,
        tone,
        model,
        history: conversationHistory
    };

    if (USE_STREAMING) {
        // Use streaming endpoint
        // First transition to chat phase with streaming placeholder
        formPhase.hidden = true;
        chatPhase.hidden = false;
        currentPhase = 'chat';
        addInputsSummary();
        addMessage('user', details);

        // Create streaming message container
        const streamingMsg = createStreamingMessage();
        let fullText = '';

        await streamEmailGeneration(
            '/generate-email/stream',
            requestBody,
            // onChunk
            (chunk, accumulated) => {
                fullText = accumulated;
                updateStreamingMessage(streamingMsg, fullText);
            },
            // onComplete
            (finalText) => {
                const emailData = parseStreamedEmail(finalText);
                currentEmail = emailData;

                // Replace streaming message with final email display
                streamingMsg.remove();

                // Increment email count and add with numbering
                incrementEmailCount();
                addAssistantMessage(emailData, initialInputsCount, initialInputsCount);

                // Add to conversation history
                conversationHistory.push({
                    role: 'user',
                    content: details,
                    email_subject: null,
                    email_body: null
                });
                conversationHistory.push({
                    role: 'assistant',
                    content: 'Generated email',
                    email_subject: emailData.subject,
                    email_body: emailData.body
                });

                updateCurrentChat();
                renderChatHistory();
                isLoading = false;
                messageInput.focus();
            },
            // onError
            (error) => {
                streamingMsg.remove();
                addMessage('assistant', `Sorry, I encountered an error: ${error.message}. Please try again.`);
                showToast(error.message, 'error');
                isLoading = false;
            }
        );
    } else {
        // Use non-streaming endpoint
        try {
            const response = await fetch(`${API_BASE}/generate-email`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to generate email');
            }

            const emailData = await response.json();
            currentEmail = emailData;

            // Update cost display if usage info is present
            if (emailData.usage && emailData.usage.cost) {
                updateCostDisplay(emailData.usage.cost);
            }

            // Add to conversation history
            conversationHistory.push({
                role: 'user',
                content: details,
                email_subject: null,
                email_body: null
            });
            conversationHistory.push({
                role: 'assistant',
                content: 'Generated email',
                email_subject: emailData.subject,
                email_body: emailData.body
            });

            // Update chat in history
            updateCurrentChat();
            renderChatHistory();

            // Transition to chat phase
            transitionToChat(details, emailData);

        } catch (error) {
            showToast(error.message, 'error');
            // Reset button
            generateBtn.disabled = false;
            generateBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                </svg>
                Generate Email
            `;
        } finally {
            isLoading = false;
        }
    }
}

function transitionToChat(userRequest, emailData) {
    // Hide form phase
    formPhase.hidden = true;

    // Show chat phase
    chatPhase.hidden = false;
    currentPhase = 'chat';

    // Add inputs summary panel
    addInputsSummary();

    // Add initial user message showing what they requested
    addMessage('user', userRequest);

    // Increment email count and update chat
    incrementEmailCount();

    // Add the generated email as assistant response with numbering
    addAssistantMessage(emailData, initialInputsCount, initialInputsCount);

    // Focus on chat input
    messageInput.focus();

    // Scroll to bottom
    scrollToBottom();
}

// Increment email count for current chat
function incrementEmailCount() {
    initialInputsCount++;
    if (currentChatId) {
        const chatIndex = chatHistory.findIndex(c => c.id === currentChatId);
        if (chatIndex !== -1) {
            chatHistory[chatIndex].emailCount = initialInputsCount;
            saveChatHistory();
        }
    }
}

function addInputsSummary() {
    if (!initialInputs) return;

    const summaryDiv = document.createElement('div');
    summaryDiv.className = 'inputs-summary';
    summaryDiv.id = 'inputs-summary';
    summaryDiv.innerHTML = `
        <div class="inputs-summary-header">
            <div class="inputs-summary-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M12 16v-4"></path>
                    <path d="M12 8h.01"></path>
                </svg>
                Initial Settings
            </div>
            <button class="inputs-summary-toggle" onclick="toggleInputsSummary()" title="Toggle details">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 15l-6-6-6 6"></path>
                </svg>
            </button>
        </div>
        <div class="inputs-summary-grid" id="inputs-summary-grid">
            <div class="input-summary-item">
                <div class="input-summary-label">Purpose</div>
                <div class="input-summary-value">${PURPOSE_LABELS[initialInputs.purpose] || initialInputs.purpose}</div>
            </div>
            <div class="input-summary-item">
                <div class="input-summary-label">Tone</div>
                <div class="input-summary-value">${TONE_LABELS[initialInputs.tone] || initialInputs.tone}</div>
            </div>
            <div class="input-summary-item">
                <div class="input-summary-label">Length</div>
                <div class="input-summary-value">${LENGTH_LABELS[initialInputs.length] || initialInputs.length}</div>
            </div>
            <div class="input-summary-item">
                <div class="input-summary-label">Model</div>
                <div class="input-summary-value">${getModelDisplayName(modelSelect.value)}</div>
            </div>
        </div>
    `;

    messagesContainer.insertBefore(summaryDiv, messagesDiv);
}

function getModelDisplayName(modelId) {
    const model = availableModels.find(m => m.id === modelId);
    return model ? model.name : modelId.split('/').pop();
}

function toggleInputsSummary() {
    const grid = document.getElementById('inputs-summary-grid');
    const toggle = document.querySelector('.inputs-summary-toggle svg');

    if (grid.style.display === 'none') {
        grid.style.display = 'grid';
        toggle.innerHTML = '<path d="M18 15l-6-6-6 6"></path>';
    } else {
        grid.style.display = 'none';
        toggle.innerHTML = '<path d="M6 9l6 6 6-6"></path>';
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isLoading) return;

    // Add user message to UI
    addMessage('user', message);

    // Add to conversation history
    conversationHistory.push({
        role: 'user',
        content: message,
        email_subject: null,
        email_body: null
    });

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    handleInputChange();

    // Show loading
    isLoading = true;
    sendBtn.disabled = true;

    if (USE_STREAMING) {
        // Use streaming
        const streamingMsg = createStreamingMessage();
        const isRefinement = currentEmail && isRefinementRequest(message);

        let endpoint, requestBody;

        if (isRefinement) {
            endpoint = '/refine-email/stream';
            requestBody = {
                original_subject: currentEmail.subject,
                original_body: currentEmail.body,
                feedback: message,
                model: modelSelect.value,
                history: conversationHistory
            };
        } else {
            const purpose = detectPurpose(message);
            const length = detectLength(message);
            const tone = initialInputs?.tone || 'professional';

            endpoint = '/generate-email/stream';
            requestBody = {
                purpose,
                details: message,
                length,
                tone,
                model: modelSelect.value,
                history: conversationHistory
            };
        }

        await streamEmailGeneration(
            endpoint,
            requestBody,
            // onChunk
            (chunk, accumulated) => {
                updateStreamingMessage(streamingMsg, accumulated);
            },
            // onComplete
            (finalText) => {
                const emailData = parseStreamedEmail(finalText);
                currentEmail = emailData;

                streamingMsg.remove();

                // Increment email count and add with numbering
                incrementEmailCount();
                addAssistantMessage(emailData, initialInputsCount, initialInputsCount);

                conversationHistory.push({
                    role: 'assistant',
                    content: 'Generated/refined email',
                    email_subject: emailData.subject,
                    email_body: emailData.body
                });

                updateCurrentChat();
                isLoading = false;
                handleInputChange();
                scrollToBottom();
            },
            // onError
            (error) => {
                streamingMsg.remove();
                addMessage('assistant', `Sorry, I encountered an error: ${error.message}. Please try again.`);
                showToast(error.message, 'error');
                isLoading = false;
                handleInputChange();
            }
        );
    } else {
        // Use non-streaming
        const loadingMsg = addLoadingMessage();

        try {
            let response;

            // Check if this is a refinement request or new email
            if (currentEmail && isRefinementRequest(message)) {
                response = await refineEmail(message);
            } else {
                response = await generateEmailFromChat(message);
            }

            // Remove loading
            loadingMsg.remove();

            // Update cost display if usage info is present
            if (response.usage && response.usage.cost) {
                updateCostDisplay(response.usage.cost);
            }

            // Increment email count and add assistant response with numbering
            incrementEmailCount();
            addAssistantMessage(response, initialInputsCount, initialInputsCount);
            currentEmail = response;

            // Add to conversation history
            conversationHistory.push({
                role: 'assistant',
                content: 'Generated/refined email',
                email_subject: response.subject,
                email_body: response.body
            });

            // Update chat history
            updateCurrentChat();

        } catch (error) {
            loadingMsg.remove();
            addMessage('assistant', `Sorry, I encountered an error: ${error.message}. Please try again.`);
            showToast(error.message, 'error');
        } finally {
            isLoading = false;
            handleInputChange();
        }

        // Scroll to bottom
        scrollToBottom();
    }
}

function isRefinementRequest(message) {
    const refinementKeywords = [
        // Standard refinements
        'make it', 'change', 'shorter', 'longer', 'more', 'less',
        'casual', 'formal', 'friendly', 'professional', 'urgent',
        'add', 'remove', 'update', 'modify', 'revise', 'edit',
        'tone', 'rewrite', 'adjust', 'tweak',
        // Creative style transformations
        'like a', 'as a', 'in the style', 'write as', 'sound like',
        'pirate', 'shakespeare', 'yoda', 'gen z', 'genz', 'millennial',
        'medieval', 'victorian', 'cowboy', 'robot', 'alien',
        'funny', 'humorous', 'serious', 'dramatic', 'poetic',
        'hip hop', 'rapper', 'valley girl', 'surfer', 'british',
        'australian', 'southern', 'new york', 'texan',
        'emoji', 'meme', 'sarcastic', 'enthusiastic', 'deadpan',
        'corporate', 'startup', 'academic', 'casual friday',
        'lingo', 'slang', 'speak', 'talk', 'style'
    ];

    const lowerMessage = message.toLowerCase();
    return refinementKeywords.some(keyword => lowerMessage.includes(keyword));
}

async function generateEmailFromChat(details) {
    // Detect purpose from message
    const purpose = detectPurpose(details);
    const length = detectLength(details);
    const tone = initialInputs?.tone || 'professional';
    const model = modelSelect.value;

    const response = await fetch(`${API_BASE}/generate-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            purpose,
            details,
            length,
            tone,
            model,
            history: conversationHistory
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to generate email');
    }

    return response.json();
}

async function refineEmail(feedback) {
    const model = modelSelect.value;

    const response = await fetch(`${API_BASE}/refine-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            original_subject: currentEmail.subject,
            original_body: currentEmail.body,
            feedback,
            model,
            history: conversationHistory
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to refine email');
    }

    return response.json();
}

function detectPurpose(text) {
    const lower = text.toLowerCase();

    if (lower.includes('thank') || lower.includes('grateful') || lower.includes('appreciate')) {
        return 'relationship_builder';
    }
    if (lower.includes('follow up') || lower.includes('following up') || lower.includes('check in')) {
        return 'follow_up';
    }
    if (lower.includes('schedule') || lower.includes('meeting') || lower.includes('calendar') || lower.includes('appointment')) {
        return 'scheduling';
    }
    if (lower.includes('feedback') || lower.includes('opinion') || lower.includes('thoughts')) {
        return 'feedback_request';
    }
    if (lower.includes('inform') || lower.includes('update') || lower.includes('let them know') || lower.includes('share') || lower.includes('explain') || lower.includes('educate')) {
        return 'educational_content';
    }
    if (lower.includes('reconnect') || lower.includes('catch up') || lower.includes('how are you') || lower.includes('relationship')) {
        return 'relationship_builder';
    }

    return 'other'; // Default
}

function detectLength(text) {
    const lower = text.toLowerCase();

    if (lower.includes('short') || lower.includes('brief') || lower.includes('quick')) {
        return 'short';
    }
    if (lower.includes('long') || lower.includes('detailed') || lower.includes('comprehensive')) {
        return 'long';
    }

    return 'medium';
}

function addMessage(type, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const avatarIcon = type === 'user'
        ? '<svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'
        : '<svg viewBox="0 0 24 24"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>';

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatarIcon}</div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(content)}</div>
        </div>
    `;

    messagesDiv.appendChild(messageDiv);
    scrollToBottom();

    return messageDiv;
}

function addAssistantMessage(email, currentIndex = null, totalCount = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    const emailId = `email-${Date.now()}`;

    // Generate version footer for bottom right
    const versionFooter = (currentIndex !== null && totalCount !== null)
        ? `<div class="email-version-footer"><span class="email-version">${currentIndex} / ${totalCount}</span></div>`
        : '';

    messageDiv.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
        </div>
        <div class="message-content">
            <div class="message-text">Here's your email:</div>
            <div class="email-display" id="${emailId}">
                <div class="email-header">
                    <span class="email-label">Generated Email</span>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <button class="edit-email-btn" onclick="toggleEditMode('${emailId}', this)">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                            </svg>
                            Edit
                        </button>
                        <button class="copy-btn" onclick="copyEmail(this, '${emailId}')">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"></path>
                            </svg>
                            Copy
                        </button>
                    </div>
                </div>
                <div class="email-subject">
                    <div class="email-subject-label">Subject</div>
                    <div class="email-subject-text" data-field="subject">${escapeHtml(email.subject)}</div>
                </div>
                <div class="email-body">
                    <div class="email-body-text" data-field="body">${escapeHtml(email.body)}</div>
                </div>
                ${versionFooter}
            </div>
            <div class="message-text" style="margin-top: 12px; color: var(--text-muted); font-size: 0.875rem;">
                Want any changes? Just tell me what to adjust.
            </div>
        </div>
    `;

    // Store email data on the element
    messageDiv.dataset.emailSubject = email.subject;
    messageDiv.dataset.emailBody = email.body;

    messagesDiv.appendChild(messageDiv);
    scrollToBottom();
}

function toggleEditMode(emailId, btn) {
    const emailDisplay = document.getElementById(emailId);
    if (!emailDisplay) return;

    const subjectEl = emailDisplay.querySelector('[data-field="subject"]');
    const bodyEl = emailDisplay.querySelector('[data-field="body"]');
    const isEditing = btn.classList.contains('editing');

    if (isEditing) {
        // Save and exit edit mode
        subjectEl.contentEditable = 'false';
        bodyEl.contentEditable = 'false';
        subjectEl.classList.remove('editable');
        bodyEl.classList.remove('editable');
        btn.classList.remove('editing');
        btn.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            Edit
        `;

        // Update current email
        currentEmail.subject = subjectEl.textContent;
        currentEmail.body = bodyEl.textContent;
        updateCurrentChat();

        showToast('Changes saved!', 'success');
    } else {
        // Enter edit mode
        subjectEl.contentEditable = 'true';
        bodyEl.contentEditable = 'true';
        subjectEl.classList.add('editable');
        bodyEl.classList.add('editable');
        btn.classList.add('editing');
        btn.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Save
        `;

        subjectEl.focus();
    }
}

function addLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';

    messageDiv.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
        </div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    messagesDiv.appendChild(messageDiv);
    scrollToBottom();

    return messageDiv;
}

function createStreamingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant streaming';

    messageDiv.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
        </div>
        <div class="message-content">
            <div class="streaming-text"></div>
            <div class="streaming-cursor"></div>
        </div>
    `;

    messagesDiv.appendChild(messageDiv);
    scrollToBottom();

    return messageDiv;
}

function updateStreamingMessage(messageDiv, text) {
    const streamingText = messageDiv.querySelector('.streaming-text');
    if (streamingText) {
        streamingText.textContent = text;
        scrollToBottom();
    }
}

function startNewChat() {
    // Save current chat if exists
    if (currentChatId) {
        updateCurrentChat();
    }

    // Clear messages
    messagesDiv.innerHTML = '';

    // Remove inputs summary if it exists
    const inputsSummary = document.getElementById('inputs-summary');
    if (inputsSummary) {
        inputsSummary.remove();
    }

    currentEmail = null;
    conversationHistory = [];
    initialInputs = null;
    currentChatId = null;
    initialInputsCount = 0;

    // Reset cost display
    displayCurrentChatCost();

    // Reset form
    emailForm.reset();
    purposeSelect.value = '';
    toneSelect.value = 'professional';
    detailsInput.value = '';

    // Reset generate button
    generateBtn.disabled = false;
    generateBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
        </svg>
        Generate Email
    `;

    // Show form phase, hide chat phase
    formPhase.hidden = false;
    chatPhase.hidden = true;
    currentPhase = 'form';

    // Clear chat input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    handleInputChange();

    // Update history display
    renderChatHistory();

    // Focus on details input
    detailsInput.focus();
}

async function copyEmail(btn, emailId) {
    const emailDisplay = document.getElementById(emailId);
    let subject, body;

    if (emailDisplay) {
        const subjectEl = emailDisplay.querySelector('[data-field="subject"]');
        const bodyEl = emailDisplay.querySelector('[data-field="body"]');
        subject = subjectEl ? subjectEl.textContent : currentEmail.subject;
        body = bodyEl ? bodyEl.textContent : currentEmail.body;
    } else if (currentEmail) {
        subject = currentEmail.subject;
        body = currentEmail.body;
    } else {
        return;
    }

    const emailText = `Subject: ${subject}\n\n${body}`;

    try {
        await navigator.clipboard.writeText(emailText);
        btn.classList.add('copied');
        btn.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Copied!
        `;

        showToast('Copied to clipboard!', 'success');

        setTimeout(() => {
            btn.classList.remove('copied');
            btn.innerHTML = `
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"></path>
                </svg>
                Copy
            `;
        }, 2000);
    } catch (error) {
        showToast('Failed to copy', 'error');
    }
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type = '') {
    toastText.textContent = message;
    toast.className = 'toast' + (type ? ` ${type}` : '');
    toast.hidden = false;

    setTimeout(() => {
        toast.hidden = true;
    }, 3000);
}

// Streaming helper function
async function streamEmailGeneration(endpoint, requestBody, onChunk, onComplete, onError) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') {
                        onComplete(fullText);
                        return;
                    }
                    if (data.startsWith('[ERROR]')) {
                        throw new Error(data.slice(8));
                    }
                    fullText += data;
                    onChunk(data, fullText);
                }
            }
        }

        onComplete(fullText);
    } catch (error) {
        onError(error);
    }
}

// Parse streamed email content to extract subject and body
function parseStreamedEmail(text) {
    let subject = '';
    let body = text;

    // Try to extract subject from the text
    const subjectMatch = text.match(/^Subject:\s*(.+?)(?:\n\n|\r\n\r\n)/i);
    if (subjectMatch) {
        subject = subjectMatch[1].trim();
        body = text.slice(subjectMatch[0].length).trim();
    } else {
        // Check for "Subject:" at the start
        const lines = text.split('\n');
        if (lines[0] && lines[0].toLowerCase().startsWith('subject:')) {
            subject = lines[0].replace(/^subject:\s*/i, '').trim();
            body = lines.slice(1).join('\n').trim();
            // Remove leading empty lines from body
            body = body.replace(/^\n+/, '');
        }
    }

    return { subject, body };
}

// Navigate to a specific email in the conversation (scroll to it)
function navigateEmail(index) {
    const emailDisplays = messagesDiv.querySelectorAll('.email-display');
    if (index >= 1 && index <= emailDisplays.length) {
        const targetEmail = emailDisplays[index - 1];
        if (targetEmail) {
            targetEmail.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // Add a brief highlight effect
            targetEmail.style.boxShadow = '0 0 0 2px var(--primary)';
            setTimeout(() => {
                targetEmail.style.boxShadow = '';
            }, 1500);
        }
    }
}

// Make functions globally available
window.copyEmail = copyEmail;
window.toggleInputsSummary = toggleInputsSummary;
window.toggleEditMode = toggleEditMode;
window.renameChat = renameChat;
window.saveRename = saveRename;
window.handleRenameKey = handleRenameKey;
window.deleteChat = deleteChat;
window.navigateEmail = navigateEmail;
