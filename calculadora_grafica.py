"""Calculadora gráfica com operações básicas e histórico de cálculos."""

import re
import tkinter as tk
from decimal import Decimal, DecimalException, DivisionByZero
from typing import Optional


COR_FUNDO = "#171923"
COR_PAINEL = "#222633"
COR_DISPLAY = "#10131a"
COR_TEXTO = "#f4f4f5"
COR_SECUNDARIA = "#a7adbb"
COR_BOTAO = "#303747"
COR_BOTAO_OPERADOR = "#414c62"
COR_DESTAQUE = "#5b8def"
COR_ERRO = "#ff7373"


def calcular(primeiro: Decimal, operador: str, segundo: Decimal) -> Decimal:
    """Executa uma operação e deixa erros de entrada explícitos."""
    if not primeiro.is_finite() or not segundo.is_finite():
        raise ValueError("Os valores precisam ser números finitos.")
    if operador == "+":
        resultado = primeiro + segundo
    elif operador == "-":
        resultado = primeiro - segundo
    elif operador == "*":
        resultado = primeiro * segundo
    elif operador == "/":
        if segundo == 0:
            raise DivisionByZero
        resultado = primeiro / segundo
    else:
        raise ValueError("Operação inválida.")
    if not resultado.is_finite():
        raise ValueError("O resultado não é um número finito.")
    return resultado


def formatar_numero(numero: Decimal) -> str:
    """Exibe o resultado sem zeros decimais desnecessários."""
    texto = format(numero, "f")
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return "0" if texto in ("-0", "") else texto


