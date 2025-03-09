import random
import pyttsx3

class LotoGame:
    def __init__(self):
        self.barrels = list(range(1, 91))
        random.shuffle(self.barrels)
        self.engine = self.init_tts()
        
    def init_tts(self):
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Скорость речи
        
        # Попытка установить русский голос
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'ru' in voice.languages or 'RU' in voice.id:
                engine.setProperty('voice', voice.id)
                break
        return engine
    
    def say(self, text):
        print(text)
        self.engine.say(text)
        self.engine.runAndWait()
    
    def draw_barrel(self):
        if self.barrels:
            return self.barrels.pop()
        else:
            return None

# Пример использования
game = LotoGame()

game.say("Лото: Игра началась!")
game.say("Нажимайте пробел и Enter, чтобы вытащить бочонок...")

while True:
    input()
    barrel = game.draw_barrel()
    
    if barrel is None:
        game.say("Все бочонки закончились!")
        break
    game.say(str(barrel))
    print(f"Выпал бочонок: {barrel}")
    print(f"Осталось: {len(game.barrels)}")

# Освобождение ресурсов синтезатора речи
game.engine.stop()