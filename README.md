# Calculadora gráfica

Calculadora de operações básicas com interface gráfica, desenvolvida em Python
com Tkinter.

## Funcionalidades

- Adição, subtração, multiplicação e divisão.
- Uso dos botões da interface ou do teclado.
- Edição da expressão: clique nela para posicionar o cursor, inserir ou
  substituir números.
- Apagar o caractere anterior ao cursor com o botão `←` ou a tecla
  `Backspace`. Se houver um trecho selecionado, ele será apagado.
- Histórico dos cálculos realizados.
- Limpeza da conta e do histórico com o botão `C` ou a tecla `Esc`.
- Exibição de mensagens para operações inválidas, como divisão por zero.

## Requisitos

- Python 3.
- Tkinter, incluído na instalação padrão do Python para Windows.

O projeto não requer a instalação de pacotes externos.

## Como executar

Abra um terminal na pasta do projeto e execute:

```powershell
py -3 calculadora_grafica.py
```

Se o comando `py` não estiver disponível, tente:

```powershell
python calculadora_grafica.py
```

## Como usar

1. Digite os números e escolha uma operação pelos botões ou pelo teclado.
2. Pressione `=` ou `Enter` para calcular.
3. Para corrigir a expressão, clique sobre ela e edite usando o cursor ou
   selecione o trecho que deseja substituir.
4. Use `←` ou `Backspace` para apagar; use `C` ou `Esc` para limpar a
   calculadora.

## Arquivo principal

- `calculadora_grafica.py`: implementação da interface e das operações da
  calculadora.
