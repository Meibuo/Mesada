// game.js - Sistema Completo de Mesada Gamificada
let currentPlayer = null;

// Criar novo jogador
async function createPlayer() {
    const nameInput = document.getElementById('playerName');
    const name = nameInput ? nameInput.value.trim() : '';
    
    console.log('Tentando criar jogador:', name);
    
    if (!name) {
        showMessage('❌ Digite um nome para o herói!', 'defeat');
        return;
    }
    
    const btn = document.getElementById('createBtn');
    btn.disabled = true;
    btn.textContent = 'Criando...';
    
    try {
        const response = await fetch('/create_player', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({nome: name})
        });
        
        const data = await response.json();
        console.log('Resposta do servidor:', data);
        
        if (data.success) {
            currentPlayer = data.player;
            showMessage(`🎉 Bem-vindo, ${name}! Sua jornada começa agora!`, 'success');
            showGameInterface();
        } else {
            showMessage('❌ Erro ao criar jogador: ' + (data.error || 'Tente outro nome'), 'defeat');
        }
    } catch (error) {
        console.error('Erro detalhado:', error);
        showMessage('❌ Erro de conexão com o servidor!', 'defeat');
    } finally {
        btn.disabled = false;
        btn.textContent = '🎯 Começar Jornada';
    }
}

// Login de jogador existente
async function loginPlayer() {
    const nameInput = document.getElementById('loginName');
    const name = nameInput ? nameInput.value.trim() : '';
    
    if (!name) {
        showMessage('❌ Digite seu nome de herói!', 'defeat');
        return;
    }
    
    try {
        const response = await fetch(`/get_player/${name}`);
        const data = await response.json();
        
        if (data.success) {
            currentPlayer = data.player;
            showMessage(`🎉 Bem-vindo de volta, ${name}!`, 'success');
            showGameInterface();
        } else {
            showMessage('❌ Herói não encontrado! Crie um novo personagem.', 'defeat');
        }
    } catch (error) {
        console.error('Erro no login:', error);
        showMessage('❌ Erro de conexão!', 'defeat');
    }
}

// Mostrar interface do jogo
function showGameInterface() {
    const playerCreation = document.querySelector('.player-creation');
    const gameInterface = document.getElementById('gameInterface');
    
    if (playerCreation) playerCreation.style.display = 'none';
    if (gameInterface) gameInterface.style.display = 'block';
    
    loadGameInterface();
}

// Carregar interface principal do jogo
function loadGameInterface() {
    const gameInterface = document.getElementById('gameInterface');
    
    if (!currentPlayer) {
        showMessage('❌ Erro: Jogador não carregado!', 'defeat');
        return;
    }
    
    gameInterface.innerHTML = `
        <div class="player-stats">
            <h2>👤 ${currentPlayer.nome} - Nível ${currentPlayer.level}</h2>
            <div class="stats-grid">
                <div class="stat">⭐ XP: ${currentPlayer.xp}/${currentPlayer.xp_need}</div>
                <div class="stat">💰 Mesada: R$ ${currentPlayer.mesada.toFixed(2)}</div>
                <div class="stat">✅ Missões: ${currentPlayer.tasks_completed}</div>
                <div class="stat">⚔️ Vitórias: ${currentPlayer.battles_won}/${currentPlayer.battles_won + currentPlayer.battles_lost}</div>
            </div>
            
            <div class="skills-equipment">
                <div class="skills">
                    <h4>💪 Habilidades:</h4>
                    <div class="skill-item">🗡️ Força: ${currentPlayer.skills.forca}</div>
                    <div class="skill-item">🛡️ Defesa: ${currentPlayer.skills.defesa}</div>
                    <div class="skill-item">🍀 Sorte: ${currentPlayer.skills.sorte}</div>
                    <div class="skill-item">🧠 Inteligência: ${currentPlayer.skills.inteligencia}</div>
                </div>
                
                <div class="equipment">
                    <h4>🎒 Equipado:</h4>
                    <div class="equip-item">🏹 Arma: ${currentPlayer.equipped.weapon ? currentPlayer.equipped.weapon.name : 'Nenhuma'}</div>
                    <div class="equip-item">🛡️ Armadura: ${currentPlayer.equipped.armor ? currentPlayer.equipped.armor.name : 'Nenhuma'}</div>
                    <div class="equip-item">💎 Acessório: ${currentPlayer.equipped.accessory ? currentPlayer.equipped.accessory.name : 'Nenhum'}</div>
                </div>
            </div>
        </div>

        <div class="game-nav">
            <button onclick="showSection('missions')">🎯 Missões</button>
            <button onclick="showSection('battles')">⚔️ Batalhas</button>
            <button onclick="showSection('shop')">🛍️ Loja</button>
            <button onclick="showSection('inventory')">🎒 Inventário</button>
            <button onclick="showSection('achievements')">🏆 Conquistas</button>
            <button onclick="showSection('leaderboard')">📊 Ranking</button>
        </div>

        <div id="gameContent">
            <!-- Conteúdo dinâmico será carregado aqui -->
        </div>

        <div id="gameMessages"></div>
    `;
    
    showSection('missions');
}

