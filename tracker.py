# Tracker per Combattimenti in D&D 5e

# Classe per rappresentare un combattente, che contiene nome, HP, CA, iniziativa e condizioni
class Combattente:
    def __init__(self, nome, ca, hpAttuali, hpMassimi, hpTemporanei, iniziativa):
        self.nome = nome
        self.ca = ca 
        self.hpAttuali = hpAttuali
        self.hpMassimi = hpMassimi
        self.hpTemporanei = hpTemporanei
        self.iniziativa = iniziativa
        self.condizioni = []
        
# Funzioni per subire danno, curare, aggiungere e rimuovere condizioni
    def subire_danno(self, danno):
        if self.hpTemporanei > 0:
            danno_rimanente = danno - self.hpTemporanei
            self.hpTemporanei = max(0, self.hpTemporanei - danno)
            if danno_rimanente > 0:
                self.hpAttuali = max(0, self.hpAttuali - danno_rimanente)
    
    def curare(self, cura):
        self.hpAttuali = min(self.hpMassimi, self.hpAttuali + cura)

    def aggiungere_condizione(self, condizione, durata):
        self.condizioni.append({'Condizione': condizione, 'Durata': durata})
    
    

    def rimuovere_condizione(self, condizione):
        self.condizioni = [c for c in self.condizioni if c['Condizione'] != condizione]

    def aggiungere_hp_temporanei(self, hp):
        if hp > self.hpTemporanei:
            self.hpTemporanei = hp

    def aggiornare_condizioni(self):
        for condizione in self.condizioni:
            condizione['Durata'] -= 1
        self.condizioni = [c for c in self.condizioni if c['Durata'] > 0]

# Classe per gestire il combattimento
class Combattimento:
    def __init__(self):
        self.combattenti = []
        self.turno_attuale = 0
        self.round_attuale = 1

    def aggiungere_combattente(self, combattente):
        self.combattenti.append(combattente)
        self.ordinare_iniziativa()

    def ordinare_iniziativa(self):
        self.combattenti.sort(key=lambda c: c.iniziativa, reverse=True)

    def prossimo_turno(self):
        if not self.combattenti:
            return None
        combattente_corrente = self.combattenti[self.turno_attuale]
        combattente_corrente.aggiornare_condizioni()
        self.turno_attuale = (self.turno_attuale + 1) % len(self.combattenti)
        if self.turno_attuale == 0:
            self.round_attuale += 1
        return combattente_corrente