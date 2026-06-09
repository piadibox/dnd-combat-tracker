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