// Mostrar diferentes seções do jogo
async function showSection(section) {
    const contentDiv = document.getElementById('gameContent');
    
    switch(section) {
        case 'missions':
            contentDiv.innerHTML = `
                <div class="section-header">
                    <h3>🎯 Missões Diárias</h3>
                    <p>Complete missões para ganhar XP e aumentar sua mesada!</p>
                </div>
                <div class="missions-grid">
                    <div class="mission-card" onclick="completeTask('Lavar louça', 1)">
                        <div class="mission-icon">🍽️</div>
                        <div class="mission-info">
                            <h4>Lavar louça</h4>
                            <p>Dificuldade: Fácil</p>
                            <div class="rewards">
                                <span class="xp-reward">+25 XP</span>
                                <span class="money-reward">+R$ 2,50</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mission-card" onclick="completeTask('Fazer lição', 2)">
                        <div class="mission-icon">📚</div>
                        <div class="mission-info">
                            <h4>Fazer lição</h4>
                            <p>Dificuldade: Médio</p>
                            <div class="rewards">
                                <span class="xp-reward">+50 XP</span>
                                <span class="money-reward">+R$ 5,00</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mission-card" onclick="completeTask('Limpar quarto', 3)">
                        <div class="mission-icon">🧹</div>
                        <div class="mission-info">
                            <h4>Limpar quarto</h4>
                            <p>Dificuldade: Difícil</p>
                            <div class="rewards">
                                <span class="xp-reward">+75 XP</span>
                                <span class="money-reward">+R$ 7,50</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mission-card" onclick="completeTask('Estudar extra', 2)">
                        <div class="mission-icon">📖</div>
                        <div class="mission-info">
                            <h4>Estudar matéria extra</h4>
                            <p>Dificuldade: Médio</p>
                            <div class="rewards">
                                <span class="xp-reward">+50 XP</span>
                                <span class="money-reward">+R$ 5,00</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            break;
            
        case 'battles':
            contentDiv.innerHTML = `
                <div class="section-header">
                    <h3>⚔️ Batalhas Épicas</h3>
                    <p>Enfrente inimigos para ganhar recompensas maiores!</p>
                </div>
                <div class="battles-grid">
                    <div class="battle-card" onclick="startBattle(1)">
                        <div class="battle-icon">🐉</div>
                        <div class="battle-info">
                            <h4>Dragão Pequeno</h4>
                            <p>Dificuldade: Fácil</p>
                            <div class="rewards">
                                <span class="xp-reward">+60 XP</span>
                                <span class="money-reward">+R$ 8,00</span>
                            </div>
                            <div class="battle-chance">Chance de vitória: Alta</div>
                        </div>
                    </div>
                    
                    <div class="battle-card" onclick="startBattle(2)">
                        <div class="battle-icon">🧙‍♂️</div>
                        <div class="battle-info">
                            <h4>Mago Malvado</h4>
                            <p>Dificuldade: Médio</p>
                            <div class="rewards">
                                <span class="xp-reward">+120 XP</span>
                                <span class="money-reward">+R$ 16,00</span>
                            </div>
                            <div class="battle-chance">Chance de vitória: Média</div>
                        </div>
                    </div>
                    
                    <div class="battle-card" onclick="startBattle(3)">
                        <div class="battle-icon">👹</div>
                        <div class="battle-info">
                            <h4>Rei Demônio</h4>
                            <p>Dificuldade: Difícil</p>
                            <div class="rewards">
                                <span class="xp-reward">+180 XP</span>
                                <span class="money-reward">+R$ 24,00</span>
                            </div>
                            <div class="battle-chance">Chance de vitória: Baixa</div>
                        </div>
                    </div>
                </div>
            `;
            break;
            
        case 'shop':
            await loadShop();
            break;
            
        case 'inventory':
            loadInventory();
            break;
            
        case 'achievements':
            await loadAchievements();
            break;
            
        case 'leaderboard':
            await loadLeaderboard();
            break;
    }
}

// Completar missão
async function completeTask(taskName, difficulty) {
    try {
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
            
            // Verificar se subiu de nível
            if (data.result.level_ups > 0) {
                showMessage(`🎉 LEVEL UP! Agora você é nível ${data.player.level}! Mesada aumentada!`, 'victory');
            }
            
            // Verificar conquistas
            if (data.result.new_achievements && data.result.new_achievements.length > 0) {
                data.result.new_achievements.forEach(ach => {
                    showMessage(`🏆 Conquista desbloqueada: ${ach.name}! +R$ ${ach.reward},00`, 'victory');
                });
            }
            
            loadGameInterface();
        } else {
            showMessage('❌ Erro ao completar missão!', 'defeat');
        }
    } catch (error) {
        showMessage('❌ Erro de conexão!', 'defeat');
        console.error('Error:', error);
    }
}

// Iniciar batalha
async function startBattle(difficulty) {
    try {
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
            if (data.result.victory) {
                currentPlayer = data.player;
                let message = data.result.message;
                
                // Adicionar informação sobre drop de item
                if (data.result.item_drop) {
                    message += ` 🎁 Item dropado: ${data.result.item_drop.name}!`;
                }
                
                showMessage(message, 'victory');
                
                // Verificar se subiu de nível
                if (data.result.level_ups > 0) {
                    showMessage(`🎉 LEVEL UP! Agora você é nível ${data.player.level}!`, 'victory');
                }
                
                // Verificar conquistas
                if (data.result.new_achievements && data.result.new_achievements.length > 0) {
                    data.result.new_achievements.forEach(ach => {
                        showMessage(`🏆 Conquista desbloqueada: ${ach.name}! +R$ ${ach.reward},00`, 'victory');
                    });
                }
            } else {
                showMessage(data.result.message, 'defeat');
            }
            
            loadGameInterface();
        } else {
            showMessage('❌ Erro na batalha!', 'defeat');
        }
    } catch (error) {
        showMessage('❌ Erro de conexão!', 'defeat');
        console.error('Error:', error);
    }
}

// Carregar loja
async function loadShop() {
    try {
        const response = await fetch('/shop');
        const data = await response.json();
        
        let shopHTML = `
            <div class="section-header">
                <h3>🛍️ Loja do Reino</h3>
                <p>Compre equipamentos para melhorar suas habilidades!</p>
            </div>
            <div class="shop-grid">
        `;
        
        data.items.forEach(item => {
            const canAfford = currentPlayer.mesada >= item.price;
            shopHTML += `
                <div class="shop-item ${!canAfford ? 'cannot-afford' : ''}">
                    <div class="item-icon">${item.name.split(' ')[0]}</div>
                    <div class="item-info">
                        <h4>${item.name}</h4>
                        <div class="item-type">Tipo: ${item.type}</div>
                        <div class="item-stats">
                            ${item.power ? `🗡️ Poder: +${item.power}` : ''}
                            ${item.defense ? `🛡️ Defesa: +${item.defense}` : ''}
                            ${item.luck ? `🍀 Sorte: +${item.luck}` : ''}
                        </div>
                        <div class="item-price">💰 R$ ${item.price},00</div>
                        <button 
                            onclick="buyItem(${item.id})" 
                            ${!canAfford ? 'disabled' : ''}
                            class="buy-btn ${!canAfford ? 'disabled' : ''}"
                        >
                            ${canAfford ? 'Comprar' : 'Mesada Insuficiente'}
                        </button>
                    </div>
                </div>
            `;
        });
        
        shopHTML += '</div>';
        document.getElementById('gameContent').innerHTML = shopHTML;
    } catch (error) {
        showMessage('❌ Erro ao carregar loja!', 'defeat');
        console.error('Error:', error);
    }
}

// Comprar item
async function buyItem(itemId) {
    try {
        const response = await fetch('/buy', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                player_name: currentPlayer.nome,
                item_id: itemId
            })
        });
        
        const data = await response.json();
        if (data.success) {
            currentPlayer = data.player;
            showMessage('✅ Item comprado com sucesso! Verifique seu inventário!', 'success');
            loadGameInterface();
            showSection('inventory');
        } else {
            showMessage('❌ Mesada insuficiente para comprar este item!', 'defeat');
        }
    } catch (error) {
        showMessage('❌ Erro ao comprar item!', 'defeat');
        console.error('Error:', error);
    }
}

// Carregar inventário
function loadInventory() {
    let inventoryHTML = `
        <div class="section-header">
            <h3>🎒 Seu Inventário</h3>
            <p>Gerencie seus itens e equipamentos!</p>
        </div>
    `;
    
    if (currentPlayer.inventory.length === 0) {
        inventoryHTML += `
            <div class="empty-inventory">
                <div class="empty-icon">🎒</div>
                <h4>Seu inventário está vazio</h4>
                <p>Visite a loja para comprar itens incríveis!</p>
                <button onclick="showSection('shop')" class="btn-shop">🛍️ Ir para a Loja</button>
            </div>
        `;
    } else {
        inventoryHTML += `
            <div class="inventory-grid">
                ${currentPlayer.inventory.map(item => `
                    <div class="inventory-item">
                        <div class="item-icon">${item.name.split(' ')[0]}</div>
                        <div class="item-info">
                            <h4>${item.name}</h4>
                            <div class="item-type">Tipo: ${item.type}</div>
                            <div class="item-stats">
                                ${item.power ? `🗡️ Poder: +${item.power}` : ''}
                                ${item.defense ? `🛡️ Defesa: +${item.defense}` : ''}
                                ${item.luck ? `🍀 Sorte: +${item.luck}` : ''}
                            </div>
                            <button onclick="equipItem('${item.name}')" class="equip-btn">
                                Equipar
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    // Mostrar itens equipados
    inventoryHTML += `
        <div class="equipped-section">
            <h4>🎯 Itens Equipados</h4>
            <div class="equipped-items">
                <div class="equipped-item">
                    <strong>🏹 Arma:</strong> ${currentPlayer.equipped.weapon ? currentPlayer.equipped.weapon.name : 'Nenhuma'}
                </div>
                <div class="equipped-item">
                    <strong>🛡️ Armadura:</strong> ${currentPlayer.equipped.armor ? currentPlayer.equipped.armor.name : 'Nenhuma'}
                </div>
                <div class="equipped-item">
                    <strong>💎 Acessório:</strong> ${currentPlayer.equipped.accessory ? currentPlayer.equipped.accessory.name : 'Nenhum'}
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('gameContent').innerHTML = inventoryHTML;
}

// Equipar item
async function equipItem(itemName) {
    try {
        const response = await fetch('/equip', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                player_name: currentPlayer.nome,
                item_name: itemName
            })
        });
        
        const data = await response.json();
        if (data.success) {
            currentPlayer = data.player;
            showMessage('✅ Item equipado com sucesso!', 'success');
            loadGameInterface();
        } else {
            showMessage('❌ Erro ao equipar item!', 'defeat');
        }
    } catch (error) {
        showMessage('❌ Erro ao equipar item!', 'defeat');
        console.error('Error:', error);
    }
}

