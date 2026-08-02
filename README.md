# OpenCode Conversation

**Integrace pro hlasové ovládání chytré domácnosti v českém jazyce.**

Konverzační agent pro Home Assistant poháněný serverem [opencode](https://opencode.ai) (`opencode serve`).

Promění kterýkoli model dostupný v opencode v hlasově ovladatelného konverzačního agenta v Home Assistantu.

## Požadavky

Pro hlasového agenta s modelem **Big Pickle** začni instalací OpenCode — Big Pickle je model, který dostaneš právě přes něj.

- Home Assistant 2024.4 nebo novější
- Nainstalovaný a spuštěný add-on **OpenCode** (server `opencode serve`)
- Zakoupený oficiální hlasový satelit Home Assistant (Home Assistant Voice)

### Kde opencode najdeš

Opencode běží jako **add-on uvnitř Home Assistantu** — není to samostatný program na počítači. Najdeš ho v **Nastavení → Doplňky (Add-ons)**.

### Jak opencode nainstalovat do HA

1. Přejdi do **Nastavení → Doplňky → Obchod s doplňky**.
2. Klikni na **⋮ (tři tečky) → Repozitáře** a přidej repozitář: `https://github.com/magnusoverli/opencode`
3. V obchodě vyhledej add-on **OpenCode** a klikni na **Instalovat**.
4. Spusť add-on tlačítkem **Start**.
5. V **Konfiguraci** add-onu povol běh serveru (`enable_server: true`, port `4096`) a restartuj add-on.

Spuštěný add-on vystavuje HTTP API opencode (`/global/health`, `/session`, `/session/{id}/message`), ke kterému se integrace připojuje.

**Důležité:** Pro hlasové použití je nutné mít zakoupený oficiální hlasový satelit Home Assistant (Home Assistant Voice). Na ostatních zařízeních bylo testováno jen omezeně, resp. nebylo testováno vůbec — na Google Home, Alexa a dalších komerčních hlasových asistentech to rozhodně nepojede.

## Instalace

Tuto integraci můžeš nainstalovat, i když už opencode máš — integrace se připojí k tvému stávajícímu opencode serveru. **Pokud opencode nainstalovaný nemáš, integrace bez něj nebude fungovat.**

### HACS

1. Přidej tento repozitář do HACS jako vlastní repozitář (typ: **Integration**).
2. Vyhledej **OpenCode Conversation** a nainstaluj ho.
3. Restartuj Home Assistant.

### Ručně

Zkopíruj složku `custom_components/opencode_conversation/` do svého adresáře `custom_components/` a restartuj Home Assistant.

## Nastavení

1. Přejdi do **Nastavení → Zařízení a služby → Přidat integraci → OpenCode Conversation**.
2. Zadej URL svého opencode serveru — protože add-on běží na stejném zařízení jako Home Assistant, použij adresu svého Home Assistantu s portem `4096` (např. `http://192.168.1.50:4096`).
3. Pole pro uživatelské jméno a heslo nech prázdné. Vyplň je pouze tehdy, pokud jsi svůj opencode server sám chránil heslem.
4. Model nech nastavený na `opencode/big-pickle` (Big Pickle) — to je model, který pro hlasového agenta potřebuješ a který dostaneš právě po instalaci OpenCode. Agenta opencode nech na `build`, systémovou výzvu můžeš upravit.

Po nastavení vyber **OpenCode** jako konverzačního agenta v pipeline Assist (nebo u jednotlivého satelitu), abys s ním mluvil hlasem.

## Důležité poznámky

- **Předplatné Nabu Casa:** Hlasové ovládání (rozpoznávání řeči a čtení odpovědí) běží přes Home Assistant Cloud. Spolehlivě tedy integrace funguje jen s aktivním předplatným Nabu Casa; bez něj je hlasové použití omezené.
- **Model Big Pickle:** Výchozí model `opencode/big-pickle` může být kdykoli zpoplatněn nebo přestat být dostupný. Pokud k tomu dojde, stačí v nastavení integrace změnit model na vlastní.
- **Alternativa ChatGPT:** Jako výkonnější alternativu můžeš použít modely ChatGPT dostupné v opencode (provider `openai`, např. `openai/gpt-4o`). **Pozor:** je to zpoplatněný model a v souvislosti s Home Assistantem je velmi nákladný — při častém hlasovém používání (mnoho krátkých dotazů denně) se náklady rychle nasčítají.
- **Lokální modely (Ollama):** Byl testován lokální model přes Ollama (8B i vyšší) — výsledky byly neuspokojivé.

## Možnosti konfigurace

| Možnost | Popis | Výchozí |
| --- | --- | --- |
| `url` | Základní URL opencode serveru (adresa HA s portem `4096`) | `http://<adresa_HA>:4096` |
| `username` | Uživatelské jméno pro HTTP Basic Auth | `opencode` |
| `password` | Heslo pro HTTP Basic Auth | *(prázdné)* |
| `model` | Použitý model ve tvaru `provider/model-id` | `opencode/big-pickle` |
| `agent` | Spouštěný opencode agent | `build` |
| `system_prompt` | Systémová výzva posílaná s každou zprávou | *(česká)* |

## Vlastní instrukce

Kompletní obsah souboru `AGENTS.local.md`:

```text
# Vlastní instrukce

## Odpovídání
- V běžném textu odpovědí (např. přes satelit) vynechávej lomítka — jak dopředná (/), tak zpětná (\).
```

Soubor `AGENTS.local.md` najdeš v konfiguračním adresáři Home Assistantu, vedle `configuration.yaml` (např. `/config/AGENTS.local.md`). Do něj si můžeš zapsat vlastní trvalé instrukce pro agenta — platí jak pro práci v OpenCode, tak pro hlasové odpovědi přes satelit. Pokud soubor neexistuje, prostě ho vytvoř; instrukce v něm se načítají při startu opencode serve, takže po jakékoli změně je potřeba opencode serve restartovat (nebo začít novou session).

## Licence

MIT

## Poděkování

Poděkování týmu **OpenCode** (anomalyco/opencode) a všem, kteří se podíleli na vývoji a zprovoznění modelu **Big Pickle** a jeho bezplatného zpřístupnění.

