from nim import train, play
import sys

# if run using format 'python play.py n'
# lets AI play n games for training
# otherwise, defaults to 10000 games

if len(sys.argv) == 2:
    n = int(sys.argv[1])
    ai = train(n)
else: 
    ai = train(10000)

play(ai)
