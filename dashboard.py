import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
from datetime import datetime

class Dashboard:
    def __init__(self, master):
        self.master = master
        self.master.title("Controle Financeiro")
        self.master.geometry("800x600")

        # Initial data setup
        self.dados = []
        self.orcamento_inicial = 0.0
        self.tipos = ["Receita", "Despesa"]

        # Input frame setup
        self.frame_inputs = tk.Frame(master)
        self.frame_inputs.pack(padx=10, pady=10, fill=tk.X)
        self.setup_input_fields()

        # Table frame setup
        self.frame_table = tk.Frame(master)
        self.frame_table.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.setup_table()

        # Balance label
        self.label_saldo = tk.Label(master, text=f"Saldo Atual: {self.orcamento_inicial:.2f}")
        self.label_saldo.pack(padx=10, pady=10, anchor=tk.W)

        # Load categories and existing data
        self.carregar_categorias()
        self.carregar_dados()
        self.calcular_orcamento()

    def setup_input_fields(self):
        """Sets up the input fields for the dashboard."""
        # Configure grid layout
        for col in range(6):
            self.frame_inputs.grid_columnconfigure(col, weight=1)
        for row in range(2):
            self.frame_inputs.grid_rowconfigure(row, weight=1)

        # Create input widgets
        self.label_data = tk.Label(self.frame_inputs, text="Data (DD/MM/AAAA):")
        self.label_data.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_data = tk.Entry(self.frame_inputs, width=15)
        self.entry_data.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.label_categoria = tk.Label(self.frame_inputs, text="Categoria:")
        self.label_categoria.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.combobox_categoria = ttk.Combobox(self.frame_inputs, state="readonly", width=15)
        self.combobox_categoria.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        self.label_descricao = tk.Label(self.frame_inputs, text="Descrição:")
        self.label_descricao.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.entry_descricao = tk.Entry(self.frame_inputs, width=15)
        self.entry_descricao.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        self.label_tipo = tk.Label(self.frame_inputs, text="Tipo:")
        self.label_tipo.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.combobox_tipo = ttk.Combobox(self.frame_inputs, values=self.tipos, state="readonly", width=15)
        self.combobox_tipo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        self.label_valor = tk.Label(self.frame_inputs, text="Valor:")
        self.label_valor.grid(row=2, column=4, padx=5, pady=5, sticky=tk.W)
        self.entry_valor = tk.Entry(self.frame_inputs, width=15)
        self.entry_valor.grid(row=2, column=5, padx=5, pady=5, sticky=tk.W)

      
        self.botao_adicionar = tk.Button(self.frame_inputs, text="Adicionar Entrada", command=self.adicionar_entrada)
        self.botao_adicionar.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)

        self.botao_editar = tk.Button(self.frame_inputs, text="Editar Selecionado", command=self.editar_entrada)
        self.botao_editar.grid(row=3, column=3, padx=5, pady=5, sticky=tk.W)

        self.botao_apagar = tk.Button(self.frame_inputs, text="Apagar Selecionado", command=self.apagar_entrada)
        self.botao_apagar.grid(row=3, column=4, padx=5, pady=5, sticky=tk.W)

    def setup_table(self):
        """Sets up the data display table."""
        self.tree = ttk.Treeview(self.frame_table, columns=("Data", "Categoria", "Descrição", "Valor", "Tipo"), show='headings', selectmode='browse')
        self.tree.heading("Data", text="Data")
        self.tree.heading("Categoria", text="Categoria")
        self.tree.heading("Descrição", text="Descrição")
        self.tree.heading("Valor", text="Valor")
        self.tree.heading("Tipo", text="Tipo")

        # Configure column properties
        self.tree.column("Data", width=100, anchor=tk.W)
        self.tree.column("Categoria", width=150, anchor=tk.W)
        self.tree.column("Descrição", width=200, anchor=tk.W)
        self.tree.column("Valor", width=100, anchor=tk.E)
        self.tree.column("Tipo", width=100, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def criar_conexao(self):
        """Creates a connection to the MySQL database."""
        try:
            conexao = mysql.connector.connect(
                host='172.16.78.127',
                user='sala',
                password='admin',
                database='db_sgp',
                port=3300
            )
            if conexao.is_connected():
                return conexao
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao conectar ao MySQL: {e}")
            return None

    def carregar_categorias(self):
        """Loads categories from the database into the combobox."""
        conexao = self.criar_conexao()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT nome FROM categorias")
            categorias = cursor.fetchall()
            self.combobox_categoria['values'] = [categoria[0] for categoria in categorias]
            cursor.close()
            conexao.close()

    def carregar_dados(self):
        """Loads existing entries from the database into the treeview."""
        conexao = self.criar_conexao()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT data, categoria, descricao, valor, tipo FROM entradas")
            entradas = cursor.fetchall()
            for entrada in entradas:
                data, categoria, descricao, valor, tipo = entrada
                valor = float(valor)  # Ensure value is float
                self.dados.append({
                    "Data": data,
                    "Categoria": categoria,
                    "Descrição": descricao,
                    "Valor": valor,
                    "Tipo": tipo
                })
                self.tree.insert("", tk.END, values=(data, categoria, descricao, valor, tipo))
            cursor.close()
            conexao.close()

    def validar_data(self, data):
        """Validates the date format."""
        try:
            data_formatada = datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
            return data_formatada
        except ValueError:
            messagebox.showerror("Erro", "Data deve estar no formato DD/MM/AAAA!")
            return None

    def adicionar_entrada(self):
        """Adds a new entry to the database and updates the display."""
        data = self.entry_data.get()
        categoria = self.combobox_categoria.get()
        descricao = self.entry_descricao.get()
        valor = self.entry_valor.get()
        tipo = self.combobox_tipo.get()

        if not all([data, categoria, descricao, valor, tipo]):
            messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos!")
            return

        data_formatada = self.validar_data(data)
        if not data_formatada:
            return

        try:
            valor = float(valor)
        except ValueError:
            messagebox.showerror("Erro", "Valor deve ser um número!")
            return

        if tipo not in self.tipos:
            messagebox.showerror("Erro", "Tipo deve ser 'Receita' ou 'Despesa'!")
            return

        # Insert data into the database
        self.inserir_dado(data_formatada, categoria, descricao, valor, tipo)

        # Update local data and UI
        self.dados.append({
            "Data": data_formatada,
            "Categoria": categoria,
            "Descrição": descricao,
            "Valor": valor,
            "Tipo": tipo
        })
        self.tree.insert("", tk.END, values=(data_formatada, categoria, descricao, valor, tipo))
        self.limpar_campos()
        self.calcular_orcamento()

    def editar_entrada(self):
        """Loads selected entry into input fields for editing."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Nenhuma entrada selecionada!")
            return

        item_id = selected_item[0]
        item_values = self.tree.item(item_id, "values")

        # Populate fields with selected item values
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, item_values[0])
        self.combobox_categoria.set(item_values[1])
        self.entry_descricao.delete(0, tk.END)
        self.entry_descricao.insert(0, item_values[2])
        self.entry_valor.delete(0, tk.END)
        self.entry_valor.insert(0, item_values[3])
        self.combobox_tipo.set(item_values[4])

        # Change button to save changes
        self.botao_adicionar.config(text="Salvar Alterações", command=lambda: self.salvar_alteracoes(item_id))

    def salvar_alteracoes(self, item_id):
        """Saves changes made to the selected entry."""
        data = self.entry_data.get()
        categoria = self.combobox_categoria.get()
        descricao = self.entry_descricao.get()
        valor = self.entry_valor.get()
        tipo = self.combobox_tipo.get()

        if not all([data, categoria, descricao, valor, tipo]):
            messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos!")
            return

        data_formatada = self.validar_data(data)
        if not data_formatada:
            return

        try:
            valor = float(valor)
        except ValueError:
            messagebox.showerror("Erro", "Valor deve ser um número!")
            return

        # Update entry in the database
        self.atualizar_dado(item_id, data_formatada, categoria, descricao, valor, tipo)

        # Update the treeview item
        self.tree.item(item_id, values=(data_formatada, categoria, descricao, valor, tipo))
        self.limpar_campos()
        self.botao_adicionar.config(text="Adicionar Entrada", command=self.adicionar_entrada)
        self.calcular_orcamento()

    def apagar_entrada(self):
        """Deletes the selected entry from the database and updates the display."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Nenhuma entrada selecionada!")
            return

        item_id = selected_item[0]
        item_values = self.tree.item(item_id, "values")

        # Remove item from the database
        self.apagar_dado(item_values[0], item_values[1], item_values[2], float(item_values[3]), item_values[4])

        # Remove item from local data and treeview
        self.dados = [item for item in self.dados if not (item["Data"] == item_values[0] and item["Categoria"] == item_values[1] and item["Descrição"] == item_values[2] and item["Valor"] == float(item_values[3]) and item["Tipo"] == item_values[4])]
        self.tree.delete(item_id)

        self.calcular_orcamento()

    def calcular_orcamento(self):
        """Calculates and updates the current balance."""
        receitas_totais = sum(item["Valor"] for item in self.dados if item["Tipo"] == "Receita")
        despesas_totais = sum(item["Valor"] for item in self.dados if item["Tipo"] == "Despesa")
        saldo_atual = self.orcamento_inicial + receitas_totais - despesas_totais

        self.label_saldo.config(text=f"Saldo Atual: {saldo_atual:.2f}")

    def limpar_campos(self):
        """Clears all input fields."""
        self.entry_data.delete(0, tk.END)
        self.combobox_categoria.set('')
        self.entry_descricao.delete(0, tk.END)
        self.entry_valor.delete(0, tk.END)
        self.combobox_tipo.set('')

    def inserir_dado(self, data, categoria, descricao, valor, tipo):
        """Inserts a new entry into the database."""
        conexao = self.criar_conexao()
        if conexao:
            cursor = conexao.cursor()
            query = """
                INSERT INTO entradas (data, categoria, descricao, valor, tipo)
                VALUES (%s, %s, %s, %s, %s)
            """
            valores = (data, categoria, descricao, valor, tipo)
            try:
                cursor.execute(query, valores)
                conexao.commit()
                messagebox.showinfo("Sucesso", "Entrada adicionada com sucesso!")
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao inserir dados: {e}")
            finally:
                cursor.close()
                conexao.close()

    def atualizar_dado(self, item_id, data, categoria, descricao, valor, tipo):
        """Updates an existing entry in the database."""
        conexao = self.criar_conexao()
        if conexao:
            cursor = conexao.cursor()
            query = """
                UPDATE entradas
                SET data = %s, categoria = %s, descricao = %s, valor = %s, tipo = %s
                WHERE data = %s AND categoria = %s AND descricao = %s AND valor = %s AND tipo = %s
            """
            valores = (data, categoria, descricao, valor, tipo, 
                       self.tree.item(item_id, "values")[0], 
                       self.tree.item(item_id, "values")[1], 
                       self.tree.item(item_id, "values")[2], 
                       self.tree.item(item_id, "values")[3], 
                       self.tree.item(item_id, "values")[4])
            try:
                cursor.execute(query, valores)
                conexao.commit()
                messagebox.showinfo("Sucesso", "Entrada atualizada com sucesso!")
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao atualizar dados: {e}")
            finally:
                cursor.close()
                conexao.close()

    def apagar_dado(self, data, categoria, descricao, valor, tipo):
        """Deletes an entry from the database."""
        conexao = self.criar_conexao()
        if conexao:
            cursor = conexao.cursor()
            query = """
                DELETE FROM entradas
                WHERE data = %s AND categoria = %s AND descricao = %s AND valor = %s AND tipo = %s
            """
            valores = (data, categoria, descricao, valor, tipo)
            try:
                cursor.execute(query, valores)
                conexao.commit()
                messagebox.showinfo("Sucesso", "Entrada apagada com sucesso!")
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao apagar dados: {e}")
            finally:
                cursor.close()
                conexao.close()
