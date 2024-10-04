import tkinter as tk
from tkinter import messagebox
import mysql.connector
from dashboard import Dashboard  # Certifique-se de que esse módulo exista

class Login:
    def __init__(self, master):
        self.master = master
        master.title("Login")
        master.geometry("400x300")  # Aumenta o tamanho da janela
        master.configure(bg="#f0f0f0")  # Cor de fundo

        # Título
        title_label = tk.Label(master, text="Login", font=("Arial", 24), bg="#f0f0f0")
        title_label.pack(pady=20)

        # Usuário
        tk.Label(master, text="Usuário:", font=("Arial", 14), bg="#f0f0f0").pack()
        self.entry_usuario = tk.Entry(master, font=("Arial", 14), width=30)
        self.entry_usuario.pack(pady=5)

        # Senha
        tk.Label(master, text="Senha:", font=("Arial", 14), bg="#f0f0f0").pack()
        self.entry_senha = tk.Entry(master, font=("Arial", 14), show="*", width=30)
        self.entry_senha.pack(pady=5)

        # Botões
        button_frame = tk.Frame(master, bg="#f0f0f0")
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Login", command=self.login, font=("Arial", 12), bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cadastrar", command=self.cadastro, font=("Arial", 12), bg="#2196F3", fg="white", width=10).pack(side=tk.LEFT, padx=10)

    def conectar_db(self):
        try:
            return mysql.connector.connect(
                host='172.16.78.127',      # Altere para o seu host
                user='sala',           # Altere para o seu usuário do MySQL
                password='admin',      # Altere para a sua senha do MySQL
                database='mysql',   # Altere para o seu banco de dados
                port=3300  
            )
        except mysql.connector.Error as err:
            messagebox.showerror("Erro de Conexão", f"Erro ao conectar ao banco de dados: {err}")
            return None

    def login(self):
        username = self.entry_usuario.get().strip()
        password = self.entry_senha.get().strip()
        
        db = self.conectar_db()
        if db is None:
            return
        
        cursor = db.cursor()
        
        try:
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            resultado = cursor.fetchone()

            if resultado:
                stored_password = resultado[0]
                if password == stored_password:
                    messagebox.showinfo("Login", "Login realizado com sucesso!")
                    self.master.destroy()  # Fecha a tela de login
                    self.abrir_dashboard()  # Abre o dashboard
                else:
                    messagebox.showerror("Erro", "Usuário ou senha inválidos.")
            else:
                messagebox.showerror("Erro", "Usuário não encontrado.")
        finally:
            cursor.close()
            db.close()

    def cadastro(self):
        cadastro_window = tk.Toplevel(self.master)
        cadastro_window.title("Cadastro de Usuário")
        cadastro_window.geometry("400x300")
        cadastro_window.configure(bg="#f0f0f0")

        tk.Label(cadastro_window, text="Cadastro de Usuário", font=("Arial", 24), bg="#f0f0f0").pack(pady=20)

        tk.Label(cadastro_window, text="Usuário:", font=("Arial", 14), bg="#f0f0f0").pack()
        entry_novo_usuario = tk.Entry(cadastro_window, font=("Arial", 14), width=30)
        entry_novo_usuario.pack(pady=5)

        tk.Label(cadastro_window, text="Senha:", font=("Arial", 14), bg="#f0f0f0").pack()
        entry_nova_senha = tk.Entry(cadastro_window, font=("Arial", 14), show="*", width=30)
        entry_nova_senha.pack(pady=5)

        def cadastrar_usuario():
            username = entry_novo_usuario.get().strip()
            password = entry_nova_senha.get().strip()

            db = self.conectar_db()
            if db is None:
                return

            cursor = db.cursor()

            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                db.commit()
                messagebox.showinfo("Cadastro", "Usuário cadastrado com sucesso!")
                cadastro_window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao cadastrar: {err}")
            finally:
                cursor.close()
                db.close()

        tk.Button(cadastro_window, text="Cadastrar", command=cadastrar_usuario, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=20)

    def abrir_dashboard(self):
        dashboard_root = tk.Tk()
        Dashboard(dashboard_root)  # Inicializa o dashboard
        dashboard_root.mainloop()
