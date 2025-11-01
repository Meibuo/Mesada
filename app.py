from flask import Flask, render_template, request, jsonify
import random
from datetime import datetime
import pg8000
import os
import json

app = Flask(__name__)
app.secret_key = '30591bbfa70ae38582897d226608fd99'

# Configuração do PostgreSQL com pg8000
def get_db_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://mesada_db_user:rJFcZevYmO079FkW9ndlqV4gtLNvdbx9@dpg-d438j52li9vc73cng1ug-a/mesada_db')
    
    try:
        # Parse da URL de conexão
        url_parts = DATABASE_URL.replace('postgresql://', '').split('@')
        user_pass = url_parts[0].split(':')
        host_db = url_parts[1].split('/')
        host_port = host_db[0].split(':')
        
        conn = pg8000.connect(
            user=user_pass[0],
            password=user_pass[1],
            host=host_port[0],
            port=int(host_port[1]) if len(host_port) > 1 else 5432,
            database=host_db[1]
        )
        return conn
    except Exception as e:
        print(f"❌ Erro na conexão com o banco: {e}")
        raise e

# Inicializar banco de dados
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        print("✅ Conectado ao banco. Criando tabela players...")
        
        # Verificar se a tabela já existe
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'players'
            );
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("📦 Criando tabela players...")
            # Tabela de jogadores
            cur.execute('''
                CREATE TABLE players (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) UNIQUE NOT NULL,
                    level INTEGER DEFAULT 1,
                    xp INTEGER DEFAULT 0,
                    xp_need INTEGER DEFAULT 100,
                    mesada DECIMAL(10,2) DEFAULT 10.00,
                    tasks_completed INTEGER DEFAULT 0,
                    battles_won INTEGER DEFAULT 0,
                    battles_lost INTEGER DEFAULT 0,
                    total_money_earned DECIMAL(10,2) DEFAULT 10.00,
                    skills TEXT DEFAULT '{"forca": 1, "defesa": 1, "sorte": 1, "inteligencia": 1}',
                    inventory TEXT DEFAULT '[]',
                    equipped TEXT DEFAULT '{"weapon": null, "armor": null, "accessory": null}',
                    achievements_unlocked TEXT DEFAULT '[]',
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✅ Tabela players criada com sucesso!")
        else:
            print("✅ Tabela players já existe.")
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        # Não levanta exceção para não quebrar o app

# Dados do jogo
shop_items = []
achievements = []

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
    def __init__(self, data):
        self.id = data[0]
        self.nome = data[1]
        self.level = data[2] or 1
        self.xp = data[3] or 0
        self.xp_need = data[4] or 100
        self.mesada = float(data[5] or 10.00)
        self.tasks_completed = data[6] or 0
        self.battles_won = data[7] or 0
        self.battles_lost = data[8] or 0
        self.total_money_earned = float(data[9] or 10.00)
        
        # Parse JSON fields
        self.skills = json.loads(data[10]) if data[10] else {"forca": 1, "defesa": 1, "sorte": 1, "inteligencia": 1}
        self.inventory = json.loads(data[11]) if data[11] else []
        self.equipped = json.loads(data[12]) if data[12] else {"weapon": None, "armor": None, "accessory": None}
        self.achievements_unlocked = json.loads(data[13]) if data[13] else []
        self.join_date = data[14]
    
    def save(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE players SET 
                    level = %s, xp = %s, xp_need = %s, mesada = %s, 
                    tasks_completed = %s, battles_won = %s, battles_lost = %s,
                    total_money_earned = %s, skills = %s, inventory = %s,
                    equipped = %s, achievements_unlocked = %s
                WHERE id = %s
            ''', (
                self.level, self.xp, self.xp_need, self.mesada,
                self.tasks_completed, self.battles_won, self.battles_lost,
                self.total_money_earned, json.dumps(self.skills), 
                json.dumps(self.inventory), json.dumps(self.equipped),
                json.dumps(self.achievements_unlocked), self.id
            ))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar jogador: {e}")
            return False
    
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
        self.mesada += 8.00
        # Melhorar habilidades aleatórias
        skill_to_up = random.choice(list(self.skills.keys()))
        self.skills[skill_to_up] += 1
    
    def complete_task(self, task_name, difficulty):
        xp_reward = difficulty * 25
        money_reward = difficulty * 2.50
        
        level_ups = self.add_xp(xp_reward)
        self.mesada += money_reward
        self.total_money_earned += money_reward
        self.tasks_completed += 1
        
        # Verificar conquistas
        new_achievements = self.check_achievements()
        
        success = self.save()
        
        if not success:
            return {
                'error': 'Erro ao salvar progresso'
            }
        
        return {
            'xp': xp_reward,
            'money': money_reward,
            'level_ups': level_ups,
            'new_achievements': new_achievements,
            'message': f'✅ Missão "{task_name}" completa! +{xp_reward} XP +R${money_reward:.2f}'
        }
    
    def battle(self, difficulty):
        # Calcular chance de vitória
        base_chance = 0.5 + (self.level * 0.05)
        weapon_bonus = self.equipped['weapon']['power'] * 0.02 if self.equipped['weapon'] else 0
        skill_bonus = self.skills['forca'] * 0.03
        
        success_chance = min(0.9, base_chance + weapon_bonus + skill_bonus - (difficulty * 0.1))
        victory = random.random() < success_chance
        
        if victory:
            xp_reward = difficulty * 60
            money_reward = difficulty * 8.00
            level_ups = self.add_xp(xp_reward)
            self.mesada += money_reward
            self.total_money_earned += money_reward
            self.battles_won += 1
            
            # Chance de drop de item
            item_drop = None
            if random.random() < 0.3:
                item_drop = random.choice(shop_items)
                self.inventory.append(item_drop)
            
            new_achievements = self.check_achievements()
            success = self.save()
            
            if not success:
                return {
                    'error': 'Erro ao salvar progresso'
                }
            
            return {
                'victory': True,
                'xp': xp_reward,
                'money': money_reward,
                'level_ups': level_ups,
                'item_drop': item_drop,
                'new_achievements': new_achievements,
                'message': f'🏆 Vitória épica! +{xp_reward} XP +R${money_reward:.2f}' + 
                          (f' + {item_drop["name"]}' if item_drop else '')
            }
        else:
            self.battles_lost += 1
            success = self.save()
            
            if not success:
                return {
                    'error': 'Erro ao salvar progresso'
                }
            
            return {
                'victory': False,
                'message': '💀 Derrota! Mais sorte na próxima vez!'
            }
    
    def buy_item(self, item_id):
        item = next((i for i in shop_items if i['id'] == item_id), None)
        if item and self.mesada >= item['price']:
            self.mesada -= item['price']
            self.inventory.append(item)
            return self.save()
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
            return self.save()
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
        
        if new_achievements:
            self.save()
        
        return new_achievements

