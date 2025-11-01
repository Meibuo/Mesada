from flask import Flask, render_template, request, jsonify
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = '30591bbfa70ae38582897d226608fd99'

# Dados do jogo
players = {}
shop_items = []
achievements = []
leaderboard = []

# Inicializar dados do jogo
def init_game_data():
    global shop_items, achievements
    
    # Itens da loja
    shop_items = [
        {'id': 1, 'name': '🏹 Arco Mágico', 'price': 50, 'type': 'weapon', 'power': 10},
        {'id': 2, 'name': '🛡️ Escudo Heróico', 'price': 40, 'type': 'armor', 'defense': 8},
        {'id': 3, 'name': '💎 Pedra da Sorte', 'price': 30, 'type': 'accessory', 'luck': 5},
        {'id': 4, 'name': '🎒 Bolsa Expansiva', 'price': 25, 'type': 'utility', 'capacity': 3},
        {'id': 5, 'name': '⚡ Poção de Energia', 'price': 15, 'type': 'consumable', 'effect': 'energy_boost'}
    ]
    
    # Conquistas
    achievements = [
        {'id': 1, 'name': '🎯 Primeiros Passos', 'description': 'Complete sua primeira missão', 'reward': 25},
        {'id': 2, 'name': '⚔️ Guerreiro Iniciante', 'description': 'Vença 5 batalhas', 'reward': 50},
        {'id': 3, 'name': '💰 Economista', 'description': 'Acumule R$ 50,00', 'reward': 30},
        {'id': 4, 'name': '🏆 Mestre das Missões', 'description': 'Complete 20 missões', 'reward': 100},
        {'id': 5, 'name': '👑 Lendário', 'description': 'Alcance o nível 10', 'reward': 200}
    ]

class Player:
    def __init__(self, nome):
        self.nome = nome
        self.level = 1
        self.xp = 0
        self.xp_need = 100
        self.mesada = 10.00  # Mesada inicial
        self.tasks_completed = 0
        self.battles_won = 0
        self.battles_lost = 0
        self.total_money_earned = 10.00
        self.skills = {
            'forca': 1,
            'defesa': 1,
            'sorte': 1,
            'inteligencia': 1
        }
        self.inventory = []
        self.equipped = {
            'weapon': None,
            'armor': None,
            'accessory': None
        }
        self.achievements_unlocked = []
        self.join_date = datetime.now().isoformat()
    
    def add_xp(self, amount):
        self.xp += amount
        level_ups = 0
        while self.xp >= self.xp_need:
            self.level_up()
            level_ups += 1
        return level_ups
    
    def level_up(self):
        self.level += 1
        self.xp -= self.xp_need
        self.xp_need = int(self.xp_need * 1.5)
        self.mesada += 8.00  # Aumento maior de mesada
        # Melhorar habilidades aleatórias
        skill_to_up = random.choice(list(self.skills.keys()))
        self.skills[skill_to_up] += 1
    
    def complete_task(self, task_name, difficulty):
        xp_reward = difficulty * 25
        money_reward = difficulty * 2.50
        
        self.add_xp(xp_reward)
        self.mesada += money_reward
        self.total_money_earned += money_reward
        self.tasks_completed += 1
        
        # Verificar conquistas
        self.check_achievements()
        
        return {
            'xp': xp_reward,
            'money': money_reward,
            'message': f'✅ Missão "{task_name}" completa! +{xp_reward} XP +R${money_reward:.2f}'
        }
    
    def battle(self, difficulty):
        # Calcular chance de vitória baseada em level, equipamentos e skills
        base_chance = 0.5 + (self.level * 0.05)
        weapon_bonus = self.equipped['weapon']['power'] * 0.02 if self.equipped['weapon'] else 0
        skill_bonus = self.skills['forca'] * 0.03
        
        success_chance = min(0.9, base_chance + weapon_bonus + skill_bonus - (difficulty * 0.1))
        victory = random.random() < success_chance
        
        if victory:
            xp_reward = difficulty * 60
            money_reward = difficulty * 8.00
            self.add_xp(xp_reward)
            self.mesada += money_reward
            self.total_money_earned += money_reward
            self.battles_won += 1
            
            # Chance de drop de item
            item_drop = None
            if random.random() < 0.3:  # 30% de chance de drop
                item_drop = random.choice(shop_items)
                self.inventory.append(item_drop)
            
            self.check_achievements()
            
            return {
                'victory': True,
                'xp': xp_reward,
                'money': money_reward,
                'item_drop': item_drop,
                'message': f'🏆 Vitória épica! +{xp_reward} XP +R${money_reward:.2f}' + 
                          (f' + {item_drop["name"]}' if item_drop else '')
            }
        else:
            self.battles_lost += 1
            return {
                'victory': False,
                'message': '💀 Derrota! Mais sorte na próxima vez!'
            }
    
    def buy_item(self, item_id):
        item = next((i for i in shop_items if i['id'] == item_id), None)
        if item and self.mesada >= item['price']:
            self.mesada -= item['price']
            self.inventory.append(item)
            return True
        return False
    
    def equip_item(self, item_name):
        item = next((i for i in self.inventory if i['name'] == item_name), None)
        if item:
            slot = item['type']
            # Desequipar item atual se houver
            if self.equipped[slot]:
                self.inventory.append(self.equipped[slot])
            self.equipped[slot] = item
            self.inventory.remove(item)
            return True
        return False
    
    def check_achievements(self):
        new_achievements = []
        
        for achievement in achievements:
            if achievement['id'] not in self.achievements_unlocked:
                unlocked = False
                
                if achievement['id'] == 1 and self.tasks_completed >= 1:
                    unlocked = True
                elif achievement['id'] == 2 and self.battles_won >= 5:
                    unlocked = True
                elif achievement['id'] == 3 and self.total_money_earned >= 50:
                    unlocked = True
                elif achievement['id'] == 4 and self.tasks_completed >= 20:
                    unlocked = True
                elif achievement['id'] == 5 and self.level >= 10:
                    unlocked = True
                
                if unlocked:
                    self.achievements_unlocked.append(achievement['id'])
                    self.mesada += achievement['reward']
                    new_achievements.append(achievement)
        
        return new_achievements

