import sys
import os

sys.path.append(os.path.dirname("ccdexplorer_fundamentals"))
#
from ccdexplorer_fundamentals.cis import StandardIdentifiers, CIS, LoggedEvents
from rich import print

print(list(StandardIdentifiers))