class Calculadora:
    def __init__(self, janela: tk.Tk) -> None:
        self.janela = janela
        self.janela.title("Calculadora")
        self.janela.configure(bg=COR_FUNDO)
        self.janela.resizable(False, False)

        self.valor_atual = "0"
        self.valor_anterior: Optional[Decimal] = None
        self.operador: Optional[str] = None
        self.substituir_atual = False
        self.erro = False
        self.editando_expressao = False
        self.edicao_invalida = False

        self._montar_interface()
        self._atualizar_expressao()
        self.janela.bind("<Key>", self._tecla)

    def _montar_interface(self) -> None:
        conteudo = tk.Frame(self.janela, bg=COR_FUNDO, padx=18, pady=16)
        conteudo.pack()

        tk.Label(
            conteudo,
            text="CALCULADORA",
            font=("Arial", 12, "bold"),
            fg=COR_SECUNDARIA,
            bg=COR_FUNDO,
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.display = tk.StringVar(value=self.valor_atual)
        self.expressao = tk.StringVar()
        self.entrada_expressao = tk.Entry(
            conteudo,
            textvariable=self.expressao,
            bg=COR_DISPLAY,
            fg=COR_SECUNDARIA,
            insertbackground=COR_TEXTO,
            selectbackground=COR_BOTAO_OPERADOR,
            exportselection=False,
            font=("Arial", 12),
            justify="right",
            width=30,
            relief="flat",
            bd=0,
            cursor="xterm",
            highlightthickness=1,
            highlightbackground=COR_BOTAO,
            highlightcolor=COR_DESTAQUE,
        )
        self.entrada_expressao.grid(row=1, column=0, sticky="ew", ipady=6)
        self.entrada_expressao.bind("<FocusIn>", self._iniciar_edicao)
        self.entrada_expressao.bind("<KeyRelease>", self._sincronizar_expressao)

        visor = tk.Entry(
            conteudo,
            textvariable=self.display,
            state="readonly",
            readonlybackground=COR_DISPLAY,
            fg=COR_TEXTO,
            insertbackground=COR_TEXTO,
            font=("Arial", 28, "bold"),
            justify="right",
            width=18,
            relief="flat",
            bd=0,
        )
        visor.grid(row=2, column=0, sticky="ew", ipady=16, pady=(0, 14))

        painel = tk.Frame(conteudo, bg=COR_FUNDO)
        painel.grid(row=3, column=0)

        teclado = tk.Frame(painel, bg=COR_FUNDO)
        teclado.grid(row=0, column=0, sticky="n")

        botoes = [
            ("C", 0, 0, self.limpar, COR_ERRO),
            ("←", 0, 1, self.apagar, COR_BOTAO_OPERADOR),
            ("/", 0, 2, lambda: self.escolher_operador("/"), COR_BOTAO_OPERADOR),
            ("*", 0, 3, lambda: self.escolher_operador("*"), COR_BOTAO_OPERADOR),
            ("7", 1, 0, lambda: self.digito("7"), COR_BOTAO),
            ("8", 1, 1, lambda: self.digito("8"), COR_BOTAO),
            ("9", 1, 2, lambda: self.digito("9"), COR_BOTAO),
            ("-", 1, 3, lambda: self.escolher_operador("-"), COR_BOTAO_OPERADOR),
            ("4", 2, 0, lambda: self.digito("4"), COR_BOTAO),
            ("5", 2, 1, lambda: self.digito("5"), COR_BOTAO),
            ("6", 2, 2, lambda: self.digito("6"), COR_BOTAO),
            ("+", 2, 3, lambda: self.escolher_operador("+"), COR_BOTAO_OPERADOR),
            ("1", 3, 0, lambda: self.digito("1"), COR_BOTAO),
            ("2", 3, 1, lambda: self.digito("2"), COR_BOTAO),
            ("3", 3, 2, lambda: self.digito("3"), COR_BOTAO),
            ("=", 3, 3, self.igual, COR_DESTAQUE),
            ("0", 4, 0, lambda: self.digito("0"), COR_BOTAO),
            (".", 4, 2, self.decimal, COR_BOTAO),
        ]
        for texto, linha, coluna, comando, cor in botoes:
            tk.Button(
                teclado,
                text=texto,
                command=comando,
                font=("Arial", 16, "bold"),
                bg=cor,
                fg=COR_TEXTO,
                activebackground=COR_DESTAQUE,
                activeforeground=COR_TEXTO,
                relief="flat",
                bd=0,
                width=5,
                height=2,
                cursor="hand2",
            ).grid(
                row=linha,
                column=coluna,
                sticky="nsew",
                padx=3,
                pady=3,
                columnspan=2 if texto == "0" else 1,
                rowspan=2 if texto == "=" else 1,
            )

        historico_painel = tk.Frame(painel, bg=COR_PAINEL, padx=10, pady=10)
        historico_painel.grid(row=0, column=1, sticky="ns", padx=(14, 0))
        tk.Label(
            historico_painel,
            text="HISTÓRICO",
            font=("Arial", 10, "bold"),
            fg=COR_SECUNDARIA,
            bg=COR_PAINEL,
        ).pack(anchor="w", pady=(0, 8))

        historico_frame = tk.Frame(historico_painel, bg=COR_PAINEL)
        historico_frame.pack(fill="both", expand=True)
        self.historico = tk.Listbox(
            historico_frame,
            width=22,
            height=14,
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            selectbackground=COR_BOTAO_OPERADOR,
            font=("Arial", 10),
            relief="flat",
            highlightthickness=0,
            activestyle="none",
        )
        self.historico.pack(side="left", fill="both", expand=True)
        rolagem = tk.Scrollbar(historico_frame, command=self.historico.yview)
        rolagem.pack(side="right", fill="y")
        self.historico.configure(yscrollcommand=rolagem.set)

    def _atualizar_display(self) -> None:
        self.display.set(self.valor_atual)
        self._atualizar_expressao()

    def _atualizar_expressao(self) -> None:
        if self.editando_expressao:
            return
        if self.erro or self.operador is None or self.valor_anterior is None:
            self.expressao.set("")
            return
        texto = f"{formatar_numero(self.valor_anterior)} {self.operador}"
        if not self.substituir_atual:
            texto += f" {self.valor_atual}"
        self.expressao.set(texto)

    def _iniciar_edicao(self, _evento: tk.Event) -> None:
        self.editando_expressao = True
        texto = self.expressao.get()
        if texto.endswith("="):
            self.expressao.set(texto[:-1].rstrip())

    def _inserir_expressao(self, texto: str) -> None:
        entrada = self.entrada_expressao
        if entrada.selection_present():
            inicio = entrada.index(tk.SEL_FIRST)
            fim = entrada.index(tk.SEL_LAST)
            entrada.delete(inicio, fim)
            entrada.icursor(inicio)
        else:
            inicio = entrada.index(tk.INSERT)
        entrada.insert(inicio, texto)
        entrada.icursor(inicio + len(texto))
        entrada.selection_clear()
        self.editando_expressao = True
        self._sincronizar_expressao()

    def _sincronizar_expressao(self, _evento: Optional[tk.Event] = None) -> None:
        if not self.editando_expressao:
            return
        texto = self.expressao.get()
        if "," in texto:
            self.expressao.set(texto.replace(",", "."))
        padrao = (
            r"\s*(-?(?:\d+(?:\.\d*)?|\.\d+))"
            r"(?:\s*([+\-*/])(?:\s*(-?(?:\d+(?:\.\d*)?|\.\d+))?)?)?"
            r"\s*(?:=)?\s*"
        )
        correspondencia = re.fullmatch(padrao, self.expressao.get())
        if correspondencia is None:
            self.edicao_invalida = True
            self.display.set("Entrada inválida")
            return

        primeiro, operador, segundo = correspondencia.groups()
        self.erro = False
        self.edicao_invalida = False
        if operador is None:
            self.valor_anterior = None
            self.operador = None
            self.valor_atual = primeiro
            self.substituir_atual = False
        else:
            self.valor_anterior = Decimal(primeiro)
            self.operador = operador
            self.substituir_atual = segundo is None
            self.valor_atual = segundo if segundo is not None else primeiro
        self.display.set(self.valor_atual)

    def _registrar_historico(self, expressao: str) -> None:
        self.historico.insert(0, expressao)

    def _mostrar_erro(self, mensagem: str) -> None:
        self.editando_expressao = False
        self.edicao_invalida = False
        self.valor_atual = mensagem
        self.display.set(mensagem)
        self.erro = True
        self.valor_anterior = None
        self.operador = None
        self.substituir_atual = True
        self._atualizar_expressao()

    def digito(self, numero: str) -> None:
        if self.editando_expressao:
            self._inserir_expressao(numero)
            return
        if self.erro or self.substituir_atual:
            if self.operador is None:
                self.expressao.set("")
            self.valor_atual = numero
            self.erro = False
            self.substituir_atual = False
        elif self.valor_atual == "0":
            self.valor_atual = numero
        else:
            self.valor_atual += numero
        self._atualizar_display()

    def decimal(self) -> None:
        if self.editando_expressao:
            self._inserir_expressao(".")
            return
        if self.erro or self.substituir_atual:
            if self.operador is None:
                self.expressao.set("")
            self.valor_atual = "0."
            self.erro = False
            self.substituir_atual = False
        elif "." not in self.valor_atual:
            self.valor_atual += "."
        self._atualizar_display()

    def escolher_operador(self, operador: str) -> None:
        if self.erro:
            return
        if self.editando_expressao:
            self._inserir_expressao(f" {operador} ")
            return
        try:
            atual = Decimal(self.valor_atual)
            if self.operador is not None and not self.substituir_atual:
                anterior = self.valor_anterior
                if anterior is None:
                    raise ValueError("Entrada inválida.")
                segundo = atual
                atual = calcular(anterior, self.operador, segundo)
                self._registrar_historico(
                    f"{formatar_numero(anterior)} {self.operador} "
                    f"{formatar_numero(segundo)} = {formatar_numero(atual)}"
                )
                self.valor_atual = formatar_numero(atual)
                self._atualizar_display()
            self.valor_anterior = atual
            self.operador = operador
            self.substituir_atual = True
            self._atualizar_expressao()
        except DivisionByZero:
            self._mostrar_erro("Divisão por zero")
        except (DecimalException, ValueError):
            self._mostrar_erro("Entrada inválida")

    def igual(self) -> None:
        if self.editando_expressao:
            self._sincronizar_expressao()
            if self.edicao_invalida:
                self.display.set("Entrada inválida")
                return
        if self.erro or self.operador is None:
            return
        if self.substituir_atual:
            self._mostrar_erro("Entrada inválida")
            return
        try:
            segundo = Decimal(self.valor_atual)
            anterior = self.valor_anterior
            if anterior is None:
                raise ValueError("Entrada inválida.")
            resultado = calcular(anterior, self.operador, segundo)
        except DivisionByZero:
            self._mostrar_erro("Divisão por zero")
            return
        except (DecimalException, ValueError):
            self._mostrar_erro("Entrada inválida")
            return

        expressao = (
            f"{formatar_numero(anterior)} {self.operador} "
            f"{formatar_numero(segundo)} = {formatar_numero(resultado)}"
        )
        texto_expressao = (
            f"{formatar_numero(anterior)} {self.operador} "
            f"{formatar_numero(segundo)} ="
        )
        self._registrar_historico(expressao)
        self.editando_expressao = False
        self.edicao_invalida = False
        self.valor_atual = formatar_numero(resultado)
        self.valor_anterior = None
        self.operador = None
        self.substituir_atual = True
        self._atualizar_display()
        self.expressao.set(texto_expressao)

    def apagar(self) -> None:
        if self.editando_expressao:
            entrada = self.entrada_expressao
            if entrada.selection_present():
                entrada.delete(tk.SEL_FIRST, tk.SEL_LAST)
            else:
                posicao = entrada.index(tk.INSERT)
                if posicao:
                    entrada.delete(posicao - 1)
                    entrada.icursor(posicao - 1)
            self._sincronizar_expressao()
            return
        if self.erro:
            self.valor_atual = "0"
            self.erro = False
        elif not self.substituir_atual:
            self.valor_atual = (
                self.valor_atual[:-1] if len(self.valor_atual) > 1 else "0"
            )
            if self.valor_atual in ("-", ""):
                self.valor_atual = "0"
        self._atualizar_display()

    def limpar(self) -> None:
        self.editando_expressao = False
        self.edicao_invalida = False
        self.valor_atual = "0"
        self.valor_anterior = None
        self.operador = None
        self.substituir_atual = False
        self.erro = False
        self.historico.delete(0, tk.END)
        self._atualizar_display()

    def _tecla(self, evento: tk.Event) -> None:
        if self.janela.focus_get() == self.entrada_expressao:
            if evento.keysym in ("Return", "KP_Enter", "equal") or evento.char == "=":
                self.igual()
                return "break"
            if evento.keysym == "Escape":
                self.limpar()
                return "break"
            return
        tecla = evento.char
        if tecla.isdigit():
            self.digito(tecla)
        elif tecla in "+-*/":
            self.escolher_operador(tecla)
        elif tecla in ".,":
            self.decimal()
        elif evento.keysym in ("Return", "KP_Enter", "equal"):
            self.igual()
        elif evento.keysym == "BackSpace":
            self.apagar()
        elif evento.keysym == "Escape":
            self.limpar()


def main() -> None:
    janela = tk.Tk()
    Calculadora(janela)
    janela.mainloop()


if __name__ == "__main__":
    main()