// Carregar conquistas
async function loadAchievements() {
    try {
        const response = await fetch(`/achievements/${currentPlayer.nome}`);
        const data = await response.json();
        
        let achievementsHTML = `
            <div class="section-header">
                <h3>🏆 Suas Conquistas</h3>
                <p>Desbloqueie conquistas para ganhar recompensas especiais!</p>
            </div>
        `;
        
        // Conquistas desbloqueadas
        achievementsHTML += `
            <div class="achievements-section">
                <h4>✅ Desbloqueadas (${data.unlocked.length})</h4>
                ${data.unlocked.length === 0 ? 
                    '<p class="no-achievements">Nenhuma conquista desbloqueada ainda. Continue jogando!</p>' : 
                    '<div class="achievements-grid">' + 
                    data.unlocked.map(ach => `
                        <div class="achievement unlocked">
                            <div class="achievement-icon">🏆</div>
                            <div class="achievement-info">
                                <h5>${ach.name}</h5>
                                <p>${ach.description}</p>
                                <div class="achievement-reward">🎁 Recompensa: R$ ${ach.reward},00</div>
                            </div>
                        </div>
                    `).join('') + '</div>'
                }
            </div>
        `;
        
        // Conquistas disponíveis
        achievementsHTML += `
            <div class="achievements-section">
                <h4>🔒 Disponível (${data.available.length})</h4>
                ${data.available.length === 0 ? 
                    '<p class="no-achievements">Todas as conquistas foram desbloqueadas! 🎉</p>' : 
                    '<div class="achievements-grid">' +
                    data.available.map(ach => `
                        <div class="achievement locked">
                            <div class="achievement-icon">🔒</div>
                            <div class="achievement-info">
                                <h5>${ach.name}</h5>
                                <p>${ach.description}</p>
                                <div class="achievement-reward">🎁 Recompensa: R$ ${ach.reward},00</div>
                            </div>
                        </div>
                    `).join('') + '</div>'
                }
            </div>
        `;
        
        document.getElementById('gameContent').innerHTML = achievementsHTML;
    } catch (error) {
        showMessage('❌ Erro ao carregar conquistas!', 'defeat');
        console.error('Error:', error);
    }
}

