import discord
from discord.ext import commands
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Canale dei log unificato per registrare tutti i comandi eseguiti
CANALE_COMANDI_LOGS_ID = 1548706968347218061

# Ruoli per avviare/gestire il turno (comando /shift)
RUOLI_TURNO = [1545769249908465714, 1547328150201966622]

# Ruoli specifici per gestire/modificare le ore e per licenziare
RUOLI_GESTIONE = [1547327746865111060, 1545769096392605749]

# Ruoli autorizzati per inserire e rimuovere soggetti dalla lista dei ricercati
RUOLI_RICERCATO = [1545769096392605749, 1547328150201966622]

# Ruolo specifico per il comando /mandato
RUOLO_MANDATO = 1547327746865111060

# Ruolo specifico per il comando /mandato-list e /mandato-modifica
RUOLO_MANDATO_LIST = 1547328150201966622

# Ruolo specifico per il comando /mandato-modifica
RUOLO_MANDATO_MODIFICA = 1547327746865111060

# Ruoli autorizzati per inviare l'annuncio ufficiale
RUOLI_ANNUNCIO = [1545769096392605749, 1547328150201966622, 1547327746865111060]

# Ruoli autorizzati per i comandi matricola
RUOLO_MATRICOLA_PDS = 1547328167126110288
RUOLO_MATRICOLA_CC = 1547328155646431282
RUOLO_MATRICOLA_ESER = 1547328163409821826
RUOLO_MATRICOLA_GDF = 1547328159484219593
RUOLO_MATRICOLA_IMPORTANTE = 1547328170523623568

# Ruoli autorizzati per il comando /pulisci
RUOLI_PULISCI = [1547327743627370547, 1545769096392605749]

# Lista dei ruoli consentiti da poter richiedere tramite il comando /richiesta-ruolo
RUOLI_RICHIESTA_VALIDI = [
    1547328170523623568,
    1547328167126110288,
    1547328163409821826,
    1547328159484219593,
    1547328155646431282
]

# ID del canale dei log dove inviare le richieste
CANALE_LOGS_ID = 1548659930943459338

# Canale specifico in cui inviare il pannello di verifica
CANALE_VERIFICA_ID = 1547925995397587075

# Ruoli autorizzati ad accettare o rifiutare le richieste nel canale log
RUOLI_ACCETTAZIONE = [1547327746865111060, 1545769096392605749]

# Ruoli autorizzati per visualizzare/gestire le liste delle matricole
RUOLI_VISUALIZZA_MATRICOLE = [
    1547327746865111060,
    1545769096392605749,
    1547328150201966622,
    1547328167126110288,
    1547328155646431282,
    1547328163409821826,
    1547328159484219593,
    1547328170523623568
]

# Ruolo di verifica ufficiale
RUOLO_VERIFICA = 1547328349469413516

# Ruoli autorizzati per i comandi di allerta
RUOLI_ALLERTA = [1547327746865111060, 1545769249908465714]

# Dizionari e liste per memorizzare i dati in memoria
db_turni = {}
db_ricercati = []
db_mandati = []
db_matricole_pds = []
db_matricole_cc = []
db_matricole_eser = []
db_matricole_gdf = []
db_matricole_importante = []

# Stato di allerta predefinito (normale)
ALLERTA_DEFAULT = {
    "livello": "Verde",
    "titolo": "Situazione Normale",
    "descrizione": "Nessuna criticità rilevante sul territorio.",
    "colore": discord.Color.green(),
    "autore": "Sistema"
}

db_allerta_attuale = ALLERTA_DEFAULT.copy()

def check_ruoli_turno(interaction: discord.Interaction):
    return any(role.id in RUOLI_TURNO for role in interaction.user.roles)

def check_ruoli_gestione(interaction: discord.Interaction):
    return any(role.id in RUOLI_GESTIONE for role in interaction.user.roles)

def check_ruoli_ricercato(interaction: discord.Interaction):
    return any(role.id in RUOLI_RICERCATO for role in interaction.user.roles)

def check_ruolo_mandato(interaction: discord.Interaction):
    return any(role.id == RUOLO_MANDATO for role in interaction.user.roles)

def check_ruolo_mandato_list(interaction: discord.Interaction):
    return any(role.id == RUOLO_MANDATO_LIST for role in interaction.user.roles)

def check_ruolo_mandato_modifica(interaction: discord.Interaction):
    return any(role.id == RUOLO_MANDATO_MODIFICA for role in interaction.user.roles)

def check_ruoli_annuncio(interaction: discord.Interaction):
    return any(role.id in RUOLI_ANNUNCIO for role in interaction.user.roles)

def check_ruoli_accettazione(interaction: discord.Interaction):
    return any(role.id in RUOLI_ACCETTAZIONE for role in interaction.user.roles)

def check_ruoli_visualizza_matricole(interaction: discord.Interaction):
    return any(role.id in RUOLI_VISUALIZZA_MATRICOLE for role in interaction.user.roles)

def check_ruoli_allerta(interaction: discord.Interaction):
    return any(role.id in RUOLI_ALLERTA for role in interaction.user.roles)

