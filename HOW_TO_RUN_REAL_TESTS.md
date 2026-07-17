# Como Rodar Testes Reais (Glaive of Void)

Este documento foca **apenas** na execução em modelo real + comparação.

## 1. Preparar os prompts (já feito)

Os prompts prontos estão em:
`activation_results/full_experiment_package/`

Cada arquivo `<convo_id>_prompts.md` contém a sequência completa de turns (quiet + loud).

## 2. Executar em modelo real

Para cada convo:

- Pegue o arquivo de prompts.
- Alimente turn por turn no modelo.
- Salve as respostas reais no formato:

```json
[
  {"turn": 1, "model_response": "texto completo da resposta do modelo..."},
  {"turn": 2, "model_response": "..."},
  ...
]
```

Recomendação de nome de arquivo:
`activation_results/meus_resultados/<convo_id>_real.json`

## 3. Comparar com baseline de simulação

Depois de ter seus arquivos `*_real.json`, rode:

```bash
python skills/activation_experiment_stub.py --mode compare \
    --real activation_results/meus_resultados/
```

Ou usando o wrapper:

```bash
python tools/experiment_quickstart.py compare --real activation_results/meus_resultados/
```

Isso vai mostrar, para cada convo:
- sustain_sim vs sustain_real
- advancement por turn (sim vs real)
- tamanho e características das respostas reais

## 4. Usar fatias de alta pureza (opcional, mas recomendado)

Se quiser sinal mais forte de chronic:

```bash
python tools/experiment_quickstart.py prepare \
    --chronic data/quiet_cheese_samples/chronic_dominant/chronic_ultra_pure_95pct.jsonl
```

Ou manualmente:

```bash
python skills/activation_experiment_stub.py --mode prepare \
    --chronic-dominant data/quiet_cheese_samples/chronic_dominant/chronic_pure_90pct.jsonl \
    --num-chronic 8
```

## Dicas práticas

- Grave sempre: nome do modelo, temperatura, system prompt, data.
- Comece com 3-5 convos menores para testar o fluxo.
- Use os `example_real_runs/` como referência de formato.
- Depois compare tudo contra `activation_results/full_sim_reports/`.

## O que já está pronto

- 85 convos completos
- Pacotes de prompts com contexto chronic
- Baseline de simulação para todos
- Ferramentas de comparação
- Fatias de 85%, ~90% e ~95%+ chronic

Falta apenas: você rodar os prompts em modelo(s) e trazer os resultados de volta.

Boa sorte. Quando tiver resultados reais, é só apontar a pasta com --real.
