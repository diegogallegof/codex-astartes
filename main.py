from dotenv import load_dotenv
load_dotenv()

from core.calgar import Calgar
from agents.torias import Torias
from agents.cassius import Cassius
from agents.pythol import Pythol
from agents.tigurius import Tigurius
from agents.servitor import Servitor


def main():
    print("=" * 50)
    print("  CODEX ASTARTES — Ultramarines Security Chapter")
    print("  'Our struggle is not against flesh and blood,'")
    print("  'but against the powers of this dark world.'")
    print("=" * 50)
    print()

    calgar = Calgar()

    calgar.enlist(Torias(calgar))
    calgar.enlist(Cassius(calgar))
    calgar.enlist(Pythol(calgar))
    calgar.enlist(Tigurius(calgar))
    calgar.enlist(Servitor(calgar))

    calgar.deploy()
    calgar.stand_by()


if __name__ == "__main__":
    main()