// Carregar ranking
async function loadLeaderboard() {
    try {
        const response = await fetch('/leaderboard');
        const data = await response.json();
        
        let leaderboardHTML = `
            <div class="section-header">
                <h3>📊 Ranking dos Heróis</h3>
                <p>Compare seu progresso com outros aventureiros!</p>
            </div>
            <div class="leaderboard">
        `;
        
        if (data.leaderboard.length === 0) {
            leaderboardHTML += '<p>Nenhum jogador no ranking ainda.</p>';
        } else {
            data.leaderboard.forEach((player, index) => {
                const rankEmoji = index === 0 ? '👑' : index === 1 ? '🥈' : index === 2 ? '🥉' : '🔸';
                const isCurrentPlayer = player.name === currentPlayer.nome;
                
                leaderboardHTML += `
                    <div class="leaderboard-item ${isCurrentPlayer ? 'current-player' : ''}">
                        <span class="rank">${rankEmoji} ${index + 1}</span>
                        <span class="name">${player.name} ${isCurrentPlayer ? '(Você)' : ''}</span>
                        <span class="level">Nível ${player.level}</span>
                        <span class="mesada">R$ ${player.mesada.toFixed(2)}</span>
                        <span class="stats">✅${player.tasks} ⚔️${player.battles_won}</span>
                    </div>
                `;
            });
        }
        
        leaderboardHTML += '</div>';
        document.getElementById('gameContent').innerHTML = leaderboardHTML;
    } catch (error) {
        showMessage('❌ Erro ao carregar ranking!', 'defeat');
        console.error('Error:', error);
    }
}