# Inicializar app
@app.before_first_request
def initialize():
    print("🚀 Inicializando aplicação...")
    init_db()
    init_game_data()
    print("✅ Aplicação inicializada!")

# Rotas da API
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_player', methods=['POST'])
def create_player():
    try:
        nome = request.json['nome']
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar se jogador já existe
        cur.execute('SELECT * FROM players WHERE nome = %s', (nome,))
        existing_player = cur.fetchone()
        
        if existing_player:
            cur.close()
            conn.close()
            return jsonify({'success': True, 'player': Player(existing_player).__dict__})
        
        # Criar novo jogador
        cur.execute('''
            INSERT INTO players (nome) VALUES (%s) RETURNING *
        ''', (nome,))
        
        new_player = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        player_obj = Player(new_player)
        return jsonify({'success': True, 'player': player_obj.__dict__})
        
    except Exception as e:
        print(f"❌ Erro ao criar jogador: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_player/<player_name>')
def get_player(player_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM players WHERE nome = %s', (player_name,))
        player_data = cur.fetchone()
        cur.close()
        conn.close()
        
        if player_data:
            player_obj = Player(player_data)
            return jsonify({'success': True, 'player': player_obj.__dict__})
        else:
            return jsonify({'success': False, 'error': 'Jogador não encontrado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/complete_task', methods=['POST'])
def complete_task():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM players WHERE nome = %s', (data['nome'],))
        player_data = cur.fetchone()
        
        if player_data:
            player = Player(player_data)
            result = player.complete_task(data['task_name'], data['difficulty'])
            return jsonify({'success': True, 'result': result, 'player': player.__dict__})
        return jsonify({'success': False, 'error': 'Jogador não encontrado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/battle', methods=['POST'])
def battle():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM players WHERE nome = %s', (data['nome'],))
        player_data = cur.fetchone()
        
        if player_data:
            player = Player(player_data)
            result = player.battle(data['difficulty'])
            return jsonify({'success': True, 'result': result, 'player': player.__dict__})
        return jsonify({'success': False, 'error': 'Jogador não encontrado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/shop')
def get_shop():
    return jsonify({'items': shop_items})

@app.route('/buy', methods=['POST'])
def buy_item():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM players WHERE nome = %s', (data['player_name'],))
        player_data = cur.fetchone()
        
        if player_data:
            player = Player(player_data)
            if player.buy_item(data['item_id']):
                return jsonify({'success': True, 'player': player.__dict__})
            else:
                return jsonify({'success': False, 'error': 'Mesada insuficiente ou item não encontrado'})
        return jsonify({'success': False, 'error': 'Jogador não encontrado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/equip', methods=['POST'])
def equip_item():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM players WHERE nome = %s', (data['player_name'],))
        player_data = cur.fetchone()
        
        if player_data:
            player = Player(player_data)
            if player.equip_item(data['item_name']):
                return jsonify({'success': True, 'player': player.__dict__})
            else:
                return jsonify({'success': False, 'error': 'Item não encontrado no inventário'})
        return jsonify({'success': False, 'error': 'Jogador não encontrado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/achievements/<player_name>')
def get_achievements(player_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM players WHERE nome = %s', (player_name,))
        player_data = cur.fetchone()
        
        if player_data:
            player = Player(player_data)
            player_achs = [a for a in achievements if a['id'] in player.achievements_unlocked]
            available_achs = [a for a in achievements if a['id'] not in player.achievements_unlocked]
            return jsonify({
                'success': True,
                'unlocked': player_achs,
                'available': available_achs
            })
        return jsonify({'success': False, 'error': 'Jogador não encontrado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/leaderboard')
def get_leaderboard():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT nome, level, xp, mesada, tasks_completed, battles_won FROM players ORDER BY level DESC, xp DESC LIMIT 10')
        players_data = cur.fetchall()
        cur.close()
        conn.close()
        
        leaderboard_data = [{
            'name': p[0],
            'level': p[1],
            'xp': p[2],
            'mesada': float(p[3]),
            'tasks': p[4],
            'battles_won': p[5]
        } for p in players_data]
        
        return jsonify({'success': True, 'leaderboard': leaderboard_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/dashboard/<player_name>')
def dashboard(player_name):
    return render_template('dashboard.html')

# Health check para Render
@app.route('/health')
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM players')
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy', 
            'message': 'App está funcionando!',
            'players_count': count,
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'database': 'disconnected'
        }), 500

# Rota para debug - criar tabela manualmente se necessário
@app.route('/debug/create_table')
def debug_create_table():
    try:
        init_db()
        return jsonify({'success': True, 'message': 'Tabela criada/verificada com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Inicializar banco na startup
    init_db()
    init_game_data()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)