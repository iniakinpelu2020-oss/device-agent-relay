const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN;
const TELEGRAM_API = `https://api.telegram.org/bot${TELEGRAM_TOKEN}`;

// Store connected agents and pending task queue
let pendingTasks = [];
let agentStatus = { laptopConnected: false, lastSeen: null };

// Helper function to send messages to Telegram
async function sendMessage(chatId, text) {
    try {
        await axios.post(`${TELEGRAM_API}/sendMessage`, {
            chat_id: chatId,
            text: text,
            parse_mode: 'Markdown'
        });
    } catch (err) {
        console.error('Failed to send Telegram message:', err.message);
    }
}

// Endpoint 1: Telegram Webhook (Receives commands from your phone)
app.post('/telegram-webhook', async (req, res) => {
    const message = req.body.message;
    if (!message || !message.text) return res.sendStatus(200);

    const chatId = message.chat.id;
    const commandText = message.text.trim();

    // Handle /start command
    if (commandText === '/start') {
        const welcomeMessage = 
`🤖 *Device Agent Controller Online*

Send any instruction (e.g., *"fetch document.pdf"*, *"run script"*).

*Current Status:*
• Laptop Agent: ${agentStatus.laptopConnected ? '🟢 Online' : '🔴 Offline'}
• Queued Tasks: ${pendingTasks.length}`;

        await sendMessage(chatId, welcomeMessage);
        return res.sendStatus(200);
    }

    // Handle /status command
    if (commandText === '/status') {
        const statusMessage = 
`📊 *System Status*
• Laptop: ${agentStatus.laptopConnected ? '🟢 Online' : '🔴 Offline'}
• Last Active: ${agentStatus.lastSeen ? agentStatus.lastSeen.toISOString() : 'Never'}
• Pending Tasks: ${pendingTasks.length}`;

        await sendMessage(chatId, statusMessage);
        return res.sendStatus(200);
    }

    // Queue standard execution commands
    const task = {
        id: Date.now(),
        command: commandText,
        chatId: chatId,
        timestamp: new Date()
    };
    pendingTasks.push(task);

    await sendMessage(
        chatId, 
        `⏳ *Task Queued:* "${commandText}"\nAgent Status: ${agentStatus.laptopConnected ? '🟢 Online' : '🔴 Offline (Fallback active)'}`
    );

    res.sendStatus(200);
});

// Endpoint 2: Agent Poll (Desktop / Cloud VM polls for tasks)
app.get('/agent/poll', (req, res) => {
    agentStatus.laptopConnected = true;
    agentStatus.lastSeen = new Date();

    if (pendingTasks.length > 0) {
        const nextTask = pendingTasks.shift();
        return res.json({ status: 'task_available', task: nextTask });
    }
    res.json({ status: 'idle' });
});

// Endpoint 3: Agent Results (Agent returns execution output)
app.post('/agent/results', async (req, res) => {
    const { chatId, output } = req.body;
    await sendMessage(chatId, `✅ *Task Completed:*\n\n\`\`\`\n${output}\n\`\`\``);
    res.sendStatus(200);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Relay active on port ${PORT}`));
