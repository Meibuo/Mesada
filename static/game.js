let currentPlayer = null;

async function createPlayer() {
    const name = document.getElementById('playerName').value;
    
    const response = await fetch('/create_player', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({nome: name})
    });
    
    const data = await response.json();
    
    if (data.success) {
        currentPlayer = data.player;
        showGameInterface();
    }
}

function showGameInterface() {
    document.querySelector('.player-creation').style.display = 'none';
    document.getElementById('gameInterface').style.display = 'block';
    
    // Carregar interface do jogo
    loadGameInterface();
}

function loadGameInterface() {
    const gameInterface = document.getElementById('gameInterface');
    
    gameInterface.innerHTML = `
        <div class="player-stats">
            <h2>👤 ${currentPlayer.nome}</h2>
            <div class="stats-grid">
                <div class="stat">🎯 Level: ${currentPlayer.level}</div>
                <div class="stat">⭐ XP: ${currentPlayer.xp}/${currentPlayer.xp_need}</div>
                <div class="stat">💰 Mesada: R$ ${currentPlayer.mesada.toFixed(2)}</div>
                <div class="stat">✅ Tasks: ${currentPlayer.tasks_completed}</div>
            </div>
        </div>

        <div class="missions">
            <h3>🎯 Missões Diárias</h3>
            <div class="mission" onclick="completeTask('Lavar louça', 1)">
                🍽️ Lavar louça (+25 XP, +R$ 2,00)
            </div>
            <div class="mission" onclick="completeTask('Fazer lição', 2)">
                📚 Fazer lição (+50 XP, +R$ 4,00)
            </div>
            <div class="mission" onclick="completeTask('Limpar quarto', 3)">
                🧹 Limpar quarto (+75 XP, +R$ 6,00)
            </div>
        </div>

        <div class="battles">
            <h3>⚔️ Batalhas</h3>
            <div class="battle" onclick="startBattle(1)">
                🐉 Dragão Pequeno (Fácil)
            </div>
            <div class="battle" onclick="startBattle(2)">
                🧙‍♂️ Mago Malvado (Médio)
            </div>
            <div class="battle" onclick="startBattle(3)">
                👹 Rei Demônio (Difícil)
            </div>
        </div>

        <div id="gameMessages"></div>
    `;
}

async function completeTask(taskName, difficulty) {
    const response = await fetch('/complete_task', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            nome: currentPlayer.nome,
            task_name: taskName,
            difficulty: difficulty
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        currentPlayer = data.player;
        showMessage(data.result.message, 'success');
        loadGameInterface();
    }
}

async function startBattle(difficulty) {
    const response = await fetch('/battle', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            nome: currentPlayer.nome,
            difficulty: difficulty
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        if (data.victory) {
            currentPlayer = data.player;
            showMessage(data.message, 'victory');
        } else {
            showMessage(data.message, 'defeat');
        }
        loadGameInterface();
    }
}

function showMessage(message, type) {
    const messagesDiv = document.getElementById('gameMessages');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    messageElement.textContent = message;
    messagesDiv.appendChild(messageElement);
    
    setTimeout(() => {
        messageElement.remove();
    }, 5000);
}