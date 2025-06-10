import tkinter as tk
import random


WINDOW_WIDTH = 1000  # Širina prozora
WINDOW_HEIGHT = 400  # Visina prozora
GROUND_Y = 300  # Y koordinata tla
DINO_WIDTH = 40  # Širina dinosaura
DINO_HEIGHT = 50  # Visina dinosaura
OBSTACLE_HEIGHT = 40  # Visina prepreke
GRAVITY = 3  # Gravitacija koja utječe na skok
NUM_OBSTACLES = 1  # Broj početnih prepreka
BASE_SPEED = 15  # Brzina prepreka


class DinoGame:
    def __init__(self, master):
        self.master = master  # Glavni prozor igre
        master.title("Dino Game - Tkinter")  # Naziv prozora

        master.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")  # Postavljanje veličine prozora

        # Onemogućavanje promjene veličine prozora
        master.resizable(False, False)

        # Kreiranje platna za igru
        self.canvas = tk.Canvas(master, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="skyblue", highlightthickness=0)
        self.canvas.pack()

        # Kreiranje buttona za skok i restart
        self.jump_button = tk.Button(master, text="Skok", command=self.jump)
        self.jump_button.place(x=WINDOW_WIDTH // 2 - 70, y=WINDOW_HEIGHT - 80)  # Pozicija buttona Skok

        self.restart_button = tk.Button(master, text="Igraj ponovo", command=self.restart_game, state="disabled")
        self.restart_button.place(x=WINDOW_WIDTH // 2 - 70, y=WINDOW_HEIGHT - 40)  # Pozicija buttona Restart

        # Tekst za prikaz rezultata, levela i rekorda
        self.score_text = None
        self.level_text = None
        self.highscore_text = None
        self.game_over_text = None

        self.highscore = 0  # Početni rekord

        # Pokretanje postavki igre
        self.setup_game()
        self.animate()

    def setup_game(self):
        # Brisanje svih objekata sa platna
        self.canvas.delete("all")
        self.score = 0  # Početni rezultat
        self.level = 1  # Početni level
        self.running = True  # Oznaka da igra traje
        self.dino_y = GROUND_Y - DINO_HEIGHT  # Početna Y pozicija dinosaura
        self.is_jumping = False  # Zastavica da li je dinosaur u skoku
        self.jump_velocity = 0  # Početna brzina skoka

        # Crtanje tla
        self.canvas.create_line(0, GROUND_Y, WINDOW_WIDTH, GROUND_Y, fill="gray", width=3)

        # Kreiranje dinosaura
        self.dino = self.canvas.create_rectangle(50, self.dino_y, 50 + DINO_WIDTH, self.dino_y + DINO_HEIGHT,
                                                 fill="black")

        # Kreiranje prepreka
        self.obstacles = []
        for _ in range(NUM_OBSTACLES):
            self.obstacles.append(self.create_obstacle())

        # Ažuriranje prikaza rezultata i levela
        self.update_labels()
        self.jump_button.config(state="normal")  # Omogućavanje dugmeta za skok
        self.restart_button.config(state="disabled")  # Button za restart je isključeno na početku

    def create_obstacle(self):
        # Kreiranje prepreke na slučajnoj poziciji
        x = random.randint(WINDOW_WIDTH, WINDOW_WIDTH + 300)
        width = 20  # Početna širina prepreke
        if self.score >= 20:
            width = random.choice([20, 30, 40])  # Širina prepreke raste s rezultatom

        if self.score >= 30 and random.random() < 0.5:
            # Ako je rezultat dovoljno visok, stvaramo dvije povezane prepreke
            gap = random.randint(10, 20)
            k1 = self.canvas.create_rectangle(x, GROUND_Y - OBSTACLE_HEIGHT,
                                              x + width, GROUND_Y, fill="green")
            k2 = self.canvas.create_rectangle(x + width + gap, GROUND_Y - OBSTACLE_HEIGHT,
                                              x + width * 2 + gap, GROUND_Y, fill="green")
            return [k1, k2]
        else:
            # Jednostavna prepreka
            single = self.canvas.create_rectangle(x, GROUND_Y - OBSTACLE_HEIGHT,
                                                  x + width, GROUND_Y, fill="green")
            return [single]

    def jump(self):
        # Funkcija koja omogućava dinosauru da skoči
        if not self.is_jumping and self.running:
            self.is_jumping = True
            self.jump_velocity = -20  # Početna brzina skoka

    def animate(self):
        # Animacija igre, koja se stalno ponavlja
        if not self.running:
            return

        if self.is_jumping:
            # Ako je dinosaur u skoku, pomičemo ga gore i primjenjujemo gravitaciju
            self.canvas.move(self.dino, 0, self.jump_velocity)
            self.dino_y += self.jump_velocity
            self.jump_velocity += GRAVITY  # Gravitacija povećava brzinu pada
            if self.dino_y >= GROUND_Y - DINO_HEIGHT:
                # Ako je dinosaur sletio, postavljamo ga na tlo
                self.dino_y = GROUND_Y - DINO_HEIGHT
                self.canvas.coords(self.dino, 50, self.dino_y, 50 + DINO_WIDTH, self.dino_y + DINO_HEIGHT)
                self.is_jumping = False

        for i in range(len(self.obstacles)):
            new_obs_list = []
            for obs in self.obstacles[i]:
                # Pomicanje svake prepreke lijevo
                self.canvas.move(obs, -BASE_SPEED, 0)
                coords = self.canvas.coords(obs)

                # Provjera sudara s preprekom
                if self.check_collision(self.canvas.coords(self.dino), coords):
                    self.running = False  # Kraj igre ako je došlo do sudara
                    self.highscore = max(self.highscore, self.score)  # Ažuriranje rekorda
                    self.show_game_over()  # Prikazivanje kraja igre
                    self.jump_button.config(state="disabled")  # Onemogućavanje skakanja
                    self.restart_button.config(state="normal")  # Omogućavanje dugmeta za restart
                    return

                # Ako prepreka nije izašla izvan ekrana, ostaje na ekranu
                if coords[2] >= 0:
                    new_obs_list.append(obs)
                else:
                    self.canvas.delete(obs)  # Ako je prepreka izašla, brišemo je

            if not new_obs_list:
                # Ako više nema prepreka, stvaramo nove
                self.score += 1
                self.obstacles[i] = self.create_obstacle()
                self.update_level()
                self.update_labels()  # Ažuriranje rezultata i levela
            else:
                self.obstacles[i] = new_obs_list

        # Pozivanje animacije svakih 30 milisekundi
        self.master.after(30, self.animate)

    def update_level(self):
        # Ažuriranje levela na temelju rezultata
        new_level = self.score // 10 + 1
        if new_level != self.level:
            self.level = new_level

    def update_labels(self):
        # Ažuriranje svih prikaza rezultata, levela i rekorda
        if self.score_text:
            self.canvas.delete(self.score_text)
        if self.level_text:
            self.canvas.delete(self.level_text)
        if self.highscore_text:
            self.canvas.delete(self.highscore_text)

        # Prikaz rezultata na ekranu
        self.score_text = self.canvas.create_text(WINDOW_WIDTH // 2, 20,
                                                  text=f"Rezultat: {self.score}",
                                                  font=("Arial", 16), fill="black")

        # Prikaz levela na ekranu
        self.level_text = self.canvas.create_text(WINDOW_WIDTH - 100, 20,
                                                  text=f"Level: {self.level}",
                                                  font=("Arial", 16), fill="blue")

        # Prikaz rekorda na ekranu
        self.highscore_text = self.canvas.create_text(WINDOW_WIDTH // 2 + 150, 20,
                                                      text=f"Rekord: {self.highscore}",
                                                      font=("Arial", 16), fill="darkred")

    def show_game_over(self):
        # Prikazivanje teksta "KRAJ IGRE"
        self.update_labels()  # Ažuriranje prikaza rezultata i levela
        self.game_over_text = self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
                                                      text="KRAJ IGRE!",
                                                      font=("Arial", 32, "bold"),
                                                      fill="red")

    def restart_game(self):
        # Funkcija za ponovno pokretanje igre
        self.canvas.delete("all")  # Brisanje svih objekata sa platna
        self.score_text = None
        self.level_text = None
        self.highscore_text = None
        self.game_over_text = None
        self.setup_game()  # Postavljanje igre na početne postavke
        self.animate()  # Pokretanje animacije

    def check_collision(self, dino, obs):
        # Provjera sudara između dinosaura i prepreke
        return not (
            dino[2] < obs[0] or  
            dino[0] > obs[2] or  
            dino[3] < obs[1] or  
            dino[1] > obs[3]     
        )


# Pokretanje igre
root = tk.Tk()  
game = DinoGame(root)  
root.mainloop()  
