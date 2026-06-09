# Tracker per Combattimenti in D&D 5e
import json

# Ogni combattente ha: nome, classe armatura (CA), HP attuali, HP massimi,
# HP temporanei (scudo extra che si consuma prima degli HP veri), iniziativa
# e una lista di condizioni attive (es. "Avvelenato", "Stordito").
class Combattente:
    def __init__(self, nome, ca, hpAttuali, hpMassimi, hpTemporanei, iniziativa):
        self.nome = nome
        self.ca = ca
        self.hpAttuali = hpAttuali
        self.hpMassimi = hpMassimi
        self.hpTemporanei = hpTemporanei
        self.iniziativa = iniziativa
        self.condizioni = []  # lista di dizionari {'Condizione': str, 'Durata': int}

    def subire_danno(self, danno):
        # Gli HP temporanei assorbono il danno per primi.
        # Se il danno supera gli HP temporanei, il resto va agli HP veri.
        if self.hpTemporanei > 0:
            danno_rimanente = danno - self.hpTemporanei
            self.hpTemporanei = max(0, self.hpTemporanei - danno)
            if danno_rimanente > 0:
                self.hpAttuali = max(0, self.hpAttuali - danno_rimanente)
        else:
            # Nessun HP temporaneo: il danno va direttamente agli HP attuali
            self.hpAttuali = max(0, self.hpAttuali - danno)

    def curare(self, cura):
        # La cura non può portare gli HP oltre il massimo
        self.hpAttuali = min(self.hpMassimi, self.hpAttuali + cura)

    def aggiungere_condizione(self, condizione, durata):
        # Aggiunge una condizione con una durata espressa in round
        self.condizioni.append({'Condizione': condizione, 'Durata': durata})

    def rimuovere_condizione(self, condizione):
        # Rimuove tutte le voci che corrispondono al nome della condizione
        self.condizioni = [c for c in self.condizioni if c['Condizione'] != condizione]

    def aggiungere_hp_temporanei(self, hp):
        # Gli HP temporanei non si sommano: si tiene solo il valore più alto
        if hp > self.hpTemporanei:
            self.hpTemporanei = hp

    def aggiornare_condizioni(self):
        # Chiamato alla fine del turno del combattente:
        # scala di 1 la durata di ogni condizione ed elimina quelle scadute
        for condizione in self.condizioni:
            condizione['Durata'] -= 1
        self.condizioni = [c for c in self.condizioni if c['Durata'] > 0]

    def to_dict(self):
        # Converte il combattente in un dizionario Python puro,
        # così json.dump() può scriverlo su file senza problemi.
        return {
            'nome': self.nome,
            'ca': self.ca,
            'hpAttuali': self.hpAttuali,
            'hpMassimi': self.hpMassimi,
            'hpTemporanei': self.hpTemporanei,
            'iniziativa': self.iniziativa,
            'condizioni': self.condizioni,
        }

    @classmethod
    def from_dict(cls, dati):
        # @classmethod riceve la classe stessa (cls) invece di un'istanza (self),
        # quindi può creare un oggetto nuovo senza che ne esista già uno.
        # Usato per ricostruire un Combattente da un dizionario letto da file JSON.
        c = cls(
            nome=dati['nome'],
            ca=dati['ca'],
            hpAttuali=dati['hpAttuali'],
            hpMassimi=dati['hpMassimi'],
            hpTemporanei=dati['hpTemporanei'],
            iniziativa=dati['iniziativa'],
        )
        # .get('condizioni', []) restituisce [] se la chiave manca nel file
        # (es. file salvato con una versione vecchia del codice)
        c.condizioni = dati.get('condizioni', [])
        return c


# Gestisce una sessione di combattimento: tiene traccia dei combattenti,
# del turno corrente e del round.
class Combattimento:
    def __init__(self):
        self.combattenti = []
        self.turno_attuale = 0   # indice del combattente che deve agire ora
        self.round_attuale = 1

    def aggiungere_combattente(self, combattente):
        # Dopo ogni aggiunta riordina la lista per iniziativa
        self.combattenti.append(combattente)
        self.ordinare_iniziativa()

    def ordinare_iniziativa(self):
        # Ordine decrescente: chi ha iniziativa più alta agisce prima
        self.combattenti.sort(key=lambda c: c.iniziativa, reverse=True)

    def prossimo_turno(self):
        if not self.combattenti:
            return None

        # Recupera il combattente di turno e aggiorna le sue condizioni
        combattente_corrente = self.combattenti[self.turno_attuale]
        combattente_corrente.aggiornare_condizioni()

        # Avanza l'indice; se torna a 0 significa che tutti hanno agito: nuovo round
        self.turno_attuale = (self.turno_attuale + 1) % len(self.combattenti)
        if self.turno_attuale == 0:
            self.round_attuale += 1

        return combattente_corrente


def salva_combattimento(combattimento, percorso):
    dati = {
        'turno_attuale': combattimento.turno_attuale,
        'round_attuale': combattimento.round_attuale,
        'combattenti': [c.to_dict() for c in combattimento.combattenti],
    }
    with open(percorso, 'w', encoding='utf-8') as f:
        json.dump(dati, f, ensure_ascii=False, indent=2)


def carica_combattimento(percorso):
    with open(percorso, 'r', encoding='utf-8') as f:
        dati = json.load(f)
    combattimento = Combattimento()
    combattimento.combattenti = [Combattente.from_dict(c) for c in dati['combattenti']]
    combattimento.turno_attuale = dati['turno_attuale']
    combattimento.round_attuale = dati['round_attuale']
    return combattimento