async def registra_log_comando(interaction: discord.Interaction, dettagli: str):
    try:
        canale = interaction.guild.get_channel(CANALE_COMANDI_LOGS_ID)
        if canale:
            embed = discord.Embed(
                title=f"📊 Log Comando: /{interaction.command.name if interaction.command else 'sconosciuto'}",
                description=f"**Utente:** {interaction.user.mention} (`{interaction.user}`)\n**Dettagli:** {dettagli}",
                color=discord.Color.dark_grey(),
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await canale.send(embed=embed)
    except Exception as e:
        print(f"Errore durante l'invio del log comando: {e}")

class ShiftView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not check_ruoli_turno(interaction):
            await interaction.response.send_message("Non hai i permessi per utilizzare questi pulsanti.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Attiva", style=discord.ButtonStyle.green, custom_id="shift_attiva")
    async def attiva(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        ora_attuale = datetime.now()
        
        if uid not in db_turni:
            db_turni[uid] = {"stato": "attivo", "inizio": ora_attuale, "secondi_totali": 0}
        else:
            db_turni[uid]["stato"] = "attivo"
            db_turni[uid]["inizio"] = ora_attuale

        embed = discord.Embed(
            title="🟢 Servizio Attivato",
            description=f"L'operatore {interaction.user.mention} è ora **In Servizio**.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await registra_log_comando(interaction, "Ha attivato il turno di servizio tramite pulsante.")

    @discord.ui.button(label="Pausa", style=discord.ButtonStyle.blurple, custom_id="shift_pausa")
    async def pausa(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        ora_attuale = datetime.now()

        if uid in db_turni and db_turni[uid]["stato"] == "attivo":
            durata = (ora_attuale - db_turni[uid]["inizio"]).total_seconds()
            db_turni[uid]["secondi_totali"] += durata
            db_turni[uid]["stato"] = "pausa"

        embed = discord.Embed(
            title="🟡 Servizio in Pausa",
            description=f"L'operatore {interaction.user.mention} è andato in **Pausa**.",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await registra_log_comando(interaction, "Ha messo in pausa il turno di servizio tramite pulsante.")

    @discord.ui.button(label="Disattiva", style=discord.ButtonStyle.red, custom_id="shift_disattiva")
    async def disattiva(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        ora_attuale = datetime.now()

        if uid in db_turni and db_turni[uid]["stato"] == "attivo":
            durata = (ora_attuale - db_turni[uid]["inizio"]).total_seconds()
            db_turni[uid]["secondi_totali"] += durata

        if uid in db_turni:
            db_turni[uid]["stato"] = "disattivato"

        embed = discord.Embed(
            title="🔴 Servizio Disattivato",
            description=f"L'operatore {interaction.user.mention} ha terminato il servizio.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await registra_log_comando(interaction, "Ha disattivato il turno di servizio tramite pulsante.")

class RichiestaRuoloView(discord.ui.View):
    def __init__(self, utente_id: int, ruolo_id: int):
        super().__init__(timeout=None)
        self.utente_id = utente_id
        self.ruolo_id = ruolo_id

    @discord.ui.button(label="Accetta", style=discord.ButtonStyle.green, custom_id="richiesta_accetta")
    async def accetta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not check_ruoli_accettazione(interaction):
            await interaction.response.send_message("Non possiedi i ruoli necessari per accettare questa richiesta.", ephemeral=True)
            return

        guild = interaction.guild
        member = guild.get_member(self.utente_id)
        if not member:
            try:
                member = await guild.fetch_member(self.utente_id)
            except discord.NotFound:
                await interaction.response.send_message("L'utente che ha fatto la richiesta non si trova più nel server.", ephemeral=True)
                return

        role = guild.get_role(self.ruolo_id)
        if not role:
            await interaction.response.send_message("Il ruolo richiesto non esiste più.", ephemeral=True)
            return

        try:
            await member.add_roles(role)
        except discord.Forbidden:
            await interaction.response.send_message("Il bot non ha i permessi per assegnare questo ruolo.", ephemeral=True)
            return

        for child in self.children:
            child.disabled = True

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.add_field(name="Stato", value=f"✅ Accettato da {interaction.user.mention}", inline=False)

        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message(f"Hai accettato la richiesta e assegnato il ruolo a {member.mention}.", ephemeral=True)
        await registra_log_comando(interaction, f"Ha accettato la richiesta di ruolo per <@{self.utente_id}> (Ruolo ID: {self.ruolo_id}).")

    @discord.ui.button(label="Rifiuta", style=discord.ButtonStyle.red, custom_id="richiesta_rifiuta")
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not check_ruoli_accettazione(interaction):
            await interaction.response.send_message("Non possiedi i ruoli necessari per rifiutare questa richiesta.", ephemeral=True)
            return

        guild = interaction.guild
        member = guild.get_member(self.utente_id)
        if not member:
            try:
                member = await guild.fetch_member(self.utente_id)
            except discord.NotFound:
                member = None

        role = guild.get_role(self.ruolo_id)

        for child in self.children:
            child.disabled = True

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.add_field(name="Stato", value=f"❌ Rifiutato da {interaction.user.mention}", inline=False)

        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message("Hai rifiutato la richiesta.", ephemeral=True)
        await registra_log_comando(interaction, f"Ha rifiutato la richiesta di ruolo per <@{self.utente_id}> (Ruolo ID: {self.ruolo_id}).")

        if member and role:
            try:
                await member.send(f"La tua richiesta per il ruolo **{role.name}** è stata **rifiutata**.")
            except discord.Forbidden:
                pass

class VerificaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verificati", style=discord.ButtonStyle.green, custom_id="bottone_verifica_ufficiale")
    async def verifica_pulsante(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(RUOLO_VERIFICA)
        
        if not role:
            await interaction.response.send_message("Errore: Il ruolo di verifica non esiste o è stato eliminato.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.response.send_message("Sei già stato verificato in precedenza!", ephemeral=True)
            return

        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Verifica completata con successo! Ti è stato assegnato il ruolo.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Il bot non ha i permessi necessari per assegnarti questo ruolo.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("Si è verificato un errore imprevisto durante l'assegnazione del ruolo.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Bot online come {bot.user}")

@bot.tree.command(name="shift", description="Gestisci il tuo stato di servizio")
async def shift(interaction: discord.Interaction):
    if not check_ruoli_turno(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per usare questo comando.", ephemeral=True)
        return

    embed = discord.Embed(
        title="📋 Gestione Turno Forze dell'Ordine",
        description="Seleziona un'opzione per aggiornare il tuo stato di servizio:",
        color=discord.Color.dark_blue()
    )
    
    view = ShiftView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    await registra_log_comando(interaction, "Ha aperto il pannello di gestione del turno personale.")

@bot.tree.command(name="shift_utente", description="Visualizza le ore di servizio effettuate da un utente")
async def shift_utente(interaction: discord.Interaction, utente: discord.Member = None):
    target = utente or interaction.user
    uid = target.id

    secondi_totali = 0
    if uid in db_turni:
        secondi_totali = db_turni[uid]["secondi_totali"]
        if db_turni[uid]["stato"] == "attivo":
            secondi_totali += (datetime.now() - db_turni[uid]["inizio"]).total_seconds()

    ore = int(secondi_totali // 3600)
    minuti = int((secondi_totali % 3600) // 60)

    embed = discord.Embed(
        title=f"⏱️ Ore di Servizio - {target.display_name}",
        description=f"L'utente {target.mention} ha accumulato:\n\n**{ore} ore** e **{minuti} minuti** di servizio.",
        color=discord.Color.teal()
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)
    await registra_log_comando(interaction, f"Ha visualizzato le ore di servizio di {target.mention} ({ore}h {minuti}m).")

@bot.tree.command(name="shift_gestisci", description="Aggiungi o rimuovi ore/minuti di servizio a un utente")
async def shift_gestisci(interaction: discord.Interaction, azione: str, utente: discord.Member, ore: int = 0, minuti: int = 0):
    if not check_ruoli_gestione(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per utilizzare questo comando di gestione.", ephemeral=True)
        return

    azione = azione.lower()
    if azione not in ["aggiungi", "rimuovi"]:
        await interaction.response.send_message("Azione non valida. Usa 'aggiungi' oppure 'rimuovi' nel parametro azione.", ephemeral=True)
        return

    uid = utente.id
    if uid not in db_turni:
        db_turni[uid] = {"stato": "disattivato", "inizio": datetime.now(), "secondi_totali": 0}

    secondi_da_variare = (ore * 3600) + (minuti * 60)

    if azione == "aggiungi":
        db_turni[uid]["secondi_totali"] += secondi_da_variare
        testo_azione = "aggiunto a"
        colore = discord.Color.green()
    else:
        db_turni[uid]["secondi_totali"] = max(0, db_turni[uid]["secondi_totali"] - secondi_da_variare)
        testo_azione = "rimosso da"
        colore = discord.Color.red()

    totale_sec = db_turni[uid]["secondi_totali"]
    if db_turni[uid]["stato"] == "attivo":
        totale_sec += (datetime.now() - db_turni[uid]["inizio"]).total_seconds()

    h_tot = int(totale_sec // 3600)
    m_tot = int((totale_sec % 3600) // 60)

    embed = discord.Embed(
        title="⚙️ Ore di Servizio Aggiornate",
        description=f"Sono stati **{testo_azione}** {utente.mention} **{ore}h {minuti}m**.\n\nNuovo totale: **{h_tot} ore** e **{m_tot} minuti**.",
        color=colore
    )
    await interaction.response.send_message(embed=embed)
    await registra_log_comando(interaction, f"Ha modificato le ore di {utente.mention} ({azione} {ore}h {minuti}m). Totale: {h_tot}h {m_tot}m.")

@bot.tree.command(name="licenziamento", description="Licenzia un utente rimuovendogli il ruolo delle forze dell'ordine")
async def licenziamento(interaction: discord.Interaction, utente: discord.Member, ruolo: discord.Role, motivo: str):
    if not check_ruoli_gestione(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per utilizzare questo comando di licenziamento.", ephemeral=True)
        return

    if ruolo not in utente.roles:
        await interaction.response.send_message(f"L'utente {utente.mention} non possiede il ruolo {ruolo.mention}.", ephemeral=True)
        return

    try:
        await utente.remove_roles(ruolo)
    except discord.Forbidden:
        await interaction.response.send_message("Errore: Il bot non ha i permessi necessari per rimuovere questo ruolo.", ephemeral=True)
        return
    except discord.HTTPException:
        await interaction.response.send_message("Si è verificato un errore imprevisto durante la rimozione del ruolo.", ephemeral=True)
        return

    if utente.id in db_turni:
        db_turni[utente.id] = {"stato": "disattivato", "inizio": datetime.now(), "secondi_totali": 0}

    embed = discord.Embed(
        title="📢 NOTIFICA DI LICENZIAMENTO",
        description=f"L'operatore {utente.mention} è stato sollevato dall'incarico.",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="Ruolo Rimosso", value=ruolo.mention, inline=False)
    embed.add_field(name="Motivazione", value=motivo, inline=False)
    embed.set_footer(text=f"Provvedimento eseguito da {interaction.user.display_name}")
    embed.set_thumbnail(url=utente.display_avatar.url)

    await interaction.response.send_message(embed=embed)
    await registra_log_comando(interaction, f"Ha licenziato {utente.mention} rimuovendo il ruolo {ruolo.name}. Motivazione: {motivo}")

@bot.tree.command(name="ricercato", description="Inserisci un soggetto nella lista dei ricercati")
async def ricercato(
    interaction: discord.Interaction, 
    nome_cognome: str, 
    nick_roblox: str, 
    motivo: str, 
    foto_allegata: discord.Attachment
):
    if not check_ruoli_ricercato(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per inserire un soggetto nella lista dei ricercati.", ephemeral=True)
        return

    dati_ricercato = {
        "nome": nome_cognome,
        "roblox": nick_roblox,
        "motivo": motivo,
        "foto": foto_allegata.url,
        "autore": interaction.user.display_name
    }
    db_ricercati.append(dati_ricercato)

    embed = discord.Embed(
        title="🚨 MANDATO DI CATTURA / RICERCATO",
        description="Un nuovo soggetto è stato ufficialmente inserito nella lista dei ricercati.",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="Nome e Cognome", value=nome_cognome, inline=True)
    embed.add_field(name="Nick Roblox", value=nick_roblox, inline=True)
    embed.add_field(name="Motivo del Mandato", value=motivo, inline=False)
    embed.set_image(url=foto_allegata.url)
    embed.set_footer(text=f"Inserito da {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    await registra_log_comando(interaction, f"Ha inserito il ricercato: {nome_cognome} (Roblox: {nick_roblox}). Motivo: {motivo}")

@bot.tree.command(name="ricercato-lista", description="Visualizza la lista di tutti i soggetti ricercati")
async def ricercato_lista(interaction: discord.Interaction):
    if not db_ricercati:
        embed = discord.Embed(
            title="📋 Lista Ricercati",
            description="Al momento non c'è alcun soggetto inserito nella lista dei ricercati.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await registra_log_comando(interaction, "Ha visualizzato la lista dei ricercati (risultata vuota).")
        return

    await interaction.response.send_message("📋 **Elenco ufficiale dei soggetti ricercati:**", ephemeral=False)
    
    for r in db_ricercati:
        embed = discord.Embed(
            title=f"🚨 Ricercato: {r['nome']}",
            color=discord.Color.dark_red()
        )
        embed.add_field(name="Nick Roblox", value=r['roblox'], inline=True)
        embed.add_field(name="Segnalato da", value=r['autore'], inline=True)
        embed.add_field(name="Motivo", value=r['motivo'], inline=False)
        embed.set_image(url=r['foto'])
        
        await interaction.channel.send(embed=embed)
    
    await registra_log_comando(interaction, f"Ha visualizzato la lista dei ricercati ({len(db_ricercati)} soggetti).")

@bot.tree.command(name="ricercato-rimuovi", description="Rimuovi un soggetto dalla lista dei ricercati")
async def ricercato_rimuovi(interaction: discord.Interaction, nick_roblox: str, motivo: str):
    if not check_ruoli_ricercato(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per rimuovere un soggetto dalla lista dei ricercati.", ephemeral=True)
        return

    trovato = None
    for r in db_ricercati:
        if r['roblox'].lower() == nick_roblox.lower():
            trovato = r
            break

    if not trovato:
        await interaction.response.send_message(f"Nessun ricercato trovato con il Nick Roblox: **{nick_roblox}**.", ephemeral=True)
        return

    db_ricercati.remove(trovato)

    embed = discord.Embed(
        title="✅ SOGGETTO RIMOSSO DAI RICERCATI",
        description=f"Il mandato per **{trovato['nome']}** (Roblox: `{trovato['roblox']}`) è stato chiuso.",
        color=discord.Color.green()
    )
    embed.add_field(name="Motivo della rimozione", value=motivo, inline=False)
    embed.set_footer(text=f"Rimosso da {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    await registra_log_comando(interaction, f"Ha rimosso il ricercato Roblox: {nick_roblox}. Motivazione: {motivo}")

@bot.tree.command(name="mandato", description="Emetti un mandato ufficiale")
async def mandato(
    interaction: discord.Interaction, 
    nome: str, 
    cognome: str, 
    tipo_di_mandato: str, 
    motivo: str, 
    foto_allegate: discord.Attachment
):
    if not check_ruolo_mandato(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per utilizzare questo comando.", ephemeral=True)
        return

    nome_cognome_completo = f"{nome} {cognome}"
    dati_mandato = {
        "nome": nome,
        "cognome": cognome,
        "nome_completo": nome_cognome_completo,
        "tipo": tipo_di_mandato,
        "motivo": motivo,
        "foto": foto_allegate.url,
        "autore": interaction.user.display_name
    }
    db_mandati.append(dati_mandato)

    embed = discord.Embed(
        title="📜 NUOVO MANDATO EMESSO",
        description=f"È stato registrato un nuovo mandato per **{nome_cognome_completo}**.",
        color=discord.Color.dark_orange()
    )
    embed.add_field(name="Nome e Cognome", value=nome_cognome_completo, inline=True)
    embed.add_field(name="Tipo di Mandato", value=tipo_di_mandato, inline=True)
    embed.add_field(name="Motivo", value=motivo, inline=False)
    embed.set_image(url=foto_allegate.url)
    embed.set_footer(text=f"Emesso da {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    await registra_log_comando(interaction, f"Ha emesso un mandato ({tipo_di_mandato}) per {nome_cognome_completo}. Motivo: {motivo}")

@bot.tree.command(name="mandato-list", description="Visualizza l'elenco dei mandati emessi")
async def mandato_list(interaction: discord.Interaction):
    if not check_ruolo_mandato_list(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per visualizzare la lista dei mandati.", ephemeral=True)
        return

    if not db_mandati:
        embed = discord.Embed(
            title="📋 Lista Mandati",
            description="Al momento non ci sono mandati registrati.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await registra_log_comando(interaction, "Ha visualizzato la lista dei mandati (risultata vuota).")
        return

    await interaction.response.send_message("📋 **Elenco ufficiale dei mandati attivi:**", ephemeral=False)
    
    for m in db_mandati:
        embed = discord.Embed(
            title=f"📜 Mandato: {m['nome_completo']}",
            color=discord.Color.dark_orange()
        )
        embed.add_field(name="Nome", value=m['nome'], inline=True)
        embed.add_field(name="Cognome", value=m['cognome'], inline=True)
        embed.add_field(name="Tipo di Mandato", value=m['tipo'], inline=True)
        embed.add_field(name="Emesso da", value=m['autore'], inline=True)
        embed.add_field(name="Motivo", value=m['motivo'], inline=False)
        embed.set_image(url=m['foto'])
        
        await interaction.channel.send(embed=embed)

    await registra_log_comando(interaction, f"Ha visualizzato la lista dei mandati ({len(db_mandati)} mandati attivi).")

@bot.tree.command(name="mandato-modifica", description="Modifica o rimuovi un mandato esistente")
async def mandato_modifica(
    interaction: discord.Interaction, 
    azione: str, 
    nome_cognome: str, 
    tipo_di_mandato: str = None, 
    motivo: str = None
):
    if not check_ruolo_mandato_modifica(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per eseguire questa modifica.", ephemeral=True)
        return

    azione = azione.lower().strip()
    if azione not in ["rimuovi", "modifica"]:
        await interaction.response.send_message("Azione non valida. Usa 'rimuovi' oppure 'modifica'.", ephemeral=True)
        return

    trovato = None
    for m in db_mandati:
        if m['nome_completo'].lower() == nome_cognome.lower() or f"{m['nome']} {m['cognome']}".lower() == nome_cognome.lower():
            trovato = m
            break

    if not trovato:
        for r in db_ricercati:
            if r['nome'].lower() == nome_cognome.lower():
                if azione == "rimuovi":
                    db_ricercati.remove(r)
                    embed = discord.Embed(
                        title="✅ SOGGETTO RIMOSSO",
                        description=f"Il soggetto **{r['nome']}** è stato rimosso dalla lista dei ricercati.",
                        color=discord.Color.green()
                    )
                    embed.set_footer(text=f"Modificato da {interaction.user.display_name}")
                    await interaction.response.send_message(embed=embed)
                    await registra_log_comando(interaction, f"Ha rimosso il ricercato {r['nome']} tramite mandato-modifica.")
                    return
                else:
                    if tipo_di_mandato:
                        r['motivo'] = f"[{tipo_di_mandato}] {motivo}" if motivo else r['motivo']
                    elif motivo:
                        r['motivo'] = motivo
                    
                    embed = discord.Embed(
                        title="✏️ MANDATO AGGIORNATO",
                        description=f"Il mandato per **{r['nome']}** è stato modificato con successo.",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="Nuovo Motivo / Dettagli", value=r['motivo'], inline=False)
                    embed.set_footer(text=f"Modificato da {interaction.user.display_name}")
                    await interaction.response.send_message(embed=embed)
                    await registra_log_comando(interaction, f"Ha modificato il ricercato {r['nome']} tramite mandato-modifica.")
                    return

        await interaction.response.send_message(f"Nessun mandato o ricercato trovato con il nome: **{nome_cognome}**.", ephemeral=True)
        return

    if azione == "rimuovi":
        db_mandati.remove(trovato)
        embed = discord.Embed(
            title="🗑️ MANDATO RIMOSSO",
            description=f"Il mandato per **{trovato['nome_completo']}** è stato eliminato con successo.",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Rimosso da {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)
        await registra_log_comando(interaction, f"Ha eliminato il mandato per {trovato['nome_completo']}.")

    elif azione == "modifica":
        if tipo_di_mandato:
            trovato['tipo'] = tipo_di_mandato
        if motivo:
            trovato['motivo'] = motivo

        embed = discord.Embed(
            title="✏️ MANDATO MODIFICATO",
            description=f"Il mandato per **{trovato['nome_completo']}** è stato aggiornato.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Tipo di Mandato", value=trovato['tipo'], inline=True)
        embed.add_field(name="Motivo", value=trovato['motivo'], inline=False)
        if trovato.get('foto'):
            embed.set_image(url=trovato['foto'])
        embed.set_footer(text=f"Modificato da {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        await registra_log_comando(interaction, f"Ha modificato il mandato per {trovato['nome_completo']}.")

@bot.tree.command(name="allerta-modifica", description="Modifica lo stato di allerta dello Stato")
async def allerta_modifica(
    interaction: discord.Interaction, 
    livello: str, 
    titolo: str, 
    descrizione: str
):
    if not check_ruoli_allerta(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per modificare lo stato di allerta dello Stato.", ephemeral=True)
        return

    livello_clean = livello.capitalize().strip()
    mappatura_colori = {
        "Verde": discord.Color.green(),
        "Rosso": discord.Color.red(),
        "Viola": discord.Color.purple(),
        "Nera": discord.Color.dark_embed()
    }

    if livello_clean not in mappatura_colori:
        await interaction.response.send_message("Livello di allerta non valido. Scegli tra: `Verde`, `Rosso`, `Viola`, `Nera`.", ephemeral=True)
        return

    db_allerta_attuale["livello"] = livello_clean
    db_allerta_attuale["titolo"] = titolo
    db_allerta_attuale["descrizione"] = descrizione
    db_allerta_attuale["colore"] = mappatura_colori[livello_clean]
    db_allerta_attuale["autore"] = interaction.user.display_name

    embed = discord.Embed(
        title=f"🚨 STATO DI ALLERTA AGGIORNATO: {livello_clean.upper()}",
        description=f"**{titolo}**\n\n{descrizione}",
        color=mappatura_colori[livello_clean],
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"Aggiornato da {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    await registra_log_comando(interaction, f"Ha modificato lo stato di allerta dello Stato in: {livello_clean} ({titolo}).")

@bot.tree.command(name="allerta-configura", description="Elimina/ripristina lo stato di allerta attuale riportandolo a verde normale")
async def allerta_configura(interaction: discord.Interaction):
    if not check_ruoli_allerta(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per configurare o eliminare lo stato di allerta dello Stato.", ephemeral=True)
        return

    global db_allerta_attuale
    db_allerta_attuale = ALLERTA_DEFAULT.copy()
    db_allerta_attuale["autore"] = interaction.user.display_name

    embed = discord.Embed(
        title="🛡️ STATO DI ALLERTA RIPRISTINATO",
        description="L'allerta attuale è stata eliminata/configurata ed è tornata allo stato predefinito (**Verde**).",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"Ripristinato da {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    await registra_log_comando(interaction, "Ha eliminato l'allerta attuale ripristinando quella predefinita.")

@bot.tree.command(name="allerta-modifica-elenco", description="Visualizza una panoramica rapida dei livelli di allerta disponibili nello Stato")
async def allerta_modifica_elenco(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📋 Elenco Livelli di Allerta Statali",
        description="I livelli di allerta configurabili nel sistema di sicurezza sono i seguenti:",
        color=discord.Color.dark_blue()
    )
    embed.add_field(name="🟢 Allerta Verde", value="Situazione di normalità e controllo ordinario.", inline=False)
    embed.add_field(name="🔴 Allerta Rosso", value="Situazione di pericolo elevato o emergenza in corso.", inline=False)
    embed.add_field(name="🟣 Allerta Viola", value="Situazione di massima criticità o crisi straordinaria.", inline=False)
    embed.add_field(name="⬛ Allerta Nera", value="Stato di emergenza totale, coprifuoco o blocco operativo.", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    await registra_log_comando(interaction, "Ha visualizzato l'elenco dei livelli di allerta.")

@bot.tree.command(name="allerta", description="Visualizza lo stato di allerta attuale dello Stato")
async def allerta(interaction: discord.Interaction):
    embed = discord.Embed(
        title=f"🛡️ STATO DI ALLERTA ATTUALE: {db_allerta_attuale['livello'].upper()}",
        description=f"**{db_allerta_attuale['titolo']}**\n\n{db_allerta_attuale['descrizione']}",
        color=db_allerta_attuale['colore'],
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"Ultimo aggiornamento da: {db_allerta_attuale['autore']}")

    await interaction.response.send_message(embed=embed)
    await registra_log_comando(interaction, f"Ha consultato lo stato di allerta corrente (Attuale: {db_allerta_attuale['livello']}).")

@bot.tree.command(name="pulisci", description="Elimina un determinato numero di messaggi dal canale")
async def pulisci(interaction: discord.Interaction, quantita: int):
    if not any(role.id in RUOLI_PULISCI for role in interaction.user.roles):
        await interaction.response.send_message("Non possiedi i ruoli necessari per utilizzare questo comando.", ephemeral=True)
        return

    if quantita <= 0:
        await interaction.response.send_message("Inserisci una quantità maggiore di 0.", ephemeral=True)
        return

    try:
        await interaction.response.send_message(f"Eliminazione di {quantita} messaggi in corso...", ephemeral=True)
        cancellati = await interaction.channel.purge(limit=quantita)
        await registra_log_comando(interaction, f"Ha pulito il canale eliminando {len(cancellati)} messaggi.")
    except discord.Forbidden:
        await interaction.followup.send("Il bot non ha i permessi necessari per eliminare i messaggi in questo canale.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"Si è verificato un errore durante l'eliminazione: {e}", ephemeral=True)

@bot.tree.command(name="verifica", description="Invia il pannello per la verifica e l'assegnazione del ruolo")
async def verifica(interaction: discord.Interaction):
    if not check_ruoli_gestione(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per inviare questo pannello di verifica.", ephemeral=True)
        return

    canale = interaction.guild.get_channel(CANALE_VERIFICA_ID)
    if not canale:
        await interaction.response.send_message("Errore: Impossibile trovare il canale di verifica configurato.", ephemeral=True)
        return

    embed = discord.Embed(
        title="🔒 Sistema di Verifica",
        description="Clicca sul pulsante sottostante per completare la verifica e ottenere accesso al server.",
        color=discord.Color.blue()
    )
    
    view = VerificaView()
    await canale.send(embed=embed, view=view)
    await interaction.response.send_message(f"Pannello di verifica inviato con successo nel canale {canale.mention}!", ephemeral=True)
    await registra_log_comando(interaction, f"Ha inviato il pannello di verifica nel canale {canale.name}.")

@bot.tree.command(name="annuncio", description="Crea un annuncio ufficiale per le Forze dell'Ordine")
async def annuncio(interaction: discord.Interaction, titolo: str, descrizione: str):
    if not check_ruoli_annuncio(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per inviare questo annuncio.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"📢 {titolo}",
        description=descrizione,
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Annuncio ufficiale emesso da {interaction.user.display_name}")
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("Annuncio inviato con successo!", ephemeral=True)
    await registra_log_comando(interaction, f"Ha pubblicato l'annuncio ufficiale: '{titolo}'.")

@bot.tree.command(name="richiesta-ruolo", description="Invia una richiesta per ottenere un ruolo specifico")
async def richiesta_ruolo(interaction: discord.Interaction, ruolo: discord.Role, motivo: str, allega_foto: discord.Attachment):
    if ruolo.id not in RUOLI_RICHIESTA_VALIDI:
        await interaction.response.send_message("Non puoi richiedere questo ruolo. Scegli uno dei ruoli autorizzati.", ephemeral=True)
        return

    canale_logs = interaction.guild.get_channel(CANALE_LOGS_ID)
    if not canale_logs:
        await interaction.response.send_message("Errore: Canale dei log non trovato. Contatta gli amministratori.", ephemeral=True)
        return

    embed = discord.Embed(
        title="📝 Nuova Richiesta Ruolo",
        description=f"L'utente {interaction.user.mention} ha inviato una richiesta di promozione/assegnazione.",
        color=discord.Color.orange()
    )
    embed.add_field(name="Ruolo Richiesto", value=ruolo.mention, inline=False)
    embed.add_field(name="Motivo", value=motivo, inline=False)
    embed.set_image(url=allega_foto.url)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(text=f"ID Utente: {interaction.user.id}")

    view = RichiestaRuoloView(interaction.user.id, ruolo.id)
    await canale_logs.send(embed=embed, view=view)

    await interaction.response.send_message("La tua richiesta è stata inviata con successo al comando competente!", ephemeral=True)
    await registra_log_comando(interaction, f"Ha inoltrato una richiesta per il ruolo {ruolo.name}. Motivazione: {motivo}")

@bot.tree.command(name="matricola-pds", description="Registra la matricola PDS di un operatore")
async def matricola_pds(interaction: discord.Interaction, nome_cognome: str, matricola: str):
    if not check_ruoli_visualizza_matricole(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per utilizzare questo comando.", ephemeral=True)
        return

    dati_matricola = {
        "nome": nome_cognome,
        "matricola": matricola,
        "autore": interaction.user.display_name
    }
    db_matricole_pds.append(dati_matricola)

    embed = discord.Embed(
        title="🪪 REGISTRAZIONE MATRICOLA PDS",
        description="È stata registrata una nuova matricola ufficiale PDS.",
        color=discord.Color.blue()
    )
    embed.add_field(name="Nome e Cognome", value=nome_cognome, inline=True)
    embed.add_field(name="Matricola", value=matricola, inline=True)
    embed.set_footer(text=f"Registrato da {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    await registra_log_comando(interaction, f"Ha registrato la matricola PDS di {nome_cognome} (Matricola: {matricola}).")

@bot.tree.command(name="matricola-cc", description="Registra la matricola CC di un operatore")
async def matricola_cc(interaction: discord.Interaction, nome_cognome: str, matricola: str):
    if not check_ruoli_visualizza_matricole(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per utilizzare questo comando.", ephemeral=True)
        return

    dati_matricola = {
        "nome": nome_cognome,
        "matricola": matricola,
        "autore": interaction.user.display_name
    }
    db_matricole_cc.append(dati_matricola)

    embed = discord.Embed(
        title="🪪 REGISTRAZIONE MATRICOLA CC",
        description="È stata registrata una nuova matricola ufficiale CC.",
        color=discord.Color.dark_blue()
    )
    embed.add_field(name="Nome e Cognome", value=nome_cognome, inline=True)
    embed.add_field(name="Matricola", value=matricola, inline=True)
    embed.set_footer(text=f"Registrato da {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    await registra_log_comando(interaction, f"Ha registrato la matricola CC di {nome_cognome} (Matricola: {matricola}).")

@bot.tree.command(name="matricola-eser", description="Registra la matricola Esercito di un operatore")
async def matricola_eser(interaction: discord.Interaction, nome_cognome: str, matricola: str):
    if not check_ruoli_visualizza_matricole(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per utilizzare questo comando.", ephemeral=True)
        return

    dati_matricola = {
        "nome": nome_cognome,
        "matricola": matricola,
        "autore": interaction.user.display_name
    }
    db_matricole_eser.append(dati_matricola)

    embed = discord.Embed(
        title="🪪 REGISTRAZIONE MATRICOLA ESERCITO",
        description="È stata registrata una nuova matricola ufficiale dell'Esercito.",
        color=discord.Color.green()
    )
    embed.add_field(name="Nome e Cognome", value=nome_cognome, inline=True)
    embed.add_field(name="Matricola", value=matricola, inline=True)
    embed.set_footer(text=f"Registrato da {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    await registra_log_comando(interaction, f"Ha registrato la matricola Esercito di {nome_cognome} (Matricola: {matricola}).")

@bot.tree.command(name="matricola-gdf", description="Registra la matricola Guardia di Finanza di un operatore")
async def matricola_gdf(interaction: discord.Interaction, nome_cognome: str, matricola: str):
    if not check_ruoli_visualizza_matricole(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per utilizzare questo comando.", ephemeral=True)
        return

    dati_matricola = {
        "nome": nome_cognome,
        "matricola": matricola,
        "autore": interaction.user.display_name
    }
    db_matricole_gdf.append(dati_matricola)

    embed = discord.Embed(
        title="🪪 REGISTRAZIONE MATRICOLA GUARDIA DI FINANZA",
        description="È stata registrata una nuova matricola ufficiale della Guardia di Finanza.",
        color=discord.Color.gold()
    )
    embed.add_field(name="Nome e Cognome", value=nome_cognome, inline=True)
    embed.add_field(name="Matricola", value=matricola, inline=True)
    embed.set_footer(text=f"Registrato da {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    await registra_log_comando(interaction, f"Ha registrato la matricola GDF di {nome_cognome} (Matricola: {matricola}).")

@bot.tree.command(name="matricola-aggiungi", description="Aggiungi una matricola specificando nome-cognome, matricola e corpo")
async def matricola_aggiungi(interaction: discord.Interaction, nome_cognome: str, matricola: str, corpo: str):
    if not check_ruoli_visualizza_matricole(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per utilizzare questo comando.", ephemeral=True)
        return

    corpo = corpo.lower().strip()
    
    mappatura = {
        "pds": ("Polizia di Stato (PDS)", db_matricole_pds, discord.Color.blue()),
        "cc": ("Carabinieri (CC)", db_matricole_cc, discord.Color.dark_blue()),
        "esercito": ("Esercito", db_matricole_eser, discord.Color.green()),
        "gdf": ("Guardia di Finanza (GDF)", db_matricole_gdf, discord.Color.gold()),
        "importante": ("Ruolo Importante", db_matricole_importante, discord.Color.purple())
    }

    if corpo not in mappatura:
        await interaction.response.send_message("Corpo non valido. Scegli tra: `pds`, `cc`, `esercito`, `gdf`, `importante`.", ephemeral=True)
        return

    nome_corpo, lista_db, colore = mappatura[corpo]

    dati_matricola = {
        "nome": nome_cognome,
        "matricola": matricola,
        "autore": interaction.user.display_name
    }
    lista_db.append(dati_matricola)

    embed = discord.Embed(
        title=f"🪪 REGISTRAZIONE MATRICOLA - {nome_corpo}",
        description="È stata registrata con successo una nuova matricola.",
        color=colore
    )
    embed.add_field(name="Nome e Cognome", value=nome_cognome, inline=True)
    embed.add_field(name="Matricola", value=matricola, inline=True)
    embed.set_footer(text=f"Registrato da {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed, ephemeral=True)
    await registra_log_comando(interaction, f"Ha aggiunto la matricola ({nome_corpo}) per {nome_cognome} (Matricola: {matricola}).")

@bot.tree.command(name="matricola-list", description="Visualizza l'elenco delle matricole registrate per un corpo specifico")
async def matricola_list(interaction: discord.Interaction, corpo: str):
    if not check_ruoli_visualizza_matricole(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per visualizzare le liste delle matricole.", ephemeral=True)
        return

    corpo = corpo.lower().strip()
    
    mappatura = {
        "pds": ("Polizia di Stato (PDS)", db_matricole_pds, discord.Color.blue()),
        "cc": ("Carabinieri (CC)", db_matricole_cc, discord.Color.dark_blue()),
        "esercito": ("Esercito", db_matricole_eser, discord.Color.green()),
        "gdf": ("Guardia di Finanza (GDF)", db_matricole_gdf, discord.Color.gold()),
        "importante": ("Ruolo Importante", db_matricole_importante, discord.Color.purple())
    }

    if corpo not in mappatura:
        await interaction.response.send_message("Corpo non valido. Scegli tra: `pds`, `cc`, `esercito`, `gdf`, `importante`.", ephemeral=True)
        return

    nome_corpo, lista_db, colore = mappatura[corpo]

    if not lista_db:
        embed = discord.Embed(
            title=f"📋 Elenco Matricole - {nome_corpo}",
            description="Al momento non ci sono matricole registrate per questo corpo.",
            color=colore
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await registra_log_comando(interaction, f"Ha visualizzato la lista matricole per {nome_corpo} (risultata vuota).")
        return

    embed = discord.Embed(
        title=f"📋 Elenco Ufficiale Matricole - {nome_corpo}",
        description=f"Totale registrati: **{len(lista_db)}**",
        color=colore
    )

    for idx, item in enumerate(lista_db, start=1):
        embed.add_field(
            name=f"#{idx} - {item['nome']}",
            value=f"**Matricola:** `{item['matricola']}`\n*Registrato da:* {item['autore']}",
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)
    await registra_log_comando(interaction, f"Ha visualizzato la lista matricole per {nome_corpo} ({len(lista_db)} elementi).")

@bot.tree.command(name="matricola-rimuovi", description="Rimuovi una matricola registrata specificando il corpo e la matricola")
async def matricola_rimuovi(interaction: discord.Interaction, corpo: str, matricola: str):
    if not check_ruoli_visualizza_matricole(interaction):
        await interaction.response.send_message("Non possiedi i ruoli necessari per rimuovere una matricola.", ephemeral=True)
        return

    corpo = corpo.lower().strip()
    
    mappatura = {
        "pds": ("Polizia di Stato (PDS)", db_matricole_pds),
        "cc": ("Carabinieri (CC)", db_matricole_cc),
        "esercito": ("Esercito", db_matricole_eser),
        "gdf": ("Guardia di Finanza (GDF)", db_matricole_gdf),
        "importante": ("Ruolo Importante", db_matricole_importante)
    }

    if corpo not in mappatura:
        await interaction.response.send_message("Corpo non valido. Scegli tra: `pds`, `cc`, `esercito`, `gdf`, `importante`.", ephemeral=True)
        return

    nome_corpo, lista_db = mappatura[corpo]

    tv = None
    for item in lista_db:
        if item['matricola'].lower() == matricola.lower():
            tv = item
            break

    if not tv:
        await interaction.response.send_message(f"Nessuna matricola trovata corrispondente a **{matricola}** nel corpo **{nome_corpo}**.", ephemeral=True)
        return

    lista_db.remove(tv)

    embed = discord.Embed(
        title="🗑️ MATRICOLA RIMOSSA",
        description=f"La matricola è stata eliminata con successo dal database.",
        color=discord.Color.red()
    )
    embed.add_field(name="Corpo", value=nome_corpo, inline=True)
    embed.add_field(name="Nome e Cognome", value=tv['nome'], inline=True)
    embed.add_field(name="Matricola Rimossa", value=f"`{tv['matricola']}`", inline=False)
    embed.set_footer(text=f"Rimosso da {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed, ephemeral=True)
    await registra_log_comando(interaction, f"Ha rimosso la matricola `{matricola}` dal corpo {nome_corpo}.")

@bot.tree.command(name="lista-commandi", description="Visualizza l'elenco completo di tutti i comandi disponibili")
async def lista_commandi(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 Elenco Comandi Disponibili",
        description="Ecco la lista di tutti i comandi configurati nel bot per le Forze dell'Ordine:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="⏱️ Gestione Turni",
        value=(
            "`/shift` - Apre il pannello interattivo per gestire il servizio\n"
            "`/shift_utente` - Visualizza le ore di servizio di un utente\n"
            "`/shift_gestisci` - Aggiunge o rimuove ore/minuti di servizio"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚖️ Gestione Personale e Sicurezza",
        value=(
            "`/licenziamento` - Solleva un utente dall'incarico e rimuove il ruolo\n"
            "`/ricercato` - Inserisce un soggetto nella lista dei ricercati\n"
            "`/ricercato-lista` - Visualizza la lista dei soggetti ricercati\n"
            "`/ricercato-rimuovi` - Rimuove un soggetto dai ricercati\n"
            "`/mandato` - Emetti un mandato ufficiale\n"
            "`/mandato-list` - Visualizza l'elenco dei mandati emessi\n"
            "`/mandato-modifica` - Modifica o rimuove un mandato esistente"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🚨 Stato di Allerta e Comunicazioni",
        value=(
            "`/allerta` - Visualizza lo stato di allerta attuale dello Stato\n"
            "`/allerta-modifica` - Modifica lo stato di allerta dello Stato\n"
            "`/allerta-configura` - Elimina/ripristina lo stato di allerta attuale\n"
            "`/allerta-modifica-elenco` - Panoramica rapida dei livelli di allerta\n"
            "`/annuncio` - Crea un annuncio ufficiale"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🪪 Gestione Matricole",
        value=(
            "`/matricola-pds` - Registra la matricola PDS\n"
            "`/matricola-cc` - Registra la matricola CC\n"
            "`/matricola-eser` - Registra la matricola Esercito\n"
            "`/matricola-gdf` - Registra la matricola Guardia di Finanza\n"
            "`/matricola-aggiungi` - Aggiunge una matricola specificando il corpo\n"
            "`/matricola-list` - Visualizza l'elenco matricole per corpo\n"
            "`/matricola-rimuovi` - Rimuove una matricola registrata"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🛠️ Utilità e Amministrazione",
        value=(
            "`/pulisci` - Elimina un determinato numero di messaggi\n"
            "`/verifica` - Invia il pannello per la verifica\n"
            "`/richiesta-ruolo` - Invia una richiesta per un ruolo specifico\n"
            "`/lista-commandi` - Mostra questo elenco di comandi"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"Richiesto da {interaction.user.display_name}")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    await registra_log_comando(interaction, "Ha visualizzato la lista completa dei comandi.")

@bot.event
async def setup_hook():
    await bot.tree.sync()

bot.run("MTU0ODY0Mzk5NDUwOTI1NDc2OQ.GGGs2z.s8Ix0dCP0G9H3HJUB9Xw9I2cSFxcubdilGA2Ic")
