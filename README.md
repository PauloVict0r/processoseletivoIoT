# Paulo Victor Santos Souza
## **GitHub:** PauloVict0r

---
  
## 1️⃣ Visão Geral da Solução

O objetivo do projeto é fornecer um sistema inteligente de auxílio de estacionamento simples e barato que possa ser facilmente instalado em vagas residenciais ou comerciais para auxiliar veiculos que não possuam esse tipo de sistema ou servir como dupla camada de auxílio caso já possua. O sistema embarcado utiliza um sensor ultrassônico para monitorar a distância entre o veículo e o fim da vaga, ou um obstáculo, em tempo real. Dependendo da distância medida e da movimentação, o sistema fornece feedback audiovisual dinâmico através de bipes sonoros (Buzzer) e luzes de alerta (NeoPixels RGB), indicando claramente os status de vaga livre, manobra em andamento e totalmente estacionado, para gerênciar melhor os recursos do sistema e deixar margem para futuros incrementos (discutidos ao final do relatório).

---

## 2️⃣ Arquitetura do Sistema Embarcado

A arquitetura do firmware foi desenvolvida em MicroPython com foco em resistência a falhas e operação paralela (não-bloqueante). O fluxo lógico opera da seguinte forma:

1. **Leitura Física:** A cada 100ms, o ESP32 emite e mede o tempo de resposta do sinal ultrassônico usando a função de hardware `time_pulse_us()`.
2. **Filtro Digital:** O dado passa pela classe `MovingAverage`, que aplica um filtro de média móvel nas últimas 5 leituras, removendo ruídos e "falsos positivos".
3. **Máquina de Estados:** O *loop* principal rastreia a distância e o tempo decorrido desde o último movimento para definir 3 estados:
   - **VAGA LIVRE (> 150cm):** Feedback visual verde indicando área limpa.
   - **ESTACIONANDO (0 a 150cm com variação de distância):** Avaliação de proximidade com cores (Amarelo/Vermelho) e PWM no Buzzer (500Hz/1000Hz).
   - **ESTACIONADO (Parado por 5s):** O sistema entende o fim da manobra de estacionamento, apagando as luzes e silenciando alarmes.

Toda a orquestração é feita através de relógios usando (`time.ticks_ms()`), para processamento assíncrono.

---

## 3️⃣ Componentes Utilizados na Simulação

Os componentes mapeados no `diagram.json` foram projetados para alta eficiência:

- **Placa Controller:** `board-esp32-devkit-c-v4` (Aproveita a robustez e conectividade futura).
- **Sensor Ultrassônico (`wokwi-hc-sr04`):** Responsável por medir a distância física do obstáculo (Pinos TRIG 5 e ECHO 18).
- **Fita de LEDs RGB (`wokwi-neopixel-canvas`):** Matriz linear de 3 LEDs WS2812B controlada pelo pino de dados `GPIO 22`. Permite comandar as 3 "lâmpadas" em cores variadas gastando apenas 1 porta do microcontrolador.
- **Buzzer (`wokwi-buzzer`):** Transdutor sonoro no pino 23, operado via modulação por largura de pulso (PWM).

---

## 4️⃣ Decisões Técnicas Relevantes

- **Temporização Não-Bloqueante:** inicialmente utilizei os comandos de `time.sleep()` para testes, mas migrei para deltas de tempo (`time.ticks_diff`), de forma que o sistema consegue processar a lógica do buzzer em alta frequência sem atrasar a taxa de amostragem do sensor ultrassônico, rodando tarefas em "paralelo".
- **Watchdog Timer (WDT):** Implementei um *Watchdog* de 5 segundos. Em caso de *crash* sistêmico no *loop*, o WDT corta a energia lógicamente e reinicia o ESP32 sozinho, um componente vital para um sistema que trabalha com segurança veicular.
- **Substituição por NeoPixel (Economia de Hardware):** Inicialmente projetei o sistema com 3 circuitos de LED paralelos (cada um com seus resistores e fios), mas os substituí por uma arquitetura NeoPixel endereçável para baratear a PCB final, simplificar a fiação do projeto e reduzir pontos de falha elétrica.

---

## 5️⃣ Resultados Obtidos

- O simulador processa sem falhas a mudança de contexto visual e sonora de forma responsiva e agradável de acordo com o slider do HC-SR04.
- **Integração Contínua (CI):** A pipeline configurada no GitHub Actions compila o binário de *filesystem* do MicroPython (`fs.bin`) utilizando a infraestrutura do Docker, sobe no Wokwi remotamente, valida a lógica eletrônica e escuta ativamente pela string de inicialização (`"SMART_PARKING_V2_OK"`). Garantindo a estabilidade do repositório do projeto.

---

## 6️⃣ Comentários Adicionais

- **Limitações:** O campo de visão de um sensor HC-SR04 é cônico e restrito a cerca de 15 graus. Para uma implementação mais robusta seria ideal um sensor mais capaz ou o emprego de múltiplos sensores para garantir maior precisão.
- **Evoluções Futuras:** Como o projeto se baseia em um módulo ESP32, o sistema pode ser realizar conexões via MQTT. O próximo passo seria o envio da informação binária (Ocupado/Livre) em tempo real para uma nuvem (ex: AWS IoT Core), criando um mapa *live* de vagas livres, no caso do emprego do sistema em grandes centros comerciais como shoppings centers ou estacionamentos privados, etc.
- **É um projeto simples e compacto, mas que do meu ponto de vista, possui uma boa utilidade pois pode tanto auxiliar condutores cujos carros que não possuem sistemas desse tipo nativamente, sendo uma opção mais simples e barata, como também fornecer a clientes de shoppings e estacionamentos privados acesso direto a disponibilidade de vagas e auxilia-los no processo de estacionar.