# Rotas da API
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_player', methods=['POST'])
def create_player():
    nome = request.json['nome']
    players[nome] = Player(nome)
    return jsonify({'success': True, 'player': players[nome].__dict__})

@app.route('/complete_task', methods=['POST'])
def complete_task():
    data = request.json
    player = players.get(data['nome'])
    if player:
        result = player.complete_task(data['task_name'], data['difficulty'])
        return jsonify({'success': True, 'result': result, 'player': player.__dict__})
    return jsonify({'success': False})

@app.route('/battle', methods=['POST'])
def battle():
    data = request.json
    player = players.get(data['nome'])
    if player:
        result = player.battle(data['difficulty'])
        return jsonify({'success': True, 'result': result, 'player': player.__dict__})
    return jsonify({'success': False})

@app.route('/shop')
def get_shop():
    return jsonify({'items': shop_items})

@app.route('/buy', methods=['POST'])
def buy_item():
    data = request.json
    player = players.get(data['player_name'])
    if player and player.buy_item(data['item_id']):
        return jsonify({'success': True, 'player': player.__dict__})
    return jsonify({'success': False})

@app.route('/equip', methods=['POST'])
def equip_item():
    data = request.json
    player = players.get(data['player_name'])
    if player and player.equip_item(data['item_name']):
        return jsonify({'success': True, 'player': player.__dict__})
    return jsonify({'success': False})

@app.route('/achievements/<player_name>')
def get_achievements(player_name):
    player = players.get(player_name)
    if player:
        player_achs = [a for a in achievements if a['id'] in player.achievements_unlocked]
        available_achs = [a for a in achievements if a['id'] not in player.achievements_unlocked]
        return jsonify({
            'unlocked': player_achs,
            'available': available_achs
        })
    return jsonify({'success': False})

@app.route('/leaderboard')
def get_leaderboard():
    ranked_players = sorted(players.values(), key=lambda p: (p.level, p.xp), reverse=True)
    leaderboard_data = [{
        'name': p.nome,
        'level': p.level,
        'xp': p.xp,
        'mesada': p.mesada,
        'tasks': p.tasks_completed,
        'battles_won': p.battles_won
    } for p in ranked_players[:10]]  # Top 10
    
    return jsonify({'leaderboard': leaderboard_data})

@app.route('/dashboard/<player_name>')
def dashboard(player_name):
    player = players.get(player_name)
    if player:
        return render_template('dashboard.html', player=player)
    return "Jogador não encontrado!"

# Inicializar dados do jogo
init_game_data()

if __name__ == '__main__':
    app.run(debug=True)