// Mostrar mensagens no jogo
function showMessage(message, type) {
    const messagesDiv = document.getElementById('gameMessages');
    if (!messagesDiv) {
        console.log('Mensagem:', message, 'Tipo:', type);
        return;
    }
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    messageElement.innerHTML = message;
    messagesDiv.appendChild(messageElement);
    
    // Rolagem automática para a mensagem mais recente
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    // Remover mensagem após 5 segundos
    setTimeout(() => {
        if (messageElement.parentNode) {
            messageElement.remove();
        }
    }, 5000);
}

// Tecla Enter para criar jogador
document.addEventListener('DOMContentLoaded', function() {
    const playerNameInput = document.getElementById('playerName');
    const loginNameInput = document.getElementById('loginName');
    
    if (playerNameInput) {
        playerNameInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                createPlayer();
            }
        });
    }
    
    if (loginNameInput) {
        loginNameInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                loginPlayer();
            }
        });
    }
    
    // Focar no primeiro input
    if (playerNameInput) {
        playerNameInput.focus();
    }
});

// Efeitos visuais para os botões
document.addEventListener('click', function(e) {
    if (e.target.tagName === 'BUTTON' && !e.target.disabled) {
        e.target.style.transform = 'scale(0.95)';
        setTimeout(() => {
            e.target.style.transform = '';
        }, 150);
    }
});